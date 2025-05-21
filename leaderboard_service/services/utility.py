from enum import Enum


# STATUS_NAME (STATUS_CODE, DESCRIPTION,
class StatusCode(Enum):
    # server issues
    SUCCESS = (200, "Success", True)
    INTERNAL_SERVER_ERROR = (
        500, "Ops! Internal server error", False)
    BAD_REQUEST = (400, "Bad Request", False)