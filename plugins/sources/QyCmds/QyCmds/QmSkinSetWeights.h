#pragma once
#include "CommandBase.h"

class QmSkinSetWeights : CommandBase {
public:
	static MString Name() { return "qmSkinSetWeights"; }
	static void* Creator() { return new QmSkinSetWeights(); }

	bool isUndoable() { return true; }

	MStatus redoIt();
	MStatus undoIt();

protected:
	MSyntax CreateSyntax();
	MStatus ParseArguments(const ArgParser& parser);

private:
	std::vector<int> components_;
	std::vector<int> influences_;
	std::vector<float> values_;
};
