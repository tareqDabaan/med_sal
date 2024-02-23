from django.contrib.auth.models import Group, Permission
from django.contrib.auth import get_user_model
from django.db.models.query import QuerySet


Users = get_user_model()


class Groups:
    
    # def __init__(self, name: str) -> None:
    #     self.group = Group.objects.get(name=name)
    
    # just groups
    def add_group(self, name) -> str:
        # no need to be in this class
        group = Group.objects.create(name=name)
        return f"<group created: {group.name}>"
    
    def delete_group(self) -> str:
        group = self.group.delete()
        return f"<group deleted: {group.name}>"
    
    def get_group(self, name) -> Group:
        group = Group.objects.get(name=name)
        
        return group
    
    def get_user_groups(self, user_id: int) -> QuerySet[Group]:
        return Users.objects.prefetch_related("groups").get(pk=user_id).groups
    
    # user with groups
    def add_user(self, user_id: int, group_id: int) -> str: #
        user = Users.objects.prefetch_related("groups").get(id=user_id)
        user.groups.add(group_id)
        user.save()
        
        return f"{user} added to group"
    
    def delete_user_from_group(self, user_id: int, group_id: int) -> str: #
        user: Users = Users.objects.prefetch_related("groups").get(pk=user_id)
        user.groups.remove(group_id)
        
        return f"{user} deleted from group"
    
    # permissions with groups
    def get_permissions(self, group_id: str) -> QuerySet[Permission] : #  QuerySet[Permission] | QuerySet
        return Group.objects.prefetch_related("permissions").get(id=group_id).permissions
    
    def has_permission(self, perm_name: str, group: Group) -> bool: #
        permission = group.permissions.filter(codename=perm_name)
        if not permission.exists():
            print("not exists")
            return False
        
        return True
    
    def add_permission(self, perm_id: int, group_id: str) -> str: #
        group = Group.objects.prefetch_related("permissions").get(id=group_id)
        group.permissions.add(perm_id)
        
        return f"new perm added to: {group.name}"
    
    def add_permissions(self, group_id: str, perms_ids: list[int]) -> str: #
        group = Group.objects.prefetch_related("permissions").get(id=group_id)
        group.permissions.add(*perms_ids)
        
        return f"new perms added to: {group.name}"
    
    def delete_permissions(self, perm_objs: list[Permission]) -> str:
        self.group.permissions.remove(*perm_objs)
        
        return f"{perm_objs} deleted from group: {self.group.name}"
    
    def switch_permissions(self, perm_objs: list[Permission]) -> str:
        self.group.permissions.set(perm_objs)
        
        return f"{self.group.name} permissions switched to: {perm_objs}"
    
    def flush_permissions(self) -> str:
        self.group.permissions.clear()
        
        return f"{self.group.name} has no permissions"


class UserGroups:
    
    def __init__(self, user) -> None:
        self.user = user
    
    # groups with user
    def flush_user_groups(self) -> str:
        self.user.groups.clear()
        
        return f"user: {self.user} groups flushed"
    
    def switch_user_groups(self, groups: list[str]) -> str:
        self.user.groups.set(groups)
        
        return f"user {self.user} now has these groups: {groups}"