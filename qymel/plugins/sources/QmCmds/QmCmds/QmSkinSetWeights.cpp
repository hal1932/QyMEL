#include "stdafx.h"
#include "QmSkinSetWeights.h"
#include "node_utils.h"
#include "component_utils.h"
#include "array_utils.h"
#include "nodetypes.h"
#include <iostream>
#include <string>

MSyntax QmSkinSetWeights::CreateSyntax() {
	MSyntax syntax;
	syntax.addArg(MSyntax::kString);

	syntax.addFlag("p", "path", MSyntax::kString);

	syntax.addFlag("c", "components", MSyntax::kLong);
	syntax.makeFlagMultiUse("c");

	syntax.addFlag("i", "influenceIndices", MSyntax::kLong);
	syntax.makeFlagMultiUse("i");

	syntax.addFlag("v", "values", MSyntax::kDouble);
	syntax.makeFlagMultiUse("v");

	return syntax;
}

MStatus QmSkinSetWeights::ParseArguments(const ArgParser& parser) {
	MIntArray components;
	auto status = parser.FlagArguments<MIntArray>(&components, "c");
	if (!status) {
		return status;
	}

	status = parser.FlagArguments(&influences_, "i");
	if (!status) {
		return status;
	}

	status = parser.FlagArguments(&values_, "v");
	if (!status) {
		return status;
	}

	MStringArray dagpaths;
	status = parser.FlagArguments(&dagpaths, "c");
	if (dagpaths.length() != 1) {
		MGlobal::displayError("a node path must be specified");
		return MStatus::kFailure;
	}

	dagpath_ = utils::GetDagPath(dagpaths[0], &status);
	if (!status) {
		status = dagpath_.extendToShape();
	}
	if (status.error()) {
		MGlobal::displayError("cannot retrieve shapes from " + dagpaths[0]);
		return MStatus::kFailure;
	}

	MStringArray args;
	status = parser.CommandArguments(&args);
	if (!status) {
		return status;
	}
	if (args.length() != 1) {
		MGlobal::displayError("a skinCluster name must be specified");
		return MStatus::kFailure;
	}

	cluster_ = utils::GetDependencyNode(args[0]);
	if (cluster_.isNull() || !cluster_.hasFn(MFn::kSkinClusterFilter)) {
		MGlobal::displayError(args[0] + " is not a valid skinCluster");
		return MStatus::kFailure;
	}

	if (components.length() == 0) {
		components_ = Mesh(dagpath_.node()).VertexComponents();
	} else {
		components_ = utils::ComponentsFromArray(MFn::kMeshVertComponent, components);
	}

	if (influences_.length() == 0) {
		influences_ = SkinCluster(cluster_).InfluenceObjectIndices();
	}

	return MStatus::kSuccess;
}

MStatus QmSkinSetWeights::redoIt() {
	MFnSkinCluster mfn(cluster_);
	return mfn.setWeights(dagpath_, components_, influences_, values_, false, &old_weights_);
}

MStatus QmSkinSetWeights::undoIt() {
	MFnSkinCluster mfn(cluster_);
	return mfn.setWeights(dagpath_, components_, influences_, old_weights_, false);
}
