from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

from django.utils import timezone


class UserManager(BaseUserManager):
    """Кастомный менеджер пользователей"""
    def create_user(self, email, first_name, last_name, password=None, **extra_fields):
        if not email:
            raise ValueError("Email обязательное поле")
        email = self.normalize_email(email)
        user = self.model(email=email, first_name=first_name, last_name=last_name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, first_name, last_name, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, first_name, last_name, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """Кастомная модель пользователя"""
    first_name = models.CharField('Имя', max_length=50)
    last_name = models.CharField('Фамилия', max_length=50)
    middle_name = models.CharField('Отчество', max_length=50, blank=True)
    email = models.EmailField('email', unique=True)
    is_active = models.BooleanField('Активен', default=True)
    is_staff = models.BooleanField('Персонал', default=False)
    date_add = models.DateTimeField('Дата регистрации', auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def __str__(self):
        return self.email


class Role(models.Model):
    """Модель роли пользователя"""
    name = models.CharField('Роль', max_length=50, unique=True)

    def __str__(self):
        return self.name


class UserRole(models.Model):
    """Связующая модель между пользователями и их ролями"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_roles')
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='role_users')

    class Meta:
        unique_together = ('user', 'role')


class Resource(models.Model):
    """Модель ресурса, к которому можно назначать права"""
    name = models.CharField('Ресурс', max_length=50, unique=True)

    def __str__(self):
        return self.name


class Permission(models.Model):
    """Модель прав доступа"""
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='permissions')
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE, related_name='permissions')
    can_read = models.BooleanField('Чтение', default=False)
    can_write = models.BooleanField('Запись', default=False)
    can_delete = models.BooleanField('Удаление', default=False)

    class Meta:
        unique_together = ('role', 'resource')

    def __str__(self):
        return f"{self.role.name} - {self.resource.name}"


class RefreshToken(models.Model):
    """Модель refresh токена"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=300, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expired_at = models.DateTimeField()

    def is_expired(self):
        return timezone.now() >= self.expired_at


class BlacklistedToken(models.Model):
    """Модель access токена добавленного в Blacklisted"""
    token = models.CharField(max_length=300, unique=True)
    blacklisted_at = models.DateTimeField(auto_now_add=True)
    expired_at = models.DateTimeField()

    def is_expired(self):
        return timezone.now() >= self.expired_at
