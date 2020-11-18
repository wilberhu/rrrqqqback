from django.contrib import auth
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from django.shortcuts import redirect
from rest_framework import generics, status
from users.serializers import UserSerializer, TokenSerializer, PasswordSerializer
from util.permissions import IsSuperuser, IsSelf, IsOwnerOrReadOnly, IsAnyone
from rest_framework.response import Response
from django.contrib.auth.hashers import make_password, check_password

from rest_framework.decorators import api_view

from rest_framework.reverse import reverse
from django.http import HttpResponse
from PIL import Image
from strategies.models import Strategy

from rest_framework import status
import os
import base64

import datetime
import shutil


class UserList(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsSuperuser,)

    def get_queryset(self):
        fields = self.serializer_class.Meta.fields
        if(self.request.query_params.get('sort') == None or
                self.request.query_params.get('sort').lstrip("-") not in fields):
            return User.objects.all()
        else:
            return User.objects.all().order_by(self.request.query_params.get('sort'))

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        response = {}
        if not serializer.is_valid(raise_exception=False):
            response["error"] = True
            response["detail"] = "Request parameter wrong"
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        if "password" not in request.data or request.data["password"] == "":
            response = {
                "password": [
                    "This field may not be blank."
                ]
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        # 创建的用户名已经存在
        if User.objects.filter(username=request.data["username"]).exists():
            response["error"] = True
            response["detail"] = "Username has been used."
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        password = make_password(request.data["password"])

        # useradd -m admin
        # echo "admin:password123" | chpasswd
        # os.system('useradd -m ' + request.data["username"])
        # os.system('echo "' + request.data["username"] + ':' + request.data["password"] + '" | chpasswd')
        serializer.save(password=password)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class UserDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsSelf,)
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    def put(self, request, *args, **kwargs):
        response = {}

        if User.objects.get(id=kwargs["pk"]).username != request.data["username"] and \
                User.objects.filter(username=request.data["username"]).exists():
            response["error"] = True
            response["detail"] = "Username has been used."
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        os.system('useradd -m ' + request.data["username"])
        os.system('echo "' + request.data["username"] + ':' + request.data["password"] + '" | chpasswd')
        return self.update(request, *args, **kwargs)


    def delete(self, request, *args, **kwargs):
        user = User.objects.get(id=kwargs["pk"])

        py_folder = os.path.join("media/strategy", user.username)
        if os.path.exists(py_folder):
            shutil.rmtree(py_folder)

        # os.system('userdel ' + request.data["username"])
        return self.destroy(request, *args, **kwargs)


@api_view(['POST'])
def user_login(request):
    """
    List all code snippets, or create a new snippet.
    """
    if request.method == 'POST':
        username = base64.b64decode(request.data['username'])
        password = base64.b64decode(request.data['password'])
        username = username.decode('utf-8')
        password = password.decode('utf-8')

        # 用户不存在
        user_list = User.objects.filter(username=username)
        if not user_list.exists():
            response = {
                "code": 40001,
                "detail": "用户不存在"
            }
            return Response(response, status=status.HTTP_401_UNAUTHORIZED)

        # 密码错误
        user = user_list[0]
        if not check_password(password, user.password):
            response = {
                "code": 40002,
                "detail": "密码不正确"
            }
            return Response(response, status=status.HTTP_401_UNAUTHORIZED)

        # 无管理员权限
        # if not user.is_staff:
        #     response = {
        #         "code": 40003,
        #         "detail": "用户无管理员权限"
        #     }
        #     return Response(response, status=status.HTTP_401_UNAUTHORIZED)

        token = Token.objects.get(user_id=user)
        response = {
            "code": 20000,
            "data": {
                "token": str(token)
            }
        }
        return Response(response, status=status.HTTP_201_CREATED)


@api_view(['GET'])
def user_info(request):
    """
    List all code snippets, or create a new snippet.
    """
    if request.method == 'GET':
        token_list = Token.objects.filter(key=request.META["HTTP_AUTHORIZATION"].split(" ")[1])
        if not token_list.exists():
            response = {
                "code": 40001,
                "detail": "token过期"
            }
            return Response(response, status=status.HTTP_401_UNAUTHORIZED)

        token = token_list[0]
        my_user = User.objects.get(id=token.user_id)
        if my_user.is_staff:
            role = "admin"
        else:
            role = "user"
        response = {
            "code": 20000,
            "data": {
                "roles": [
                    role
                ],
                "name": my_user.username,
                "introduction": "I am a super administrator",
                "avatar": reverse('user-head-portrait', kwargs={'pk': "admin"}, request=request),
            }
        }
        return Response(response, status=status.HTTP_200_OK)


@api_view(['POST'])
def user_logout(request):
    """
    List all code snippets, or create a new snippet.
    """
    if request.method == 'POST':
        # print(request.META['HTTP_X_TOKEN'])
        response = {
            "code": 20000,
            "detail": "logout successful"
        }
        return Response(response, status=status.HTTP_200_OK)


class ImageUrl(generics.GenericAPIView):
    # permission_classes = (permissions.IsAuthenticated,
    #                       IsOwner,)

    def get(self, request, *args, **kwargs):
        try:
            with open(os.path.join("media/portrait", kwargs["pk"] + "_head_portrait.jpg"), "rb") as f:
                return HttpResponse(f.read(), content_type="image/gif")
        except IOError:
            # red = Image.new('RGBA', (64, 64), (129, 214, 213))
            # response = HttpResponse(content_type="image/png")
            # red.save(response, "PNG")
            # return response
            with open(os.path.join("media/portrait", "admin_head_portrait.gif"), "rb") as f:
                return HttpResponse(f.read(), content_type="image/gif")



class TokenView(generics.RetrieveUpdateAPIView):

    permission_classes = (IsAnyone,)

    serializer_class = TokenSerializer

    def get(self, request, *args, **kwargs):
        if str(request.user) == "AnonymousUser":
            return Response({"token": ''}, status=status.HTTP_204_NO_CONTENT)
        token = Token.objects.get(user_id=request.user.id)
        return Response({"token": token.key}, status=status.HTTP_200_OK)

    def put(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        response = {}
        if not serializer.is_valid(raise_exception=False):
            response["error"] = True
            response["detail"] = "Request parameter wrong"
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        user_list = User.objects.filter(username=request.data["username"])
        user = user_list[0]

        if request.user.is_staff:
            # 用户不存在

            if not user_list.exists():
                response = {
                    "code": 20004,
                    "detail": "用户不存在"
                }
                return Response(response, status=status.HTTP_204_NO_CONTENT)

            expire_token = Token.objects.get(user_id=user)
            expire_token.delete()
            token, created = Token.objects.update_or_create(user=user)
            if not created:
                # update the created time of the token to keep it valid
                token.created = datetime.datetime.now()
                token.save()
            return Response({"token": token.key}, status=status.HTTP_202_ACCEPTED)
        if not check_password(request.data["password"], user.password):
            response["error"] = True
            response["detail"] = "The username and password is incorrect."
            return Response(response, status=status.HTTP_403_FORBIDDEN)

        expire_token = Token.objects.get(user_id=user.id)
        expire_token.delete()
        token, created = Token.objects.update_or_create(user=user)
        if not created:
            # update the created time of the token to keep it valid
            token.created = datetime.datetime.now()
            token.save()

        return Response({"token": token.key}, status=status.HTTP_202_ACCEPTED)


class PasswordChangeView(generics.CreateAPIView):

    permission_classes = (IsAnyone,)

    serializer_class = PasswordSerializer
    # 可修改用户名或者密码

    def create(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)
        response = {}
        if not serializer.is_valid(raise_exception=False):
            response["error"] = True
            response["detail"] = "Request parameter wrong"
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.get(username=request.data["username"])

        if not check_password(request.data["oldpassword"], user.password):
            response["error"] = True
            response["detail"] = "The password is incorrect."
            return Response(response, status=status.HTTP_403_FORBIDDEN)

        # if (request.data["username"] != request.user.username and
        #         User.objects.filter(username=request.data["username"]).exists()):
        #     response["error"] = True
        #     response["detail"] = "Username has been used."
        #     return Response(response, status=status.HTTP_400_BAD_REQUEST)


        kwargs = {
            "password": make_password(request.data["newpassword"])
        }
        if "username" in request.data:
            kwargs["username"] = request.data["username"]
        User.objects.filter(username=request.user).update(**kwargs)

        response["error"] = False
        response["detail"] = "Change success"
        return Response(response, status=status.HTTP_201_CREATED)