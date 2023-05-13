#pragma once
#include "CommandBase.h"
#include "MeshEditCommand.h"

class QmMeshEditor final : CommandBase {
public:
    ~QmMeshEditor();
    static MString Name() { return "qmMeshEditor"; }
    static void* Creator() { return new QmMeshEditor(); }

    bool isUndoable() const { return p_edit_command_ != nullptr; }

    MStatus redoIt();
    MStatus undoIt();

private:
    MSyntax CreateSyntax();
    MStatus ParseArguments(const ArgParser& parser);
    MStatus ExecuteEditor(MeshEditCommand* p_editor);

private:
    bool is_query_;

    bool points_;
    bool normals_;
    bool vertex_normals_;
    bool face_vertex_normals_;
    bool colors_;
    bool vertex_colors_;
    bool face_vertex_colors_;
    bool uv_;

    MDagModifier modifier_;

    MeshEditCommand* p_edit_command_ = nullptr;
    MeshEditContext edit_context_;
};

