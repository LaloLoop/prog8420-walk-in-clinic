from asciimatics.scene import Scene

from src.views.admin_panel import AdminPanelView
from src.views.login import LoginView


def scenes_setup(controller):
    def app_views(screen, scene):
        scenes = [
            Scene([LoginView(screen, controller)], -1, name="Main"),
            Scene([AdminPanelView(screen)], -1, name="Admin Panel")
        ]

        screen.play(scenes, stop_on_resize=True, start_scene=scene, allow_int=True)

    return app_views