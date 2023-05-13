#pragma once
#include "ArgParser.h"

class CommandBase : public MPxCommand {
public:
	virtual ~CommandBase() {}

	MStatus doIt(const MArgList& args) {
		auto syntax = CreateSyntax();
		ArgParser parser(syntax, args);
		auto status = ParseArguments(parser);
		if (status.error()) {
			return status;
		}
		return redoIt();
	}

	virtual MStatus redoIt() = 0;
	virtual MStatus undoIt() { return MStatus::kFailure;}

protected:
	virtual MSyntax CreateSyntax() { return MSyntax(); }
	virtual MStatus ParseArguments(const ArgParser& parser) { return MStatus::kSuccess; }
};
