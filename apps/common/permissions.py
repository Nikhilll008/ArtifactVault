
from rest_framework.permissions import BasePermission


class IsCurator(BasePermission):
    message = 'Valid curator authentication (Authorization: Token <token>) is required for this action.'

    def has_permission(self, request, view) -> bool:
        return isinstance(request.user, dict)
