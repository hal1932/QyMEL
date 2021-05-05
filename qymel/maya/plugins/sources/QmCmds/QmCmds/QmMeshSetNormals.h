#pragma once
#include "CommandBase.h"

class QmMeshSetNormals final : CommandBase {
public:
	static MString Name() { return "qmMeshSetNormals"; }
	static void* Creator() { return new QmMeshSetNormals(); }

	bool isUndoable() const { return true; }

	MStatus redoIt();
	MStatus undoIt();

private:
	MSyntax CreateSyntax();
	MStatus ParseArguments(const ArgParser& parser);

private:
	struct VtxFaces_ {
		MIntArray vertices;
		MIntArray faces;

		void append(const MIntArray& v) { vertices.append(v[0]); faces.append(v[1]); }
		size_t length() { return vertices.length(); }
	};
	MDagPath mesh_;
	MIntArray vertices_;
	VtxFaces_ vtx_faces_;
	MVectorArray normals_;
	MFloatVectorArray old_normals_;
};
