from rest_framework import serializers
from .models import Competition, ActivityGoal, Team, Points


class CompetitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Competition
        fields = ['id', 'owner', 'name', 'start_date', 'start_date_fmt', 'start_date_epoch', 'end_date', 'end_date_fmt', 'end_date_epoch', 'has_teams', 'join_code']
        read_only_fields = ['owner', 'join_code']


class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ['id', 'name', 'competition', 'user']
        read_only_fields = ['user']


class ActivityGoalSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityGoal
        fields = '__all__'
        read_only_fields = []


class PointsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Points
        fields = ['id', 'goal', 'award', 'workout', 'points_raw', 'points_capped']
        read_only_fields = []
