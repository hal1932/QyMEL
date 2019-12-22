#include "stdafx.h"
#include "QmMeshSetNormals.h"
#include "node_utils.h"
#include "component_utils.h"
#include "array_utils.h"
#include "nodetypes.h"
#include <iostream>
#include <string>

MSyntax QmMeshSetNormals::CreateSyntax() {
	MSyntax syntax;
	syntax.addArg(MSyntax::kString);

	syntax.addFlag("m", "mesh", MSyntax::kString);

	syntax.addFlag("v", "vertices", MSyntax::kLong);
	syntax.makeFlagMultiUse("v");

	syntax.addFlag("vf", "faceVertices", MSyntax::kLong, MSyntax::kLong);
	syntax.makeFlagMultiUse("vf");

	syntax.addFlag("n", "normals", MSyntax::kDouble, MSyntax::kDouble, MSyntax::kDouble, MSyntax::kDouble);
	syntax.makeFlagMultiUse("n");

	return syntax;
}

MStatus QmMeshSetNormals::ParseArguments(const ArgParser& parser) {
	MStatus status;

	MString mesh_path;
	status = parser.getFlagArgument("mesh", 0, mesh_path);
	if (!status) {
		return status;
	}

	mesh_ = utils::GetDagPath(mesh_path, &status);
	if (!status) {
		return status;
	}

	status = mesh_.extendToShapeDirectlyBelow(0);
	if (!status) {
		return status;
	}

	parser.SelectFlagArguments<MVectorArray, MVector>(&normals_, "n", [](auto args) {
		MVector normal;
		normal.x = static_cast<float>(args.asDouble(0));
		normal.y = static_cast<float>(args.asDouble(1));
		normal.z = static_cast<float>(args.asDouble(2));
		return normal;
	});
	
	const auto use_vertices = parser.isFlagSet("v");
	const auto use_vtxfaces = parser.isFlagSet("vf");

	if (use_vertices && !use_vtxfaces) {
		status = parser.FlagArguments(&vertices_, "v");
		if (!status) {
			return status;
		}
		if (vertices_.length() == 0) {
			MGlobal::displayError("one or more vertex indices must be specified");
			return MStatus::kFailure;
		}
		if (vertices_.length() != normals_.length()) {
			MGlobal::displayError("equal numbers of vertices and normals must be specified");
			return MStatus::kFailure;
		}
	} else if (!use_vertices && use_vtxfaces) {
		parser.EnumerateFlagArguments("vf", [this](const MArgList& args) {
			auto index = 0U;
			const auto vtx_face = args.asIntArray(index);
			vtx_faces_.append(vtx_face);
		});
		status = parser.FlagArguments(&vtx_faces_, "vf");
		if (!status) {
			return status;
		}
		if (vtx_faces_.length() == 0) {
			MGlobal::displayError("one or more vtxFace indices must be specified");
			return MStatus::kFailure;
		}
		if (vtx_faces_.length() != normals_.length()) {
			MGlobal::displayError("equal numbers of vtxFace and normals must be specified");
			return MStatus::kFailure;
		}
	} else {
		MGlobal::displayError("either vertices or faces must be specified");
		return MStatus::kFailure;
	}

	return MStatus::kSuccess;
}

MStatus QmMeshSetNormals::redoIt() {
	MFnMesh mfn(mesh_);
	mfn.getNormals(old_normals_, MSpace::kObject);

	if (vertices_.length() > 0) {
		return mfn.setVertexNormals(normals_, vertices_, MSpace::kObject);
	}
	if (vtx_faces_.length() > 0) {
		return mfn.setFaceVertexNormals(normals_, vtx_faces_.faces, vtx_faces_.vertices, MSpace::kObject);
	}

	return MStatus::kFailure;
}

MStatus QmMeshSetNormals::undoIt() {
	MFnMesh mfn(mesh_);
	return mfn.setNormals(old_normals_, MSpace::kObject);
}
