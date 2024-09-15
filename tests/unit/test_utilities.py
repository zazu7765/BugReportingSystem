import pytest

from app import create_app
from models import db, User, Sprint, BugReport
from utilities import check_existing_employee, hash_password, check_existing_username, send_email, check_date_in_sprint, \
    check_existing_sprint_by_name, check_existing_bug_report_by_number, check_existing_email


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


@pytest.fixture
def dbClient(client):
    existing_employee = User(username="test_user", email="test_email@email.com",
                             password=hash_password("test_password"),
                             employee_id="123456789")
    db.session.add(existing_employee)
    db.session.commit()
    return client

@pytest.fixture
def dataClient(dbClient):
    sprint_1 = Sprint(start_date='2024-01-01', end_date='2024-01-14', name='Test Sprint')
    db.session.add(sprint_1)
    db.session.commit()

    bug_1 = BugReport(number=1, bug_type='Type A', description='Description A',
                       is_open=True, user_id=1, sprint_id=1)

    db.session.add(bug_1)

    db.session.commit()

@pytest.fixture
def mock_smtp(monkeypatch):
    class MockSMTP:
        def __init__(self, *args, **kwargs):
            pass

        def sendmail(self, *args, **kwargs):
            pass

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            pass

    monkeypatch.setattr("utilities.smtplib.SMTP_SSL", MockSMTP)
    return MockSMTP


@pytest.mark.parametrize("employee_id, expected", [
    ("123456789", True),
    ("987654321", False)
])
def test_check_existing_employee_pass(dbClient, employee_id, expected):
    result = check_existing_employee(employee_id)
    assert (result is not None) == expected


@pytest.mark.parametrize("username, expected", [
    ("test_user", True),
    ("bad_user", False)
])
def test_check_existing_username_pass(dbClient, username, expected):
    result = check_existing_username(username)
    assert (result is not None) == expected


@pytest.mark.parametrize("email, expected", [
    ("test_email@email.com", True),
    ("nonexistent_email@email.com", False)
])
def test_check_existing_email(dbClient, email, expected):
    result = check_existing_email(email)
    assert (result is not None) == expected


@pytest.mark.parametrize("number, expected", [
    (1, True),
    (999, False)
])
def test_check_existing_bug_report_by_number(dataClient, number, expected):
    result = check_existing_bug_report_by_number(number)
    assert (result is not None) == expected


@pytest.mark.parametrize("sprint_name, expected", [
    ("Test Sprint", True),
    ("Nonexistent Sprint", False)
])
def test_check_existing_sprint_by_name(dataClient, sprint_name, expected):
    result = check_existing_sprint_by_name(sprint_name)
    assert (result is not None) == expected


@pytest.mark.parametrize("date, expected", [
    ("2024-01-01", True),
    ("2024-12-31", False)
])
def test_check_date_in_sprint(dataClient, date, expected):
    result = check_date_in_sprint(date)
    assert (result is not None) == expected


def test_hash_password():
    password = "test_password"
    hashed_password = hash_password(password)
    assert hashed_password != password
    assert len(hashed_password) > 0


def test_send_email(mock_smtp):
    assert send_email('receiver@example.com', 'Test Subject', 'Test Body') == 1
