#include <Python.h>
#include <math.h>

typedef struct{
    double m;
    double x;double y;
    double dx;double dy;
    double ax;double ay;
    int isStationary;
} Star;

inline void calc_acc(Star *planets,int n,double G){
    // 根据引力公式计算加速度
    for (int i = 0; i < n; i++) {
        for (int j = i + 1; j < n; j++) {
            double dx = planets[j].x - planets[i].x;
            double dy = planets[j].y - planets[i].y;
            if ( !(dx == 0 && dy == 0) ) { // 避免距离为0引发除零错误
                double b = G / pow(dx * dx + dy * dy, 1.5);
                if (planets[i].isStationary == 0) { // 不是不需要移动的太阳
                    planets[i].ax += b * dx * planets[j].m;
                    planets[i].ay += b * dy * planets[j].m;
                }
                planets[j].ax -= b * dx * planets[i].m;
                planets[j].ay -= b * dy * planets[i].m;
            }
        }
    }
}
void simulate(Star *planets,int n,double G,double dt,int steps){
    // 简单的欧拉法引力模拟
    for (int _ = 0; _ < steps; _++) { // 迭代多次
        calc_acc(planets,n,G);
        // 根据加速度，计算速度和位移
        for (int i = 0; i < n; i++) {
            planets[i].dx += dt * planets[i].ax;
            planets[i].dy += dt * planets[i].ay;
            planets[i].ax = planets[i].ay = 0; // 重置累加的加速度为0

            planets[i].x += dt * planets[i].dx;
            planets[i].y += dt * planets[i].dy;
        }
    }
}
void simulate_2RungeKutta(Star *planets,int n,double G,double dt,int steps){
    // 2阶龙格-库塔法的引力模拟 (备用)
    double *x1=(double *)malloc(sizeof(double)*n);double *y1=(double *)malloc(sizeof(double)*n);
    double *ax1=(double *)malloc(sizeof(double)*n);double *ay1=(double *)malloc(sizeof(double)*n);
    double *dx1=(double *)malloc(sizeof(double)*n);double *dy1=(double *)malloc(sizeof(double)*n);
    for (int _ = 0; _ < steps; _++) {
        calc_acc(planets,n,G);
        for (int i = 0; i < n; i++) {
            x1[i]=planets[i].x;y1[i]=planets[i].y;
            ax1[i]=planets[i].ax;ay1[i]=planets[i].ay;
            dx1[i]=planets[i].dx;dy1[i]=planets[i].dy;

            planets[i].dx += dt * planets[i].ax;
            planets[i].dy += dt * planets[i].ay;
            planets[i].ax = planets[i].ay = 0;

            planets[i].x += dt * (dx1[i]+planets[i].dx)/2;
            planets[i].y += dt * (dy1[i]+planets[i].dy)/2;
        }
        calc_acc(planets,n,G); // 计算预估的下一状态的加速度
        for (int i = 0; i < n; i++) {
            planets[i].dx = dx1[i] + dt * (ax1[i]+planets[i].ax)/2;
            planets[i].dy = dy1[i] + dt * (ay1[i]+planets[i].ay)/2;
            planets[i].ax = planets[i].ay = 0;

            planets[i].x = x1[i] + dt * (dx1[i]+planets[i].dx)/2;
            planets[i].y = y1[i] + dt * (dy1[i]+planets[i].dy)/2;
        }
    }
    free(x1);free(y1);free(ax1);
    free(ay1);free(dx1);free(dy1);
}

// -- Python接口部分 --
PyDoc_STRVAR(module_doc, u8"solar_system_accelerate_util模块，使用了C代码提升计算的性能，用于精细度更高的模拟。");
PyDoc_STRVAR(accelerate_doc, u8"accelerate(planets,G,dt,steps,sun_type)\n用于加速引力模拟的计算。");

#define GET_ATTR(c_obj,obj,attr) \
{\
	PyObject *val=PyObject_GetAttrString((obj),#attr);\
	(c_obj).attr=PyFloat_AsDouble(val);\
	Py_DECREF(val);\
}
#define SET_ATTR(c_obj,obj,attr) \
{\
	PyObject *val=PyFloat_FromDouble((c_obj).attr);\
    PyObject_SetAttrString((obj), #attr, val);\
	Py_DECREF(val);\
}

// accelerate函数
static PyObject* accelerate(PyObject* self, PyObject* args, PyObject* kwargs) {
    static char* keywords[] = {"planets", "G", "dt", "steps", "sun_type", NULL};
    int steps; double G, dt;
    PyObject *lst, *sun_type;

    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "OddiO", keywords, &lst, &G, &dt, 
		&steps, &sun_type)) {
        return NULL;
    }

    PyObject *lst_obj = PySequence_Fast(lst, "expect a sequence");
    if (lst_obj == NULL) {return NULL;}

    Py_ssize_t n = PySequence_Fast_GET_SIZE(lst_obj);
	Star *planets = (Star*)malloc(n * sizeof(Star));
	if (planets == NULL) {
        Py_DECREF(lst_obj);return PyErr_NoMemory();
    }

    for (Py_ssize_t i = 0; i < n; ++i) {
        PyObject *star = PySequence_Fast_GET_ITEM(lst_obj, i);
		GET_ATTR(planets[i],star,m);
		GET_ATTR(planets[i],star,x);
		GET_ATTR(planets[i],star,y);
		GET_ATTR(planets[i],star,dx);
		GET_ATTR(planets[i],star,dy);
		planets[i].ax = planets[i].ay = 0;
        planets[i].isStationary = PyObject_IsInstance(star,sun_type);

        if (PyErr_Occurred()) {
			free(planets);Py_DECREF(lst_obj);
            return NULL;
        }
    }

	// 进行引力模拟
    simulate(planets,n,G,dt,steps);

	// 修改行星的属性，返回结果
    for (Py_ssize_t i = 0; i < n; ++i) {
        PyObject *star = PySequence_Fast_GET_ITEM(lst_obj, i);

		SET_ATTR(planets[i],star,m);
		SET_ATTR(planets[i],star,x);
		SET_ATTR(planets[i],star,y);
		SET_ATTR(planets[i],star,dx);
		SET_ATTR(planets[i],star,dy);

        if (PyErr_Occurred()) {
            free(planets);Py_DECREF(lst_obj);
            return NULL;
        }
    }
    free(planets);
	Py_DECREF(lst_obj);
    Py_RETURN_NONE; // 函数不返回值，直接修改列表planets
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