#pragma once
#include "node_utils.h"
#include "component_utils.h"

class DependencyNode {
public:
	DependencyNode(MObject mobject) : mobject(mobject) {}

protected:
	MObject mobject;
};

class SkinCluster : public DependencyNode {
public:
	SkinCluster(MObject mobject) : DependencyNode(mobject) {}

	MIntArray InfluenceObjectIndices() {
		MFnSkinCluster mfn(mobject);
		MDagPathArray paths;
		mfn.influenceObjects(paths);

		MIntArray indices;
		indices.setLength(paths.length());
		for (auto i = 0U; i < paths.length(); ++i) {
			indices[i] = mfn.indexForInfluenceObject(paths[i]);
		}

		return indices;
	}
};

class DagNode : public DependencyNode {
public:
	DagNode(MObject mobject) : DependencyNode(mobject) {
		mdagpath = utils::GetDagPath(mobject);
	}

protected:
	MDagPath mdagpath;
};

class Mesh : public DagNode {
public:
	Mesh(MObject mobject) : DagNode(mobject) {}

	MObject VertexComponents(const std::vector<int>& indices) const {
		return utils::ComponentsFromStdVector(MFn::kMeshVertComponent, indices);
	}

	MObject VertexComponents() const {
		MFnMesh mfn(mobject);

		std::vector<int> indices;
		indices.resize(mfn.numVertices());
		for (auto i = 0; i < indices.size(); ++i) {
			indices[i] = i;
		}

		return VertexComponents(indices);
	}
};
