#include "stdafx.h"
#include "MeshEditCommand.h"
#include "array_utils.h"

#pragma warning(push)
#pragma warning(disable: 26812)
MStatus PointCommand::Query() {
    MFnMesh mfn(p_context_->mesh);
    MPointArray points;
    const auto status = mfn.getPoints(points, p_context_->space);
    utils::ConvertArray(&p_context_->results, points);
    return status;
}

MStatus PointCommand::Edit() {
    MFnMesh mfn(p_context_->mesh);
    MPointArray points;
    utils::ConvertArray(&points, p_context_->values);
    return mfn.setPoints(points, p_context_->space);
}

MStatus PointCommand::SaveState() {
    MFnMesh mfn(p_context_->mesh);
    return mfn.getPoints(points_, p_context_->space);
}

MStatus PointCommand::RestoreState() {
    MFnMesh mfn(p_context_->mesh);
    return mfn.setPoints(points_, p_context_->space);
}
#pragma warning(pop)


MStatus NormalCommand::Query() {
    MFnMesh mfn(p_context_->mesh);
    MFloatVectorArray normals;
    const auto status = mfn.getNormals(normals, p_context_->space);
    utils::ConvertArray(&p_context_->results, normals);
    return status;
}

MStatus  NormalCommand::Edit() {
    MFnMesh mfn(p_context_->mesh);
    MFloatVectorArray normals;
    utils::ConvertArray(&normals, p_context_->values);
    return mfn.setNormals(normals, p_context_->space);
}

MStatus  NormalCommand::SaveState() {
    MFnMesh mfn(p_context_->mesh);
    return mfn.getNormals(normals_, p_context_->space);
}

MStatus  NormalCommand::RestoreState() {
    MFnMesh mfn(p_context_->mesh);
    return mfn.setNormals(normals_, p_context_->space);
}


MStatus VertexNormalCommand::Query() {
    MFnMesh mfn(p_context_->mesh);
    MFloatVectorArray normals;
    const auto status = mfn.getVertexNormals(false, normals, p_context_->space);
    utils::ConvertArray(&p_context_->results, normals);
    return status;
}

MStatus VertexNormalCommand::Edit() {
    MFnMesh mfn(p_context_->mesh);
    MVectorArray normals;
    utils::ConvertArray(&normals, p_context_->values);

    MIntArray vertices;
    vertices.setLength(mfn.numVertices());
    for (auto i = 0U; i < vertices.length(); ++i) {
        vertices[i] = i;
    }

    return mfn.setVertexNormals(normals, vertices, p_context_->space);
}

MStatus VertexNormalCommand::SaveState() {
    MFnMesh mfn(p_context_->mesh);
    return mfn.getNormals(normals_, p_context_->space);
}

MStatus VertexNormalCommand::RestoreState() {
    MFnMesh mfn(p_context_->mesh);
    return mfn.setNormals(normals_, p_context_->space);
}


MStatus FaceVertexNormalCommand::Query() {
    MFnMesh mfn(p_context_->mesh);
    MFloatVectorArray normals;
    MStatus status;
    for (auto i = 0; i < mfn.numPolygons(); ++i) {
        MFloatVectorArray vec;
        status = mfn.getFaceVertexNormals(i, vec, p_context_->space);
        if (status.error()) {
            return status;
        }
        for (const auto& v : vec) {
            normals.append(v);
        }
    }
    utils::ConvertArray(&p_context_->results, normals);
    return status;
}

MStatus FaceVertexNormalCommand::Edit() {
    MFnMesh mfn(p_context_->mesh);

    MIntArray vertices, faces, dummy;
    auto status = mfn.getVertices(dummy, vertices);
    if (status.error()) {
        return status;
    }
    utils::MakeSequence(&faces, 0, vertices.length());

    MVectorArray normals;
    utils::ConvertArray(&normals, normals_);

    status = mfn.setFaceVertexNormals(normals, faces, vertices, p_context_->space);
    utils::ConvertArray(&p_context_->results, normals);
    return status;
}

MStatus FaceVertexNormalCommand::SaveState() {
    MFnMesh mfn(p_context_->mesh);
    return mfn.getNormals(normals_, p_context_->space);
}

MStatus FaceVertexNormalCommand::RestoreState() {
    MFnMesh mfn(p_context_->mesh);
    return mfn.setNormals(normals_, p_context_->space);
}


namespace {
    MStatus GetColors(MColorArray* p_result, const MDagPath& mesh, const std::string& color_set) {
        const MString cs(color_set.c_str());
        const auto p_color_set = cs.length() > 0 ? &cs : nullptr;

        MFnMesh mfn(mesh);
        return mfn.getColors(*p_result, p_color_set);
    }

    MStatus SetColors(const MColorArray& values, const MDagPath& mesh, const std::string& color_set) {
        const MString cs(color_set.c_str());
        const auto p_color_set = cs.length() > 0 ? &cs : nullptr;

        MFnMesh mfn(mesh);
        return mfn.setColors(values, p_color_set);
    }

    std::string PushColorSet(MFnMesh& mfn, const std::string& color_set) {
        if (color_set.empty()) {
            return std::string();
        }
        const auto current = mfn.currentColorSetName();
        if (strcmp(color_set.c_str(), current.asChar()) == 0) {
            return std::string();
        }

        mfn.setCurrentColorSetName(MString(color_set.c_str()));
        return std::string(current.asChar());
    }

    void PopColorSet(MFnMesh& mfn, const std::string& color_set) {
        if (color_set.empty()) {
            return;
        }
        mfn.setCurrentColorSetName(MString(color_set.c_str()));
    }
}

MStatus ColorCommand::Query() {
    MColorArray colors;
    const auto status = GetColors(&colors, p_context_->mesh, p_context_->color_set);
    utils::ConvertArray(&p_context_->results, colors);
    return status;
}

MStatus ColorCommand::Edit() {
    MColorArray colors;
    utils::ConvertArray(&colors, p_context_->values);
    return SetColors(colors, p_context_->mesh, p_context_->color_set);
}

MStatus ColorCommand::SaveState() {
    return GetColors(&colors_, p_context_->mesh, p_context_->color_set);
}

MStatus ColorCommand::RestoreState() {
    return SetColors(colors_, p_context_->mesh, p_context_->color_set);
}


MStatus VertexColorCommand::Query() {
    MFnMesh mfn(p_context_->mesh);

    const MString cs(p_context_->color_set.c_str());
    const auto p_color_set = cs.length() > 0 ? &cs : nullptr;

    MColorArray colors;
    const auto status = mfn.getVertexColors(colors, p_color_set);
    utils::ConvertArray(&p_context_->results, colors);

    return status;
}

MStatus VertexColorCommand::Edit() {
    MFnMesh mfn(p_context_->mesh);

    MColorArray colors;
    utils::ConvertArray(&colors, p_context_->values);

    MIntArray vertices;
    utils::MakeSequence(&vertices, 0, mfn.numVertices());

    const auto color_set = PushColorSet(mfn, p_context_->color_set);
    mfn.setVertexColors(colors, vertices, &modifier_);
    const auto status = modifier_.doIt();
    PopColorSet(mfn, color_set);
    return status;
}

MStatus VertexColorCommand::SaveState() {
    return MStatus::kSuccess;
}

MStatus VertexColorCommand::RestoreState() {
    MFnMesh mfn(p_context_->mesh);
    const auto color_set = PushColorSet(mfn, p_context_->color_set);
    const auto status = modifier_.undoIt();
    PopColorSet(mfn, color_set);
    return status;
}


MStatus FaceVertexColorCommand::Query() {
    MFnMesh mfn(p_context_->mesh);

    const MString cs(p_context_->color_set.c_str());
    const auto p_color_set = cs.length() > 0 ? &cs : nullptr;

    MColorArray colors;
    const auto status = mfn.getFaceVertexColors(colors, p_color_set);

    utils::ConvertArray(&p_context_->results, colors);
    return status;
}

MStatus FaceVertexColorCommand::Edit() {
    MFnMesh mfn(p_context_->mesh);

    MIntArray vertexCounts, vertices;
    auto status = mfn.getVertices(vertexCounts, vertices);
    if (status.error()) {
        return status;
    }

    MIntArray faces;
    faces.setLength(vertices.length());
    auto f = 0, lv = 0;
    for (auto i = 0U; i < faces.length(); ++i) {
        if (++lv > vertexCounts[f]) {
            ++f;
            lv = 0;
        }
        faces[i] = f;
    }

    MColorArray colors;
    utils::ConvertArray(&colors, p_context_->values);

    const auto color_set = PushColorSet(mfn, p_context_->color_set);
    mfn.setFaceVertexColors(colors, faces, vertices, &modifier_);
    status = modifier_.doIt();
    PopColorSet(mfn, color_set);

    return status;
}

MStatus FaceVertexColorCommand::SaveState() {
    return MStatus::kSuccess;
}

MStatus FaceVertexColorCommand::RestoreState() {
    MFnMesh mfn(p_context_->mesh);
    const auto color_set = PushColorSet(mfn, p_context_->color_set);
    const auto status = modifier_.undoIt();
    PopColorSet(mfn, color_set);
    return status;
}


MStatus UvCommand::Query() {
    MFnMesh mfn(p_context_->mesh);

    const MString uv_set(p_context_->uv_set.c_str());
    const auto p_uv_set = uv_set.length() > 0 ? &uv_set : nullptr;

    MFloatArray uArray, vArray;
    const auto status = mfn.getUVs(uArray, vArray, p_uv_set);

    MFloatArray uvs;
    utils::ZipArray(&uvs, uArray, vArray);

    utils::ConvertArray(&p_context_->results, uvs);

    return status;
}

MStatus UvCommand::Edit() {
    MFnMesh mfn(p_context_->mesh);

    MFloatArray values;
    utils::ConvertArray(&values, p_context_->values);

    MFloatArray uArray, vArray;
    utils::UnzipArray(&uArray, &vArray, values);

    const MString uv_set(p_context_->uv_set.c_str());
    const auto p_uv_set = uv_set.length() > 0 ? &uv_set : nullptr;

    return mfn.setUVs(uArray, vArray, p_uv_set);
}

MStatus UvCommand::SaveState() {
    MFnMesh mfn(p_context_->mesh);

    const MString uv_set(p_context_->uv_set.c_str());
    const auto p_uv_set = uv_set.length() > 0 ? &uv_set : nullptr;

    return mfn.getUVs(uArray_, vArray_, p_uv_set);
}

MStatus UvCommand::RestoreState() {
    MFnMesh mfn(p_context_->mesh);

    const MString uv_set(p_context_->uv_set.c_str());
    const auto p_uv_set = uv_set.length() > 0 ? &uv_set : nullptr;

    return mfn.setUVs(uArray_, vArray_, p_uv_set);
}
