from django.core.management.base import BaseCommand
from myauth.models import User, Role, UserRole, Permission, Resource


class Command(BaseCommand):
    """Команда инициализирует базовые роли, ресурсы и права доступа,
    а также создаёт двух тестовых пользователей"""
    def init_roles_and_permissions(self):
        # Создание ролей
        moderator_role, _ = Role.objects.get_or_create(name='Moderator')
        user_role, _ = Role.objects.get_or_create(name='User')

        # Создание ресурсов
        profile_resource, _ = Resource.objects.get_or_create(name='Profile')
        newsfeed_resource, _ = Resource.objects.get_or_create(name='NewsFeed')

        # Назначение прав для Profile
        Permission.objects.update_or_create(
            role=user_role,
            resource=profile_resource,
            defaults={'can_read': True, 'can_write': True, 'can_delete': True}
        )
        Permission.objects.update_or_create(
            role=moderator_role,
            resource=profile_resource,
            defaults={'can_read': True, 'can_write': True, 'can_delete': True}
        )

        # Назначение прав для NewsFeed
        Permission.objects.update_or_create(
            role=user_role,
            resource=newsfeed_resource,
            defaults={'can_read': True, 'can_write': False, 'can_delete': False}
        )
        Permission.objects.update_or_create(
            role=moderator_role,
            resource=newsfeed_resource,
            defaults={'can_read': True, 'can_write': True, 'can_delete': True}
        )

        self.stdout.write(self.style.SUCCESS('Роли, ресурсы и разрешения успешно инициализированы!'))


    def handle(self, *args, **kwargs):
        self.init_roles_and_permissions()

        moderator = User.objects.create_user(
            email='mod@mail.ru',
            password='modpassword',
            first_name='Илья',
            last_name='Модератор'
        )

        user = User.objects.create_user(
            email='user@mail.ru',
            password='userpassword',
            first_name='Илья',
            last_name='Пользователь'
        )

        mod_role = Role.objects.get(name='Moderator')
        user_role = Role.objects.get(name='User')

        UserRole.objects.create(user=moderator, role=mod_role)
        UserRole.objects.create(user=user, role=user_role)

        self.stdout.write(self.style.SUCCESS('Тестовые пользователи и роли успешно созданы!'))
