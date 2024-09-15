import pytest

from app import create_app
from models import db, User, Sprint, BugReport
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
    sprint = Sprint(start_date='2024-01-01', end_date='2024-01-14', name='Sprint 1', bugs=[])
    db.session.add(sprint)
    db.session.commit()

    bug_report = BugReport(number=1, bug_type='Type A', description='Bug description', is_open=True,
                           is_fixed=False, reason_for_close="", user_id=user.id, sprint_id=sprint.id)
    db.session.add(bug_report)

    db.session.commit()
    client.post('/login', data={
        'username': 'test_user',
        'password': 'test_password'
    }, follow_redirects=True)
    return client


def test_bugs_route(logged_in_client):
    response = logged_in_client.get('/bugs')
    assert response.status_code == 200


def test_bug_route_existing_bug(logged_in_client):
    response = logged_in_client.get('/bugs/1')
    assert response.status_code == 200


def test_bug_route_non_existing_bug(logged_in_client):
    response = logged_in_client.get('/bugs/999')
    assert response.status_code == 404


def test_bug_report_route_get(logged_in_client):
    response = logged_in_client.get('/bug_report')
    assert response.status_code == 200


def test_bug_report_route_post_existing_bug(logged_in_client):
    response = logged_in_client.post('/bug_report', data={
        'report_number': '1',
        'bug_type': 'Type',
        'bug_summary': 'Summary',
        'current_date': '2022-01-01',
        'update_notification': 'on'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Bug report already exists!' in response.data


def test_bug_report_route_post_no_sprint(logged_in_client):
    response = logged_in_client.post('/bug_report', data={
        'report_number': '2',
        'bug_type': 'Type',
        'bug_summary': 'Summary',
        'current_date': '2022-01-01',
        'update_notification': 'on'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'There is no sprint for this date yet, please create one!' in response.data


def test_subscribe_bug_report_route(logged_in_client):
    response = logged_in_client.post('/subscribe_bug_report/1', data={})
    assert response.status_code == 302  # Redirects to /bugs/1


def test_edit_bug_report_route(logged_in_client):
    response = logged_in_client.post('/edit_bug_report/1', data={
        'report_number': '1',
        'bug_type': 'Updated Type',
        'description': 'Updated Description'
    })
    assert response.status_code == 302  # Redirects to /bugs/1


def test_close_bug_report_route(logged_in_client):
    response = logged_in_client.post('/bug_report/close/1', data={'close_reason': 'Reason'})
    assert response.status_code == 302  # Redirects to /bugs/1


def test_fix_bug_report_route(logged_in_client):
    response = logged_in_client.post('/bug_report/fix/1', data={})
    assert response.status_code == 302  # Redirects to /bugs/1


def test_sprint_route_get(logged_in_client):
    response = logged_in_client.get('/sprint')
    assert response.status_code == 200


def test_sprint_route_post_existing_sprint(logged_in_client):
    response = logged_in_client.post('/sprint', data={
        'sprint_name': 'Sprint 1',
        'start_date': '2022-01-01',
        'end_date': '2022-01-07'
    }, follow_redirects=True)
    assert response.status_code == 200


def test_sprint_route_post_new_sprint(logged_in_client):
    response = logged_in_client.post('/sprint', data={
        'sprint_name': 'New Sprint',
        'start_date': '2022-01-08',
        'end_date': '2022-01-14'
    }, follow_redirects=True)
    assert response.status_code == 200  # Redirects to /sprint


def test_sprint_statistics_route(logged_in_client):
    response = logged_in_client.get('/sprint_statistics', follow_redirects=True)
    assert response.status_code == 200
