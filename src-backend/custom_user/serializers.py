from rest_framework import serializers
from .models import CustomUser


class CustomUserSerializer(serializers.ModelSerializer):
    my = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ['id', 'my', 'email', 'first_name', 'last_name', 'gender', 'username', 'password', 'is_verified', 'strava_athlete_id', 'strava_allow_follow', 'strava_last_synced_at', 'my_competitions', 'my_teams', 'goal_active_days', 'goal_workout_minutes', 'goal_distance']
        read_only_fields = ['is_verified', 'strava_athlete_id', 'strava_last_synced_at']
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def get_my(self, obj):
        user = self.context['request'].user
        return obj.pk == user.pk

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            email=validated_data.get('email'),
            first_name=validated_data.get('first_name'),
            last_name=validated_data.get('last_name', None),
            password=validated_data.get('password'),
            gender=validated_data.get('gender', None),
        )
        return user

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        user = self.context['request'].user

        # Omit 'secret' fields of other users that this user is not allowed to see
        if instance.pk != user.pk:
            rep.pop('email', None)
            rep.pop('first_name', None)
            rep.pop('last_name', None)
            rep.pop('gender', None)
            rep.pop('password', None)
            rep.pop('strava_last_synced_at', None)

            if not rep['strava_allow_follow']:
                rep.pop('strava_athlete_id', None)

        return rep


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # If instance exists, it's an update (PUT/PATCH), make fields optional
        if self.instance:
            self.fields['email'].required = False
            self.fields['password'].required = False
            self.fields['first_name'].required = False
            self.fields['last_name'].required = False