#include "stdafx.h"
#include "QmMeshEditor.h"
#include "node_utils.h"
#include "array_utils.h"

namespace {
    void AddFlag(MSyntax* p_syntax, const char* short_name, const char* long_name, MSyntax::MArgType type, bool multi_use) {
        p_syntax->addFlag(short_name, long_name, type);
        if (multi_use) {
            p_syntax->makeFlagMultiUse(short_name);
        }
    }
}

QmMeshEditor::~QmMeshEditor() {
    if (p_edit_command_ != nullptr) {
        SafeDelete(&p_edit_command_);
    }
}

MSyntax QmMeshEditor::CreateSyntax() {
    MSyntax syntax;

    syntax.addArg(MSyntax::kString); // node name

    //syntax.enableQuery(true); // “®ì‚µ‚È‚¢
    AddFlag(&syntax, "q", "query", MSyntax::kBoolean, false);

    AddFlag(&syntax, "p", "points", MSyntax::kBoolean, false);

    AddFlag(&syntax, "n", "normals", MSyntax::kBoolean, false);
    AddFlag(&syntax, "vn", "vertexNormals", MSyntax::kBoolean, false);
    AddFlag(&syntax, "fvn", "faceVertexNormals", MSyntax::kBoolean, false);

    AddFlag(&syntax, "c", "colors", MSyntax::kBoolean, false);
    AddFlag(&syntax, "vc", "vertexColors", MSyntax::kBoolean, false);
    AddFlag(&syntax, "fvc", "faceVertexColors", MSyntax::kBoolean, false);

    AddFlag(&syntax, "uv", "uvCoords", MSyntax::kBoolean, false);

    AddFlag(&syntax, "s", "space", MSyntax::kLong, false);
    AddFlag(&syntax, "uvs", "uvSet", MSyntax::kString, false);
    AddFlag(&syntax, "cs", "colorSet", MSyntax::kString, false);

    AddFlag(&syntax, "v", "values", MSyntax::kDouble, true);

    return syntax;
}

MStatus QmMeshEditor::ParseArguments(const ArgParser& parser) {
    MStatus status = MStatus::kSuccess;

    auto is_flag_set = false;

#define _GET_FLAG(VALUE, NAME) \
    do { \
        VALUE = parser.isFlagSet(NAME, &status); \
        is_flag_set = is_flag_set || VALUE; \
        if (status.error()) { \
            MGlobal::displayError(status.errorString()); \
            return status; \
        } \
    } while (false)

    _GET_FLAG(is_query_, "q");
    _GET_FLAG(points_, "p");
    _GET_FLAG(normals_, "n");
    _GET_FLAG(vertex_normals_, "vn");
    _GET_FLAG(face_vertex_normals_, "fvn");
    _GET_FLAG(colors_, "c");
    _GET_FLAG(vertex_colors_, "vc");
    _GET_FLAG(face_vertex_colors_, "fvc");
    _GET_FLAG(uv_, "uv");
#undef _GET_FLAG

    if (!is_flag_set) {
        MGlobal::displayError("a target component flag must be specified");
        return MStatus::kFailure;
    }

    MStringArray args;
    status = parser.CommandArguments(&args);
    if (status.error()) {
        MGlobal::displayError(status.errorString());
        return status;
    }
    if (args.length() != 1) {
        MGlobal::displayError("a mesh node name must be specified");
        return MStatus::kFailure;
    }

    auto mesh = utils::GetDagPath(args[0], &status);
    if (mesh.hasFn(MFn::kTransform)) {
        status = mesh.extendToShape();
    }
    if (status.error()) {
        return status;
    }
    edit_context_.mesh = mesh;

    status = parser.FlagArguments(&edit_context_.values, "v");
    if (status.error()) {
        return status;
    }

    edit_context_.uv_set = std::string(parser.flagArgumentString("-u", 0).asChar());
    edit_context_.color_set = std::string(parser.flagArgumentString("-cs", 0).asChar());

    const auto space = parser.flagArgumentInt("-s", 0);
#pragma warning(push)
#pragma warning(disable: 26812)
    edit_context_.space = space == 0 ? MSpace::kObject : (MSpace::Space)space;
#pragma warning(pop)

    return status;
}

MStatus QmMeshEditor::ExecuteEditor(MeshEditCommand* p_editor) {
    p_editor->SetContext(&edit_context_);

    MStatus status;
    if (is_query_) {
        status = p_editor->Query();
        setResult(edit_context_.results);
    } else {
        status = p_editor->SaveState();
        if (status.error()) {
            return status;
        }
        status = p_editor->Edit();
        p_edit_command_ = p_editor;
    }

    return status;
}

MStatus QmMeshEditor::redoIt() {
    MStatus status = MStatus::kSuccess;
    clearResult();

    edit_context_.results.clear();

#define _COND_EDIT(EXPR, EDITOR) \
    do { \
        if (EXPR) { \
            auto p_editor = new EDITOR(); \
            status = ExecuteEditor(p_editor); \
        } \
    } while (false)

    _COND_EDIT(points_, PointCommand);
    _COND_EDIT(normals_, NormalCommand);
    _COND_EDIT(vertex_normals_, VertexNormalCommand);
    _COND_EDIT(face_vertex_normals_, FaceVertexNormalCommand);
    _COND_EDIT(colors_, ColorCommand);
    _COND_EDIT(vertex_colors_, VertexColorCommand);
    _COND_EDIT(face_vertex_colors_, FaceVertexColorCommand);
    _COND_EDIT(uv_, UvCommand);
#undef _COND_EDIT

    if (status.error()) {
        MGlobal::displayInfo(status.errorString());
    }

    return status;
}

MStatus QmMeshEditor::undoIt() {
    if (p_edit_command_ == nullptr) {
        return MStatus::kSuccess;
    }
    return p_edit_command_->RestoreState();
}
