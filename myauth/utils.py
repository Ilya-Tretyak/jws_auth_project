from myauth.models import Permission, Resource, UserRole


def has_permission(user, resource_name, action):
    try:
        resource = Resource.objects.get(name=resource_name)
    except Resource.DoesNotExist:
        return False

    user_roles = UserRole.objects.filter(user=user)

    for user_role in user_roles:
        role = user_role.role
        try:
            permission = Permission.objects.get(role=role, resource=resource)
            if action == 'read' and permission.can_read:
                return True
            if action == 'write' and permission.can_write:
                return True
            if action == 'delete' and permission.can_delete:
                return True
        except Permission.DoesNotExist:
            continue

    return False
