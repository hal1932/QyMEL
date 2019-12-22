#pragma once
#include "CommandBase.h"

class QmSkinSetWeights final : CommandBase {
public:
	static MString Name() { return "qmSkinSetWeights"; }
	static void* Creator() { return new QmSkinSetWeights(); }

	bool isUndoable() const { return true; }

	MStatus redoIt();
	MStatus undoIt();

private:
	MSyntax CreateSyntax();
	MStatus ParseArguments(const ArgParser& parser);

private:
	MObject components_;
	MIntArray influences_;
	MFloatArray values_;

	MObject cluster_;
	MDagPath dagpath_;
	MFloatArray old_weights_;
};
