#include <Python.h>

PyDoc_STRVAR(convptr_doc, "convptr(pointer)"
"\n"
"Convert a integer pointer to a Python object,as a reverse of id()."
"\xe5\xb0\x86\xe6\x95\xb4\xe6\x95\xb0\xe6\x8c\x87\xe9\x92\x88\xe8\xbd\xac\xe6\x8d\xa2\xe4\xb8\xbaPython\xe5\xaf\xb9\xe8\xb1\xa1\xef\xbc\x8c\xe4\xb8\x8eid()\xe7\x9b\xb8\xe5\x8f\x8d\xe3\x80\x82\n"
"Warning:converting an invalid pointer may cause crashing."); //Unicode表示的中文: 将整数指针转换为Python对象，与id()相反。
PyDoc_STRVAR(py_inc_doc, "py_incref(object,n)"
"\n"
"Increase the reference count of an object for n."
"\xe5\xb0\x86\xe5\xaf\xb9\xe8\xb1\xa1\xe7\x9a\x84\xe5\xbc\x95\xe7\x94\xa8\xe8\xae\xa1\xe6\x95\xb0\xe5\xa2\x9e\xe5\x8a\xa0n\xe3\x80\x82\n"
"Warning:improper using of this function may cause Python to crash.");//将对象的引用计数增加n。
PyDoc_STRVAR(py_dec_doc, "py_decref(object,n)"
"\n"
"Decrease the reference count of an object for n."
"\xe5\xb0\x86\xe5\xaf\xb9\xe8\xb1\xa1\xe7\x9a\x84\xe5\xbc\x95\xe7\x94\xa8\xe8\xae\xa1\xe6\x95\xb0\xe5\x87\x8f\xe5\xb0\x8fn\xe3\x80\x82\n"
"Warning:improper using of this function may cause Python to crash.");//将对象的引用计数减小n。


PyObject* pyobj_extension_convptr(PyObject* self, PyObject* args, PyObject* kwargs) {
    PyObject* obj = NULL;
    unsigned long long number = 0; // long类型在32位可用, 在64位会引发OverflowError

    /* Parse positional and keyword arguments */
    static char* keywords[] = { "pointer", NULL };
    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "L", keywords, &number)) {
        return NULL;
    }

    /* Function implementation starts here */
    obj = (PyObject*)number;
    return obj;
}
PyObject* py_incref(PyObject* self, PyObject* args, PyObject* kwargs) {
    PyObject *obj = NULL;
    unsigned int n;

    static char* keywords[] = { "object", "n", NULL};
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

/*
 * List of functions to add to pyobj_extension in exec_pyobj_extension().
 */
static PyMethodDef pyobj_extension_functions[] = {
    { "convptr", (PyCFunction)pyobj_extension_convptr, METH_VARARGS | METH_KEYWORDS, convptr_doc },
    { "py_incref", (PyCFunction)py_incref, METH_VARARGS | METH_KEYWORDS, py_inc_doc },
    { "py_decref", (PyCFunction)py_decref, METH_VARARGS | METH_KEYWORDS, py_dec_doc },
    { NULL, NULL, 0, NULL } /* marks end of array */
};

/*
 * Initialize pyobj_extension. May be called multiple times, so avoid
 * using static state.
 */
int exec_pyobj_extension(PyObject *module) {
    PyModule_AddFunctions(module, pyobj_extension_functions);

    PyModule_AddStringConstant(module, "__author__", "qfcy");
    PyModule_AddStringConstant(module, "__version__", "1.2.1");

    return 0; /* success */
}

/* Documentation for pyobj_extension. */

// 模块 pyobj_extension - pyobject库的扩展模块, 主要包含操作Python底层对象引用, 以及对象指针的函数, 使用 C语言编写
PyDoc_STRVAR(pyobj_extension_doc, "\xe6\xa8\xa1\xe5\x9d\x97 pyobj_extension - pyobject\xe5\xba\x93\xe7\x9a\x84\xe6\x89\xa9\xe5\xb1\x95\xe6\xa8\xa1\xe5\x9d\x97, \xe4\xb8\xbb\xe8\xa6\x81\xe5\x8c\x85\xe5\x90\xab\xe6\x93\x8d\xe4\xbd\x9cPython\xe5\xba\x95\xe5\xb1\x82\xe5\xaf\xb9\xe8\xb1\xa1\xe5\xbc\x95\xe7\x94\xa8, \xe4\xbb\xa5\xe5\x8f\x8a\xe5\xaf\xb9\xe8\xb1\xa1\xe6\x8c\x87\xe9\x92\x88\xe7\x9a\x84\xe5\x87\xbd\xe6\x95\xb0, \xe4\xbd\xbf\xe7\x94\xa8 C\xe8\xaf\xad\xe8\xa8\x80\xe7\xbc\x96\xe5\x86\x99");


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
