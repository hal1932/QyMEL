#pragma once
#include "CommandBase.h"

class QmBatchSetVertexColor final : CommandBase {
public:
	static MString Name() { return "qmBatchSetVertexColor"; }
	static void* Creator() { return new QmBatchSetVertexColor(); }

	bool isUndoable() const { return true; }

	MStatus redoIt();
	MStatus undoIt();

private:
	MSyntax CreateSyntax();
	MStatus ParseArguments(const ArgParser& parser);

private:
	MDagPath mesh_;
	MIntArray vertices_;
	MColorArray colors_;

	MDGModifier modifier_;
};
