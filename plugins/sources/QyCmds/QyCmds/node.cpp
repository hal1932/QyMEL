#include "node_utils.h"

namespace {
	void SetStatus(MStatus* p_dest, const MStatus src) {
		if (p_dest != nullptr) {
			*p_dest = src;
		}
	}
}

MObject utils::GetDependencyNode(const MString& node_name, MStatus* p_status) {
	MSelectionList list;
	MStatus status = list.add(node_name);
	if (status.error()) {
		SetStatus(p_status, status);
		return MObject::kNullObj;
	}

	MObject node;
	status = list.getDependNode(0, node);
	SetStatus(p_status, status);

	return status.error() ? MObject::kNullObj : node;
}

MDagPath utils::GetDagPath(const MString& node_name, MStatus* p_status) {
	MSelectionList list;
	MStatus status = list.add(node_name);
	if (status.error()) {
		SetStatus(p_status, status);
		return MDagPath();
	}

	MDagPath dagpath;
	status = list.getDagPath(0, dagpath);
	SetStatus(p_status, status);

	return status.error() ? MDagPath() : dagpath;
}

MDagPath utils::GetDagPath(const MObject& node, MStatus* p_status) {
	MSelectionList list;
	MStatus status = list.add(node);
	if (status.error()) {
		SetStatus(p_status, status);
		return MDagPath();
	}

	MDagPath dagpath;
	status = list.getDagPath(0, dagpath);
	SetStatus(p_status, status);

	return status.error() ? MDagPath() : dagpath;
}
