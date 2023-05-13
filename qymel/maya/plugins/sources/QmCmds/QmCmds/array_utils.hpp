template<class TArray>
inline void ZipArray(TArray* p_result, const TArray& source_lhs, const TArray& source_rhs) {
	p_result->setLength(source_lhs.length() * 2);
	for (auto i = 0U; i < source_lhs.length(); ++i) {
		(*p_result)[i * 2 + 0] = source_lhs[i];
		(*p_result)[i * 2 + 1] = source_rhs[i];
	}
}

template<class TArray>
inline void UnzipArray(TArray* p_result_lhs, TArray* p_result_rhs, const TArray& source) {
	p_result_lhs->setLength(source.length() / 2);
	p_result_rhs->setLength(source.length() / 2);
	for (auto i = 0U; i < p_result_lhs->length(); ++i) {
		(*p_result_lhs)[i] = source[i * 2 + 0];
		(*p_result_rhs)[i] = source[i * 2 + 1];
	}
}

template<class TDestArray, class TSourceArray>
inline void ConvertArray(TDestArray* p_result, const TSourceArray& source) {}

template<>
inline void ConvertArray(MDoubleArray* p_result, const MFloatArray& source) {
	p_result->setLength(source.length());
	for (auto i = 0U; i < p_result->length(); ++i) {
		(*p_result)[i] = source[i];
	}
}

template<>
inline void ConvertArray(MFloatArray* p_result, const MDoubleArray& source) {
	p_result->setLength(source.length());
	for (auto i = 0U; i < p_result->length(); ++i) {
		(*p_result)[i] = static_cast<float>(source[i]);
	}
}

template<>
inline void ConvertArray(MDoubleArray* p_result, const MPointArray& source) {
	p_result->setLength(source.length() * 3);
	for (auto i = 0U; i < source.length(); ++i) {
		(*p_result)[i * 3 + 0] = source[i].x;
		(*p_result)[i * 3 + 1] = source[i].y;
		(*p_result)[i * 3 + 2] = source[i].z;
	}
}

template<>
inline void ConvertArray(MDoubleArray* p_result, const MFloatVectorArray& source) {
	p_result->setLength(source.length() * 3);
	for (auto i = 0U; i < source.length(); ++i) {
		(*p_result)[i * 3 + 0] = source[i].x;
		(*p_result)[i * 3 + 1] = source[i].y;
		(*p_result)[i * 3 + 2] = source[i].z;
	}
}

template<>
inline void ConvertArray(MDoubleArray* p_result, const MColorArray& source) {
	p_result->setLength(source.length() * 4);
	for (auto i = 0U; i < source.length(); ++i) {
		float r, g, b, a;
		source[i].get(MColor::kRGB, r, g, b, a);
		(*p_result)[i * 4 + 0] = r;
		(*p_result)[i * 4 + 1] = g;
		(*p_result)[i * 4 + 2] = b;
		(*p_result)[i * 4 + 3] = a;
	}
}

template<>
inline void ConvertArray(MColorArray* p_result, const MDoubleArray& source) {
	p_result->setLength(source.length() / 4);
	for (auto i = 0U; i < p_result->length(); ++i) {
		(*p_result)[i] = MColor(
			static_cast<float>(source[i * 4 + 0]),
			static_cast<float>(source[i * 4 + 1]),
			static_cast<float>(source[i * 4 + 2]),
			static_cast<float>(source[i * 4 + 3])
		);
	}
}

template<>
inline void ConvertArray<MPointArray>(MPointArray* p_result, const MDoubleArray& source) {
	p_result->setLength(source.length() / 3);
	for (auto i = 0U; i < p_result->length(); ++i) {
		(*p_result)[i] = MPoint(
			source[i * 3 + 0],
			source[i * 3 + 1],
			source[i * 3 + 2]
		);
	}
}

template<>
inline void ConvertArray<MFloatVectorArray>(MFloatVectorArray* p_result, const MDoubleArray& source) {
	p_result->setLength(source.length() / 3);
	for (auto i = 0U; i < p_result->length(); ++i) {
		(*p_result)[i] = MFloatVector(
			static_cast<float>(source[i * 3 + 0]),
			static_cast<float>(source[i * 3 + 1]),
			static_cast<float>(source[i * 3 + 2])
		);
	}
}

template<>
inline void ConvertArray<MVectorArray>(MVectorArray* p_result, const MDoubleArray& source) {
	p_result->setLength(source.length() / 3);
	for (auto i = 0U; i < p_result->length(); ++i) {
		(*p_result)[i] = MVector(
			source[i * 3 + 0],
			source[i * 3 + 1],
			source[i * 3 + 2]
		);
	}
}

template<>
inline void ConvertArray<MVectorArray>(MVectorArray* p_result, const MFloatVectorArray& source) {
	p_result->setLength(source.length());
	for (auto i = 0U; i < p_result->length(); ++i) {
		const auto& s = source[i];
		(*p_result)[i] = MVector(s.x, s.y, s.z);
	}
}

template<class TArray>
inline void MakeSequence(TArray* p_result, int start, int count) {
	p_result->setLength(count);
	for (auto i = start; i < start + count; ++i) {
		(*p_result)[i] = start + i;
	}
}