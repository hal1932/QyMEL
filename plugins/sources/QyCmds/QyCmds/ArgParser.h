#pragma once

class ArgParser : public MArgParser {
public:
	ArgParser(const MSyntax& syntax, const MArgList& args)
		: MArgParser(syntax, args)
	{}

	template<class T>
	std::vector<T> SelectFlagArguments(const char* flag, std::function<T(const MArgList&)> selector) const {
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
	std::vector<T> CommandArguments() const {
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
	std::vector<T> FlagArguments(const char* flag) const { return std::vector<T>(); }

	template<>
	std::vector<int> FlagArguments(const char* flag) const {
		return SelectFlagArguments<int>(flag, [](const MArgList& args) { return args.asInt(0); });
	}

	template<>
	std::vector<float> FlagArguments(const char* flag) const {
		return SelectFlagArguments<float>(flag, [](const MArgList& args) { return static_cast<float>(args.asDouble(0)); });
	}

	template<>
	std::vector<MString> FlagArguments(const char* flag) const {
		return SelectFlagArguments<MString>(flag, [](const MArgList& args) { return args.asString(0); });
	}
};

