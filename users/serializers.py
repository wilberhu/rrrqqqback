from rest_framework import serializers

from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from django.contrib.auth.hashers import make_password, check_password

class UserSerializer(serializers.HyperlinkedModelSerializer):

    username = serializers.CharField(max_length=200)
    password = serializers.CharField(max_length=200, allow_blank=True, default='')

    token = serializers.SerializerMethodField('get_user_token')
    def get_user_token(self, instance):
        return Token.objects.get(user_id=instance.id).key

    def to_representation(self, instance):
        representation = super(UserSerializer, self).to_representation(instance)
        representation['password'] = ''
        return representation

    # def create(self, validated_data):
    #     return User.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.username = validated_data.get('username', instance.username)
        instance.password = instance.password \
            if validated_data.get('password', instance.password) == "" \
            else make_password(validated_data.get('password', instance.password))
        print(validated_data.get('password', instance.password))
        instance.email = validated_data.get('email', instance.email)
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.is_staff = True if validated_data.get('is_staff', instance.is_staff) else False
        instance.is_superuser = True if validated_data.get('is_superuser', instance.is_superuser) else False
        instance.save()
        return instance

    class Meta:
        model = User
        fields = ('url', 'id', 'username', 'password', 'token',
                  'email', 'first_name', 'last_name', 'is_superuser', 'is_staff')


class TokenSerializer(serializers.HyperlinkedModelSerializer):

    username = serializers.CharField(max_length=200, allow_blank=False)
    password = serializers.CharField(max_length=200, allow_blank=True, default="")

    class Meta:
        model = User
        fields = ('username', 'password')


class PasswordSerializer(serializers.HyperlinkedModelSerializer):

    username = serializers.CharField(max_length=200, allow_blank=True, default="")
    oldpassword = serializers.CharField(max_length=200, allow_blank=False)
    newpassword = serializers.CharField(max_length=200, allow_blank=False)

    class Meta:
        model = User
        fields = ('username', 'oldpassword', 'newpassword')
