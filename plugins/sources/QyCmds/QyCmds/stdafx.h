#pragma once
#include <vector>
#include <memory>
#include <algorithm>
#include <functional>

#include <maya/MGlobal.h>
#include <maya/MSelectionList.h>

#include <maya/MFnPlugin.h>
#include <maya/MPxCommand.h>
#include <maya/MSyntax.h>
#include <maya/MArgParser.h>
#include <maya/MArgList.h>

#include <maya/MObject.h>
#include <maya/MObjectHandle.h>
#include <maya/MPlug.h>
#include <maya/MDagPath.h>
#include <maya/MDagModifier.h>

#include <maya/MFnDependencyNode.h>
#include <maya/MFnDagNode.h>
#include <maya/MFnTransform.h>

#include <maya/MItDependencyNodes.h>
#include <maya/MItDag.h>

#include <maya/MVector.h>
#include <maya/MPoint.h>
