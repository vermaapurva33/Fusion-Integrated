from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import NotFound, BadRequestError

from fusion_auth.permissions import HasPermission
from modules.elm.models import LeaveApplication
from modules.elm.api.serializers import LeaveApplicationSerializer


class LeaveApplicationDecideView(APIView):
    permission_classes = [HasPermission("elm.application.approve")]

    def post(self, request, pk):
        user_id = request.user.user_id
        application = LeaveApplication.objects.filter(pk=pk, applicant__elm_unit_head_link__unit_head_id=user_id).first()
        if not application:
            raise NotFound("Application not found or not authorized")

        decision = request.data.get("decision")
        if decision not in ["approve", "reject"]:
            raise BadRequestError("Decision must be approve or reject", code="invalid_decision")

        if application.status != "PENDING":
            raise BadRequestError("Only a pending application can be decided", code="not_pending")

        if application.leave_type_id not in ("CL", "RH"):
            raise BadRequestError("The Unit Head can finally decide only CL and RH", code="not_final_authority")

        application.status = "APPROVED" if decision == "approve" else "REJECTED"
        application.decided_by_id = user_id
        application.decided_at = django.utils.timezone.now()
        application.save()

        return Response(LeaveApplicationSerializer(application).data)
