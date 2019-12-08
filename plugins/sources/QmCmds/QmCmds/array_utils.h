#pragma once

namespace utils {

	template<class T, class TArray>
	inline std::vector<T> ArrayToStdVector(const TArray& source);

	template<class TArray, class T>
	inline void ArrayCopyFromStdVector(TArray* p_array, const std::vector<T>& source);

	#include "array_utils.hpp"
}// namespace array
