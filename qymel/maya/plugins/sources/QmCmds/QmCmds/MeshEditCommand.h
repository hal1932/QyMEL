#pragma once

struct MeshEditContext {
    MDagPath mesh;
    MSpace::Space space;
    std::string color_set;
    std::string uv_set;
    MDoubleArray values;
    MDoubleArray results;
};

class MeshEditCommand {
public:
    void SetContext(MeshEditContext* p_context) {
        p_context_ = p_context;
    }

    virtual MStatus Query() = 0;
    virtual MStatus Edit() = 0;
    virtual MStatus SaveState() = 0;
    virtual MStatus RestoreState() = 0;

protected:
    MeshEditContext* p_context_;
};

#pragma warning(push)
#pragma warning(disable: 26812)
class PointCommand final : public MeshEditCommand {
public:
    MStatus Query();
    MStatus Edit();
    MStatus SaveState();
    MStatus RestoreState();

private:
    MPointArray points_;
};
#pragma warning(pop)

class NormalCommand final : public MeshEditCommand {
public:
    MStatus Query();
    MStatus Edit();
    MStatus SaveState();
    MStatus RestoreState();

private:
    MFloatVectorArray normals_;
};

class VertexNormalCommand final : public MeshEditCommand {
public:
    MStatus Query();
    MStatus Edit();
    MStatus SaveState();
    MStatus RestoreState();

private:
    MFloatVectorArray normals_;
};

class FaceVertexNormalCommand final : public MeshEditCommand {
public:
    MStatus Query();
    MStatus Edit();
    MStatus SaveState();
    MStatus RestoreState();

private:
    MFloatVectorArray normals_;
};

class ColorCommand final : public MeshEditCommand {
public:
    MStatus Query();
    MStatus Edit();
    MStatus SaveState();
    MStatus RestoreState();

private:
    MColorArray colors_;
};

class VertexColorCommand final : public MeshEditCommand {
public:
    MStatus Query();
    MStatus Edit();
    MStatus SaveState();
    MStatus RestoreState();

private:
    MDagModifier modifier_;
};

class FaceVertexColorCommand final : public MeshEditCommand {
public:
    MStatus Query();
    MStatus Edit();
    MStatus SaveState();
    MStatus RestoreState();

private:
    MDGModifier modifier_;
};

class UvCommand final : public MeshEditCommand {
public:
    MStatus Query();
    MStatus Edit();
    MStatus SaveState();
    MStatus RestoreState();

private:
    MFloatArray uArray_;
    MFloatArray vArray_;
};