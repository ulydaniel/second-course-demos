from app.schemas.dashboard import StaffMember
from app.services import mock_data


def list_staff() -> list[StaffMember]:
    return [StaffMember(**member) for member in mock_data.STAFF]
