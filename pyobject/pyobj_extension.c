#include <Python.h>

PyDoc_STRVAR(convptr_doc, u8"convptr(pointer)"
    u8"\n"
    u8"Convert a integer pointer to a Python object, as a reverse of id()."
    u8"将整数指针转换为Python对象，与id()相反。\n"
    u8"Warning:Converting an invalid pointer may lead to crashes.");
PyDoc_STRVAR(py_inc_doc, u8"py_incref(obj)"
    u8"\n"
    u8"Increase the reference count of an object."
    u8"将对象的引用计数增加1。\n"
    u8"Warning:Improper use of this function may lead to crashes.");
PyDoc_STRVAR(py_dec_doc, u8"py_decref(obj)"
    u8"\n"
    u8"Decrease the reference count of an object."
    u8"将对象的引用计数减小1。\n"
    u8"Warning:Improper use of this function may lead to crashes.");
PyDoc_STRVAR(getrealref_doc, u8"getrealrefcount(obj)"
    u8"\n"
    u8"Get the actual reference count of an object before calling getrealrefcount(). Unlike "
    u8"sys.getrefcount(), this function ignores the reference count increase when called.\n"
    u8"获取调用本函数前对象的实际引用计数。和sys.getrefcount()不同，不考虑调用时新增的引用计数。");
PyDoc_STRVAR(setref_doc, u8"setrefcount(obj, n)"
    u8"\n"
    u8"Set the actual reference count of an object before calling setrefcount() to n, "
    u8"as a reverse of getrealrefcount().\n"
    u8"设置对象的实际引用计数(调用函数前)为n，和getrealrefcount()相反。\n"
    u8"Warning:Improper use of this function may lead to crashes.");
PyDoc_STRVAR(list_in_doc, u8"list_in(obj, lst)"
    u8"\n"
    u8"判断obj是否在列表或元组lst中。\n与Python内置的obj in lst调用多次\"==\"运算符(__eq__)相比，"
    u8"本函数直接比较对象的指针，提高了效率。\n"
    u8"Determine whether `obj` is in the sequence `lst`.\nCompared to the built-in "
    u8"Python call `obj in lst` that invokes the `==` operator (__eq__) multiple times, "
    u8"this function directly compares the pointers to improve efficiency.");

static const int REFCNT_DELTA=2; // 调用时新增的引用计数
PyObject* convptr(PyObject* self, PyObject* args) {
    PyObject* obj = NULL;
    size_t num = 0;
    if (!PyArg_ParseTuple(args,((sizeof(void*)==8)?"K":"k"), &num)) { // 同时兼容32和64位
        return NULL;
    }

    obj = (PyObject*)num; // 获取指针对应的Python对象
    Py_INCREF(obj);
    return obj;
}
PyObject* py_incref(PyObject* self, PyObject* args) {
    PyObject* obj = NULL;
    if (!PyArg_ParseTuple(args, "O", &obj)) {
        return NULL;
    }

    Py_INCREF(obj);
    Py_RETURN_NONE;
}
PyObject* py_decref(PyObject* self, PyObject* args) {
    PyObject* obj = NULL;
    if (!PyArg_ParseTuple(args, "O", &obj)) {
        return NULL;
    }

    Py_DECREF(obj);
    Py_RETURN_NONE;
}
PyObject* getrealrefcount(PyObject* self, PyObject* args) {
    PyObject *obj;
    if (!PyArg_ParseTuple(args,"O",&obj)){
        return NULL;
    }
    return PyLong_FromSsize_t(obj->ob_refcnt-REFCNT_DELTA);
}
PyObject* setrefcount(PyObject* self, PyObject* args, PyObject* kwargs) {
    PyObject *obj;Py_ssize_t n;
    static char* keywords[]={"obj","n",NULL};
    if (!PyArg_ParseTupleAndKeywords(args,kwargs,"On",keywords,&obj,&n)){
        return NULL;
    }
    obj->ob_refcnt=n+REFCNT_DELTA;
    Py_RETURN_NONE;
}
PyObject* list_in(PyObject* self, PyObject* args, PyObject* kwargs) {
    PyObject *obj, *lst_obj;
    // 解析输入参数，参数为待查找对象和一个序列(列表或元组)
    static char* keywords[] = {"obj", "lst", NULL};
    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "OO", keywords, &obj, &lst_obj)) {
        return NULL;
    }
    PyObject *lst = PySequence_Fast(lst_obj, "expect a sequence");
    Py_ssize_t n = PySequence_Fast_GET_SIZE(lst);
    PyObject* item;

    for (Py_ssize_t i = 0; i < n; ++i) {
        item = PySequence_Fast_GET_ITEM(lst, i);  // 获取索引i的元素
        if (obj == item) {
            Py_DECREF(lst);
            Py_RETURN_TRUE;
        }
    }

    Py_DECREF(lst);
    Py_RETURN_FALSE;
}
PyObject* _list_setnull(PyObject* self, PyObject* args) {
    PyObject* list;Py_ssize_t index;
    if (!PyArg_ParseTuple(args, "On", &list, &index)) return NULL; 
    if (!PyList_Check(list)) {
        PyErr_SetString(PyExc_TypeError, "Expected a list");
        return NULL;
    }

    if(PyList_SetItem(list, index, NULL) < 0) return NULL;
    Py_RETURN_NONE;
}

/*
 * List of functions to add to pyobj_extension in exec_pyobj_extension().
 */
static PyMethodDef pyobj_extension_functions[] = {
    { "convptr", (PyCFunction)convptr, METH_VARARGS, convptr_doc },
    { "py_incref", (PyCFunction)py_incref, METH_VARARGS, py_inc_doc },
    { "py_decref", (PyCFunction)py_decref, METH_VARARGS, py_dec_doc },
    { "getrealrefcount", (PyCFunction)getrealrefcount, METH_VARARGS, getrealref_doc },
    { "setrefcount", (PyCFunction)setrefcount, METH_VARARGS | METH_KEYWORDS, setref_doc },
    { "list_in", (PyCFunction)list_in, METH_VARARGS | METH_KEYWORDS, list_in_doc },
    { "_list_setnull", (PyCFunction)_list_setnull, METH_VARARGS, "_list_setnull(lst,index)"},
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
