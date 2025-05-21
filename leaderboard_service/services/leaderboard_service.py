import uuid

from leaderboard_service.services.leaderboard_model_service import LeaderBoardModelService

class LeaderBoardService:

    def __init__(self):
        self.__leaderboard_model_service = LeaderBoardModelService()


    def create_user(self,data):
        data = {
            "user_id": uuid.uuid4(),
            "user_name": data.get("user_name")
        }
        self.__leaderboard_model_service.create_user(data)

    def create_game(self, data):
        data = {
            "game_id": uuid.uuid4(),
            "game_name": data.get("game_name")
        }
        self.__leaderboard_model_service.create_game(data)


    def crate_score(self, data):
        data = {
            "game_id": data.get("game_id"),
            "user_id": data.get("user_id"),
            "score": data.get("score"),
        }
        self.__leaderboard_model_service.create_score(data)





