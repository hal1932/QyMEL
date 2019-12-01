template<class T>
inline std::vector<T> ArgParser::SelectFlagArguments(const char* flag, std::function<T(const MArgList&)> selector) const {
	std::vector<T> result;

	for (auto i = 0U; i < numberOfFlagUses(flag); ++i) {
		uint pos;
		auto status = getFlagArgumentPosition(flag, i, pos);
		if (status.error()) {
			break;
		}

		MArgList args;
		status = getFlagArgumentList(flag, i, args);
		if (status.error()) {
			break;
		}

		selector(args);
		result.push_back(selector(args));
	}

	return std::move(result);
}

template<class T>
inline std::vector<T> ArgParser::CommandArguments() const {
	std::vector<T> result;

	auto index = 0U;
	while (true) {
		T arg;
		const auto status = getCommandArgument(index, arg);
		if (status.error()) {
			break;
		}
		result.push_back(arg);
		++index;
	}

	return std::move(result);
}

template<class T>
inline std::vector<T> ArgParser::FlagArguments(const char* flag) const {
	MGlobal::displayError("not implemented template class type");
	return std::vector<T>();
}

template<>
inline std::vector<int> ArgParser::FlagArguments(const char* flag) const {
	return SelectFlagArguments<int>(flag, [](const MArgList& args) { return args.asInt(0); });
}

template<>
inline std::vector<float> ArgParser::FlagArguments(const char* flag) const {
	return SelectFlagArguments<float>(flag, [](const MArgList& args) { return static_cast<float>(args.asDouble(0)); });
}

template<>
inline std::vector<double> ArgParser::FlagArguments(const char* flag) const {
	return SelectFlagArguments<double>(flag, [](const MArgList& args) { return args.asDouble(0); });
}

template<>
inline std::vector<MString> ArgParser::FlagArguments(const char* flag) const {
	return SelectFlagArguments<MString>(flag, [](const MArgList& args) { return args.asString(0); });
}
