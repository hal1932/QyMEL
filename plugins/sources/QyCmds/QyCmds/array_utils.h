#pragma once

namespace utils {

	inline std::vector<int> ArrayToStdVector(const MIntArray& source) {
		std::vector<int> result;
		result.resize(source.length());
		for (auto i = 0U; i < source.length(); ++i) {
			result[i] = source[i];
		}
		return result;
	}

	inline std::vector<float> ArrayToStdVector(const MFloatArray& source) {
		std::vector<float> result;
		result.resize(source.length());
		for (auto i = 0U; i < source.length(); ++i) {
			result[i] = source[i];
		}
		return result;
	}

	inline void ArrayCopyFromStdVector(MIntArray* p_array, const std::vector<int>& source) {
		p_array->setLength(static_cast<unsigned int>(source.size()));
		for (auto i = 0U; i < p_array->length(); ++i) {
			(*p_array)[i] = source[i];
		}
	}

	inline void ArrayCopyFromStdVector(MFloatArray* p_array, const std::vector<float>& source) {
		p_array->setLength(static_cast<unsigned int>(source.size()));
		for (auto i = 0U; i < p_array->length(); ++i) {
			(*p_array)[i] = source[i];
		}
	}

}// namespace array

