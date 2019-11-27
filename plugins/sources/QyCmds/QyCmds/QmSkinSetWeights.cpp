#include "stdafx.h"
#include "QmSkinSetWeights.h"


MSyntax QmSkinSetWeights::CreateSyntax() {
	MSyntax syntax;
	syntax.addArg(MSyntax::kString);

	syntax.addFlag("c", "components", MSyntax::kLong);
	syntax.makeFlagMultiUse("c");

	syntax.addFlag("i", "influenceIndices", MSyntax::kLong);
	syntax.makeFlagMultiUse("i");

	syntax.addFlag("v", "values", MSyntax::kDouble);
	syntax.makeFlagMultiUse("v");

	return syntax;
}

MStatus QmSkinSetWeights::ParseArguments(const ArgParser& parser) {
	components_.clear();
	influences_.clear();
	values_.clear();

	parser.EnumerateFlagArgumentList("c", [this](const MArgList& args) { components_.push_back(args.asInt(0)); });
	parser.EnumerateFlagArgumentList("i", [this](const MArgList& args) { influences_.push_back(args.asInt(0)); });
	parser.EnumerateFlagArgumentList("v", [this](const MArgList& args) { values_.push_back(args.asDouble(0)); });

	return MStatus::kSuccess;
}

MStatus QmSkinSetWeights::redoIt() {
	return MStatus::kSuccess;
}

MStatus QmSkinSetWeights::undoIt() {
	return MStatus::kSuccess;
}
