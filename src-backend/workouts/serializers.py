from rest_framework import serializers
from .models import Workout


class WorkoutSerializer(serializers.ModelSerializer):
    class Meta:
        model = Workout
        fields = ['id', 'sport_type', 'start_datetime', 'duration', 'duration_seconds', 'intensity_category', 'kcal', 'distance', 'steps', 'strava_id']
        read_only_fields = ['id', 'duration_seconds', 'strava_id'] #'duration_seconds',