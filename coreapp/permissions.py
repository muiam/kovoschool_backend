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

class IsHeadTeacherOrTeacher(BasePermission):
    """
    Allows access only to head teachers and teachers.
    """
    def has_permission(self, request, view):
        is_authenticated = request.user and request.user.is_authenticated
        return bool(is_authenticated and (request.user.type == 'headTeacher' or request.user.type == 'teacher'))

