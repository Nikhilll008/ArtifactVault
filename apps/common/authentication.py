
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed


class MongoTokenAuthentication(BaseAuthentication):
    keyword = 'Token'

    def authenticate(self, request):
        # Import here (not at module load time) to avoid a circular
        # import between apps.common and apps.curators.
        from apps.curators.repository import CuratorRepository, SessionRepository

        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith(self.keyword + ' '):
            return None  # let DRF fall back to AnonymousUser

        token = auth_header.split(' ', 1)[1].strip()
        if not token:
            return None

        session = SessionRepository().find_one({'token': token})
        if not session:
            raise AuthenticationFailed('Invalid or expired token.')

        curator = CuratorRepository().find_one({'id': session['curatorId']})
        if not curator:
            raise AuthenticationFailed('Curator account for this token no longer exists.')

        curator.pop('password', None)
        return (curator, token)  # -> request.user = curator dict, request.auth = token

    def authenticate_header(self, request):
        return self.keyword
