import pytest

from app import create_app
from models import db, User
from utilities import check_existing_employee, hash_password


@pytest.fixture
def client():
    """Create and configure a new app instance for each test."""
    app = create_app(testing=True)
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.session.remove()
            db.drop_all()


def test_check_existing_employee_existing_user(client):
    # Set up: Add a user with the given employee_id to the database
    existing_employee = User(username="test_user", email="test_email@email.com", password=hash_password("test_password"),
                employee_id="123456789")
    db.session.add(existing_employee)
    db.session.commit()

    # Call the function with an existing employee_id
    result = check_existing_employee('123456789')

    # Assert that the function returns the user
    assert result == existing_employee
