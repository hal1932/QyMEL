#pragma once

namespace utils {

	template<class TArray>
	inline void ZipArray(TArray* p_result, const TArray& source_lhs, const TArray& source_rhs);

	template<class TArray>
	inline void UnzipArray(TArray* p_result_lhs, TArray* p_result_rhs, const TArray& source);

	template<class TDestArray, class TSourceArray>
	inline void ConvertArray(TDestArray* p_result, const TSourceArray& source);

	template<class TArray>
	inline void MakeSequence(TArray* p_result, int start, int count);

	#include "array_utils.hpp"
}// namespace array
