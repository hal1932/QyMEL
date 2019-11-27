#pragma once

class ArgParser : public MArgParser {
public:
	ArgParser(const MSyntax& syntax, const MArgList& args)
		: MArgParser(syntax, args)
	{}

	MStatus EnumerateFlagArgumentList(const char* flag, std::function<void(const MArgList&)> selector) const;
};

