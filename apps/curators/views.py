"""
CONCEPT: Django + DRF + Regex (via validators) + MongoDB
-------------------------------------------------------------
Curator accounts live entirely in MongoDB — no Django User model
involved. Passwords are hashed with Django's own password hasher
(`make_password`/`check_password`), which is a perfectly fine reuse of
Django's crypto utilities even though we're bypassing Django's ORM.
"""
from django.contrib.auth.hashers import make_password, check_password
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

from apps.common.permissions import IsCurator

from .repository import CuratorRepository, SessionRepository
from .serializers import CuratorRegisterSerializer, CuratorLoginSerializer


class CuratorRegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = CuratorRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        repo = CuratorRepository()
        if repo.email_exists(data['email']):
            return Response({'detail': 'A curator with this email already exists.'}, status=status.HTTP_409_CONFLICT)

        data = dict(data)
        data['password'] = make_password(data['password'])
        curator = repo.create_curator(data)
        curator.pop('password', None)
        return Response(curator, status=status.HTTP_201_CREATED)


class CuratorLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = CuratorLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email'].strip().lower()
        password = serializer.validated_data['password']

        curator = CuratorRepository().find_one({'email': email})
        if not curator or not check_password(password, curator.get('password', '')):
            return Response({'detail': 'Invalid email or password.'}, status=status.HTTP_401_UNAUTHORIZED)

        token = SessionRepository().create_session(curator['id'])
        curator.pop('password', None)
        return Response({'token': token, 'curator': curator})


class CuratorLogoutView(APIView):
    permission_classes = [IsCurator]

    def post(self, request):
        SessionRepository().destroy(request.auth)
        return Response({'detail': 'Logged out.'})


class CuratorMeView(APIView):
    permission_classes = [IsCurator]

    def get(self, request):
        return Response(request.user)


class CuratorListView(APIView):
    permission_classes = [IsCurator]

    def get(self, request):
        curators = CuratorRepository().find_many({}, sort=('dateJoined', -1))
        for curator in curators:
            curator.pop('password', None)
        return Response({'count': len(curators), 'results': curators})
