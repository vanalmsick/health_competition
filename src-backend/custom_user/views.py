import time
import requests
from rest_framework import viewsets
from rest_framework.permissions import BasePermission, IsAdminUser, SAFE_METHODS
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.core.cache import cache

from .models import CustomUser
from .serializers import CustomUserSerializer
from .filters import CustomUserFilter
from .strava import sync_strava

class IsOwnerOrReadOnly(BasePermission):
    """ Permission class to only allow admins and owner to edit or delete entry """
    def has_permission(self, request, view):
        # Only authenticated users
        if request.user.is_authenticated:
            return True
        return False

    def has_object_permission(self, request, view, obj):
        # Read requests always allowed
        if request.method in SAFE_METHODS:
            return True  # allow GET, HEAD, OPTIONS (GET is filtered at viweset level to only show allowed entries)
        # If admin allow all requests
        if bool(request.user and request.user.is_staff):
            return True
        # Only owner of competition can modify
        if hasattr(obj, 'owner'):
            return obj.owner == request.user
        # Only owner can modify goals and awards
        elif hasattr(obj, 'competition') and hasattr(obj.competition, 'owner'):
            return obj.competition.owner == request.user
        # Only workout user can edit workout
        elif hasattr(obj, 'user'):
            return obj.user == request.user
        return False


class UserPermissionClass(BasePermission):
    """ Allow unauthenticated users to POST data - i.e. for registration """
    def has_permission(self, request, view):
        # Only create new requsts - i.e. POST
        if request.method in ('POST', 'OPTIONS'):
            return True
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return obj.pk == request.user.pk


class CustomUserViewSet(viewsets.ModelViewSet):
    #queryset = Competition.objects.all()
    serializer_class = CustomUserSerializer

    filter_backends = [DjangoFilterBackend]
    filterset_class = CustomUserFilter

    permission_classes = [UserPermissionClass]

    def get_queryset(self):
        # return all competitions the user is owner of or a participant of
        #time.sleep(3)  # throttle for testing
        return CustomUser.objects.filter(Q(pk=self.request.user.pk) | Q(my_competitions__in=self.request.user.my_competitions.all())).distinct().order_by('username', 'id')

    def get_object(self):
        lookup_value = self.kwargs.get(self.lookup_field)

        # Modify filter if I ask for myself instead of the id number
        if str(lookup_value).lower() in ['me', 'my', 'myself', 'i']:
            lookup_value = self.request.user.id

        return get_object_or_404(self.get_queryset(), pk=lookup_value)



class LinkStravaView(APIView):
    """ API post view for users to link with Strava. """
    permission_classes = [IsAuthenticated]

    def post(self, request, code):
        user = request.user
        client_id = settings.STRAVA_CLIENT_ID
        client_secret = settings.STRAVA_CLIENT_SECRET

        if client_id == 1234321 or client_secret == "ReplaceWithClientSecret":
            return Response({"message": "Sever configuration error - STRAVA_CLIENT_ID and/or STRAVA_CLIENT_SECRET are not set."}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        response = requests.post(
            url='https://www.strava.com/oauth/token',
            data={
                'client_id': client_id,
                'client_secret': client_secret,
                'code': code,
                'grant_type': 'authorization_code'
            }
        )

        if response.ok is False:
            return Response({"message": "Invalid Strava linkage code"}, status=status.HTTP_400_BAD_REQUEST)

        strava_tokens = response.json()
        setattr(user, 'strava_refresh_token', strava_tokens.get('refresh_token', None))
        setattr(user, 'strava_athlete_id', strava_tokens.get('athlete', {}).get('id', None))
        user.save()

        cache.set(f"strava_access_token_{user.id}", strava_tokens.get('access_token', None), int(strava_tokens.get('expires_in', 21600)) - 60)
        try:
            sync_strava(user__id=user.id)
        except requests.exceptions.HTTPError as err:
            if err.response.status_code == 401:
                return Response({'message': 'Access to activities denied by Strava. Not sufficient permissions to download activities.', 'original': err.response.json()}, status=status.HTTP_403_FORBIDDEN)
            else:
                raise Response(err.response.json(), status=err.response.status_code)

        return Response({"message": "Successfully linked Strava."}, status=status.HTTP_200_OK)


class UnlinkStravaView(APIView):
    """ API post view for users to unlink Strava. """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        setattr(user, 'strava_refresh_token', None)
        setattr(user, 'strava_athlete_id', None)
        user.save()

        return Response({"message": "Successfully unlinked Strava."}, status=status.HTTP_200_OK)