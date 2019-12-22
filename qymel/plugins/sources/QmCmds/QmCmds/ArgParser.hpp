
namespace {
	template<class TArray, class TElement>
	inline MStatus CommandArguments_(const ArgParser* p_parser, TArray* p_result) {
		MStatus status;

		auto index = 0U;
		while (true) {
			TElement elem;
			status = p_parser->getCommandArgument(index, elem);
			if (!status) {
				break;
			}

			p_result->append(elem);

			++index;
		}

		return status;
	}
}

inline void ArgParser::EnumerateFlagArguments(const char* flag, std::function<void(const MArgList&)> callback) const {
	MStatus status;
	for (auto i = 0U; i < numberOfFlagUses(flag); ++i) {
		MArgList args;
		status = getFlagArgumentList(flag, i, args);
		if (!status) {
			break;
		}
		callback(args);
	}
}

template<class TArray, class TElement>
inline MStatus ArgParser::SelectFlagArguments(TArray* p_result, const char* flag, std::function<TElement(const MArgList&)> selector) const {
	MStatus status;

	for (auto i = 0U; i < numberOfFlagUses(flag); ++i) {
		MArgList args;
		status = getFlagArgumentList(flag, i, args);
		if (!status) {
			break;
		}
		p_result->append(selector(args));
	}

	return status;
}

template<class TArray>
inline MStatus ArgParser::CommandArguments(TArray* p_result) const {
	MGlobal::displayError("not implemented template class type");
	return MStatus::kFailure;
}

template<>
inline MStatus ArgParser::CommandArguments(MStringArray* p_result) const {
	return CommandArguments_<MStringArray, MString>(this, p_result);
}

template<>
inline MStatus ArgParser::CommandArguments(MDoubleArray* p_result) const {
	return CommandArguments_<MDoubleArray, double>(this, p_result);
}

template<>
inline MStatus ArgParser::CommandArguments(MIntArray* p_result) const {
	return CommandArguments_<MIntArray, int>(this, p_result);
}

template<class TArray>
inline MStatus ArgParser::FlagArguments(TArray* p_result, const char* flag) const {
	MGlobal::displayError("not implemented template class type");
	return MStatus::kFailure;
}

template<>
inline MStatus ArgParser::FlagArguments<MIntArray>(MIntArray* p_result, const char* flag) const {
	return SelectFlagArguments<MIntArray, int>(p_result, flag, [](const MArgList& args) { return args.asInt(0); });
}

template<>
inline MStatus ArgParser::FlagArguments<MDoubleArray>(MDoubleArray* p_result, const char* flag) const {
	return SelectFlagArguments<MDoubleArray, double>(p_result, flag, [](const MArgList& args) { return args.asDouble(0); });
}

template<>
inline MStatus ArgParser::FlagArguments<MStringArray>(MStringArray* p_result, const char* flag) const {
	return SelectFlagArguments<MStringArray, MString>(p_result, flag, [](const MArgList& args) { return args.asString(0); });
}

inline MStatus ArgParser::FlagArguments(MVectorArray* p_result, const char* flag, const uint element_count) const {
	return SelectFlagArguments<MVectorArray, MVector>(p_result, flag, [element_count](const MArgList& args) {
		auto index = 0U;
		return args.asVector(index, element_count);
	});
}
