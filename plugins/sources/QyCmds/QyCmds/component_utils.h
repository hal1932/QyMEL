#pragma once

namespace utils {

	inline MObject ComponentsFromStdVector(MFn::Type type, const std::vector<int>& indices) {
		MFnSingleIndexedComponent mfn;
		auto comp = mfn.create(type);
		for (auto i : indices) {
			mfn.addElement(i);
		}
		return comp;
	}

	inline MObject ComponentsFromStdVector(MFn::Type type, const std::vector<int>& indices_u, std::vector<int>& indices_v) {
		MFnDoubleIndexedComponent mfn;
		auto comp = mfn.create(type);
		for (auto i = 0; i < indices_u.size(); ++i) {
			mfn.addElement(indices_u[i], indices_v[i]);
		}
		return comp;
	}

}// namespace component
