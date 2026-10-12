"""Ownership is enforced by the selector, so a foreign id is a 404 not a 403."""
import pytest
from rest_framework.test import APIClient

from conftest import make_session
from modules.elm.models import LeaveType, LeaveApplication
from modules.directory.models import UserRef


pytestmark = pytest.mark.django_db


@pytest.fixture
def leave_type():
    return LeaveType.objects.create(code="CL", name="Casual Leave")


@pytest.fixture
def user_ref(user_id=1001):
    return UserRef.objects.create(
        user_id=user_id, username=f"u{user_id}", display_name=f"User {user_id}", kind="faculty"
    )


@pytest.fixture
def faculty_user(leave_type, user_ref):
    return make_session(
        user_id=1001,
        permissions=("elm.application.create",),
        modules=("elm",),
        kind="faculty",
        roles=("faculty",),
        active_role="faculty",
    )


@pytest.fixture
def non_faculty_user(leave_type, user_ref):
    return make_session(
        user_id=2002,
        permissions=(),
        modules=("elm",),
        kind="student",
        roles=("student",),
        active_role="student",
    )


def test_create_leave_application(faculty_user, leave_type, user_ref):
    c = APIClient()
    c.credentials(HTTP_AUTHORIZATION="Token abc")

    data = {
        "leave_type": leave_type.code,
        "start_date": "2023-10-01",
        "end_date": "2023-10-05",
        "is_half_day": False,
        "reason": "Sick"
    }

    response = c.post("/api/v1/elm/applications/create", data, format="json")
    assert response.status_code == 201
    created_application = LeaveApplication.objects.get(pk=response.json()["id"])
    assert created_application.applicant_id == faculty_user.user_id
    assert created_application.status == "PENDING"


def test_create_leave_application_without_permission(non_faculty_user, leave_type):
    c = APIClient()
    c.credentials(HTTP_AUTHORIZATION="Token abc")

    data = {
        "leave_type": leave_type.code,
        "start_date": "2023-10-01",
        "end_date": "2023-10-05",
        "is_half_day": False,
        "reason": "Sick"
    }

    response = c.post("/api/v1/elm/applications/create", data, format="json")
    assert response.status_code == 403


def test_create_leave_application_with_invalid_status(faculty_user, leave_type):
    c = APIClient()
    c.credentials(HTTP_AUTHORIZATION="Token abc")

    data = {
        "leave_type": leave_type.code,
        "start_date": "2023-10-01",
        "end_date": "2023-10-05",
        "is_half_day": False,
        "reason": "Sick",
        "status": "APPROVED"
    }

    response = c.post("/api/v1/elm/applications/create", data, format="json")
    assert response.status_code == 201
    created_application = LeaveApplication.objects.get(pk=response.json()["id"])
    assert created_application.applicant_id == faculty_user.user_id
    assert created_application.status == "PENDING"


def test_view_leave_applications(faculty_user):
    c = APIClient()
    c.credentials(HTTP_AUTHORIZATION="Token abc")

    user_ref(user_id=1002)
    LeaveApplication.objects.create(
        applicant_id=1002,
        leave_type_id=LeaveType.objects.get(code="CL").id,
        start_date="2023-10-01",
        end_date="2023-10-05",
        is_half_day=False,
        reason="Sick"
    )

    response = c.get("/api/v1/elm/applications")
    assert response.status_code == 200
    applications = response.json()["results"]
    assert len(applications) == 1
    assert applications[0]["applicant"] == faculty_user.user_id
