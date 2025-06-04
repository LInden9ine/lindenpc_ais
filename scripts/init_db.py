from peewee import IntegrityError
from api.database import create_tables, Role, User
import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


def initialize_database():
    create_tables()

    # Создаем роли
    admin_role, _ = Role.get_or_create(
        role_name='admin', description='Administrator')
    staff_role, _ = Role.get_or_create(
        role_name='staff', description='Staff member')

    # Создаем администратора по умолчанию (если еще не существует)
    try:
        User.create(
            login='admin',
            # ***WARNING: NEVER store passwords in plaintext in a real application!***
            password='password',
            email='admin@example.com',
            first_name='Admin',
            last_name='Istrator',
            role=admin_role
        )
        print("Admin user created.")
    except IntegrityError:
        print("Admin user already exists.")


if __name__ == '__main__':
    initialize_database()
    print("Database initialized.")
