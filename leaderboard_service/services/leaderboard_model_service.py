from leaderboard_service.models import Users, Games, Scores

class LeaderBoardModelService:

    def create_user(self,data):

        Users.objects.create(**data)


    def create_game(self, data):

        Games.objects.create(**data)


    def create_score(self, data):

        Scores.objects.create(**data)




