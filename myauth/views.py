from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions

from django.contrib.auth import authenticate

from myauth.serializers import RegisterSerializer, LoginSerializer, UserSerializer, UserUpdateSerializer
from myauth.jwt_utils import create_jwt_token
from myauth.utils import has_permission

from drf_yasg.utils import swagger_auto_schema


MOCK_POSTS = [
    {"id": 1, "title": "Первая новость", "content": "Содержимое первой новости"},
    {"id": 2, "title": "Вторая новость", "content": "Содержимое второй новости"},
]


class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(request_body=RegisterSerializer)
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Пользователь зарегистрирован!"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(request_body=LoginSerializer)
    def post(self, request):
        serializer = LoginSerializer(data=request.data)

        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            user = authenticate(request, email=email, password=password)

            if user is not None and user.is_active:
                token = create_jwt_token(user.id)
                return Response({"token": token})
            return Response(
                {"error": "Неверные данные пользователя или пользователь удален!"},
                status= status.HTTP_401_UNAUTHORIZED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(APIView):
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




