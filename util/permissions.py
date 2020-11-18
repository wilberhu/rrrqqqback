from django.contrib.auth.models import User
from rest_framework import permissions
from rest_framework.authtoken.models import Token


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_permission(self, request, view):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.

        if "HTTP_AUTHORIZATION" in request.META and request.META["HTTP_AUTHORIZATION"].split(" ")[0] == 'Bearer':
            my_token = request.META["HTTP_AUTHORIZATION"].split(" ")[1]
            if Token.objects.filter(key=my_token).exists():
                request.user = User.objects.get(id=Token.objects.get(key=my_token).user_id)
                return True
        elif "HTTP_TOKEN" in request.META:
            my_token = request.META["HTTP_TOKEN"]
            if Token.objects.filter(key=my_token).exists():
                request.user = User.objects.get(id=Token.objects.get(key=my_token).user_id)
                return True
        else :
            if not str(request.user) == "AnonymousUser":
                return True
        return False

class IsObjectOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if "HTTP_AUTHORIZATION" in request.META and request.META["HTTP_AUTHORIZATION"].split(" ")[0] == 'Bearer':
            my_token = request.META["HTTP_AUTHORIZATION"].split(" ")[1]
            if Token.objects.filter(key=my_token).exists():
                request.user = User.objects.get(id=Token.objects.get(key=my_token).user_id)
                return True
        elif "HTTP_TOKEN" in request.META:
            my_token = request.META["HTTP_TOKEN"]
            if Token.objects.filter(key=my_token).exists():
                request.user = User.objects.get(id=Token.objects.get(key=my_token).user_id)
                return True
        else :
            if str(request.user) == "AnonymousUser":
                return False

            elif request.user.is_staff:
                    return True
        return obj.owner == request.user


# 管理员管理用户列表
class IsSuperuser(permissions.BasePermission):
    print()
    def has_permission(self, request, view):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if "HTTP_AUTHORIZATION" in request.META and request.META["HTTP_AUTHORIZATION"].split(" ")[0] == 'Bearer':
            my_token = request.META["HTTP_AUTHORIZATION"].split(" ")[1]
            if Token.objects.filter(key=my_token).exists():
                request.user = User.objects.get(id=Token.objects.get(key=my_token).user_id)
        elif "HTTP_TOKEN" in request.META:
            my_token = request.META["HTTP_TOKEN"]
            if Token.objects.filter(key=my_token).exists():
                request.user = User.objects.get(id=Token.objects.get(key=my_token).user_id)

        if request.user.is_staff:
            return True
        return False

# 管理员或用户管理用户信息
class IsSelf(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if "HTTP_AUTHORIZATION" in request.META and request.META["HTTP_AUTHORIZATION"].split(" ")[0] == 'Bearer':
            my_token = request.META["HTTP_AUTHORIZATION"].split(" ")[1]
            if Token.objects.filter(key=my_token).exists():
                request.user = User.objects.get(id=Token.objects.get(key=my_token).user_id)
        elif "HTTP_TOKEN" in request.META:
            my_token = request.META["HTTP_TOKEN"]
            if Token.objects.filter(key=my_token).exists():
                request.user = User.objects.get(id=Token.objects.get(key=my_token).user_id)

        if request.user.is_staff:
            return True
        return obj == request.user

# 管理员管理用户列表
class IsAnyone(permissions.BasePermission):
    def has_permission(self, request, view):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if "HTTP_AUTHORIZATION" in request.META and request.META["HTTP_AUTHORIZATION"].split(" ")[0] == 'Bearer':
            my_token = request.META["HTTP_AUTHORIZATION"].split(" ")[1]
            if Token.objects.filter(key=my_token).exists():
                request.user = User.objects.get(id=Token.objects.get(key=my_token).user_id)
        elif "HTTP_TOKEN" in request.META:
            my_token = request.META["HTTP_TOKEN"]
            if Token.objects.filter(key=my_token).exists():
                request.user = User.objects.get(id=Token.objects.get(key=my_token).user_id)

        return True