from dotenv import load_dotenv

load_dotenv()

from modules.controller import controller


def main() -> None:
    controller()


if __name__ == "__main__":
    main()