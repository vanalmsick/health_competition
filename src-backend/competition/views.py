import datetime, time

from django.conf import settings
from django.db.models import Q
from django.core.exceptions import PermissionDenied
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework.permissions import BasePermission

from django.db.models import Sum, Avg, Count, ExpressionWrapper, DurationField, F, IntegerField, DateField, Window, Func, FloatField
from django.db.models.functions import TruncDay, Now, Coalesce, Cast, ExtractDay

from custom_user.views import IsOwnerOrReadOnly
from custom_user.models import CustomUser
from custom_user.strava import sync_strava
from custom_user.point_recalc import recalc_points
from .models import Competition, Team, ActivityGoal, Points
from .serializers import CompetitionSerializer, TeamSerializer, ActivityGoalSerializer, PointsSerializer


class CompetitionViewSet(viewsets.ModelViewSet):
    #queryset = Competition.objects.all()
    serializer_class = CompetitionSerializer

    permission_classes = [IsOwnerOrReadOnly]

    def get_queryset(self):
        # return all competitions the user is owner of or a participant of
        #time.sleep(3)  # throttle for testing
        return Competition.objects.filter(Q(owner=self.request.user) | Q(user=self.request.user)).distinct().order_by('-end_date', '-start_date', '-id')

    def perform_create(self, serializer):
        # when creating a new competition, set the owner to the request user
        serializer.save(owner=self.request.user)


class TeamViewSet(viewsets.ModelViewSet):
    #queryset = Team.objects.all()
    serializer_class = TeamSerializer

    permission_classes = [IsOwnerOrReadOnly]

    def get_queryset(self):
        # return all teams the user is a member of and all teams of competitions the user participates in
        #time.sleep(3)  # throttle for testing
        return Team.objects.filter(Q(user=self.request.user) | Q(competition__user=self.request.user)).distinct().order_by('name')

    def perform_create(self, serializer):

        competition_obj = serializer.validated_data.get('competition')

        # if has_teams is disabled, don't allow creation of teams
        if competition_obj.has_teams is False:
            raise PermissionDenied("Teams are disabled for this competition.")

        # only allow user to create a team if they are a member or owner of the competition
        if not (competition_obj.owner == self.request.user) and not (competition_obj in self.request.user.competitions.all()):
            raise PermissionDenied("You are not a participant of the competition you want to create a team for.")

        serializer.save()


class ActivityGoalViewSet(viewsets.ModelViewSet):
    #queryset = ActivityGoal.objects.all()
    serializer_class = ActivityGoalSerializer

    permission_classes = [IsOwnerOrReadOnly]

    def get_queryset(self):
        # return all competition categories the user is owner of or a participant of
        #time.sleep(3)  # throttle for testing
        return ActivityGoal.objects.filter(Q(competition__owner=self.request.user) | Q(competition__user=self.request.user)).distinct().order_by('name')

    def perform_create(self, serializer):
        competition_obj = serializer.validated_data.get('competition')

        # only allow user to create a team if they are a member or owner of the competition
        if competition_obj.owner != self.request.user:
            raise PermissionDenied("You can only create and edit competition goals if you are the owner.")

        serializer.save()


class PointsViewSet(viewsets.ModelViewSet):
    #queryset = Points.objects.all()
    serializer_class = PointsSerializer

    permission_classes = [IsOwnerOrReadOnly]

    def get_queryset(self):
        # return all points the user is owner of, a participant of, or of his/her own workouts
        #time.sleep(3)  # throttle for testing
        return Points.objects.filter(Q(goal__competition__owner=self.request.user) | Q(goal__competition__user=self.request.user) | Q(workout__user=self.request.user)).distinct().order_by('-workout__start_datetime', '-workout__duration', '-workout', '-workout__user')


def _add_rank(data, key, enhance_dict, id_field, rank_field='rank', reverse=True):
    sorted_data = sorted(data, key=lambda x: x[key], reverse=reverse)
    rank = 0
    last_value = None
    user_lst = []
    for idx, item in enumerate(sorted_data, start=1):
        if item[key] != last_value:
            rank = idx
            last_value = item[key]
        sorted_data[idx-1] = {**item, rank_field: rank, **enhance_dict[item[id_field]]}
        enhance_dict[item[id_field]]['rank'] = rank
        enhance_dict[item[id_field]]['points'] = item[key]
        user_lst.append(item[id_field])
    for i in [i for i in enhance_dict.keys() if i not in user_lst]:
        sorted_data.append({**enhance_dict[i], rank_field: None, key: None})
        enhance_dict[i]['rank'] = None
        enhance_dict[i]['points'] = None
    return sorted_data


class StatsPermissions(BasePermission):
    def has_permission(self, request, view):
        # Only authenticated users
        if request.user.is_authenticated:
            return True
        return False

    def has_object_permission(self, request, view, obj):
        return (request.user.id == obj.get('competition', {}).get('owner', None)) or (request.user.id in obj.get('competition', {}).get('member', []))


class CompetitionStatsQueryView(APIView):
    permission_classes = [StatsPermissions]

    @method_decorator(cache_page(30))  # cache for 30 seconds
    def get(self, request, competition):
        # Custom query logic
        try:
            competition_obj = Competition.objects.get(id=competition)
        except Competition.DoesNotExist:
            return Response({"detail": "Competition not found."}, status=status.HTTP_404_NOT_FOUND)
        all_points = Points.objects.filter(Q(award__competition__id=competition) | Q(goal__competition_id=competition))

        # For SQLite
        if settings.DATABASES.get('default', {}).get('ENGINE') == 'django.db.backends.sqlite3':
            all_points_date = (
                all_points
                .annotate(date=TruncDay('workout__start_datetime'))
                .annotate(tmp_today=TruncDay(Now()))
                .annotate(tmp_start_date=TruncDay(F('workout__start_datetime')))
                .annotate(
                    days_ago=ExpressionWrapper(
                    (F('tmp_today') - F('tmp_start_date')) / 86_400_000_000,
                    output_field=IntegerField()
                )
                )
            )
        # For Postgres
        else:
            all_points_date = (
                all_points
                .annotate(date=TruncDay('workout__start_datetime'))
                .annotate(
                    days_ago_duration=ExpressionWrapper(
                        TruncDay(Now()) - TruncDay(F('workout__start_datetime')),
                        output_field=DurationField()
                    )
                ).annotate(
                    days_ago=ExtractDay(F('days_ago_duration'))
                )
            )
        tmp_all = (
            all_points_date
            .values('days_ago')
            .annotate(total=Sum('points_capped'))
            .values('days_ago', 'total')
            .order_by('-days_ago')
        )
        results_all = {}
        for i in tmp_all:
            days_ago = i.pop('days_ago')
            results_all[days_ago] = i

        tmp_user = (
            all_points_date
            .values('days_ago', 'workout__user__id')
            .annotate(total=Sum('points_capped'))
            .order_by('-days_ago')
        )
        results_user = {}
        for i in tmp_user:
            user_id = i.pop('workout__user__id')
            days_ago = i.pop('days_ago')
            if user_id not in results_user:
                results_user[user_id] = {}
            results_user[user_id][days_ago] = i

        tmp_team = (
            all_points_date
            .values('days_ago', 'workout__user__my_teams')
            .annotate(total=Sum('points_capped'))
            .order_by('-days_ago')
        )
        results_team = {}
        for i in tmp_team:
            team_id = i.pop('workout__user__my_teams')
            days_ago = i.pop('days_ago')
            if team_id not in results_team:
                results_team[team_id] = {}
            results_team[team_id][days_ago] = i

        # Get user data
        user_dict = {i['id']: i for i in CustomUser.objects.filter(my_competitions=competition).values('id', 'username', 'strava_allow_follow', 'strava_athlete_id').order_by('username', 'id')}
        for key, value in user_dict.items():
            if value['strava_allow_follow'] is False:
                value['strava_athlete_id'] = None

        # Get user rankings
        leaderboard_user = (
            all_points
            .values('workout__user__id')
            .annotate(total_capped=Sum('points_capped'))
            .order_by('-total_capped')
        )
        leaderboard_user = _add_rank(leaderboard_user, key="total_capped", enhance_dict=user_dict, id_field='workout__user__id')

        # Get team data
        team_dict = {i.id: {'id': i.id, 'name': i.name, 'members': [user_dict.get(i.id, {'id': i.id, 'username': 'ERROR'}) for i in i.user.all()]} for i in Team.objects.filter(competition=competition).prefetch_related('user')}

        # Get team rankings
        leaderboard_team = (
            all_points
            .values('workout__user__my_teams__id')
            .annotate(total_capped=Sum('points_capped'))
            .order_by('-total_capped')
        )
        leaderboard_team = [{**i, 'total_capped': i['total_capped'] / len(team_dict[i['workout__user__my_teams__id']]['members'])} for i in leaderboard_team if i['workout__user__my_teams__id'] in team_dict]
        leaderboard_team = _add_rank(leaderboard_team, key="total_capped", enhance_dict=team_dict, id_field='workout__user__my_teams__id')


        results_team_members = (
            Team.objects.filter(competition__id=competition)
            .annotate(member_count=Count('user'))
            .values('id', 'name', 'member_count')
        )
        results_competition = {
            'name': competition_obj.name,
            'owner': competition_obj.owner.pk,
            'members': list(competition_obj.user.all().values_list('pk', flat=True)),
            'member_count': competition_obj.user.all().count(),
            'start_date': competition_obj.start_date,
            'start_date_count': (datetime.date.today() - competition_obj.start_date).days,
            'end_date': competition_obj.end_date,
            'end_date_count': (datetime.date.today() - competition_obj.end_date).days,
            'has_teams': competition_obj.has_teams,
            'goals': competition_obj.activitygoal_set.all().values(),
        }

        response_obj = {
            'timeseries': {
                'all': results_all,
                'user': results_user,
                'team': results_team,
            },
            'teams': {value['id']: value for i, value in enumerate(results_team_members)},
            'competition': results_competition,
            'leaderboard': {
                'team': leaderboard_team,
                'individual': leaderboard_user,
            }
        }
        self.check_object_permissions(request, response_obj)
        return Response(response_obj)


class FeedPermissions(BasePermission):
    def has_permission(self, request, view):
        # Only authenticated users
        if request.user.is_authenticated:
            return True
        return False

    def has_object_permission(self, request, view, obj):
        if len(obj) == 0:
            return False
        obj = obj[0]
        return request.user.id in [obj.owner.pk] + list(obj.user.all().values_list('pk', flat=True))


class FeedQueryView(APIView):
    """ API view to get the activity/point feed for a competition. """
    permission_classes = [FeedPermissions]

    def get(self, request, competition):
        # Custom query logic
        #time.sleep(3)  # throttle for testing

        competition_obj = Competition.objects.filter(id=competition)
        self.check_object_permissions(request, competition_obj)

        all_points = Points.objects.filter(Q(award__competition__id=competition) | Q(goal__competition_id=competition)).order_by('-workout__start_datetime', '-workout__duration', '-workout', '-workout__user')

        grouped_points = {i['workout']: i for i in all_points.values('workout__user', 'workout__user__username', 'workout__user__strava_allow_follow', 'workout', 'workout__sport_type', 'workout__start_datetime', 'workout__duration', 'workout__strava_id', 'award').annotate(points_capped=Sum('points_capped'), points_raw=Sum('points_raw')).order_by('-workout__start_datetime', '-workout__duration', '-workout', '-workout__user')}

        for i in all_points.values('workout', 'id', 'goal', 'goal__name', 'award', 'award__name', 'points_capped', 'points_raw'):
            if 'details' not in grouped_points[i['workout']]:
                grouped_points[i['workout']]['details'] = []
            grouped_points[i['workout']]['details'].append(i)

        return Response(list(grouped_points.values()))



class JoinCompetitionView(APIView):
    """ API post view for users to join a competition. """
    permission_classes = [IsAuthenticated]

    def post(self, request, join_code):
        competition = Competition.objects.filter(join_code=join_code.upper())
        if len(competition) == 0:
            return Response({"message": "Invalid join code."}, status=status.HTTP_400_BAD_REQUEST)
        competition = competition[0]
        competition.user.add(request.user)
        competition.save()
        return Response({"message": "Successfully joined competition.", "competition": competition.id}, status=status.HTTP_200_OK)


class JoinTeamView(APIView):
    """ API post view for users to join a team and make sure they are only a member of one team per competition. """
    permission_classes = [IsAuthenticated]

    def post(self, request, id):
        team = Team.objects.filter(id=id)
        if len(team) == 0:
            return Response({"message": "Invalid team id."}, status=status.HTTP_400_BAD_REQUEST)
        team = team[0]
        competition = team.competition
        competition_teams = competition.team_set.all()
        for competition_team in competition_teams:
            competition_team.user.remove(request.user)
            competition_team.save()
        request.user.my_teams.add(team)
        request.user.save()
        return Response({"message": "Successfully joined team.", "team": team.id}, status=status.HTTP_200_OK)