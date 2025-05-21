from leaderboard_service.services.utility import StatusCode


class BuildResponseObject:
    @staticmethod
    def get_response_object(status_code: object, description: object, success_status: object) -> object:
        response_object = {}
        response_object['meta'] = {}
        response_object['meta']['status'] = status_code
        response_object['meta']['message'] = description
        response_object['meta']['success'] = success_status
        return response_object

    @staticmethod
    def get_response_object_v2(data, status_code: StatusCode, description="") -> dict:
        response_object = {}
        response_object['meta'] = {}
        response_object['meta']['status'] = status_code.value[0]
        response_object['meta']['message'] = (
            status_code.value[1] + str(description)
        )
        response_object['meta']['success'] = status_code.value[2]
        if data:
            response_object['result'] = data
        return response_object

    @staticmethod
    def get_response_object_v3(data, status_code: StatusCode, description="") -> dict:
        response_object = BuildResponseObject.get_response_object_v2(data, status_code, description)
        response_object['result'] = data
        return response_object