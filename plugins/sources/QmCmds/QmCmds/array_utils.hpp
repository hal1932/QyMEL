
template<class T, class TArray>
inline std::vector<T> ArrayToStdVector(const TArray& source) {
	std::vector<T> result;
	result.resize(source.length());
	for (auto i = 0U; i < source.length(); ++i) {
		result[i] = source[i];
	}
	return result;
}

template<class TArray, class T>
inline void ArrayCopyFromStdVector(TArray* p_array, const std::vector<T>& source) {
	p_array->setLength(static_cast<unsigned int>(source.size()));
	for (auto i = 0U; i < p_array->length(); ++i) {
		(*p_array)[i] = source[i];
	}
}
