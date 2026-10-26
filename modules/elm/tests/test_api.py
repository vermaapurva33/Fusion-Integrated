"""Ownership is enforced by the selector, so a foreign id is a 404 not a 403."""
import pytest
from rest_framework.test import APIClient

from conftest import make_session, stub_iam, user_ref
from modules.elm.models import LeaveType, LeaveApplication
from modules.directory.models import UserRef


pytestmark = pytest.mark.django_db


@pytest.fixture
def leave_type():
    return LeaveType.objects.create(code="CL", name="Casual Leave")


def test_create_leave_application(stub_iam, leave_type, user_ref):
    session = make_session(user_id=1001, kind="faculty", modules=("elm",), permissions=("elm.application.create",))
    stub_iam(session, users={1001: user_ref(1001)})
    UserRef.objects.update_or_create(user_id=1001, defaults={"username": "u1001", "display_name": "User 1001", "kind": "faculty"})
    
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
    assert created_application.applicant_id == 1001
    assert created_application.status == "PENDING"


def test_create_leave_application_without_permission(stub_iam, leave_type, user_ref):
    session = make_session(user_id=2002, kind="student", modules=("elm",), permissions=())
    stub_iam(session, users={2002: user_ref(2002)})
    UserRef.objects.update_or_create(user_id=2002, defaults={"username": "u2002", "display_name": "User 2002", "kind": "faculty"})
    
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


def test_create_leave_application_with_invalid_status(stub_iam, leave_type, user_ref):
    session = make_session(user_id=1001, kind="faculty", modules=("elm",), permissions=("elm.application.create",))
    stub_iam(session, users={1001: user_ref(1001)})
    UserRef.objects.update_or_create(user_id=1001, defaults={"username": "u1001", "display_name": "User 1001", "kind": "faculty"})
    
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
    assert created_application.applicant_id == 1001
    assert created_application.status == "PENDING"


def test_view_leave_applications(stub_iam, leave_type, user_ref):
    session = make_session(user_id=1001, kind="faculty", modules=("elm",), permissions=("elm.application.view",))
    stub_iam(session, users={1001: user_ref(1001)})
    UserRef.objects.update_or_create(user_id=1001, defaults={"username": "u1001", "display_name": "User 1001", "kind": "faculty"})
    UserRef.objects.update_or_create(user_id=1002, defaults={"username": "u1002", "display_name": "User 1002", "kind": "faculty"})

    c = APIClient()
    c.credentials(HTTP_AUTHORIZATION="Token abc")

    for uid in (1001, 1002):
        LeaveApplication.objects.create(
            applicant_id=uid, leave_type_id="CL", start_date="2023-10-01",
            end_date="2023-10-05", is_half_day=False, reason="Sick")

    response = c.get("/api/v1/elm/applications")
    assert response.status_code == 200
    applications = response.json()
    assert len(applications) == 1
    assert applications[0]["applicant"] == 1001
