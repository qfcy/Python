#include <Python.h>

PyDoc_STRVAR(convptr_doc, u8"convptr(pointer)"
    u8"\n"
    u8"Convert a integer pointer to a Python object,as a reverse of id()."
    u8"将整数指针转换为Python对象，与id()相反。\n"
    u8"Warning:Converting an invalid pointer may lead to crashes.");
PyDoc_STRVAR(py_inc_doc, u8"py_incref(object, n)"
    u8"\n"
    u8"Increase the reference count of an object for n."
    u8"将对象的引用计数增加n。\n"
    u8"Warning:Improper use of this function may lead to crashes.");
PyDoc_STRVAR(py_dec_doc, u8"py_decref(object, n)"
    u8"\n"
    u8"Decrease the reference count of an object for n."
    u8"将对象的引用计数减小n。\n"
    u8"Warning:Improper use of this function may lead to crashes.");
PyDoc_STRVAR(py_list_in_doc, u8"list_in(obj, lst)"
    u8"\n"
    u8"判断obj是否在列表或元组lst中。\n与Python内置的obj in lst调用多次\"==\"运算符(__eq__)相比，"
    u8"本函数直接比较对象的指针，提高了效率。\n");

PyObject* pyobj_extension_convptr(PyObject* self, PyObject* args, PyObject* kwargs) {
    PyObject* obj = NULL;
    unsigned long long number = 0; // 若使用long类型，则64位会引发OverflowError

    static char* keywords[] = { "pointer", NULL };
    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "L", keywords, &number)) {
        return NULL;
    }

    obj = (PyObject*)number; // 获取指针对应的Python对象
    return obj;
}
PyObject* py_incref(PyObject* self, PyObject* args, PyObject* kwargs) {
    PyObject* obj = NULL;
    unsigned int n;

    static char* keywords[] = { "object", "n", NULL };
    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "OI", keywords, &obj, &n)) {
        return NULL;
    }

    for (unsigned int i = 0; i < n; i++) { Py_INCREF(obj); }
    return Py_None;
}
PyObject* py_decref(PyObject* self, PyObject* args, PyObject* kwargs) {
    PyObject* obj = NULL;
    unsigned int n;

    static char* keywords[] = { "object", "n", NULL };
    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "OI", keywords, &obj, &n)) {
        return NULL;
    }

    for (unsigned int i = 0; i < n; i++) { Py_DECREF(obj); }
    return Py_None;
}
PyObject* list_in(PyObject* self, PyObject* args, PyObject* kwargs) {
    PyObject *obj, *lst;

    // 解析输入参数，参数为待查找对象和一个序列(列表或元组)
    static char* keywords[] = { "obj", "lst", NULL };
    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "OO", keywords, &obj, &lst)) {
        return NULL;
    }

    // 确保输入是列表或元组
    if (!PyList_Check(lst) && !PyTuple_Check(lst)) {
        PyErr_SetString(PyExc_TypeError, "Expected a list or a tuple");
        return NULL;
    }

    Py_ssize_t n = PySequence_Size(lst);
    PyObject* item;

    for (Py_ssize_t i = 0; i < n; ++i) {
        item = PySequence_GetItem(lst, i);  // 获取索引i的元素
        if (obj == item) {
            Py_RETURN_TRUE;
        }
    }

    Py_RETURN_FALSE;
}

/*
 * List of functions to add to pyobj_extension in exec_pyobj_extension().
 */
static PyMethodDef pyobj_extension_functions[] = {
    { "convptr", (PyCFunction)pyobj_extension_convptr, METH_VARARGS | METH_KEYWORDS, convptr_doc },
    { "py_incref", (PyCFunction)py_incref, METH_VARARGS | METH_KEYWORDS, py_inc_doc },
    { "py_decref", (PyCFunction)py_decref, METH_VARARGS | METH_KEYWORDS, py_dec_doc },
    { "list_in", (PyCFunction)list_in, METH_VARARGS | METH_KEYWORDS, py_list_in_doc },
    { NULL, NULL, 0, NULL } /* marks end of array */
};

/*
 * Initialize pyobj_extension. May be called multiple times, so avoid
 * using static state.
 */
int exec_pyobj_extension(PyObject* module) {
    PyModule_AddFunctions(module, pyobj_extension_functions);

    PyModule_AddStringConstant(module, "__author__", "qfcy");
    PyModule_AddStringConstant(module, "__version__", "1.2.1");

    return 0; /* success */
}

/* Documentation for pyobj_extension. */
PyDoc_STRVAR(pyobj_extension_doc, u8"模块 pyobj_extension - pyobject库的C扩展模块, 提供一系列操作Python对象底层的函数。");

static PyModuleDef_Slot pyobj_extension_slots[] = {
    { Py_mod_exec, exec_pyobj_extension },
    { 0, NULL }
};

static PyModuleDef pyobj_extension_def = {
    PyModuleDef_HEAD_INIT,
    "pyobj_extension",
    pyobj_extension_doc,
    0,              /* m_size */
    NULL,           /* m_methods */
    pyobj_extension_slots,
    NULL,           /* m_traverse */
    NULL,           /* m_clear */
    NULL,           /* m_free */
};

PyMODINIT_FUNC PyInit_pyobj_extension() {
    return PyModuleDef_Init(&pyobj_extension_def);
}
