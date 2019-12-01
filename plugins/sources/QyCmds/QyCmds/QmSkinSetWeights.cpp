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
	const auto components = parser.FlagArguments<int>("c");
	const auto influences = parser.FlagArguments<int>("i");
	const auto values = parser.FlagArguments<float>("v");

	const auto dagpaths = parser.FlagArguments<MString>("p");
	if (dagpaths.size() != 1) {
		MGlobal::displayError("a node path must be specified");
		return MStatus::kFailure;
	}

	MStatus status;
	dagpath_ = utils::GetDagPath(dagpaths[0], &status);
	if (!status.error()) {
		status = dagpath_.extendToShape();
	}
	if (status.error()) {
		MGlobal::displayError("cannot retrieve shapes from " + dagpaths[0]);
		return MStatus::kFailure;
	}

	const auto args = parser.CommandArguments<MString>();
	if (args.size() != 1) {
		MGlobal::displayError("a skinCluster name must be specified");
		return MStatus::kFailure;
	}

	cluster_ = utils::GetDependencyNode(args[0]);
	if (cluster_.isNull() || !cluster_.hasFn(MFn::kSkinClusterFilter)) {
		MGlobal::displayError(args[0] + " is not a valid skinCluster");
		return MStatus::kFailure;
	}

	if (components.size() == 0) {
		components_ = Mesh(dagpath_.node()).VertexComponents();
	} else {
		components_ = utils::ComponentsFromStdVector(MFn::kMeshVertComponent, components);
	}

	if (influences.size() == 0) {
		influences_ = SkinCluster(cluster_).InfluenceObjectIndices();
	} else {
		utils::ArrayCopyFromStdVector(&influences_, influences);
	}

	utils::ArrayCopyFromStdVector(&values_, values);

	return MStatus::kSuccess;
}

MStatus QmSkinSetWeights::redoIt() {
	MFnSkinCluster mfn(cluster_);
	auto s = mfn.setWeights(dagpath_, components_, influences_, values_, false, &old_weights_);
	auto w = utils::ArrayToStdVector(old_weights_);
	return s;
}

MStatus QmSkinSetWeights::undoIt() {
	MFnSkinCluster mfn(cluster_);
	return mfn.setWeights(dagpath_, components_, influences_, old_weights_, false);
}
