#pragma once

namespace utils {

	MObject GetDependencyNode(const MString& node_name, MStatus* p_status = nullptr);
	MDagPath GetDagPath(const MString& node_name, MStatus* p_status = nullptr);
	MDagPath GetDagPath(const MObject& node, MStatus* p_status = nullptr);

}// namespace utils
