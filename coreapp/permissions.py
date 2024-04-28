from rest_framework.permissions import BasePermission

class IsHeadTeacher(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.type == 'headTeacher')

class IsTeacher(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.type == 'teacher')    
class IsFinance(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.type == 'accountant') 
class IsParent(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.type == 'parent')    

class IsHeadTeacherOrTeacher(BasePermission):
    """
    Allows access only to head teachers and teachers.
    """
    def has_permission(self, request, view):
        is_authenticated = request.user and request.user.is_authenticated
        return bool(is_authenticated and (request.user.type == 'headTeacher' or request.user.type == 'teacher'))

class IsAllUsers(BasePermission):
    """
    Allows access only to head teachers and teachers.
    """
    def has_permission(self, request, view):
        is_authenticated = request.user and request.user.is_authenticated
        return bool(is_authenticated and (request.user.type == 'headTeacher' or request.user.type == 'teacher' or request.user.type=='parent' or request.user.type=='accountant'))
class TeacherOrParent(BasePermission):
    """
    Allows access only to head teachers and teachers.
    """
    def has_permission(self, request, view):
        is_authenticated = request.user and request.user.is_authenticated
        return bool(is_authenticated and (request.user.type == 'parent' or request.user.type == 'teacher'))
class IsAllExceptParent(BasePermission):
    """
    Allows access only to head teachers and teachers.
    """
    def has_permission(self, request, view):
        is_authenticated = request.user and request.user.is_authenticated
        return bool(is_authenticated and (request.user.type == 'headTeacher' or request.user.type == 'teacher' or request.user.type=='accountant'))
