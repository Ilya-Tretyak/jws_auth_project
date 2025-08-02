import datetime

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions, authentication

from django.contrib.auth import authenticate

from myauth.models import (
    RefreshToken,
    BlacklistedToken,
    User,
    Role,
    UserRole
)
from myauth.serializers import (
    RegisterSerializer,
    LoginSerializer,
    LogoutSerializer,
    UserSerializer,
    UserUpdateSerializer,
    RoleSerializer
)
from myauth.jwt_utils import create_jwt_token, create_jwt_tokens, decode_jwt_token, clean_user_tokens
from myauth.utils import has_permission

from drf_yasg.utils import swagger_auto_schema


MOCK_POSTS = [
    {"id": 1, "title": "Первая новость", "content": "Содержимое первой новости"},
    {"id": 2, "title": "Вторая новость", "content": "Содержимое второй новости"},
]


class RegisterView(APIView):
    """Представление для регистрации новых пользователей"""
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(request_body=RegisterSerializer)
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Пользователь зарегистрирован!"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    """Представление для аутентификации пользователей и выдачи JWT-токена"""
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(request_body=LoginSerializer)
    def post(self, request):
        serializer = LoginSerializer(data=request.data)

        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            user = authenticate(request, email=email, password=password)

            if user is not None and user.is_active:
                clean_user_tokens(user.id)
                token = create_jwt_tokens(user.id)
                return Response({"token": token})
            return Response(
                {"error": "Неверные данные пользователя или пользователь удален!"},
                status= status.HTTP_401_UNAUTHORIZED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RefreshTokenView(APIView):
    """Представление для создания нового access токена по refresh токену"""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        refresh_token = request.data.get('refresh_token')
        if not refresh_token:
            return Response({"error": "refresh-token обязателен!"}, status=status.HTTP_400_BAD_REQUEST)

        payload = decode_jwt_token(refresh_token)
        if not payload or payload.get('type') != 'refresh':
            return Response({'error': 'Недействительный refresh_token!'}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            token_object = RefreshToken.objects.get(token=refresh_token)
        except RefreshToken.DoesNotExist:
            return Response({'error': 'refresh_token не найден!'}, status=status.HTTP_401_UNAUTHORIZED)

        if token_object.is_expired():
            return Response({'error': 'refresh_token истек!'}, status=status.HTTP_401_UNAUTHORIZED)

        access_token = create_jwt_token(payload['user_id'])

        return Response({'access_token': access_token}, status=status.HTTP_200_OK)


class LogoutView(APIView):
    """Представление для logout пользователей, удаления refresh токена и помещения access токена в Blacklisted"""
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(request_body=LogoutSerializer)
    def post(self, request):
        refresh_token = request.data.get('refresh_token')
        if not refresh_token:
            return Response({'error': 'refresh_token отсутствует!'}, status= status.HTTP_400_BAD_REQUEST)

        payload = decode_jwt_token(refresh_token)
        if not payload or payload.get('type') != 'refresh':
            return Response({'error': 'Неверный refresh_token!'}, status=status.HTTP_401_UNAUTHORIZED)

        deleted, _ = RefreshToken.objects.filter(token=refresh_token).delete()

        if deleted == 0:
            return Response({'error': 'refresh_token уже отозван или не найден!'})

        auth_header = authentication.get_authorization_header(request).decode('utf-8')
        if not auth_header or not auth_header.startswith('Bearer '):
            return Response({'error': 'access_token отсутствует в заголовке!'}, status=status.HTTP_400_BAD_REQUEST)

        access_token = auth_header.split(' ')[1]

        access_payload = decode_jwt_token(access_token)
        if not access_payload:
            return Response({'error': 'Неверный access_token'}, status=status.HTTP_401_UNAUTHORIZED)

        expired_at = datetime.datetime.fromtimestamp(access_payload['exp'], tz=datetime.timezone.utc)

        BlacklistedToken.objects.create(user=request.user, token=access_token, expired_at=expired_at)

        return Response(status=status.HTTP_204_NO_CONTENT)




class UserProfileView(APIView):
    """Представление для работы с пользователем"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        if not has_permission(request.user, "Profile", 'read'):
            return Response({'error': "Нет прав на просмотр профиля!"})

        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    @swagger_auto_schema(request_body=UserUpdateSerializer)
    def put(self, request):
        if not has_permission(request.user, "Profile", 'write'):
            return Response({'error': "Нет прав на редактирования профиля!"})

        serializer = UserUpdateSerializer(request.user, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        if not has_permission(request.user, "Profile", 'delete'):
            return Response({'error': 'нет прав на удаление профиля!'})

        user = request.user
        user.is_active = False
        user.save()
        return Response({'message': 'Аккаунт "удален"!'}, status=status.HTTP_204_NO_CONTENT)


class NewFeedView(APIView):
    """Представление для работы с новостной лентой"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        if not has_permission(request.user, "NewsFeed", 'read'):
            return Response({'error': 'Нет прав на чтение новостей!'}, status=status.HTTP_403_FORBIDDEN)
        return Response({'news': MOCK_POSTS})

    def post(self, request):
        if not has_permission(request.user, "NewsFeed", 'write'):
            return Response({'error': 'Нет прав на создание постов!'}, status=status.HTTP_403_FORBIDDEN)

        new_post = {
            'id': len(MOCK_POSTS) + 1,
            'title': "Третья новость",
            'content': "Содержимое первой новости"
        }
        MOCK_POSTS.append(new_post)

        return Response({'message': 'Пост создан!', 'post': new_post}, status=status.HTTP_201_CREATED)

    def delete(self, request, post_id):
        if not has_permission(request.user, "NewsFeed", 'delete'):
            return Response({'error': 'Нет прав на удаление постов!'}, status=status.HTTP_403_FORBIDDEN)

        for i, post in enumerate(MOCK_POSTS):
            if post['id'] == post_id:
                del MOCK_POSTS[i]
                return Response({'message': f'Пост {post_id} удален!'}, status=status.HTTP_204_NO_CONTENT)

        return Response({'message': f'Пост {post_id} удален'}, status=status.HTTP_200_OK)


class UserRoleManagementView(APIView):
    permission_classes = [permissions.IsAdminUser]

    @swagger_auto_schema(request_body=RoleSerializer)
    def post(self, request, user_id):
        role_name = request.data.get('role')
        if not role_name:
            return Response({'error': 'Роли не существует'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(id=user_id)
            role = Role.objects.get(name=role_name)
        except (User.DoesNotExist, Role.DoesNotExist):
            return Response({'error': 'User или Role не найден'}, status=status.HTTP_404_NOT_FOUND)

        UserRole.objects.filter(user=user).delete()
        UserRole.objects.create(user=user, role=role)

        return Response({'message': f'Роль {role_name} успешно присвоена пользователю {user.email}'}, status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=RoleSerializer)
    def delete(self, request, user_id):
        role_name = request.data.get('role')

        if not role_name:
            return Response({'error': 'Роли не существует'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(id=user_id)
            role = Role.objects.get(name=role_name)
        except (User.DoesNotExist, Role.DoesNotExist):
            return Response({'error': 'User или Role не найден'}, status=status.HTTP_404_NOT_FOUND)

        UserRole.objects.filter(user=user, role=role).delete()
        return Response({'status': f'Роль {role_name} успешна удалена у пользователя {user.email}'}, status=status.HTTP_200_OK)
