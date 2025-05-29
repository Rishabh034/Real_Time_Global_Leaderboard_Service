# Create your views here.
from rest_framework import views, status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from leaderboard_service.services.leaderboard_service import LeaderBoardService
from leaderboard_service.services.utility import StatusCode
from leaderboard_service.services.serializer import UserSerializer, GameSerializer, ScoreSerializer, TopKLeaderSerializer
from leaderboard_service.services.build_response_object import BuildResponseObject
from rest_framework.views import APIView

LIMIT = 100

class CreateUserView(APIView):
    """
    Api to post the score ingestion in database
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__leader_board_service = LeaderBoardService(LIMIT)

    def post(self, request):

        response_data = dict()
        response_message = str()
        response_status = StatusCode.SUCCESS
        try:
            serializer_object = UserSerializer(data=request.data)
            if serializer_object.is_valid(raise_exception=True):
                data = serializer_object.data
                self.__leader_board_service.create_user(request.data)
        except ValidationError as error:
            response_dict = BuildResponseObject.get_response_object(
                StatusCode.BAD_REQUEST.value[0],
                error.detail,
                StatusCode.BAD_REQUEST.value[2]
            )
            return Response(response_dict, status=status.HTTP_400_BAD_REQUEST)
        except Exception as error:
            response_dict = BuildResponseObject.get_response_object(
                StatusCode.INTERNAL_SERVER_ERROR.value[0],
                str(error),
                StatusCode.INTERNAL_SERVER_ERROR.value[2]
            )
            return Response(response_dict, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(
            BuildResponseObject.get_response_object_v2(response_data, response_status,
                                                       description=response_message))


class CreateGameView(views.APIView):
    """
    Api to post the score ingestion in database
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__leader_board_service = LeaderBoardService(LIMIT)

    def post(self, request):

        response_data = dict()
        response_message = str()
        response_status = StatusCode.SUCCESS
        try:
            serializer_object = GameSerializer(data=request.data)
            if serializer_object.is_valid(raise_exception=True):
                data = serializer_object.data
                self.__leader_board_service.create_game(request.data)
        except ValidationError as error:
            response_dict = BuildResponseObject.get_response_object(
                StatusCode.BAD_REQUEST.value[0],
                error.detail,
                StatusCode.BAD_REQUEST.value[2]
            )
            return Response(response_dict, status=status.HTTP_400_BAD_REQUEST)
        except Exception as error:
            response_dict = BuildResponseObject.get_response_object(
                StatusCode.INTERNAL_SERVER_ERROR.value[0],
                str(error),
                StatusCode.INTERNAL_SERVER_ERROR.value[2]
            )
            return Response(response_dict, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(
            BuildResponseObject.get_response_object_v2(response_data, response_status,
                                                       description=response_message))



class ScoreIngestionView(views.APIView):
    """
    Api to post the score ingestion in database
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__leader_board_service = LeaderBoardService(LIMIT)

    def post(self, request):

        response_data = dict()
        response_message = str()
        response_status = StatusCode.SUCCESS
        try:
            serializer_object = ScoreSerializer(data=request.data)
            if serializer_object.is_valid(raise_exception=True):
                data = serializer_object.data
                self.__leader_board_service.create_score(request.data)
        except ValidationError as error:
            response_dict = BuildResponseObject.get_response_object(
                StatusCode.BAD_REQUEST.value[0],
                error.detail,
                StatusCode.BAD_REQUEST.value[2]
            )
            return Response(response_dict, status=status.HTTP_400_BAD_REQUEST)
        except Exception as error:
            response_dict = BuildResponseObject.get_response_object(
                StatusCode.INTERNAL_SERVER_ERROR.value[0],
                str(error),
                StatusCode.INTERNAL_SERVER_ERROR.value[2]
            )
            return Response(response_dict, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(
            BuildResponseObject.get_response_object_v2(response_data, response_status,
                                                       description=response_message))


class TopKLeadersView(APIView):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__leader_board_service = LeaderBoardService(LIMIT)

    def get(self, request):
        response_data = dict()
        response_message = str()
        response_status = StatusCode.SUCCESS
        try:
            serializer_object = TopKLeaderSerializer(data=request.query_params)
            if serializer_object.is_valid(raise_exception=True):
                data = serializer_object.data
                response_data = self.__leader_board_service.get_top_k_leaders()
        except ValidationError as error:
            response_dict = BuildResponseObject.get_response_object(
                StatusCode.BAD_REQUEST.value[0],
                error.detail,
                StatusCode.BAD_REQUEST.value[2]
            )
            return Response(response_dict, status=status.HTTP_400_BAD_REQUEST)
        except Exception as error:
            response_dict = BuildResponseObject.get_response_object(
                StatusCode.INTERNAL_SERVER_ERROR.value[0],
                str(error),
                StatusCode.INTERNAL_SERVER_ERROR.value[2]
            )
            return Response(response_dict, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(
            BuildResponseObject.get_response_object_v2(response_data, response_status,
                                                       description=response_message))