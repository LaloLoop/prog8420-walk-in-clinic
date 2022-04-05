import sys

from asciimatics.exceptions import ResizeScreenError
from asciimatics.screen import Screen
from sqlalchemy import create_engine

from src.controller.controller import Controller
from src.views.setup import scenes_setup


def main():
    engine = create_engine('sqlite:///wic.sqlite', echo=False)

    controller = Controller(engine)
    controller.init_db()



    last_scene = None
    while True:
        try:
            Screen.wrapper(scenes_setup(controller), catch_interrupt=False, arguments=[last_scene])
            sys.exit(0)
        except ResizeScreenError as e:
            last_scene = e.scene


if __name__ == "__main__":
    main()