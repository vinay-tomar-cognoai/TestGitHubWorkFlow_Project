from rest_framework import permissions


class DisableOptionsPermission(permissions.BasePermission):
    """
    Permission to disallow all requests for method OPTIONS.
    """

    def has_permission(self, request, view):
        if request.method == 'OPTIONS':
            return False
        return True
