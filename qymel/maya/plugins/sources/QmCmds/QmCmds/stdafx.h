#pragma once
#include <vector>
#include <memory>
#include <string>
#include <algorithm>
#include <functional>

#include <maya/MGlobal.h>
#include <maya/MSelectionList.h>

#include <maya/MFnPlugin.h>
#include <maya/MPxCommand.h>
#include <maya/MSyntax.h>
#include <maya/MArgParser.h>
#include <maya/MArgList.h>
#include <maya/MArgDatabase.h>

#include <maya/MObject.h>
#include <maya/MObjectHandle.h>
#include <maya/MPlug.h>
#include <maya/MDagPath.h>
#include <maya/MDagPathArray.h>
#include <maya/MDagModifier.h>

#include <maya/MFnDependencyNode.h>
#include <maya/MFnDagNode.h>
#include <maya/MFnTransform.h>
#include <maya/MFnMesh.h>
#include <maya/MFnSkinCluster.h>
#include <maya/MFnSingleIndexedComponent.h>
#include <maya/MFnDoubleIndexedComponent.h>
#include <maya/MFnTripleIndexedComponent.h>

#include <maya/MItDependencyNodes.h>
#include <maya/MItDag.h>
#include <maya/MItMeshPolygon.h>

#include <maya/MVector.h>
#include <maya/MVectorArray.h>
#include <maya/MPoint.h>
#include <maya/MFloatArray.h>
#include <maya/MFloatVector.h>
#include <maya/MFloatVectorArray.h>
#include <maya/MColor.h>
#include <maya/MColorArray.h>
#include <maya/MPointArray.h>

template<class T>
inline void SafeDelete(T** pp_object) {
    if (*pp_object == nullptr) {
        return;
    }
    delete* pp_object;
    *pp_object = nullptr;
}
