from PyQt5.QtWidgets import QAction

def create_atlas_editor_actions(plugin_instance, window, menu):
    atlas_action = QAction("Show Atlas Docker", window)
    atlas_action.triggered.connect(lambda: _show_atlas_docker(window))
    menu.addAction(atlas_action)

def _show_atlas_docker(main_window):
    for docker in main_window.findChildren(object):
        if hasattr(docker, "windowTitle") and docker.windowTitle() == "Atlas Editor":
            docker.setVisible(True)
            docker.raise_()
            return