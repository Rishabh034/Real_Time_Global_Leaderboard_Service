from leaderboard_service.models import Users, Games, Scores

class LeaderBoardModelService:

    def create_user(self,data):

        Users.objects.create(**data)


    def create_game(self, data):

        Games.objects.create(**data)


    def create_score(self, data):

        Scores.objects.create(**data)

    def get_data_for_leaderboard(self):

        return Scores.objects.all().values('user_id','game_id','score','timestamp')

    def get_data_for_leaderboard_for_window(self,cutoff_time):

        return Scores.objects.all(timestap__gte = cutoff_time).values('user_id','game_id','score','timestamp')




