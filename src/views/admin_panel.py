from asciimatics.event import MouseEvent
from asciimatics.exceptions import NextScene
from asciimatics.widgets import Frame, Layout, Text, Button, PopupMenu, PopUpDialog


class AdminPanelView(Frame):
    def __init__(self, screen):
        super(AdminPanelView, self).__init__(screen,
                                        int(screen.height * 2 // 7),
                                        int(screen.width * 2 // 7),
                                        # data=form_data,
                                        has_shadow=True,
                                        title="Admin Panel")
        layout = Layout([1, 18, 1])
        self.add_layout(layout)
        layout.add_widget(
            Text(label="Hi!"), 1)
        layout2 = Layout([1, 1, 1, 1])
        self.add_layout(layout2)
        layout2.add_widget(Button("Logout", self._view), 0)
        layout2.add_widget(Button("Quit", self._quit), 3)
        self.fix()

    def process_event(self, event):
        # Handle dynamic pop-ups now.
        if (event is not None and isinstance(event, MouseEvent) and
                event.buttons == MouseEvent.DOUBLE_CLICK):
            # By processing the double-click before Frame handling, we have absolute coordinates.
            options = [
                ("Default", self._set_default),
                ("Green", self._set_green),
                ("Monochrome", self._set_mono),
                ("Bright", self._set_bright),
            ]
            if self.screen.colours >= 256:
                options.append(("Red/white", self._set_tlj))
            self._scene.add_effect(PopupMenu(self.screen, options, event.x, event.y))
            event = None

        # Pass any other event on to the Frame and contained widgets.
        return super(AdminPanelView, self).process_event(event)

    def _quit(self):
        self._scene.add_effect(
            PopUpDialog(self._screen,
                        "Are you sure?",
                        ["Yes", "No"],
                        has_shadow=True,
                        on_close=self._quit_on_yes))

    def _on_change(self):
        changed = False
        self.save()

    def _view(self):
        raise NextScene("Main")
