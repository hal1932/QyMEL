#pragma once

class ArgParser : public MArgParser {
public:
	ArgParser(const MSyntax& syntax, const MArgList& args)
		: MArgParser(syntax, args)
	{}

	template<class T>
	std::vector<T> SelectFlagArguments(const char* flag, std::function<T(const MArgList&)> selector) const;

	template<class T>
	std::vector<T> CommandArguments() const;

	template<class T>
	std::vector<T> FlagArguments(const char* flag) const;
};

#include "ArgParser.hpp"
