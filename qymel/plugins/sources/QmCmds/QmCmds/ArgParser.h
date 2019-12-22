#pragma once

class ArgParser : public MArgDatabase {
public:
	ArgParser(const MSyntax& syntax, const MArgList& args)
		: MArgDatabase(syntax, args)
	{}

	void EnumerateFlagArguments(const char* flag, std::function<void(const MArgList&)> callback) const;

	template<class TArray, class TElement>
	MStatus SelectFlagArguments(TArray* p_result, const char* flag, std::function<TElement(const MArgList&)> selector) const;

	template<class TArray>
	MStatus CommandArguments(TArray* p_result) const;

	template<class TArray>
	MStatus FlagArguments(TArray* p_result, const char* flag) const;

	MStatus FlagArguments(MVectorArray* p_result, const char* flag, const uint element_count = 3) const;
};

#include "ArgParser.hpp"
