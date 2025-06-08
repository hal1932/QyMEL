
import maya.cmds as _cmds
import maya.mel as _mel


class MenuItem(object):

    @property
    def mel_object(self) -> str:
        return self.__name

    @property
    def label(self) -> str:
        return _cmds.menuItem(self.mel_object, query=True, label=True)

    @property
    def has_child(self) -> bool:
        return _cmds.menuItem(self.mel_object, query=True, subMenu=True)

    def __init__(self, name: str):
        self.__name = name

    def __repr__(self):
        return f'MenuItem(\'{self.mel_object}\')'

    def __str__(self):
        return f'<MenuItem {self.mel_object} label="{self.label}">'

    def children(self) -> list['MenuItem']:
        items = _cmds.menu(self.mel_object, query=True, itemArray=True) or []
        return [MenuItem(item) for item in items]


class Menu(object):

    @staticmethod
    def root_menus() -> list['Menu']:
        main_window = _mel.eval('$_ = $gMainWindow')
        menus = _cmds.window(main_window, query=True, menuArray=True)
        return [Menu(menu) for menu in menus]

    @staticmethod
    def find_by_label(label: str) -> 'Menu'|None:
        for menu in Menu.root_menus():
            if menu.label == label:
                return menu
        return None

    @property
    def mel_object(self) -> str:
        return self.__mel_object

    @property
    def has_items(self) -> bool:
        return _cmds.menu(self.mel_object, query=True, numberOfItems=True) > 0

    def __init__(self, name: str|None = None):
        self.__mel_object = name
        self.__updated_properties: dict[str, object] = {}

    def __repr__(self):
        return f'Menu(\'{self.mel_object}\')'

    def __str__(self):
        return f'<Menu {self.mel_object} label="{self.label}">'

    def __getattr__(self, item: str):
        mel_object = self.__mel_object
        if not mel_object:
            raise RuntimeError('cannot get property from non-existing menu')
        return _cmds.menu(mel_object, query=True, **{item: True})

    def __setattr__(self, key: str, value: object):
        def called_from_self_init():
            import inspect
            caller_frame = inspect.currentframe().f_back
            caller_obj = caller_frame.f_locals.get('self', None)
            caller_func_name = caller_frame.f_code.co_name
            caller_func = getattr(caller_obj, caller_func_name, None)
            return caller_func == self.__init__

        if called_from_self_init():
            super().__setattr__(key, value)
        else:
            self.__updated_properties[key] = value

    def items(self) -> list[MenuItem]:
        items = _cmds.menu(self.mel_object, query=True, itemArray=True) or []
        return [MenuItem(item) for item in items]

    def apply_property_updates(self) -> None:
        if not _cmds.menu(self.__mel_object, exists=True):
            parent = self.__updated_properties.get('parent', None)
            if not parent:
                raise RuntimeError('cannot create menu without parent')
            self.__mel_object = _cmds.menu(**self.__updated_properties)
        _cmds.menu(self.mel_object, edit=True, **self.__updated_properties)

    def delete(self) -> None:
        _cmds.deleteUI(self.mel_object)

    def delete_items(self) -> None:
        _cmds.menu(self.mel_object, edit=True, deleteAllItems=True)
