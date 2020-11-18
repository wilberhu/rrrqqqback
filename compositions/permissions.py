from rest_framework import permissions
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.

        if "HTTP_AUTHORIZATION" in request.META and request.META["HTTP_AUTHORIZATION"].split(" ")[0] == "Bearer":
            token = request.META["HTTP_AUTHORIZATION"].split(" ")[-1]
            user_id = Token.objects.get(key=token).user_id
            request.user = User.objects.get(id=user_id)
            return obj.owner == request.user
        else:
            return obj.owner == request.user

    def has_permission(self, request, view):
        if "HTTP_AUTHORIZATION" in request.META and request.META["HTTP_AUTHORIZATION"].split(" ")[0] == "Bearer":
            token = request.META["HTTP_AUTHORIZATION"].split(" ")[-1]
            user_id = Token.objects.get(key=token).user_id
            request.user = User.objects.get(id=user_id)
            return True
        else:
            return True

