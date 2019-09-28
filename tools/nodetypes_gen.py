
class DependNode():

    _mfn_type = om2.MFn.kDependencyNode
    _mfn_set = om2.MFnDependencyNode
    _mel_type = ''

    @staticmethod
    def ls(*args, **kwargs):
        kwargs['type'] = DependNode._mel_type
        return _ls_nodes(*args, **kwargs)

    @staticmethod
    def create(**kwargs):
        return _create_node(DependNode._mel_type, **kwargs)

    def __init__(self, mobj):
        # type: (om2.MObject) -> NoReturn
        super(DependNode, self).__init__(mobj)


class ContainerBase(DependNode):

    _mfn_type = om2.MFn.kContainerBase
    _mfn_set = om2.
    _mel_type = 'containerBase'

    @staticmethod
    def ls(*args, **kwargs):
        kwargs['type'] = ContainerBase._mel_type
        return _ls_nodes(*args, **kwargs)

    @staticmethod
    def create(**kwargs):
        return _create_node(ContainerBase._mel_type, **kwargs)

    def __init__(self, mobj):
        # type: (om2.MObject) -> NoReturn
        super(ContainerBase, self).__init__(mobj)


class AnimCurve(DependNode):

    _mfn_type = om2.MFn.kAnimCurve
    _mfn_set = om2.MFnAnimCurve
    _mel_type = 'animCurve'

    @staticmethod
    def ls(*args, **kwargs):
        kwargs['type'] = AnimCurve._mel_type
        return _ls_nodes(*args, **kwargs)

    @staticmethod
    def create(**kwargs):
        return _create_node(AnimCurve._mel_type, **kwargs)

    def __init__(self, mobj):
        # type: (om2.MObject) -> NoReturn
        super(AnimCurve, self).__init__(mobj)


class DisplayLayer(DependNode):

    _mfn_type = om2.MFn.kDisplayLayer
    _mfn_set = om2.
    _mel_type = 'displayLayer'

    @staticmethod
    def ls(*args, **kwargs):
        kwargs['type'] = DisplayLayer._mel_type
        return _ls_nodes(*args, **kwargs)

    @staticmethod
    def create(**kwargs):
        return _create_node(DisplayLayer._mel_type, **kwargs)

    def __init__(self, mobj):
        # type: (om2.MObject) -> NoReturn
        super(DisplayLayer, self).__init__(mobj)


class GeometryFilter(DependNode):

    _mfn_type = om2.MFn.kGeometryFilter
    _mfn_set = om2.
    _mel_type = 'geometryFilter'

    @staticmethod
    def ls(*args, **kwargs):
        kwargs['type'] = GeometryFilter._mel_type
        return _ls_nodes(*args, **kwargs)

    @staticmethod
    def create(**kwargs):
        return _create_node(GeometryFilter._mel_type, **kwargs)

    def __init__(self, mobj):
        # type: (om2.MObject) -> NoReturn
        super(GeometryFilter, self).__init__(mobj)


class SkinCluster(GeometryFilter):

    _mfn_type = om2.MFn.kSkinCluster
    _mfn_set = om2.MFnSkinCluster
    _mel_type = 'skinCluster'

    @staticmethod
    def ls(*args, **kwargs):
        kwargs['type'] = SkinCluster._mel_type
        return _ls_nodes(*args, **kwargs)

    @staticmethod
    def create(**kwargs):
        return _create_node(SkinCluster._mel_type, **kwargs)

    def __init__(self, mobj):
        # type: (om2.MObject) -> NoReturn
        super(SkinCluster, self).__init__(mobj)


class Entity(ContainerBase):

    _mfn_type = om2.MFn.
    _mfn_set = om2.
    _mel_type = ''

    @staticmethod
    def ls(*args, **kwargs):
        kwargs['type'] = Entity._mel_type
        return _ls_nodes(*args, **kwargs)

    @staticmethod
    def create(**kwargs):
        return _create_node(Entity._mel_type, **kwargs)

    def __init__(self, mobj):
        # type: (om2.MObject) -> NoReturn
        super(Entity, self).__init__(mobj)


class DagNode(Entity):

    _mfn_type = om2.MFn.kDagNode
    _mfn_set = om2.MFnDagNode
    _mel_type = ''

    @staticmethod
    def ls(*args, **kwargs):
        kwargs['type'] = DagNode._mel_type
        return _ls_nodes(*args, **kwargs)

    @staticmethod
    def create(**kwargs):
        return _create_node(DagNode._mel_type, **kwargs)

    def __init__(self, mobj):
        # type: (om2.MObject) -> NoReturn
        super(DagNode, self).__init__(mobj)


class Transform(DagNode):

    _mfn_type = om2.MFn.kTransform
    _mfn_set = om2.MFnTransform
    _mel_type = 'transform'

    @staticmethod
    def ls(*args, **kwargs):
        kwargs['type'] = Transform._mel_type
        return _ls_nodes(*args, **kwargs)

    @staticmethod
    def create(**kwargs):
        return _create_node(Transform._mel_type, **kwargs)

    def __init__(self, mobj):
        # type: (om2.MObject) -> NoReturn
        super(Transform, self).__init__(mobj)


class Joint(Transform):

    _mfn_type = om2.MFn.kJoint
    _mfn_set = om2.MFnJoint
    _mel_type = 'joint'

    @staticmethod
    def ls(*args, **kwargs):
        kwargs['type'] = Joint._mel_type
        return _ls_nodes(*args, **kwargs)

    @staticmethod
    def create(**kwargs):
        return _create_node(Joint._mel_type, **kwargs)

    def __init__(self, mobj):
        # type: (om2.MObject) -> NoReturn
        super(Joint, self).__init__(mobj)


class ObjectSet(Entity):

    _mfn_type = om2.MFn.kObjectSet
    _mfn_set = om2.MFnSet
    _mel_type = 'set'

    @staticmethod
    def ls(*args, **kwargs):
        kwargs['type'] = ObjectSet._mel_type
        return _ls_nodes(*args, **kwargs)

    @staticmethod
    def create(**kwargs):
        return _create_node(ObjectSet._mel_type, **kwargs)

    def __init__(self, mobj):
        # type: (om2.MObject) -> NoReturn
        super(ObjectSet, self).__init__(mobj)


class AnimLayer(ObjectSet):

    _mfn_type = om2.MFn.kAnimLayer
    _mfn_set = om2.
    _mel_type = 'animLayer'

    @staticmethod
    def ls(*args, **kwargs):
        kwargs['type'] = AnimLayer._mel_type
        return _ls_nodes(*args, **kwargs)

    @staticmethod
    def create(**kwargs):
        return _create_node(AnimLayer._mel_type, **kwargs)

    def __init__(self, mobj):
        # type: (om2.MObject) -> NoReturn
        super(AnimLayer, self).__init__(mobj)


class ShadingEngine(ObjectSet):

    _mfn_type = om2.MFn.kShadingEngine
    _mfn_set = om2.
    _mel_type = 'shadingEngine'

    @staticmethod
    def ls(*args, **kwargs):
        kwargs['type'] = ShadingEngine._mel_type
        return _ls_nodes(*args, **kwargs)

    @staticmethod
    def create(**kwargs):
        return _create_node(ShadingEngine._mel_type, **kwargs)

    def __init__(self, mobj):
        # type: (om2.MObject) -> NoReturn
        super(ShadingEngine, self).__init__(mobj)


class Shape(DagNode):

    _mfn_type = om2.MFn.kShape
    _mfn_set = om2.
    _mel_type = 'shape'

    @staticmethod
    def ls(*args, **kwargs):
        kwargs['type'] = Shape._mel_type
        return _ls_nodes(*args, **kwargs)

    @staticmethod
    def create(**kwargs):
        return _create_node(Shape._mel_type, **kwargs)

    def __init__(self, mobj):
        # type: (om2.MObject) -> NoReturn
        super(Shape, self).__init__(mobj)


class Camera(Shape):

    _mfn_type = om2.MFn.kCamera
    _mfn_set = om2.
    _mel_type = 'camera'

    @staticmethod
    def ls(*args, **kwargs):
        kwargs['type'] = Camera._mel_type
        return _ls_nodes(*args, **kwargs)

    @staticmethod
    def create(**kwargs):
        return _create_node(Camera._mel_type, **kwargs)

    def __init__(self, mobj):
        # type: (om2.MObject) -> NoReturn
        super(Camera, self).__init__(mobj)


class GeometryShape(Shape):

    _mfn_type = om2.MFn.
    _mfn_set = om2.
    _mel_type = ''

    @staticmethod
    def ls(*args, **kwargs):
        kwargs['type'] = GeometryShape._mel_type
        return _ls_nodes(*args, **kwargs)

    @staticmethod
    def create(**kwargs):
        return _create_node(GeometryShape._mel_type, **kwargs)

    def __init__(self, mobj):
        # type: (om2.MObject) -> NoReturn
        super(GeometryShape, self).__init__(mobj)


class DeformableShape(GeometryShape):

    _mfn_type = om2.MFn.
    _mfn_set = om2.
    _mel_type = ''

    @staticmethod
    def ls(*args, **kwargs):
        kwargs['type'] = DeformableShape._mel_type
        return _ls_nodes(*args, **kwargs)

    @staticmethod
    def create(**kwargs):
        return _create_node(DeformableShape._mel_type, **kwargs)

    def __init__(self, mobj):
        # type: (om2.MObject) -> NoReturn
        super(DeformableShape, self).__init__(mobj)


class ControlPoint(DeformableShape):

    _mfn_type = om2.MFn.
    _mfn_set = om2.
    _mel_type = ''

    @staticmethod
    def ls(*args, **kwargs):
        kwargs['type'] = ControlPoint._mel_type
        return _ls_nodes(*args, **kwargs)

    @staticmethod
    def create(**kwargs):
        return _create_node(ControlPoint._mel_type, **kwargs)

    def __init__(self, mobj):
        # type: (om2.MObject) -> NoReturn
        super(ControlPoint, self).__init__(mobj)


class SurfaceShape(ControlPoint):

    _mfn_type = om2.MFn.
    _mfn_set = om2.
    _mel_type = ''

    @staticmethod
    def ls(*args, **kwargs):
        kwargs['type'] = SurfaceShape._mel_type
        return _ls_nodes(*args, **kwargs)

    @staticmethod
    def create(**kwargs):
        return _create_node(SurfaceShape._mel_type, **kwargs)

    def __init__(self, mobj):
        # type: (om2.MObject) -> NoReturn
        super(SurfaceShape, self).__init__(mobj)


class Mesh(SurfaceShape):

    _mfn_type = om2.MFn.kMesh
    _mfn_set = om2.MFnMesh
    _mel_type = 'mesh'

    @staticmethod
    def ls(*args, **kwargs):
        kwargs['type'] = Mesh._mel_type
        return _ls_nodes(*args, **kwargs)

    @staticmethod
    def create(**kwargs):
        return _create_node(Mesh._mel_type, **kwargs)

    def __init__(self, mobj):
        # type: (om2.MObject) -> NoReturn
        super(Mesh, self).__init__(mobj)

