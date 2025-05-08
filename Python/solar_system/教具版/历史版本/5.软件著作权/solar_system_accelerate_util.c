#include <Python.h>
#include <math.h>
// 文档字符串
PyDoc_STRVAR(module_doc, u8"solar_system_accelerate_util模块，使用了C语言代码提升程序的性能，用于实现精细度更高的模拟。");
PyDoc_STRVAR(accelerate_doc, u8"accelerate(steps,G,dt,lst,sun_index)\n用法与solar_system - accelerate.py中的_acc_numba()函数相同。");

// accelerate函数
static PyObject* accelerate(PyObject* self, PyObject* args, PyObject* kwargs) {
    static char* keywords[] = {"steps", "G", "dt", "lst", "sun_index", NULL};
    int steps, sun_index;
    double G, dt, dx, dy, b;
    PyObject* lst_obj;

    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "iddOi", keywords, &steps, &G, &dt, &lst_obj, &sun_index)) {
        return NULL;
    }

    PyObject* lst = PySequence_Fast(lst_obj, "expected a sequence");
    if (lst == NULL) {
        return NULL;
    }

    Py_ssize_t len = PySequence_Fast_GET_SIZE(lst);
    double* lst_data = (double*)malloc(len * sizeof(double));
    if (lst_data == NULL) {
        Py_DECREF(lst);
        return PyErr_NoMemory();
    }

    for (Py_ssize_t i = 0; i < len; ++i) {
        PyObject* item = PySequence_Fast_GET_ITEM(lst, i);
        lst_data[i] = PyFloat_AsDouble(item);
        if (PyErr_Occurred()) {
            free(lst_data);
            Py_DECREF(lst);
            return NULL;
        }
    }

    // 由Python的代码改编而来
    for (int _ = 0; _ < steps; ++_) {
        int index = sun_index * 7;
        int i, j;
        for (i = 0; i < len; i += 7) {
            for (j = i + 7; j < len; j += 7) {
                dx = lst_data[j + 1] - lst_data[i + 1];
                dy = lst_data[j + 2] - lst_data[i + 2];
                if ( !(dx == 0 && dy == 0) ) {
                    b = G / pow(sqrt(dx * dx + dy * dy), 3);
                    if (sun_index == -1 || i != index) {
                        lst_data[i + 5] += b * dx * lst_data[j + 0];
                        lst_data[i + 6] += b * dy * lst_data[j + 0];
                    }
                    lst_data[j + 5] -= b * dx * lst_data[i + 0];
                    lst_data[j + 6] -= b * dy * lst_data[i + 0];
                }
            }
        }
        for (i = 0; i < len; i += 7) {
            lst_data[i + 3] += dt * lst_data[i + 5];
            lst_data[i + 4] += dt * lst_data[i + 6];
            lst_data[i + 5] = lst_data[i + 6] = 0;

            lst_data[i + 1] += dt * lst_data[i + 3];
            lst_data[i + 2] += dt * lst_data[i + 4];
        }
    }

    PyObject* result = PyList_New(len);
    for (Py_ssize_t i = 0; i < len; ++i) {
        PyObject* value = PyFloat_FromDouble(lst_data[i]);
        PyList_SET_ITEM(result, i, value);
    }

    free(lst_data);
    Py_DECREF(lst);
    return result;
}

static PyMethodDef module_functions[] = {
    {"accelerate", (PyCFunction)accelerate, METH_VARARGS | METH_KEYWORDS, accelerate_doc},
    {NULL, NULL, 0, NULL} /* marks end of array */
};

int exec_mod(PyObject *module) {
    PyModule_AddFunctions(module, module_functions);
    // 加入版本信息
    PyModule_AddStringConstant(module, "__version__", "1.3.3");
    return 0; /* success */
}

static PyModuleDef_Slot module_slots[] = {
    { Py_mod_exec, exec_mod },
    { 0, NULL }
};

static struct PyModuleDef module_def = {
    PyModuleDef_HEAD_INIT,
    "solar_system_accelerate_util",
    module_doc,
    0,              /* m_size */
    NULL,           /* m_methods */
    module_slots,
    NULL,           /* m_traverse */
    NULL,           /* m_clear */
    NULL,           /* m_free */
};

PyMODINIT_FUNC PyInit_solar_system_accelerate_util() {
    return PyModuleDef_Init(&module_def);
}