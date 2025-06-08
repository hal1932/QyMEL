
import maya.utils as _utils
import maya.mel as _mel


def main():
    import os
    import maya_custom_menu
    import qymel.maya.user_setup_utils as uutils

    settings_path = os.path.join(os.path.dirname(uutils.current_file_path()), 'sample_settings.json')
    maya_window = _mel.eval('$_ = $gMainWindow')
    maya_custom_menu.create_custom_menu(settings_path, maya_window)


_utils.executeDeferred(main)
