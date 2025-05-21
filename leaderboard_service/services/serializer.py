from rest_framework import serializers


class ScoreSerializer(serializers.Serializer):
    user_id = serializers.UUIDField(required=True)
    game_id = serializers.UUIDField(required=True)
    score = serializers.IntegerField(required=True)

class UserSerializer(serializers.Serializer):
    user_name = serializers.CharField(required=True)

class GameSerializer(serializers.Serializer):
    game_name = serializers.CharField(required=True)

