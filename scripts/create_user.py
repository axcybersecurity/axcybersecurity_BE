import argparse
from getpass import getpass

from sqlmodel import Session

from dependencies.db import DB_ENGINE, create_db_and_table
from models.schemas import UserCreate
from models.user import Position
from services.user_service import UserService


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create a backend login account.")
    parser.add_argument("login_id", help="Login ID")
    parser.add_argument("name", help="Display name")
    parser.add_argument(
        "position",
        choices=[position.value for position in Position],
        help="User position",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    password = getpass("Password: ")
    password_confirmation = getpass("Confirm password: ")

    if not password:
        raise SystemExit("Password cannot be empty.")
    if password != password_confirmation:
        raise SystemExit("Passwords do not match.")

    create_db_and_table()
    user_data = UserCreate(
        login_id=args.login_id,
        password=password,
        name=args.name,
        position=Position(args.position),
    )

    with Session(DB_ENGINE) as session:
        user = UserService(session).create_user(user_data)

    print(f"Created user: {user.login_id} ({user.name}, {user.user_position})")


if __name__ == "__main__":
    main()
