#include "stdafx.h"
#include "QmMeshSetVertexColors.h"
#include "node_utils.h"
#include "component_utils.h"
#include "array_utils.h"
#include "nodetypes.h"
#include <iostream>
#include <string>

MSyntax QmMeshSetVertexColors::CreateSyntax() {
	MSyntax syntax;
	syntax.addArg(MSyntax::kString);

	syntax.addFlag("m", "mesh", MSyntax::kString);

	syntax.addFlag("v", "vertices", MSyntax::kLong);
	syntax.makeFlagMultiUse("v");

	syntax.addFlag("c", "colors", MSyntax::kDouble, MSyntax::kDouble, MSyntax::kDouble, MSyntax::kDouble);
	syntax.makeFlagMultiUse("c");

	return syntax;
}

MStatus QmMeshSetVertexColors::ParseArguments(const ArgParser& parser) {
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

	parser.SelectFlagArguments<MColorArray, MColor>(&colors_, "c", [](auto args) {
		MColor color;
		color.r = static_cast<float>(args.asDouble(0));
		color.g = static_cast<float>(args.asDouble(1));
		color.b = static_cast<float>(args.asDouble(2));
		color.a = static_cast<float>(args.asDouble(3));
		return color;
	});

	status = parser.FlagArguments(&vertices_, "v");
	if (!status) {
		return status;
	}
	if (vertices_.length() == 0) {
		MGlobal::displayError("one or more vertex indices must be specified");
		return MStatus::kFailure;
	}

	return MStatus::kSuccess;
}

MStatus QmMeshSetVertexColors::redoIt() {
	if (vertices_.length() != colors_.length()) {
		MColorArray colors(vertices_.length());
		const auto base_color_length = colors_.length();
		for (auto i = 0U; i < vertices_.length(); ++i) {
			colors[i] = colors_[i % base_color_length];
		}
		colors_ = colors;
	}

	MFnMesh mfn(mesh_);
	mfn.setVertexColors(colors_, vertices_, &modifier_);

	auto status = modifier_.doIt();
	if (!status) {
		return status;
	}

	return MStatus::kSuccess;
}

MStatus QmMeshSetVertexColors::undoIt() {
	return modifier_.undoIt();
}
