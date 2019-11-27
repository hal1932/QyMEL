#include "stdafx.h"
#include "ArgParser.h"

MStatus ArgParser::EnumerateFlagArgumentList(const char* flag, std::function<void(const MArgList&)> selector) const {
	for (auto i = 0U; i < numberOfFlagUses(flag); ++i) {
		uint pos;
		auto status = getFlagArgumentPosition(flag, i, pos);
		if (status != MStatus::kSuccess) {
			return status;
		}

		MArgList args;
		status = getFlagArgumentList(flag, i, args);
		if (status != MStatus::kSuccess) {
			return status;
		}

		selector(args);
	}
	return MStatus::kSuccess;
}
