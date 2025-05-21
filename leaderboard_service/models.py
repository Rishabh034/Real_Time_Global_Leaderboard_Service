import uuid
from django.db import models


class Users(models.Model):
    user_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_name = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Games(models.Model):
    game_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    game_name = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Scores(models.Model):
    user = models.ForeignKey(Users, null=False, on_delete=models.CASCADE)
    game = models.ForeignKey(Games, null=False, on_delete=models.CASCADE)
    score = models.IntegerField(null=False, blank=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['game_id', '-score']),
            models.Index(fields=['game_id', 'user_id']),
            models.Index(fields=['timestamp']),
        ]
        ordering = ['-score']  # Default ordering by highest score

    def __str__(self):
        return f"{self.user} | {self.game} | {self.score}"


