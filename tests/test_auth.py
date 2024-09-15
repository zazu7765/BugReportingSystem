import pytest

from app import create_app
from models import db, User
from utilities import hash_password


@pytest.fixture
def client():
    """Create and configure a new app instance for each test."""
    app = create_app(testing=True)
    app.config['WTF_CSRF_ENABLED'] = False
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.session.remove()
            db.drop_all()


@pytest.fixture
def logged_in_client(client):
    user = User(username="test_user", email="test_email@email.com", password=hash_password("test_password"),
                employee_id="123456789")
    db.session.add(user)
    db.session.commit()
    client.post('/login', data={
        'username': 'test_user',
        'password': 'test_password'
    }, follow_redirects=True)
    return client


def test_register_route_correct(client):
    response = client.post('/register', data={
        "username": "test_user",
        "email": "test_email@email.com",
        "password": "test_password",
        "confirm_password": "test_password",
        "employee_id": "123456789"
    }, follow_redirects=True)
    assert response.status_code == 200
    assert response.request.path == "/login"


def test_register_route_incorrect_bad_email(client):
    response = client.post('/register', data={
        "username": "test_user",
        "email": "test_email_com",
        "password": "test_password",
        "confirm_password": "test_password",
        "employee_id": "123456789"
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'alert' in response.data


def test_register_route_incorrect_bad_confirm_password(client):
    response = client.post('/register', data={
        "username": "test_user",
        "email": "test_email@email.com",
        "password": "test_password",
        "confirm_password": "not_test_password",
        "employee_id": "123456789"
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'alert' in response.data


def test_register_route_incorrect_user_exists(logged_in_client):
    logged_in_client.post('/logout')
    response = logged_in_client.post('/register', data={
        "username": "test_user",
        "email": "test_emails@email.com",
        "password": "test_password",
        "confirm_password": "test_password",
        "employee_id": "1234567890"
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'alert' in response.data


def test_register_route_incorrect_employee_id_used(logged_in_client):
    logged_in_client.post('/logout')
    response = logged_in_client.post('/register', data={
        "username": "test_users",
        "email": "test_emails@email.com",
        "password": "test_password",
        "confirm_password": "test_password",
        "employee_id": "123456789"
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'alert' in response.data


def test_register_route_incorrect_email_used(logged_in_client):
    logged_in_client.post('/logout')
    response = logged_in_client.post('/register', data={
        "username": "test_users",
        "email": "test_email@email.com",
        "password": "test_password",
        "confirm_password": "test_password",
        "employee_id": "1234567890"
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'alert' in response.data
def test_login_route_correct(client):
    user = User(username="test_user", email="test_email@email.com", password=hash_password("test_password"),
                employee_id="123456789")
    db.session.add(user)
    db.session.commit()
    response = client.post('/login', data={
        'username': 'test_user',
        'password': 'test_password'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert response.request.path == "/"


def test_login_route_incorrect(client):
    response = client.post('/login', data={
        'username': 'test_user',
        'password': 'test_password'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'alert' in response.data


def test_logout_route_correct(logged_in_client):
    """Test logout route."""
    response = logged_in_client.get('/logout', follow_redirects=True)
    assert response.status_code == 200
    assert response.request.path == "/"


def test_logout_route_incorrect(client):
    response = client.get('/logout', follow_redirects=True)
    assert response.status_code == 200

