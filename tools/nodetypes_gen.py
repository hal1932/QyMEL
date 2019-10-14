
class DependNode(MayaObject):

    _mfn_type = om2.MFn.kDependencyNode
    _mfn_set = om2.MFnDependencyNode
    _mel_type = ''

    @staticmethod
    def ls(*args, **kwargs):
        # type: (Any, Any) -> List[DependNode]
        kwargs['type'] = DependNode._mel_type
        return _graphs.ls_nodes(*args, **kwargs)

    @staticmethod
    def create(**kwargs):
        # type: (Any) -> DependNode
        return _graphs.create_node(DependNode._mel_type, **kwargs)

    def __init__(self, obj):
        # type: (Union[om2.MObject, str]) -> NoReturn
        if isinstance(obj, (str, unicode)):
            obj, _ = _graphs.get_mobject(obj)
        super(DependNode, self).__init__(obj)


class ContainerBase(DependNode):

    _mfn_type = om2.MFn.kContainerBase
    _mfn_set = om2.MFnDependencyNode
    _mel_type = 'containerBase'

    @staticmethod
    def ls(*args, **kwargs):
        # type: (Any, Any) -> List[ContainerBase]
        kwargs['type'] = ContainerBase._mel_type
        return _graphs.ls_nodes(*args, **kwargs)

    @staticmethod
    def create(**kwargs):
        # type: (Any) -> ContainerBase
        return _graphs.create_node(ContainerBase._mel_type, **kwargs)

    def __init__(self, obj):
        # type: (Union[om2.MObject, str]) -> NoReturn
        if isinstance(obj, (str, unicode)):
            obj, _ = _graphs.get_mobject(obj)
        super(ContainerBase, self).__init__(obj)


class AnimCurve(DependNode):

    _mfn_type = om2.MFn.kAnimCurve
    _mfn_set = om2.MFnAnimCurve
    _mel_type = 'animCurve'

    @staticmethod
    def ls(*args, **kwargs):
        # type: (Any, Any) -> List[AnimCurve]
        kwargs['type'] = AnimCurve._mel_type
        return _graphs.ls_nodes(*args, **kwargs)

    @staticmethod
    def create(**kwargs):
        # type: (Any) -> AnimCurve
        return _graphs.create_node(AnimCurve._mel_type, **kwargs)

    def __init__(self, obj):
        # type: (Union[om2.MObject, str]) -> NoReturn
        if isinstance(obj, (str, unicode)):
            obj, _ = _graphs.get_mobject(obj)
        super(AnimCurve, self).__init__(obj)


class DisplayLayer(DependNode):

    _mfn_type = om2.MFn.kDisplayLayer
    _mfn_set = om2.MFnDependencyNode
    _mel_type = 'displayLayer'

    @staticmethod
    def ls(*args, **kwargs):
        # type: (Any, Any) -> List[DisplayLayer]
        kwargs['type'] = DisplayLayer._mel_type
        return _graphs.ls_nodes(*args, **kwargs)

    @staticmethod
    def create(**kwargs):
        # type: (Any) -> DisplayLayer
        return _graphs.create_node(DisplayLayer._mel_type, **kwargs)

    def __init__(self, obj):
        # type: (Union[om2.MObject, str]) -> NoReturn
        if isinstance(obj, (str, unicode)):
            obj, _ = _graphs.get_mobject(obj)
        super(DisplayLayer, self).__init__(obj)


class GeometryFilter(DependNode):

    _mfn_type = om2.MFn.kGeometryFilt
    _mfn_set = om2.MFnDependencyNode
    _mel_type = 'geometryFilter'

    @staticmethod
    def ls(*args, **kwargs):
        # type: (Any, Any) -> List[GeometryFilter]
        kwargs['type'] = GeometryFilter._mel_type
        return _graphs.ls_nodes(*args, **kwargs)

    @staticmethod
    def create(**kwargs):
        # type: (Any) -> GeometryFilter
        return _graphs.create_node(GeometryFilter._mel_type, **kwargs)

    def __init__(self, obj):
        # type: (Union[om2.MObject, str]) -> NoReturn
        if isinstance(obj, (str, unicode)):
            obj, _ = _graphs.get_mobject(obj)
        super(GeometryFilter, self).__init__(obj)


class SkinCluster(GeometryFilter):

    _mfn_type = om2.MFn.kSkin
    _mfn_set = om2.MFnSkinCluster
    _mel_type = 'skinCluster'

    @staticmethod
    def ls(*args, **kwargs):
        # type: (Any, Any) -> List[SkinCluster]
        kwargs['type'] = SkinCluster._mel_type
        return _graphs.ls_nodes(*args, **kwargs)

    @staticmethod
    def create(**kwargs):
        # type: (Any) -> SkinCluster
        return _graphs.create_node(SkinCluster._mel_type, **kwargs)

    def __init__(self, obj):
        # type: (Union[om2.MObject, str]) -> NoReturn
        if isinstance(obj, (str, unicode)):
            obj, _ = _graphs.get_mobject(obj)
        super(SkinCluster, self).__init__(obj)


class Entity(ContainerBase):

    _mfn_type = om2.MFn.None
    _mfn_set = om2.None
    _mel_type = ''

    @staticmethod
    def ls(*args, **kwargs):
        # type: (Any, Any) -> List[Entity]
        kwargs['type'] = Entity._mel_type
        return _graphs.ls_nodes(*args, **kwargs)

    @staticmethod
    def create(**kwargs):
        # type: (Any) -> Entity
        return _graphs.create_node(Entity._mel_type, **kwargs)

    def __init__(self, obj):
        # type: (Union[om2.MObject, str]) -> NoReturn
        if isinstance(obj, (str, unicode)):
            obj, _ = _graphs.get_mobject(obj)
        super(Entity, self).__init__(obj)


class DagNode(Entity):

    _mfn_type = om2.MFn.kDagNode
    _mfn_set = om2.MFnDagNode
    _mel_type = ''

    @staticmethod
    def ls(*args, **kwargs):
        # type: (Any, Any) -> List[DagNode]
        kwargs['type'] = DagNode._mel_type
        return _graphs.ls_nodes(*args, **kwargs)

    @staticmethod
    def create(**kwargs):
        # type: (Any) -> DagNode
        return _graphs.create_node(DagNode._mel_type, **kwargs)

    def __init__(self, obj):
        # type: (Union[om2.MObject, str]) -> NoReturn
        if isinstance(obj, (str, unicode)):
            obj, _ = _graphs.get_mobject(obj)
        super(DagNode, self).__init__(obj)


class Transform(DagNode):

    _mfn_type = om2.MFn.kTransform
    _mfn_set = om2.MFnTransform
    _mel_type = 'transform'

    @staticmethod
    def ls(*args, **kwargs):
        # type: (Any, Any) -> List[Transform]
        kwargs['type'] = Transform._mel_type
        return _graphs.ls_nodes(*args, **kwargs)

    @staticmethod
    def create(**kwargs):
        # type: (Any) -> Transform
        return _graphs.create_node(Transform._mel_type, **kwargs)

    def __init__(self, obj):
        # type: (Union[om2.MObject, str]) -> NoReturn
        if isinstance(obj, (str, unicode)):
            obj, _ = _graphs.get_mobject(obj)
        super(Transform, self).__init__(obj)


class Joint(Transform):

    _mfn_type = om2.MFn.kJoint
    _mfn_set = om2.MFnTransform
    _mel_type = 'joint'

    @staticmethod
    def ls(*args, **kwargs):
        # type: (Any, Any) -> List[Joint]
        kwargs['type'] = Joint._mel_type
        return _graphs.ls_nodes(*args, **kwargs)

    @staticmethod
    def create(**kwargs):
        # type: (Any) -> Joint
        return _graphs.create_node(Joint._mel_type, **kwargs)

    def __init__(self, obj):
        # type: (Union[om2.MObject, str]) -> NoReturn
        if isinstance(obj, (str, unicode)):
            obj, _ = _graphs.get_mobject(obj)
        super(Joint, self).__init__(obj)


class ObjectSet(Entity):

    _mfn_type = om2.MFn.kSet
    _mfn_set = om2.MFnSet
    _mel_type = 'objectSet'

    @staticmethod
    def ls(*args, **kwargs):
        # type: (Any, Any) -> List[ObjectSet]
        kwargs['type'] = ObjectSet._mel_type
        return _graphs.ls_nodes(*args, **kwargs)

    @staticmethod
    def create(**kwargs):
        # type: (Any) -> ObjectSet
        return _graphs.create_node(ObjectSet._mel_type, **kwargs)

    def __init__(self, obj):
        # type: (Union[om2.MObject, str]) -> NoReturn
        if isinstance(obj, (str, unicode)):
            obj, _ = _graphs.get_mobject(obj)
        super(ObjectSet, self).__init__(obj)


class AnimLayer(ObjectSet):

    _mfn_type = om2.MFn.kAnimLayer
    _mfn_set = om2.MFnSet
    _mel_type = 'animLayer'

    @staticmethod
    def ls(*args, **kwargs):
        # type: (Any, Any) -> List[AnimLayer]
        kwargs['type'] = AnimLayer._mel_type
        return _graphs.ls_nodes(*args, **kwargs)

    @staticmethod
    def create(**kwargs):
        # type: (Any) -> AnimLayer
        return _graphs.create_node(AnimLayer._mel_type, **kwargs)

    def __init__(self, obj):
        # type: (Union[om2.MObject, str]) -> NoReturn
        if isinstance(obj, (str, unicode)):
            obj, _ = _graphs.get_mobject(obj)
        super(AnimLayer, self).__init__(obj)


class ShadingEngine(ObjectSet):

    _mfn_type = om2.MFn.kShadingEngine
    _mfn_set = om2.MFnDependencyNode
    _mel_type = 'shadingEngine'

    @staticmethod
    def ls(*args, **kwargs):
        # type: (Any, Any) -> List[ShadingEngine]
        kwargs['type'] = ShadingEngine._mel_type
        return _graphs.ls_nodes(*args, **kwargs)

    @staticmethod
    def create(**kwargs):
        # type: (Any) -> ShadingEngine
        return _graphs.create_node(ShadingEngine._mel_type, **kwargs)

    def __init__(self, obj):
        # type: (Union[om2.MObject, str]) -> NoReturn
        if isinstance(obj, (str, unicode)):
            obj, _ = _graphs.get_mobject(obj)
        super(ShadingEngine, self).__init__(obj)


class Shape(DagNode):

    _mfn_type = om2.MFn.kShape
    _mfn_set = om2.MFnDagNode
    _mel_type = 'shape'

    @staticmethod
    def ls(*args, **kwargs):
        # type: (Any, Any) -> List[Shape]
        kwargs['type'] = Shape._mel_type
        return _graphs.ls_nodes(*args, **kwargs)

    @staticmethod
    def create(**kwargs):
        # type: (Any) -> Shape
        return _graphs.create_node(Shape._mel_type, **kwargs)

    def __init__(self, obj):
        # type: (Union[om2.MObject, str]) -> NoReturn
        if isinstance(obj, (str, unicode)):
            obj, _ = _graphs.get_mobject(obj)
        super(Shape, self).__init__(obj)


class Camera(Shape):

    _mfn_type = om2.MFn.kCamera
    _mfn_set = om2.MFnCamera
    _mel_type = 'camera'

    @staticmethod
    def ls(*args, **kwargs):
        # type: (Any, Any) -> List[Camera]
        kwargs['type'] = Camera._mel_type
        return _graphs.ls_nodes(*args, **kwargs)

    @staticmethod
    def create(**kwargs):
        # type: (Any) -> Camera
        return _graphs.create_node(Camera._mel_type, **kwargs)

    def __init__(self, obj):
        # type: (Union[om2.MObject, str]) -> NoReturn
        if isinstance(obj, (str, unicode)):
            obj, _ = _graphs.get_mobject(obj)
        super(Camera, self).__init__(obj)


class GeometryShape(Shape):

    _mfn_type = om2.MFn.None
    _mfn_set = om2.MFnDagNode
    _mel_type = 'geometryShape'

    @staticmethod
    def ls(*args, **kwargs):
        # type: (Any, Any) -> List[GeometryShape]
        kwargs['type'] = GeometryShape._mel_type
        return _graphs.ls_nodes(*args, **kwargs)

    @staticmethod
    def create(**kwargs):
        # type: (Any) -> GeometryShape
        return _graphs.create_node(GeometryShape._mel_type, **kwargs)

    def __init__(self, obj):
        # type: (Union[om2.MObject, str]) -> NoReturn
        if isinstance(obj, (str, unicode)):
            obj, _ = _graphs.get_mobject(obj)
        super(GeometryShape, self).__init__(obj)


class DeformableShape(GeometryShape):

    _mfn_type = om2.MFn.None
    _mfn_set = om2.MFnDagNode
    _mel_type = 'deformableShape'

    @staticmethod
    def ls(*args, **kwargs):
        # type: (Any, Any) -> List[DeformableShape]
        kwargs['type'] = DeformableShape._mel_type
        return _graphs.ls_nodes(*args, **kwargs)

    @staticmethod
    def create(**kwargs):
        # type: (Any) -> DeformableShape
        return _graphs.create_node(DeformableShape._mel_type, **kwargs)

    def __init__(self, obj):
        # type: (Union[om2.MObject, str]) -> NoReturn
        if isinstance(obj, (str, unicode)):
            obj, _ = _graphs.get_mobject(obj)
        super(DeformableShape, self).__init__(obj)


class ControlPoint(DeformableShape):

    _mfn_type = om2.MFn.None
    _mfn_set = om2.MFnDagNode
    _mel_type = 'controlPoint'

    @staticmethod
    def ls(*args, **kwargs):
        # type: (Any, Any) -> List[ControlPoint]
        kwargs['type'] = ControlPoint._mel_type
        return _graphs.ls_nodes(*args, **kwargs)

    @staticmethod
    def create(**kwargs):
        # type: (Any) -> ControlPoint
        return _graphs.create_node(ControlPoint._mel_type, **kwargs)

    def __init__(self, obj):
        # type: (Union[om2.MObject, str]) -> NoReturn
        if isinstance(obj, (str, unicode)):
            obj, _ = _graphs.get_mobject(obj)
        super(ControlPoint, self).__init__(obj)


class SurfaceShape(ControlPoint):

    _mfn_type = om2.MFn.None
    _mfn_set = om2.MFnDagNode
    _mel_type = 'surfaceShape'

    @staticmethod
    def ls(*args, **kwargs):
        # type: (Any, Any) -> List[SurfaceShape]
        kwargs['type'] = SurfaceShape._mel_type
        return _graphs.ls_nodes(*args, **kwargs)

    @staticmethod
    def create(**kwargs):
        # type: (Any) -> SurfaceShape
        return _graphs.create_node(SurfaceShape._mel_type, **kwargs)

    def __init__(self, obj):
        # type: (Union[om2.MObject, str]) -> NoReturn
        if isinstance(obj, (str, unicode)):
            obj, _ = _graphs.get_mobject(obj)
        super(SurfaceShape, self).__init__(obj)


class Mesh(SurfaceShape):

    _mfn_type = om2.MFn.kMesh
    _mfn_set = om2.MFnMesh
    _mel_type = 'mesh'

    @staticmethod
    def ls(*args, **kwargs):
        # type: (Any, Any) -> List[Mesh]
        kwargs['type'] = Mesh._mel_type
        return _graphs.ls_nodes(*args, **kwargs)

    @staticmethod
    def create(**kwargs):
        # type: (Any) -> Mesh
        return _graphs.create_node(Mesh._mel_type, **kwargs)

    def __init__(self, obj):
        # type: (Union[om2.MObject, str]) -> NoReturn
        if isinstance(obj, (str, unicode)):
            obj, _ = _graphs.get_mobject(obj)
        super(Mesh, self).__init__(obj)

