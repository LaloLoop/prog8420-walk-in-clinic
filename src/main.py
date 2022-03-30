from sqlalchemy import create_engine

from src.controller.controller import Controller


def main():
    engine = create_engine('sqlite:///wic.sqlite', echo=True)

    controller = Controller(engine)
    controller.init_db()


if __name__ == "__main__":
    main()