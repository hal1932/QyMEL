#include <Python.h>
#include <maya/MFnPlugin.h>
#include <maya/MGlobal.h>
#include <maya/MItDag.h>
#include <maya/MObject.h>
#include <vector>

const char* kAUTHOR = "Siew Yi Liang";
const char* kVERSION = "1.0.0";
const char* kREQUIRED_API_VERSION = "Any";

PyObject* module = NULL;

static char MAYA_PYTHON_C_EXT_DOCSTRING[] = "An example Python C extension that makes use of Maya functionality.";
static const char HELLO_WORLD_MAYA_DOCSTRING[] = "Says hello world!";

void helloWorldMaya() {
	MGlobal::displayInfo("Hello world from the Maya Python C extension!");
	return;
}

static PyObject* pyHelloWorldMaya(PyObject* self, PyObject* args) {
	//const char* inputString;
	//if (!PyArg_ParseTuple(args, "s", &inputString)) {
	//	return NULL;
	//}

	std::vector<MObject> objs;
	MItDag ite(MItDag::kBreadthFirst);
	while (!ite.isDone()) {
		auto node = ite.currentItem();
		objs.push_back(node);
		ite.next();
	}

	PyObject* mobject_array;
	PyArg_ParseTuple(args, "O", &mobject_array);

	PyGILState_STATE pyGILState = PyGILState_Ensure();

	//helloWorldMaya();

	PyObject_CallMethod(mobject_array, (char*)"setLength", (char*)"(i)", objs.size());
	for (auto i = 0; i < objs.size(); ++i) {
		PyObject_CallMethod(mobject_array, (char*)"set", (char*)"(Oi)", objs[i], i);
	}

	//PyObject* result = Py_BuildValue("s", inputString);

	PyGILState_Release(pyGILState);

	return NULL;
}

static PyMethodDef mayaPythonCExtMethods[] = {
	{"hello_world_maya", pyHelloWorldMaya, METH_VARARGS, HELLO_WORLD_MAYA_DOCSTRING},
	{NULL, NULL, 0, NULL}
};

MStatus initializePlugin(MObject obj) {
	MFnPlugin plugin(obj, kAUTHOR, kVERSION, kREQUIRED_API_VERSION);
	if (!Py_IsInitialized()) {
		Py_Initialize();
	}

	if (Py_IsInitialized()) {
		PyGILState_STATE pyGILState = PyGILState_Ensure();

		module = Py_InitModule4("maya_python_c_ext",
			mayaPythonCExtMethods,
			MAYA_PYTHON_C_EXT_DOCSTRING,
			nullptr,
			PYTHON_API_VERSION);

		MGlobal::displayInfo("Registered Python bindings!");

		if (module == NULL) {
			return MStatus::kFailure;
		}
		Py_INCREF(module);

		PyGILState_Release(pyGILState);
	}

	return MStatus::kSuccess;
}


MStatus uninitializePlugin(MObject obj) {
	MStatus status;

	Py_DECREF(module);

	return status;
}