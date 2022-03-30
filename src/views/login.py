#!/usr/bin/env python3

import logging
import re

from asciimatics.event import MouseEvent
from asciimatics.exceptions import NextScene, StopApplication, \
    InvalidFields
from asciimatics.scene import Scene
from asciimatics.widgets import Frame, Layout, Text, \
    Button, PopUpDialog, PopupMenu

# Initial data for the form
from src.controller.controller import Controller

form_data = {
    "username": "admin@wic.com",
    "password": "pr0g4dmin"
}

logging.basicConfig(filename="forms.log", level=logging.DEBUG)


class LoginView(Frame):
    def __init__(self, screen, controller: Controller):
        super(LoginView, self).__init__(screen,
                                        int(screen.height * 2 // 7),
                                        int(screen.width * 2 // 7),
                                        data=form_data,
                                        has_shadow=True,
                                        title="Login")

        self.controller = controller

        layout = Layout([1, 18, 1])
        self.add_layout(layout)
        layout.add_widget(
            Text(label="User:",
                 name="username",
                 on_change=self._on_change,
                 validator=self._check_email), 1)
        layout.add_widget(Text("Password", name="password", on_change=self._on_change, hide_char="*"), 1)
        layout2 = Layout([1, 1, 1, 1])
        self.add_layout(layout2)
        layout2.add_widget(Button("Login", self._view), 0)
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
        return super(LoginView, self).process_event(event)

    def _set_default(self):
        self.set_theme("default")

    def _set_green(self):
        self.set_theme("green")

    def _set_mono(self):
        self.set_theme("monochrome")

    def _set_bright(self):
        self.set_theme("bright")

    def _set_tlj(self):
        self.set_theme("tlj256")

    def _on_change(self):
        changed = False
        self.save()
        for key, value in self.data.items():
            if key not in form_data or form_data[key] != value:
                changed = True
                break

    def _reset(self):
        self.reset()
        raise NextScene()

    def _view(self):
        # Build result of this form and display it.
        try:
            self.save(validate=True)
            message = "Values entered are:\n\n"
            for key, value in self.data.items():
                message += "- {}: {}\n".format(key, value)
        except InvalidFields as exc:
            message = "The following fields are invalid:\n\n"
            for field in exc.fields:
                message += "- {}\n".format(field)

        success = self.controller.login(self.data)

        if success:
            raise NextScene("Admin Panel")
        else:
            self._scene.add_effect(
                PopUpDialog(self._screen, "Login failed", ["¯\_(ツ)_/¯"]))

    def _quit(self):
        self._scene.add_effect(
            PopUpDialog(self._screen,
                        "Are you sure?",
                        ["Yes", "No"],
                        has_shadow=True,
                        on_close=self._quit_on_yes))

    @staticmethod
    def _check_email(value):
        m = re.match(r"^[a-zA-Z0-9_\-.]+@[a-zA-Z0-9_\-.]+\.[a-zA-Z0-9_\-.]+$",
                     value)
        return len(value) == 0 or m is not None

    @staticmethod
    def _quit_on_yes(selected):
        # Yes is the first button
        if selected == 0:
            raise StopApplication("User requested exit")


