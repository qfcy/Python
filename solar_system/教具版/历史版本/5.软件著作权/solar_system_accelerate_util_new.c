#include <Python.h>
#include <math.h>
// 文档字符串
PyDoc_STRVAR(module_doc, u8"solar_system_accelerate_util模块，使用了C语言代码提升程序的性能，用于精细度更高的模拟。");
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

    PyObject* py_lst = PySequence_Fast(lst_obj, "expect a sequence");
    if (py_lst == NULL) {return NULL;}

    Py_ssize_t len = PySequence_Fast_GET_SIZE(py_lst);
	int n = len / 7;
	double** lst = (double**)malloc(n * sizeof(double*));
	if (lst == NULL) {
        Py_DECREF(py_lst);return PyErr_NoMemory();
    }
	for (int i = 0; i < n; i++) {
		lst[i] = (double*)malloc(7 * sizeof(double));
		if (lst[i] == NULL) {
			for (int j = i - 1; j >= 0; --j) {  
				free(lst[j]); // 分配失败时，释放已分配的内存
			}  
			free(lst);Py_DECREF(py_lst);
			return PyErr_NoMemory();
		}
	}

    for (Py_ssize_t i = 0; i < len; ++i) {
        PyObject* item = PySequence_Fast_GET_ITEM(py_lst, i);
        lst[i/8][i%8] = PyFloat_AsDouble(item);
        if (PyErr_Occurred()) {
			for (int j = n - 1; j >= 0; --j) {  
				free(lst[j]); // 释放内存
			}  
			free(lst);Py_DECREF(py_lst);
            return NULL;
        }
    }

    // 每个天体的7项分别是天体的质量，x、y坐标，x、y速度和x、y加速度
	// 进行引力模拟
	int i, j;
    for (int _ = 0; _ < steps; ++_) { // 迭代多次
        // 根据引力计算加速度
        for (i = 0; i < n; ++i) {
            for (j = i + 1; j < n; ++j) {
                dx = planets[j].x - planets[i].x;
                dy = planets[j].y - planets[i].y;
                if ( !(dx == 0 && dy == 0) ) { // 避免距离为0引发除零错误
                    b = G / pow(sqrt(dx * dx + dy * dy), 3);
                    if (planets[i].isStationary == 0) { // 不是不需要移动的太阳
                        planets[i].ax += b * dx * planets[j].m;
                        planets[i].ay += b * dy * planets[j].m;
                    }
                    planets[j].ax -= b * dx * planets[i].m;
                    planets[j].ay -= b * dy * planets[i].m;
                }
            }
        }
        // 根据加速度，计算速度和位移
        for (i = 0; i < n; ++i) {
            planets[i].dx += dt * planets[i].ax;
            planets[i].dy += dt * planets[i].ay;
            planets[i].ax = planets[i].ay = 0;

            planets[i].x += dt * planets[i].dx;
            planets[i].y += dt * planets[i].dy;
        }
    }

	// 以Python列表类型返回结果
    PyObject* result = PyList_New(len);
    for (int i = 0; i < n; ++i) {
		for (int j = 0; j < 7; ++j) {
			PyObject* value = PyFloat_FromDouble(lst[i][j]);
			Py_ssize_t index = i * 7 + j;
			PyList_SET_ITEM(result, index, value);
		}
    }
	for (int i = n - 1; i >= 0; --i) {  
        free(lst[i]); // 释放内存
    }  
    free(lst);
    Py_DECREF(py_lst);
    return result;
}

static PyMethodDef module_functions[] = {
    {"accelerate", (PyCFunction)accelerate, METH_VARARGS | METH_KEYWORDS, accelerate_doc},
    {NULL, NULL, 0, NULL} /* marks end of array */
};

int exec_mod(PyObject *module) { // 在加载模块时执行
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