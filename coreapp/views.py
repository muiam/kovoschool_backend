import json
from django.http import Http404
from rest_framework.decorators import api_view ,APIView,permission_classes,authentication_classes
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView

from kovo_school import settings

from .permissions import IsAllExceptParent, IsAllUsers, IsFinance, IsHeadTeacher, IsHeadTeacherOrTeacher, IsParent, IsTeacher
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import AcademicYear, Bill, BillPayment, CarryForward, Curriculum, Exam, ExamResult, Fee, FeeBalance, FeePayment, Level, Month, MpesaPayments, Notification, Payslip, School, Student, StudentBill, Subject, TeacherSubject, Term, Transaction, TransactionItem, User, Week, Year, Report
from django.contrib.auth import logout

from .serializers import AcademicYearsSerializer, AssignedSubjectSerializer, BillSerializer, CarryFowardSerializer, ChangePasswordSerializer, CurriculumSerializer, ExamQueryStudentsSerializer, ExamResultCompareSerializer, ExamResultsSerializer, ExamSerializer, FeeBalanceSerializer, FeeSerializer, GetStudentForMarksSerializer, LevelSerializer, MonthsSerializer, MyReportSerilaizer, MyTokenObtainPairSerializer, NotificationSerializer, PasswordResetConfirmSerializer, PasswordResetRequestSerializer, PaySlipSerializer, PayslipsSerializer, RegisterParentSerializer, RegisterSchoolSerializer, RegisterStudentSerializer, RegisterTeacherSerializer, ReportSerializer, StudentBillSerializer, StudentSerializer, SubjectSerializer, TeacherSubjectSerializer, TermSerializer, TransactionItemSerializer, TransactionSerializer,UserSerializer, WeekSerializer, YearsSerializer, NewPaySlipSerializer
from rest_framework import status
from django.db.models import Q
from django.db.models import Count,Sum,F,IntegerField
from django.db.models.functions import Cast
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.core.mail import send_mail , EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.timezone import timedelta
from django.utils import timezone
from django.utils.html import strip_tags
from . import models
from django.utils.dateparse import parse_date
from django.db.models.functions import TruncDate
import requests
import base64
from rest_framework.request import Request
# Create your views here.

@api_view(['GET'])
def test(request):
    return Response("You are set dev")


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer



class LogoutView(APIView):
    def post(self, request):
        logout(request)
        return Response({"detail": "Successfully logged out."})



class RegisterTeacher(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsHeadTeacher]
    def post(self, request, format=None):
        try:

            serializer = RegisterTeacherSerializer(data=request.data, context={'request': request})
            if serializer.is_valid():
                # Get the current user's school
                current_user = request.user
                # Set the school of the new user to be the same as the school of the current user
                serializer.validated_data['school'] = current_user.school
                serializer.validated_data['type'] = "teacher"
                user = serializer.save()
                plaintext_password = serializer.validated_data['password']
                user = serializer.save()
                user.set_password(plaintext_password)
                user.set_password(plaintext_password)
                #send an email
                html_message = render_to_string('welcome_mail.html', {'user': user.first_name , 'school': request.user.school.name , 'email': user.email, 'password': plaintext_password})
                subject = 'Invitation to shulea'
                from_email = settings.EMAIL_HOST_USER
                to_email = user.email
                plain_message = strip_tags(html_message)
                body= plain_message
                email = EmailMultiAlternatives(subject, body, from_email, [to_email])
                email.attach_alternative(html_message, "text/html")  # Attach HTML content
                #send email
                email.send()
                user.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            print(serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(e)

    def get(self,request):
        school =request.user.school.id
        allTeachers = User.objects.filter(type='teacher', school =school)[:10]
        serializedData = UserSerializer(allTeachers,many =True)
        return Response(serializedData.data , status=status.HTTP_200_OK)
    


class RegisterParent(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAllUsers]
    def post(self, request, format=None):
        try:

            serializer = RegisterParentSerializer(data=request.data, context={'request': request})
            if serializer.is_valid():
                # Get the current user's school
                current_user = request.user
                # Set the school of the new user to be the same as the school of the current user
                serializer.validated_data['school'] = current_user.school
                serializer.validated_data['type'] = "parent"
                plaintext_password = serializer.validated_data['password']
                user = serializer.save()
                user.set_password(plaintext_password)
                #send an email
                html_message = render_to_string('welcome_mail.html', {'user': user.first_name , 'school': request.user.school.name, 'email': user.email,'password': plaintext_password})
                subject = 'Invitation to shulea'
                from_email = settings.EMAIL_HOST_USER
                to_email = user.email

                # Specify both plain text and HTML content
                text_content = ''  # Empty string for plain text content
                email = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
                email.attach_alternative(html_message, "text/html")  # Attach HTML content
                #send email
                email.send()
                user.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            print(serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(e)

    def get(self,request):
        school =request.user.school.id
        allParents = User.objects.filter(type='parent', school =school)[:10]
        serializedData = UserSerializer(allParents,many =True)
        return Response(serializedData.data , status=status.HTTP_200_OK)






#api for searching
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsHeadTeacher])
def searchTeachers(request):
    school_id = request.user.school.id
    search_term = request.query_params.get('q', '').strip()

    if search_term:
        query = Q(school=school_id, type='teacher') & (Q(email__icontains=search_term) | Q(first_name__icontains=search_term) | Q(second_name__icontains=search_term))

        teachers = User.objects.filter(query)
        serializer = UserSerializer(teachers, many=True)
        return Response(serializer.data)
    else:
        return Response([])
    

#api for searching
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsHeadTeacher])
def searchParents(request):
    school_id = request.user.school.id
    search_term = request.query_params.get('q', '').strip()

    if search_term:
        query = Q(school=school_id, type='parent') & (Q(email__icontains=search_term) | Q(first_name__icontains=search_term) | Q(second_name__icontains=search_term))

        parents = User.objects.filter(query)
        serializer = UserSerializer(parents, many=True)
        return Response(serializer.data)
    else:
        return Response([])


@api_view(['PUT'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsHeadTeacher])
def deactivateUser(request):
    user_email = request.query_params.get('email', '').strip()
    try:
        user = User.objects.get(email=user_email)
        if user.is_active :
            user.is_active =False
            user.save()
            return Response({"message": f"User {user_email} has been deactivated."}, status=200)
        user.is_active=True
        user.save()
        return Response({"message": f"User {user_email} has been deactivated."}, status=200)
    except User.DoesNotExist:
        return Response({"error": f"User with email {user_email} does not exist."}, status=404)

@api_view(['PUT'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsFinance])
def pay_pasyslip(request):
    school = request.user.school.id
    school = School.objects.get(id=school)
    expenditure_item = TransactionItem.objects.get(id=5)
    slip_id = request.query_params.get('id', '').strip()

    try:
        slip = Payslip.objects.get(id=slip_id)

        slip.paid =True
        slip.save()
        Transaction.objects.create(
            school = school,
            amount=slip.net_salary,
            description='staff payment',
            receipt_number=generate_receipt_number_for_random_use(request),
            head = expenditure_item,
            type ='expenditure'
        )
        return Response(status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response( status=status.HTTP_400_BAD_REQUEST)
class RegisterStudent(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsHeadTeacher]
    
    def post(self, request, format=None):
        serializer = RegisterStudentSerializer(data=request.data, context={'request': request})
        current_user = request.user
        if serializer.is_valid():
            serializer.validated_data['school'] = current_user.school
            serializer.save()
            return Response(serializer.data , status=status.HTTP_201_CREATED)
        print(serializer.errors)
    
        
        return Response(serializer.errors , status=status.HTTP_400_BAD_REQUEST)
    
    def get(self, request):
        school_id = request.user.school.id
        students = Student.objects.filter(school=school_id)
        serialized_data = RegisterStudentSerializer(students, many=True)
        
        # Add the class name (level name) to each serialized student object
        for data in serialized_data.data:
            level_id = data['current_level']
            level_name = Level.objects.get(id=level_id).name
            level_stream = Level.objects.get(id=level_id).stream
            data['level_name'] = level_name
            data['level_stream'] = level_stream
        
        return Response(serialized_data.data, status=status.HTTP_200_OK)

class Levels(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAllUsers]

    def post(self, request):
        school = School.objects.get(id=request.user.school.id)
        data = json.loads(request.body)
        name = data.get('name')
        stream = data.get('stream')
        Level.objects.create(
            school=school,
            name=name,
            stream=stream
        )
        return Response(status=status.HTTP_201_CREATED)
    
    def get(self, request):
        school =request.user.school.id
        allLevels = Level.objects.filter(school =school).order_by('-id')
        serializedData = LevelSerializer(allLevels,many =True)
        return Response(serializedData.data , status=status.HTTP_200_OK)
    
class AcademicYears(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAllUsers]
    
    
    def get(self, request):
        school = request.user.school.id
        allYears = AcademicYear.objects.filter(school=school).order_by('-id')
        serializedData = AcademicYearsSerializer(allYears,many =True)
        return Response(serializedData.data , status=status.HTTP_200_OK)
class Terms(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAllUsers]
    
    def get(self, request):
        year_id = request.query_params.get('year')
        if not year_id:
            raise Http404("Year ID parameter is required")

        allTerms = Term.objects.filter(year=year_id).order_by('-id')
        serializedData = TermSerializer(allTerms, many=True)
        return Response(serializedData.data, status=status.HTTP_200_OK)
    
class Exams(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAllUsers]

    def get(self, request):
        school = request.user.school.id
        year_id = request.query_params.get('year')
        term_id = request.query_params.get('term')
        
        if not year_id:
            allExams = Exam.objects.filter(school=school).order_by('-id')
        elif not term_id:
            allExams = Exam.objects.filter(school=school, year=year_id).order_by('-id')
        else:
            allExams = Exam.objects.filter(school=school, term=term_id, year=year_id).order_by('-id')
        
        serializedData = ExamSerializer(allExams, many=True)
        if allExams.exists():
            return Response(data=serializedData.data, status=status.HTTP_200_OK)
        else:
            return Response(data={'detail': 'No exams found'}, status=status.HTTP_404_NOT_FOUND)

    
class Subjects(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsHeadTeacherOrTeacher]
    def post(self, request):
            # Check if the request body is empty
            if not request.body:
                return Response({'error': 'Request body is empty'}, status=status.HTTP_400_BAD_REQUEST)

            try:
                data = json.loads(request.body)
            except json.JSONDecodeError:
                return Response({'error': 'Invalid JSON format in request body'}, status=status.HTTP_400_BAD_REQUEST)

            # Now you can proceed with handling the JSON data
            school = School.objects.get(id=request.user.school.id)
            name = data.get('name')
            level_id = data.get('level')
            all=data.get('all')
            required = data.get('required')
            if all:
                levels=Level.objects.filter(school=school)
                if not levels:
                    return Response(status=status.HTTP_404_NOT_FOUND)

                for lv in levels:
                    Subject.objects.create(
                    name=name,
                    school=school,
                    level=lv,
                    required=required,
                )
                return Response(status=status.HTTP_201_CREATED)


            else:
                level = Level.objects.get(id=level_id)
                Subject.objects.create(
                name=name,
                school=school,
                level=level,
                required=required,
            )
                return Response(status=status.HTTP_201_CREATED)
    def get(self, request):
            school_id = request.user.school.id
            all_subjects = Subject.objects.filter(school = school_id)
            serialized_data = SubjectSerializer(all_subjects, many=True)
            
            response_data = []
            for data in serialized_data.data:
                level_id = data['level']
                level = Level.objects.get(id=level_id)
                level_name = level.name
                level_stream = level.stream
                
                if level_stream is not None:
                    data['level_name'] = level_name
                    data['level_stream'] = level_stream
                    response_data.append(data)
                else:
                    data['level_name'] = level_name
                    response_data.append(data)
            
            if response_data:
                return Response(response_data, status=status.HTTP_200_OK)
            else:
                return Response(response_data, status=status.HTTP_200_OK)
        
class FreeSubjects(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsHeadTeacher]
    
    def get(self, request):
        school_id = request.user.school.id
        all_subjects = Subject.objects.filter(school=school_id)
        serialized_data = SubjectSerializer(all_subjects, many=True).data
        
        response_data = []
        
        for data in serialized_data:
            level_id = data['level']
            level = Level.objects.get(id=level_id)
            level_name = level.name
            level_stream = level.stream
            
            if level_stream is not None:
                data['level_name'] = level_name
                data['level_stream'] = level_stream
            else:
                data['level_name'] = level_name
                
            response_data.append(data)
        
        return Response(response_data, status=status.HTTP_200_OK)
        
        
class AssignSubject(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsHeadTeacher]

    def post(self, request, format=None):
        serializer = TeacherSubjectSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()        
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def get (self, request):
        teacher_id =request.query_params.get('teacher')
        if not teacher_id:
            return Response({"detail": "Missing teacher ID"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            teacher = User.objects.get(pk=teacher_id, school=request.user.school.id, type='teacher')
        except User.DoesNotExist:
            return Response({"detail": "Teacher not found"}, status=status.HTTP_404_NOT_FOUND)

      
        assigned_subjects = TeacherSubject.objects.filter(teacher=teacher).order_by('-created')
        # Serialize the queryset
        serializer = AssignedSubjectSerializer(assigned_subjects, many=True)
        # Return the serialized data
        return Response(serializer.data)
    
class TeacherSubjects(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsTeacher]
    def get(self, request):
        teacherSubjects =TeacherSubject.objects.filter(teacher = request.user).order_by('-created')
        serializer = AssignedSubjectSerializer(teacherSubjects, many=True)
        return Response(serializer.data)

class StudentsMarksFetch(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsHeadTeacherOrTeacher]
    def post(self, request):
        school_id = request.user.school.id
        year = request.data.get('year')
        term = request.data.get('term')
        exam = request.data.get('exam')
        subject = request.data.get('subject')
        level = request.data.get('level')

        students = Student.objects.filter(current_level=level, school=school_id, active=True).order_by('-id')
        if students:
            student_data_list = []
            for student in students:
                examCheck = ExamResult.objects.filter(exam=exam, subject=subject, student=student, year=year, term=term, school=school_id)
                if not examCheck:
                    student_details = Student.objects.get(admission_number = student.admission_number)
                    student_data = {
                        'admission_number': student_details.admission_number,
                        'name': student_details.name,
                        'id': student_details.id
                    }
                    student_data_list.append(student_data)

            if student_data_list:
                # Directly pass the list of dictionaries to the serializer
                serializer = GetStudentForMarksSerializer(data=student_data_list, many=True)
                if serializer.is_valid():
                    print("serilaized data is ", serializer.data)
                    return Response(serializer.data, status=status.HTTP_200_OK)
                else:
                    print(serializer.errors)
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"error": "No students found for the given criteria."}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({"error": "No students found."}, status=status.HTTP_403_FORBIDDEN)



    
        


class BulkInsertMarksView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsHeadTeacherOrTeacher]
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            exam_id = data.get('exam_id')
            subject_id = data.get('subject_id')
            year_id = data.get('year_id')
            term_id = data.get('term_id')
            level_id = data.get('level_id')
            marks = data.get('marks')
            school_id = request.user.school.id
            school = School.objects.get(id=school_id)
            saved_results = []
            for mark in marks:
                student_id = mark.get('admission_number')
                score = mark.get('mark')
                if score is not None:
                    student = Student.objects.get(admission_number=student_id)
                    curriculum = student.curriculum.name
                    grade = self.determine_grade(score, curriculum)
                    exam = Exam.objects.get(id=exam_id)
                    subject = Subject.objects.get(id=subject_id)
                    year = AcademicYear.objects.get(id=year_id)
                    term = Term.objects.get(id=term_id)
                    level = Level.objects.get(id=level_id)
                    student = Student.objects.get(admission_number=student_id)
                    print(student,exam,subject,year,term,level,score)

                    exam_saving = ExamResult()
                    exam_saving.school = school
                    exam_saving.exam = exam
                    exam_saving.subject = subject
                    exam_saving.year = year
                    exam_saving.term= term
                    exam_saving.level = level
                    exam_saving.student = student
                    exam_saving.score = score
                    exam_saving.grade = grade
                    try:
                        exam_saving.save()
                        print("saved")
                    except Exception as e:
                        # Handle exceptions during save
                        print("Error saving exam result:", e)
                    saved_results.append(exam_saving)

                   
            serializer = ExamResultsSerializer(saved_results, many=True)
            serialized_data = serializer.data
            print("data sent is ",serialized_data)
            return Response(data=serialized_data, status=status.HTTP_201_CREATED)
        
                   

        except Exception as e:
            print(str(e))
            return Response({'error': str(e)}, status=400)
        
    # def determine_grade(self, score):
    #         """Determine grade based on score."""
    #         try:
    #             score = float(score)  # Ensure score is in correct format to compare
    #         except ValueError:
    #             return 'Invalid'  # or handle invalid score format as needed

    #         if 80 <= score <= 100:
    #             return 'EE'
    #         elif 50 <= score < 79:
    #             return 'ME'
    #         elif 30 <= score < 49:
    #             return 'AE'
    #         else:
    #             return 'BE'

    def determine_grade(self, score, curriculum):
        """Determine grade based on score and curriculum."""
        try:
            score = float(score) # Ensure score is in correct format to compare
        except ValueError:
            return 'Invalid' # or handle invalid score format as needed

        if curriculum == 'CBC':
            if 80 <= score <= 100:
                return 'EE'
            elif 50 <= score < 79:
                return 'ME'
            elif 30 <= score < 49:
                return 'AE'
            else:
                return 'BE'
        elif curriculum == 'CAMBRIDGE':
            if 80 <= score <= 100:
                return 'A*'
            elif 70 <= score < 80:
                return 'A'
            elif 60 <= score < 70:
                return 'B'
            elif 50 <= score < 60:
                return 'C'
            elif 40 <= score < 50:
                return 'D'
            else:
                return 'E'
        elif curriculum == 'EDEXCEL':
            if 80 <= score <= 100:
                return 'A'
            elif 70 <= score < 80:
                return 'B'
            elif 60 <= score < 70:
                return 'C'
            elif 50 <= score < 60:
                return 'D'
            else:
                return 'E'
        else:
            return 'Invalid Curriculum'


from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Sum, F
from django.db.models.functions import Cast
from django.db.models import IntegerField
from .models import ExamResult
from .serializers import SubjectScoreSerializer

class RankStudentsAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsHeadTeacherOrTeacher]
    def get(self, request, year_id, term_id, exam_id,level_id):
        # Fetch subject scores along with student details and subject names

        print("year",year_id, "term", term_id, "exam", exam_id, "grade", level_id)
        exam_results = ExamResult.objects.filter(
            year_id=year_id,
            term_id=term_id,
            level_id=level_id,
            exam_id=exam_id
        ).select_related('student', 'subject').annotate(
            numeric_score=Cast('score', output_field=IntegerField())
        ).values('student__admission_number', 'student__name', 'student_id').annotate(
            total_score=Sum('numeric_score')
        ).order_by('-total_score')

        # Retrieve subject scores and calculate total marks for each student
        detailed_scores = []
        for result in exam_results:
            student_id = result['student_id']
            student_name = result['student__name']
            admission_number = result['student__admission_number']

            subject_scores = ExamResult.objects.filter(
                student_id=student_id,
                year_id=year_id,
                term_id=term_id,
                level_id=level_id,
                exam_id=exam_id
            ).values_list('subject__name', 'score')

            subjects_dict = {}
            total_marks = 0
            for subject_name, score in subject_scores:
                score_int = int(score)
                subjects_dict[subject_name] = score_int
                total_marks += score_int

            detailed_scores.append({
                'student': {'admission_number': admission_number, 'name': student_name},
                'subject_scores': subjects_dict,
                'total_marks': total_marks,
            })

        # Serialize the data using SubjectScoreSerializer
        serializer = SubjectScoreSerializer(detailed_scores, many=True)

        return Response(serializer.data)
            

from django.db.models import Avg
from django.db.models.functions import Cast
from django.db.models import F

@api_view(["GET"])
@authentication_classes([JWTAuthentication])  # Use JWT authentication
@permission_classes([IsHeadTeacherOrTeacher])  # Apply custom permission class

def calculate_average_percentage(request, year_id, term_id, exam_id, level_id):
    # Convert exam_id to integer
    exam_id = int(exam_id)

    # Get previous exam ID
    previous_exam_id = exam_id - 1

    # Calculate total marks for each student in the current exam
    current_total_marks = ExamResult.objects.filter(
        exam__id=exam_id,
        year__id=year_id,
        term__id=term_id,
        level__id=level_id
    ).values('student').annotate(total_marks=Sum('score'))

    # Calculate total marks for each student in the previous exam
    previous_total_marks = ExamResult.objects.filter(
        exam__id=previous_exam_id,
        year__id=year_id,
        term__id=term_id,
        level__id=level_id
    ).values('student').annotate(total_marks=Sum('score'))

    # Calculate average total marks for each student in the current exam
    num_students_current = current_total_marks.count()
    total_marks_current = sum(item['total_marks'] for item in current_total_marks)
    average_marks_current = total_marks_current / num_students_current if num_students_current > 0 else 0

    # Calculate average total marks for each student in the previous exam
    num_students_previous = previous_total_marks.count()
    total_marks_previous = sum(item['total_marks'] for item in previous_total_marks)
    average_marks_previous = total_marks_previous / num_students_previous if num_students_previous > 0 else 0

    # Calculate percentage change in average marks
    if average_marks_previous > 0:
        percentage_change = ((average_marks_current - average_marks_previous) / average_marks_previous) * 100
    else:
        percentage_change = None

    return Response({
        'average_marks_current': average_marks_current,
        'average_marks_previous': average_marks_previous,
        'percentage_change': percentage_change
    })

@api_view(["GET"])
@authentication_classes([JWTAuthentication])  # Use JWT authentication
@permission_classes([IsHeadTeacherOrTeacher])  # Apply custom permission class
def find_most_improved_students(request, year_id, term_id, exam_id, level_id):
    # Convert exam_id to integer
    exam_id = int(exam_id)

    # Get previous exam ID
    previous_exam_id = exam_id - 1
    school_id = request.user.school.id

    # Get subjects and students for better response details
    subjects = Subject.objects.filter(school_id=school_id, level_id=level_id)
    students = Student.objects.filter(school_id=school_id, current_level_id=level_id)
    # print(students)
    # Calculate total marks for each student in the current exam for each subject
    current_subject_totals = ExamResult.objects.filter(
        exam__id=exam_id,
        year__id=year_id,
        term__id=term_id,
        level__id=level_id
    ).values('student', 'subject').annotate(total_marks=Sum('score'))

    # Calculate total marks for each student in the previous exam for each subject
    previous_subject_totals = ExamResult.objects.filter(
        exam__id=previous_exam_id,
        year__id=year_id,
        term__id=term_id,
        level__id=level_id
    ).values('student', 'subject').annotate(total_marks=Sum('score'))
    # print("current total" ,current_subject_totals , "previous total", previous_subject_totals)
    # Find the most improved student per subject
    most_improved_per_subject = {}
    for current_total in current_subject_totals:
        student_id = current_total['student']
        subject_id = current_total['subject']
        current_marks = current_total['total_marks']
        
        # Check if the student had a score for the subject in the previous exam
        previous_marks = next((item['total_marks'] for item in previous_subject_totals if item['student'] == student_id and item['subject'] == subject_id), None)
        if previous_marks is not None:
            improvement = current_marks - previous_marks
            percentage_improvement = (improvement / previous_marks) * 100 if previous_marks != 0 else 0
            
            # Check if this student is the most improved for this subject so far
            if improvement > 0 and (subject_id not in most_improved_per_subject or improvement > most_improved_per_subject[subject_id]['improvement']):
                most_improved_per_subject[subject_id] = {
                    'subject_id': subject_id,
                    'subject_name': subjects.get(id=subject_id).name,
                    'student_name': Student.objects.get(id=student_id).name,
                    'admission_number': Student.objects.get(id=student_id).admission_number,
                    'improvement': improvement,
                    'percentage_improvement': percentage_improvement
                }

    return Response({'most_improved_per_subject': most_improved_per_subject})


@api_view(["GET"])
@authentication_classes([JWTAuthentication])  # Use JWT authentication
@permission_classes([IsHeadTeacherOrTeacher])  # Apply custom permission class

def find_least_improved_students(request, year_id, term_id, exam_id, level_id):
    # Convert exam_id to integer
    exam_id = int(exam_id)

    # Get previous exam ID
    previous_exam_id = exam_id - 1
    school_id = request.user.school.id

    # Get subjects and students for better response details
    subjects = Subject.objects.filter(school_id=school_id, level_id=level_id)
    students = Student.objects.filter(school_id=school_id, current_level_id=level_id)

    # Calculate total marks for each student in the current exam for each subject
    current_subject_totals = ExamResult.objects.filter(
        exam__id=exam_id,
        year__id=year_id,
        term__id=term_id,
        level__id=level_id
    ).values('student', 'subject').annotate(total_marks=Sum('score'))

    # Calculate total marks for each student in the previous exam for each subject
    previous_subject_totals = ExamResult.objects.filter(
        exam__id=previous_exam_id,
        year__id=year_id,
        term__id=term_id,
        level__id=level_id
    ).values('student', 'subject').annotate(total_marks=Sum('score'))

    # Find the most improved student per subject
    most_improved_per_subject = {}
    for current_total in current_subject_totals:
        student_id = current_total['student']
        subject_id = current_total['subject']
        current_marks = current_total['total_marks']
        
        # Check if the student had a score for the subject in the previous exam
        previous_marks = next((item['total_marks'] for item in previous_subject_totals if item['student'] == student_id and item['subject'] == subject_id), None)
        if previous_marks is not None:
            improvement = current_marks - previous_marks
            percentage_improvement = (improvement / previous_marks) * 100 if previous_marks != 0 else 0
            
            # Check if this student has a negative improvement for this subject
            if improvement < 0:
                if subject_id not in most_improved_per_subject or improvement < most_improved_per_subject[subject_id]['improvement']:
                    most_improved_per_subject[subject_id] = {
                        'subject_id': subject_id,
                        'subject_name': subjects.get(id=subject_id).name,
                        'student_name': students.get(id=student_id).name,
                        'admission_number': students.get(id=student_id).admission_number,
                        'improvement': improvement,
                        'percentage_improvement': percentage_improvement
                    }

    return Response({'least_improved_per_subject': most_improved_per_subject})


@api_view(["GET"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAllUsers])
def find_student_scores(request, year_id, term_id, exam_id, level_id, student_id):
    try:
        # Filter exams for the student within the academic year and term
        queryset = ExamResult.objects.filter(
            student__id=student_id,
            exam__id = exam_id,
            year__id=year_id,
            term__id=term_id,
            level__id=level_id,
        )

        # Calculate total marks for each student
        total_marks = {}
        for result in queryset:
            total_marks[result.exam_id] = total_marks.get(result.exam_id, 0) + result.score

        # Get previous total marks for the student
        previous_total_marks = 0  # Initialize previous total marks
        previous_queryset = ExamResult.objects.filter(
            student__id=student_id,
            level__id=level_id,
            year__id=year_id,
            term__id=term_id,
            exam__id__lt=exam_id  # Filter exams before the current exam
        )
        for prev_result in previous_queryset:
            previous_total_marks += prev_result.score

        # Calculate percentage change in total marks
        percentage_change = None
        if previous_total_marks != 0:
            percentage_change = ((total_marks[exam_id] - previous_total_marks) / previous_total_marks) * 100

        # Fetch all exams for the student within the academic year
        all_exams_queryset = ExamResult.objects.filter(
        student__id=student_id,
        year__id=year_id,
        level__id=level_id,
         ).values('exam__name').annotate(total_marks=Sum('score'))

        # Map exam names to exam-wise totals
        exam_wise_totals = {exam['exam__name']: exam['total_marks'] for exam in all_exams_queryset}

        # Serialize data with ExamResultCompareSerializer
        serializer = ExamResultCompareSerializer(queryset, many=True)
        serialized_data = serializer.data

        # Prepare response data with total marks, exam-wise totals, and percentage change
        student = Student.objects.get(id=student_id)
        response_data = {
            'student_current_grade' : student.current_level.id,
            'exam_results': serialized_data,
            'total_marks': total_marks.get(exam_id, 0),  # Get total marks for the current exam
            'previous_total_marks': previous_total_marks,
            'percentage_change': percentage_change,
            'exam_wise_totals': exam_wise_totals,
        }

        return Response(response_data)
    except Exception as e:
        return Response({"error": str(e)}, status=400)
    
@api_view(["GET"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsHeadTeacherOrTeacher])
def get_students_per_level(request, level_id):
    school = request.user.school.id
    students = Student.objects.filter(school= school, current_level = level_id, active = True)
    serializer = StudentSerializer(students, many = True)
    return Response(data= serializer.data , status= 200)
class Payroll(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsFinance]

    def get(self, request, year, month):
        school_id = request.user.school.id
        all_payrolls = Payslip.objects.filter(year=year, month=month, school=school_id)
        serializer = PayslipsSerializer(all_payrolls, many=True)

        # Calculate totals for all payrolls
        all_total_gross_salary = all_payrolls.aggregate(total_gross_salary=Sum('gross_salary'))['total_gross_salary']
        all_total_net_salary = all_payrolls.aggregate(total_net_salary=Sum('net_salary'))['total_net_salary']
        all_overall_deductions = all_payrolls.aggregate(total_deductions=Sum('total_deductions'))['total_deductions']

        # Include totals in the response
        response_data = {
            'payrolls': serializer.data,
            'totals': {
                'total_gross_salary': all_total_gross_salary,
                'total_net_salary': all_total_net_salary,
                'total_deductions': all_overall_deductions,
            }
        }

        return Response(data=response_data, status=status.HTTP_200_OK)


class NewPayslip(APIView):
    def post(self, request, format=None):
        # Get the user's school
        user_school = request.user.school.id  # Assuming user's school is associated with the user

        # Add the user's school to the request data
        request.data['school'] = user_school  # Assuming school is represented by an id

        # Create serializer with modified data
        serializer = NewPaySlipSerializer(data=request.data)

        if serializer.is_valid():
            # Extract gross salary and total allowances from request data
            gross_salary = serializer.validated_data.get('gross_salary', 0)
            total_allowances = serializer.validated_data.get('total_allowances', 0)

            # Calculate total deductions
            employee_id= serializer.validated_data.get('employeeID')
            tax = serializer.validated_data.get('tax', 0)
            social_security = serializer.validated_data.get('social_security', 0)
            health_insurance = serializer.validated_data.get('health_insurance', 0)
            other_deductions = serializer.validated_data.get('other_deductions', 0)
            advance_salary = serializer.validated_data.get('advance_salary', 0)
            affordable_housing = serializer.validated_data.get('affordable_housing', 0)
            total_deductions = tax + social_security + health_insurance + other_deductions + advance_salary + affordable_housing
            if gross_salary == 0:
                net_salary = total_allowances - total_deductions 
                print("next salary as a result of total allowances", net_salary)
            else:
                net_salary = gross_salary - total_deductions
                print("next salary as a result of gross salary", net_salary)

            # Update net_salary and total_deductions in serializer data
            serializer.validated_data['net_salary'] = net_salary
            serializer.validated_data['total_deductions'] = total_deductions
            # Save the serializer
            serializer.save()
            school = School.objects.get(id=user_school)
            recipient = User.objects.get(employee_id=employee_id)
            Notification.objects.create(
                    recipient = recipient,
                    school = school,
                    title ='you received a new payslip item',
                    message = 'Hi, your efforts are valued. Your institution added a payslip item into your account\n . Login to have a look at it\n. Success \n'
                )
            
            #send email
            html_message = render_to_string('payslip_notification.html', {'user': recipient.first_name , 'school': request.user.school.name})
            subject = 'you got paid'
            from_email = settings.EMAIL_HOST_USER
            to_email = recipient.email
            plain_message = strip_tags(html_message)
            body= plain_message
            email = EmailMultiAlternatives(subject, body, from_email, [to_email])
            email.attach_alternative(html_message, "text/html")  # Attach HTML content
            #send email
            email.send()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        elif 'non_field_errors' in serializer.errors and serializer.errors['non_field_errors'][0] == "An employee can have only one payslip per month.":
            # If the error is related to the uniqueness constraint, return a custom error message
            return Response({"error": "An employee can have only one payslip per month."}, status=status.HTTP_400_BAD_REQUEST)
        else:
            # For other validation errors, return the standard error response
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        

@api_view(["GET"])
def get_year(request):
    years = Year.objects.all()
    serializer = YearsSerializer(years , many = True)
    return Response(data= serializer.data , status= 200)

@api_view(["GET"])
def get_month(request):
    months = Month.objects.all()
    serializer = MonthsSerializer(months , many = True)
    return Response(data= serializer.data , status= 200)

@api_view(["GET"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsFinance])
def all_employees(request):
    school =request.user.school.id
    all_employees = User.objects.filter(Q(school=school) & Q(is_active=True) & ~Q(type='parent'))
    serializedData = UserSerializer(all_employees,many =True)
    return Response(serializedData.data , status=status.HTTP_200_OK)

@api_view(["GET"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsFinance])
def employee(request, id):
    school =request.user.school.id
    employee = User.objects.filter(email = id,school =school , is_active = True)
    serializedData = UserSerializer(employee,many =True)
    return Response(serializedData.data , status=status.HTTP_200_OK)

from django.db.models import Sum

@api_view(["GET"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsFinance | IsHeadTeacherOrTeacher])
def my_payslip(request, year=None):
    if year is not None:
        payslips = Payslip.objects.filter(year=year, employee=request.user.email)
    else:
        payslips = Payslip.objects.filter(employee=request.user.email)
    
    # Filter payslips where pay is True and sum their net salaries
    total_net_salary = payslips.filter(paid=True).aggregate(total_net_salary=Sum('net_salary'))['total_net_salary'] or 0
    
    serializedData = PayslipsSerializer(payslips, many=True)
    response_data = {
        'payslips': serializedData.data,
        'total_net_salary': total_net_salary
    }
    return Response(response_data)

@api_view(["GET"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsFinance | IsHeadTeacherOrTeacher])
def my_single_payslip(request, payslip):
    user = request.user.email
    payslip = Payslip.objects.filter(employee = user, pk = payslip)
    if payslip:
        serializedData = PayslipsSerializer(payslip , many = True)
        return Response(data = serializedData.data , status=status.HTTP_200_OK)
    else:
        return Response(status=status.HTTP_404_NOT_FOUND)

@api_view(["GET"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAllUsers])
def all_school_fees(request, year=None, term=None, grade=None):
    school_id = request.user.school.id
    fees = Fee.objects.filter(school=school_id)

    if year is not None:
        fees = fees.filter(academic_year=year)
    if term is not None:
        fees = fees.filter(term=term)
    if grade is not None:
        fees = fees.filter(level=grade)
    serialized_data = FeeSerializer(fees, many=True)
    return Response(data=serialized_data.data, status=status.HTTP_200_OK)


from django.db.models import Sum

@api_view(["GET"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsFinance | IsHeadTeacherOrTeacher])
def get_unpaid_fee_students(request, year_id, term_id, level_id, fee_id):
    try:
        # Retrieve the school ID from the authenticated user
        school_id = request.user.school.id
        
        # Filter students based on the provided level and school
        students = Student.objects.filter(current_level=level_id, school=school_id)
        
        # List to store unpaid students
        unpaid_students = []
        
        # Iterate over each student
        for student in students:
            # Check if the student has any fee payment records for the given year, term, and fee ID
            fee_payments = FeePayment.objects.filter(
                student=student,
                fee__academic_year_id=year_id,
                fee__term_id=term_id,
                fee_id=fee_id
            )
            
            # Calculate total paid and total fee amount for the student
            total_paid = fee_payments.aggregate(Sum('amount_paid'))['amount_paid__sum'] or 0
            
            try:
                # Retrieve the fee object
                fee = Fee.objects.get(id=fee_id, level=level_id, academic_year=year_id, term=term_id)
                total_amount = fee.amount
            except Fee.DoesNotExist:
                return Response({'error': 'Fee not found'}, status=status.HTTP_404_NOT_FOUND)

            # Determine the balance for the student
            remaining_balance = total_amount - total_paid
            
            # Check if the student hasn't paid or has a fee balance
            if remaining_balance > 0 or total_paid < total_amount:
                unpaid_students.append({
                    'student_id': student.id,
                    'student_name': student.name,
                    'balance': remaining_balance
                })
        
        # Return unpaid students
        return Response({'unpaid_students': unpaid_students}, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsFinance | IsHeadTeacherOrTeacher])
def fetch_student_carry_foward(request , student):
    try:
        total_unused_amount = CarryForward.objects.get(student=student)
        total_unused_amount = total_unused_amount.amount
    except CarryForward.DoesNotExist:
        total_unused_amount = 0
    return Response(status=status.HTTP_200_OK , data={ 'total_unused' :total_unused_amount})


import random
import string


@api_view(["GET"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsFinance])
def generate_receipt_number(request):
    # Generate a 10-digit number
    receipt_number = ''.join(random.choice('0123456789') for _ in range(10))
    
    # Generate 2 random alphabets
    alphabets = ''.join(random.choice(string.ascii_uppercase) for _ in range(2))
    
    # Concatenate the 10-digit number with the 2 random alphabets
    final_receipt_number = alphabets+receipt_number

    return Response(status=status.HTTP_200_OK , data=final_receipt_number)


def generate_receipt_number_for_random_use(request):
    # Generate a 10-digit number
    receipt_number = ''.join(random.choice('0123456789') for _ in range(10))
    
    # Generate 2 random alphabets
    alphabets = ''.join(random.choice(string.ascii_uppercase) for _ in range(2))
    
    # Concatenate the 10-digit number with the 2 random alphabets
    final_receipt_number = alphabets+receipt_number
    return final_receipt_number

@api_view(["POST"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsFinance])
def fee_payment_over(request):
    try:
        data = json.loads(request.body)
        student_id = data.get('student')
        fee_id = data.get('fee')
        amount_paid = data.get('amount_paid')
        receipt_number = data.get('receipt_number')
        level_id = data.get('level')
        academic_year_id = data.get('academic_year')
        term_id = data.get('term')
        overpay = data.get('overpay', False)
            #instances
        student = Student.objects.get(pk=student_id)
        fee = Fee.objects.get(pk=fee_id)
        level = Level.objects.get(pk=level_id)
        academic_year = AcademicYear.objects.get(pk=academic_year_id)
        term = Term.objects.get(pk=term_id)

        fee_paid_for = Fee.objects.get(id= fee_id , level =level_id , academic_year =academic_year ,term=term)
        fee_payments = FeePayment.objects.filter(
                student=student,
                academic_year=academic_year_id,
                term=term_id,
                fee=fee_id,
                level = level_id
            )

            # Calculate total paid and total fee amount for the student
        total_paid = fee_payments.aggregate(Sum('amount_paid'))['amount_paid__sum'] or 0
        print("already paid", total_paid)
        new_total = amount_paid + total_paid
        balance =0
        if new_total >= fee_paid_for.amount:
            balance = new_total -fee_paid_for.amount
            paid = fee_paid_for.amount -total_paid
            print("you are paying only", paid)
            print("what you are paying + already paid",new_total)
            print("overpayment" , balance)
            
            print("you are paying", paid)
            FeePayment.objects.create(
            student=student,
            fee=fee,
            amount_paid=paid,
            receipt_number=receipt_number,
            level=level,
            academic_year=academic_year,
            term=term,
            overpay = balance
            )
            school = School.objects.get(id=request.user.school.id)
            head = TransactionItem.objects.get(id=1)
            Transaction.objects.create(
                school = school,
                type = 'revenue',
                head = head,
                amount = paid,
                receipt_number = receipt_number,
                description = 'student fee'
            )
            feebalance = FeeBalance.objects.get(academic_year = academic_year , student = student)
            if feebalance.amount - paid <=0:
                feebalance.student = student
                feebalance.school = school
                feebalance.academic_year = academic_year
                feebalance.amount = 0
                feebalance.paid = True
                feebalance.save()

            else:
                feebalance.amount = feebalance.amount - paid
                feebalance.student = student
                feebalance.school = school
                feebalance.academic_year = academic_year
                feebalance.save()
            
        try:
            total_unused_amount = CarryForward.objects.get(student=student)
            total_unused_amount.amount = balance
            total_unused_amount.save()
        except CarryForward.DoesNotExist:
            total_unused_amount= CarryForward.objects.create(student=student, amount=0)
            
        else:
            #print("there will be a balance")
            FeePayment.objects.create(
            student=student,
            fee=fee,
            amount_paid=amount_paid,
            receipt_number=receipt_number,
            level=level,
            academic_year=academic_year,
            term=term
            )
            Transaction.objects.create(
                school = school,
                type = 'revenue',
                head = head,
                amount = amount_paid,
                receipt_number = receipt_number,
                description = 'student fee'
            )
            feebalance = FeeBalance.objects.get(academic_year = academic_year , student = student)
            if feebalance.amount - amount_paid <=0:
                feebalance.student = student
                feebalance.school = school
                feebalance.academic_year = academic_year
                feebalance.amount = 0
                feebalance.paid = True
                feebalance.save()

            else:
                feebalance.amount = feebalance.amount - amount_paid
                feebalance.student = student
                feebalance.school = school
                feebalance.academic_year = academic_year
                feebalance.save()
           
            try:
                total_unused_amount = CarryForward.objects.get(student=student)
                total_unused_amount.amount = balance
                total_unused_amount.save()
            except CarryForward.DoesNotExist:
                total_unused_amount= CarryForward.objects.create(student=student, amount=0)
            return Response(status=status.HTTP_201_CREATED)
    except Exception as e:
        print(str(e))
        return Response({'error': str(e)}, status=400)

    
    return Response(status=status.HTTP_200_OK)
    



@api_view(["POST"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsFinance])
def fee_payment_direct(request):
    try:
        data = json.loads(request.body)
        student_id = data.get('student')
        fee_id = data.get('fee')
        amount_paid = data.get('amount_paid')
        receipt_number = data.get('receipt_number')
        level_id = data.get('level')
        academic_year_id = data.get('academic_year')
        term_id = data.get('term')
            #instances
        student = Student.objects.get(pk=student_id)
        fee = Fee.objects.get(pk=fee_id)
        level = Level.objects.get(pk=level_id)
        academic_year = AcademicYear.objects.get(pk=academic_year_id)
        term = Term.objects.get(pk=term_id)
        school = request.user.school.id
        school = School.objects.get(id=school)
        fee_paid_for = Fee.objects.get(id= fee_id , school=school,  level =level_id , academic_year =academic_year ,term=term)
        total_paid = FeePayment.objects.filter(
            student = student,
            student__current_level_id=level_id,
            academic_year_id=academic_year,
            term_id=term_id,
            fee_id=fee_id
        ).aggregate(total_paid=Sum('amount_paid'))['total_paid'] or 0
        new_total = total_paid+amount_paid
        #overpay detected
        if new_total >fee_paid_for.amount:
            overpay = new_total-fee_paid_for.amount
            paid = fee_paid_for.amount - total_paid
            FeePayment.objects.create(
            student=student,
            fee=fee,
            amount_paid=paid,
            receipt_number=receipt_number,
            level=level,
            academic_year=academic_year,
            term=term,
            overpay = overpay
            )
            head = TransactionItem.objects.get(id=1)
            Transaction.objects.create(
                school = school,
                type = 'revenue',
                head = head,
                amount = paid,
                receipt_number = receipt_number,
                description = 'student fee'
            )
            feebalance = FeeBalance.objects.get(academic_year = academic_year , student = student)
            if feebalance.amount - paid <=0:
                feebalance.student = student
                feebalance.school = school
                feebalance.academic_year = academic_year
                feebalance.amount = 0
                feebalance.paid = True
                feebalance.save()

            else:
                feebalance.amount = feebalance.amount - paid
                feebalance.student = student
                feebalance.school = school
                feebalance.academic_year = academic_year
                feebalance.save()

            
            try:
                total_unused_amount = CarryForward.objects.get(student=student)
                total_unused_amount.amount = overpay
                total_unused_amount.save()
            except CarryForward.DoesNotExist:
                total_unused_amount= CarryForward.objects.create(student=student, amount=overpay)
            return Response(status=status.HTTP_201_CREATED)
        else:
            FeePayment.objects.create(
            student=student,
            fee=fee,
            amount_paid=amount_paid,
            receipt_number=receipt_number,
            level=level,
            academic_year=academic_year,
            term=term,
            )
            school = School.objects.get(id=request.user.school.id)
            head = TransactionItem.objects.get(id=1)
            Transaction.objects.create(
                school = school,
                type = 'revenue',
                head = head,
                amount = amount_paid,
                receipt_number = receipt_number,
                description = 'student fee'
            )
            feebalance = FeeBalance.objects.get(academic_year = academic_year , student = student)
            if feebalance.amount - amount_paid <=0:
                feebalance.student = student
                feebalance.school = school
                feebalance.academic_year = academic_year
                feebalance.amount = 0
                feebalance.paid = True
                feebalance.save()

            else:
                feebalance.amount = feebalance.amount - amount_paid
                feebalance.student = student
                feebalance.school = school
                feebalance.academic_year = academic_year
                feebalance.save()

            return Response(status=status.HTTP_201_CREATED)


    except Exception as e:
        print(str(e))
        return Response({'error': str(e)}, status=400)

@api_view(["GET"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsFinance])
def calculate_total_carryforward(request):
    # Fetch all students
    students = Student.objects.filter(school = request.user.school.id)
    student_data = []

    # Iterate through each student
    for student in students:
        # Check if there's a carryforward record for the student
        carryforward_record = CarryForward.objects.filter(student=student).first()
        if carryforward_record:
            # If there's a carryforward record, fetch the amount
            carryforward_amount = carryforward_record.amount
            level = student.current_level
            if level.stream:
                level = f"{level.name} {level.stream}"
            else:
                level = level.name
            student_data.append({
                'id': student.id,
                'name': student.name,
                'Adm' :student.admission_number,
                'level': level,
                'carryforward_amount': carryforward_amount
            })

    # Calculate the total carryforward amount
    total_carryforward = sum(entry['carryforward_amount'] for entry in student_data)

    # Return the response with student data and total carryforward amount
    return Response({'students': student_data, 'total_carryforward': total_carryforward}, status=status.HTTP_200_OK)



from django.db.models import Count, F

@api_view(["GET"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsFinance])
def display_student_balances(request, level_id, year_id, term_id, fee_id):
    # Retrieve all students who belong to the specified level
    school = request.user.school.id
    students = Student.objects.filter(current_level_id=level_id , school = school)

    # Retrieve the fee object
    fee = Fee.objects.get(id=fee_id, school=school)

    # Calculate the fee amount payable
    fee_amount_payable = fee.amount

    # Calculate the total number of students
    total_students = students.count()

    # Calculate the total amount payable (expected amount)
    expected_amount = fee_amount_payable * total_students

    # Calculate the total paid amount by all students for the specified fee
    total_paid = FeePayment.objects.filter(
        student__current_level_id=level_id,
        academic_year_id=year_id,
        term_id=term_id,
        fee_id=fee_id
    ).aggregate(total_paid=Sum('amount_paid'))['total_paid'] or 0

    # # Calculate the total overpaid amount by all students for the specified fee
    # total_overpaid = FeePayment.objects.filter(
    #     student__current_level_id=level_id,
    #     academic_year_id=year_id,
    #     term_id=term_id,
    #     fee_id=fee_id
    # ).aggregate(total_overpaid=Sum('overpay'))['total_overpaid'] or 0

    # Calculate the total balance of all students
    total_balance = expected_amount-total_paid

    # Calculate the percentage paid so far compared with expected
    percentage_paid = (total_paid / expected_amount) * 100 if expected_amount != 0 else 0

    # Construct the response
    response_data = {
        'totals': {
            'expected_amount': expected_amount,
            'total_balance': total_balance,
            'total_paid': total_paid,
            'percentage_paid': percentage_paid
        }
    }

    # Construct the student balances list
    student_balances = []
    for student in students:
        total_student_paid = FeePayment.objects.filter(
            student=student,
            academic_year_id=year_id,
            term_id=term_id,
            fee_id=fee_id
        ).aggregate(total_paid=Sum('amount_paid'))['total_paid'] or 0

        total_student_overpaid = FeePayment.objects.filter(
            student=student,
            academic_year_id=year_id,
            term_id=term_id,
            fee_id=fee_id
        ).aggregate(total_overpaid=Sum('overpay'))['total_overpaid'] or 0

        total_student_balance = fee_amount_payable-total_student_paid
        level =student.current_level
        if student.current_level.stream:
            level = f"{student.current_level.name} {student.current_level.stream}"
        else:
            level= student.current_level.name
        student_balances.append({
            'required':fee_amount_payable,
            'student_name': student.name,
            'student_level':level,
            'student_adm':student.admission_number,
            'outstanding_balance': total_student_balance,
            'total_paid': total_student_paid,
            'overpaid': total_student_overpaid
        })

    response_data['student_balances'] = student_balances

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(["GET"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsFinance])
def get_transactions_summary(request, start_date=None, end_date=None):
    # Get revenue and expenditure transactions
    school_id = request.user.school.id
    
    if start_date and end_date:
        transactions = Transaction.objects.filter(
            school_id=school_id,
            date__range=(parse_date(start_date), parse_date(end_date)),
            type__in=['revenue', 'expenditure']
        ).order_by('-id')
    else:
        transactions = Transaction.objects.filter(
            school_id=school_id,
            type__in=['revenue', 'expenditure']
        ).order_by('-id')
    
    serializer = TransactionSerializer(transactions, many=True)
    
    # Get sum of amounts for revenue transactions
    revenue_sum = transactions.filter(type='revenue').aggregate(revenue_sum=Sum('amount'))['revenue_sum'] or 0

    # Get sum of amounts for expenditure transactions
    expenditure_sum = transactions.filter(type='expenditure').aggregate(expenditure_sum=Sum('amount'))['expenditure_sum'] or 0

    data = {
        'revenue_sum': revenue_sum,
        'expenditure_sum': expenditure_sum,
        'balance': revenue_sum - expenditure_sum,
        'transactions': serializer.data
    }
    return Response(data=data, status=status.HTTP_200_OK)

@api_view(["GET"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsFinance])
def get_transaction_dates(request):
    school_id = request.user.school.id
    transactions = Transaction.objects.filter(school=school_id).annotate(date_only=TruncDate('date')).values_list('date_only', flat=True).distinct()
    dates = list(transactions)
    return Response(data={'all_transaction_dates': dates})


@api_view(["GET"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsFinance])
def all_get_fee_balances(request,year, level=None):
    school = request.user.school.id
    academic_year_name = AcademicYear.objects.get(school=school, id=year)
    academic_year_name = academic_year_name.name
    if level is not None:
        fee = FeeBalance.objects.filter(school=school, academic_year=year, paid=False, student__current_level=level)
    else:
        fee = FeeBalance.objects.filter(school=school, academic_year=year, paid=False)
    total_amount = fee.aggregate(total_amount=Sum('amount'))['total_amount'] or 0
    serializer = FeeBalanceSerializer(fee , many=True)
    data = {
        'fee_balances': serializer.data,
        'academic_year' :academic_year_name,
        'total_amount': total_amount
    }
    return Response(data=data , status=status.HTTP_200_OK)

@api_view(["POST"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsFinance])
def save_revenue(request):
    school = request.user.school.id
    school = School.objects.get(id=school)
    data = json.loads(request.body)
    amount = data.get('amount')
    description = data.get('description')
    receipt_number = data.get('receipt_number')
    revenue_item = data.get('revenueItem')
    revenue_item = TransactionItem.objects.get(id=revenue_item)
    if amount == "":
         return Response(status=status.HTTP_403_FORBIDDEN)
    if description == "":
         return Response(status=status.HTTP_403_FORBIDDEN)
    if receipt_number == "":
         return Response(status=status.HTTP_403_FORBIDDEN)
    if revenue_item == "":
         return Response(status=status.HTTP_403_FORBIDDEN)
    try:
        Transaction.objects.create(
            school = school,
            amount=amount,
            description=description,
            receipt_number=receipt_number,
            head = revenue_item,
            type ='revenue'
        )
        return Response(status= status.HTTP_201_CREATED)
    except Exception as e:
        print(str(e))
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
  

@api_view(["POST"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsFinance])
def save_expenditure(request):
    school = request.user.school.id
    school = School.objects.get(id=school)
    data = json.loads(request.body)
    amount = data.get('amount')
    description = data.get('description')
    receipt_number = data.get('receipt_number')
    expenditure_item = data.get('ExpenditureItem')
    expenditure_item = TransactionItem.objects.get(id=expenditure_item)
    if amount == "":
         return Response(status=status.HTTP_403_FORBIDDEN)
    if description == "":
         return Response(status=status.HTTP_403_FORBIDDEN)
    if receipt_number == "":
         return Response(status=status.HTTP_403_FORBIDDEN)
    if expenditure_item == "":
         return Response(status=status.HTTP_403_FORBIDDEN)
    try:
        Transaction.objects.create(
            school = school,
            amount=amount,
            description=description,
            receipt_number=receipt_number,
            head = expenditure_item,
            type ='expenditure'
        )
        return Response(status= status.HTTP_201_CREATED)
    except Exception as e:
        print(str(e))
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
  

@api_view(["GET"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAllUsers])
def all_weeks(request):
    school = request.user.school.id
    week = Week.objects.filter(school=school)
    serializer = WeekSerializer(week, many = True)
    return Response(data= serializer.data , status=status.HTTP_200_OK)

class StudentReport(APIView):
     authentication_classes = [JWTAuthentication]
     permission_classes = [IsHeadTeacherOrTeacher]
     def get(self,request,week =None , level=None):
         school = request.user.school.id
         report = Report.objects.filter(school =school)
         if week is not None:
                report = Report.objects.filter(school =school , week = week)
         if level is not None:
                report = Report.objects.filter(school=school,level = level)
         if level is not None and week is not None:
                 report = Report.objects.filter(school= school, level = level , week=week)
         serializer = ReportSerializer(report , many = True)
         return Response(data= serializer.data , status=status.HTTP_200_OK)
     
class MyStudentReport(APIView):
     authentication_classes = [JWTAuthentication]
     permission_classes = [IsHeadTeacherOrTeacher]
     def get(self,request,week =None , level=None):
         school = request.user.school.id
         user=request.user
         report = Report.objects.filter(school =school , teacher=user)
         if week is not None:
                report = Report.objects.filter(school =school , week = week, teacher=user)
         if level is not None:
                report = Report.objects.filter(school=school,level = level,teacher=user)
         if level is not None and week is not None:
                 report = Report.objects.filter(school= school, level = level , week=week,teacher=user)
         serializer = ReportSerializer(report , many = True)
         return Response(data= serializer.data , status=status.HTTP_200_OK)
     def post(self, request):
            user=request.user
            school = request.user.school.id
            data = json.loads(request.body)
            student = data.get('student')
            subject = data.get('subject')
            level = data.get('level')
            week = data.get('week')
            behavior_effort= data.get('behavior_effort')
            goals_achieved=data.get('goals_achieved')
            improvement_areas = data.get('improvement_areas')
            comments= data.get('comments')
            next_week_goals = data.get('next_week_goals')
            academic_progress = data.get('academic_progress')
            #instances
            student = Student.objects.get(id=student)
            school = School.objects.get(id=school)
            level = Level.objects.get(id=level)
            week = Week.objects.get(id=week)
            subject = Subject.objects.get(id=subject)

            Report.objects.create(
                academic_progress = academic_progress,
                teacher = user,
                school = school,
                student=student,
                subject=subject,
                level=level,
                week=week,
                behavior_effort=behavior_effort,
                goals_achieved=goals_achieved,
                improvement_areas=improvement_areas,
                comments=comments,
                next_week_goals=next_week_goals
            )
            more_data = Student.objects.get(id=student)
            parent = more_data.parent
            Notification.objects.create(
                    recipient = parent,
                    sender = request.user,
                    school = school,
                    title ='New report item for your kid',
                    message = 'Hi, you received a new report item for your kid \n. Make sure you have a look at it \n'
                )
            Notification.objects.create(
                    recipient = request.user,
                    school = school,
                    title ='you added a new report item',
                    message = 'Hi, your new report item was shared to both you , the parent and your school \n. success \n'
                )
            return Response(status=status.HTTP_201_CREATED)

class MyKidReport(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsParent]

    def get(self, request, student=None, week=None, level=None):
        school_id = request.user.school.id
        queryset = Report.objects.filter(student__parent=request.user, school=school_id)

        if student is not None:
            queryset = queryset.filter(student=student)

        if week is not None:
            queryset = queryset.filter(week=week)

        if level is not None:
            queryset = queryset.filter(level=level)

        serializer = ReportSerializer(queryset, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

                
@api_view(["GET"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsHeadTeacherOrTeacher])
def single_report(request ,id):
    school = request.user.school.id
    report = Report.objects.filter(school=school , id=id)
    serializer = ReportSerializer(report, many = True)
    return Response(data= serializer.data , status=status.HTTP_200_OK)   

@api_view(["GET"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsTeacher])
def my_single_report(request, id):
    school = request.user.school.id
    teacher = request.user
    report = Report.objects.filter(school=school , id=id, teacher = teacher)
    if not report.exists():
        return Response(status=status.HTTP_404_NOT_FOUND)
    serializer = ReportSerializer(report, many = True)
    return Response(data= serializer.data , status=status.HTTP_200_OK)  


@api_view(["GET"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsParent])
def my_kid_single_report(request, id):
    school = request.user.school.id
    parent = request.user
    report = Report.objects.filter(school=school , id=id, student__parent =parent)
    if not report.exists():
        return Response(status=status.HTTP_404_NOT_FOUND)
    serializer = ReportSerializer(report, many = True)
    return Response(data= serializer.data , status=status.HTTP_200_OK)  
    

@api_view(["GET"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsHeadTeacherOrTeacher])
def all_weeks_data(request):
    school = request.user.school.id
    weeks = Week.objects.filter(school=school)
    week_data = []
    for week in weeks:
        reports = Report.objects.filter(school=school, week = week).count()
        serializer = WeekSerializer(week)
        data = {
            'week' : serializer.data,
            'reports': reports
        }
        week_data.append(data)
    return Response(data= week_data, status=status.HTTP_200_OK) 

from datetime import date
@api_view(["POST"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsHeadTeacher])
def save_current_week(request):
    school_id = request.user.school.id
    today = date.today()
    current_week_number = (today.day - 1) // 7 + 1
    current_month = today.strftime("%B")  # Get the full month name
    current_year = today.year
    week_name = f"Week {current_week_number} {current_month} {current_year}"
    # Check if the week already exists for the school
    existing_week = Week.objects.filter(name=week_name, school_id=school_id).first()

    if existing_week is None:
        # If the week doesn't exist, create a new one
        try:
            Week.objects.create(name=week_name, school_id=school_id)
            return Response(data={"message": f"Week '{week_name}' saved successfully for school {school_id}"}, status=status.HTTP_201_CREATED)
        except Exception as e:
            print(str(e.errors))
    else:
        # If the week already exists, return a message indicating it
        return Response(data={"message": f"Week '{week_name}' already exists for school {school_id}"}, status=status.HTTP_200_OK)
    
@api_view(["GET"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsHeadTeacherOrTeacher])
def get_my_school_students(request, level):
    school = request.user.school.id
    students = Student.objects.filter(current_level = level , school=school)
    serializer = StudentSerializer(students , many=True)
    return Response(data = serializer.data , status=status.HTTP_200_OK)

@api_view(["GET"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAllExceptParent])
def get_my_school_students_all(request):
    school = request.user.school.id
    students = Student.objects.filter(school=school)
    serializer = StudentSerializer(students , many=True)
    return Response(data = serializer.data , status=status.HTTP_200_OK)

@api_view(["GET"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsFinance])
def get_my_school_student_bill(request,bill):
    school = request.user.school.id
    bill = Bill.objects.get(school=school, id=bill)
    serializer = BillSerializer(bill)
    return Response(data = serializer.data , status=status.HTTP_200_OK)

@api_view(["GET"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsParent])
def get_my_kid(request, level = None):
    user = request.user
    school = request.user.school.id
    if level is not None:
        students = Student.objects.filter(current_level = level , school=school, parent = user)
        serializer = StudentSerializer(students , many=True)
    else:
        students = Student.objects.filter(school=school, parent = user)
        serializer = StudentSerializer(students , many=True)
    
    return Response(data = serializer.data , status=status.HTTP_200_OK)

@api_view(["GET"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsParent])
def get_all_my_kid(request, level = None):
    user = request.user
    school = request.user.school.id
    students = Student.objects.filter(school=school, parent = user)
    serializer = StudentSerializer(students , many=True)
    
    return Response(data = serializer.data , status=status.HTTP_200_OK)



@api_view(["GET"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsHeadTeacherOrTeacher])
def get_my_subject_per_level(request, level):
    school_id = request.user.school.id
    user = request.user
    
    # Filter subjects based on the user (teacher) and school ID
    subjects = Subject.objects.filter(teachersubject__teacher=user, school=school_id, level=level)
    
    # Serialize the subjects
    serializer = SubjectSerializer(subjects, many=True)
    
    return Response(data=serializer.data, status=status.HTTP_200_OK)


@api_view(["POST"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsFinance])
def get_add_school_fee(request):
    school_id = request.user.school.id
    school_id = School.objects.get(id=school_id)
    data = json.loads(request.body)
    level = data.get('level')
    level = Level.objects.get(id=level)
    amount = data.get('amount')
    academic_year = data.get('academic_year')
    academic_year = AcademicYear.objects.get(id=academic_year)
    term = data.get('term')
    term = Term.objects.get(id=term)
    Fee.objects.create(
        school = school_id,
        level = level,
        term =term,
        academic_year = academic_year,
        amount = amount
    )
   
    try:
        students = Student.objects.filter(current_level=level, school=school_id)
        fee_balances = FeeBalance.objects.filter(academic_year=academic_year, student__in=students)

        for student in students:
            student_fee_balances = [fb for fb in fee_balances if fb.student == student]
            if student_fee_balances:
                for feebalance in student_fee_balances:
                    feebalance.amount = feebalance.amount+amount
                    feebalance.save()
            else:
                FeeBalance.objects.create(
                    school =school_id,
                    academic_year=academic_year,
                    student=student,
                    amount=amount,
                )
        return Response(status=status.HTTP_201_CREATED)
    except Exception as e:
        print(str(e))
        return Response(data={'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



from django.db.models.functions import ExtractMonth
from django.http import JsonResponse
from .models import Transaction
from datetime import datetime
from calendar import month_name
@api_view(["GET"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsFinance])
def revenue_vs_expenditure(request, year):
    school = request.user.school.id
    months_data = {}

    # Initialize months data with zeros
    for month in range(1, 13):
        months_data[month] = {
            'month_name': month_name[month],
            'total_revenue': 0,
            'total_expenditure': 0,
        }

    # Populate months data with revenue and expenditure
    revenue_by_month = Transaction.objects.filter(date__year=year, type='revenue', school=school) \
        .annotate(month=ExtractMonth('date')) \
        .values('month') \
        .annotate(total_revenue=Sum('amount')) \
        .order_by('month')

    expenditure_by_month = Transaction.objects.filter(date__year=year, type='expenditure', school=school) \
        .annotate(month=ExtractMonth('date')) \
        .values('month') \
        .annotate(total_expenditure=Sum('amount')) \
        .order_by('month')
    total_deductions = Payslip.objects.filter(date__year=year ,paid = True , school= school).aggregate(total_deductions =Sum('total_deductions'))
    total_deductions_amount = total_deductions.get('total_deductions', 0)
    for item in revenue_by_month:
        months_data[item['month']]['total_revenue'] = item['total_revenue']

    for item in expenditure_by_month:
        months_data[item['month']]['total_expenditure'] = item['total_expenditure']

    # Calculate balance at hand
    balance_at_hand = 0
    for month_data in months_data.values():
        balance_at_hand += month_data['total_revenue'] - month_data['total_expenditure']

    data = {
        'months_data': list(months_data.values()),
        'balance_at_hand': balance_at_hand,
        'total_deductions': total_deductions_amount
    }
    return Response(data=data, status=status.HTTP_200_OK)


@api_view(["GET"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAllUsers])
def get_my_kid_fee_statements(request, year, term,fee, grade,student):
    year_obj = AcademicYear.objects.get(id=year)
    term_obj = Term.objects.get(id=term)
    grade_obj = Level.objects.get(id=grade)
    fee_obj = Fee.objects.get(id=fee)
    required = fee_obj.amount

    payments = FeePayment.objects.filter(
        student=student,
        level=grade_obj,
        academic_year=year_obj,
        term=term_obj,
        fee=fee_obj,
    )

    total_paid = payments.aggregate(total_paid=Sum('amount_paid'))['total_paid'] or 0
    balance = required - total_paid
    if balance<=0:
        balance =0
    else:
        balance=balance

    payment_data = [{
        'id': payment.id,
        'date' :  payment.date_paid,
        'amount_paid': payment.amount_paid,
        'receipt_number' : payment.receipt_number,
        'fowarded' : payment.overpay,
        # Add other fields as needed
    } for payment in payments]

    payment_data = {
        'payments': payment_data,
        'total': total_paid,
        'balance' : balance,
        'required': required,
    }

    return Response(data=payment_data, status=status.HTTP_200_OK)


@api_view(["GET"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsParent])
def get_my_learner_year_achievement(request, student_id=None):
    school = request.user.school
    year = AcademicYear.objects.filter(school=school).order_by('-id').first()
    if not year:
        return Response({"message": "No academic year found for the school."}, status=status.HTTP_404_NOT_FOUND)

    if student_id is None:
        # If student_id is not provided, get the first student associated with the parent
        user = request.user
        first_student = Student.objects.filter(parent=user).first()  # Accessing the first student
        if not first_student:
            return Response({"message": "No student found for the parent."}, status=status.HTTP_404_NOT_FOUND)
        else:
            student_id = first_student.id
    exams = Exam.objects.filter(year=year, school=school)
    exam_results = []
    for exam in exams:
        exam_result = ExamResult.objects.filter(exam=exam, student_id=student_id).aggregate(total_score=Sum('score'))
        if exam_result['total_score'] is not None:
            exam_data = {
                "academic_year" : year.name,
                "exam_id": exam.id,
                "exam_name": exam.name,
                "total_score": exam_result['total_score']
            }
            exam_results.append(exam_data)
    
    return Response(data=exam_results , status=status.HTTP_200_OK)

@api_view(["GET"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsParent])
def my_kids_data(request):
    user = request.user
    students_number = Student.objects.filter(school=request.user.school.id, parent=user).count()
    
    # Aggregate the total amount across all students
    total_wallet_balance = CarryForward.objects.filter(student__parent=user).aggregate(total_amount=Sum('amount'))['total_amount'] or 0

    student_data = {
        'student_number': students_number,
        'total_wallet_balance': total_wallet_balance
    }

    return Response(data=student_data, status=status.HTTP_200_OK)

@api_view(["GET"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAllUsers])
def get_unread_notifications(request):
    user = request.user
    unread_cont = Notification.objects.filter(recipient = user , is_read = False).count()
    unread = Notification.objects.filter(recipient = user , is_read = False)
    serializer = NotificationSerializer(unread , many =True)
    return Response(data ={'count': unread_cont , 'unread' : serializer.data} , status=status.HTTP_200_OK)

@api_view(["PUT"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAllUsers])
def update_unread_notifications(request, id):
    user = request.user
    # Get the unread notification with the given ID for the current user
    unread_notifications = Notification.objects.filter(recipient=user, is_read=False, id=id)
    
    # Check if the unread notification exists
    if unread_notifications.exists():
        # Update the is_read field of each unread notification
        unread_notifications.update(is_read=True)
        return Response(status=status.HTTP_200_OK)
    else:
        return Response({"error": "Unread notification not found"}, status=status.HTTP_404_NOT_FOUND)


class Notifications(APIView):
    def post(self,request , type):
        school = request.user.school.id
        school = School.objects.get(id=school)
        # data = json.loads(request.body)
        subject = request.data.get('subject')
        message = request.data.get('message')
        if type == 'parent':
            parents = User.objects.filter(is_active = True, school=school , type='parent')
            for parent in parents:
                Notification.objects.create(
                    recipient = parent,
                    sender = request.user,
                     school = school,
                    title =subject,
                    message = message
                )
            return Response(status=status.HTTP_201_CREATED)
        elif type == 'teacher':
            teachers = User.objects.filter(is_active = True, school=school , type='teacher')
            for teacher in teachers:
                Notification.objects.create(
                    recipient = teacher,
                    sender = request.user,
                     school = school,
                    title = subject,
                    message = message
                )
            return Response(status=status.HTTP_201_CREATED)
        elif type == 'all':
            users= User.objects.filter(is_active = True, school=school)
            for user in users:
                Notification.objects.create(
                    recipient = user,
                    sender = request.user,
                     school = school,
                    title = subject,
                    message = message
                )
            return Response(status=status.HTTP_201_CREATED)
        elif type =='single':
            recipient = request.data.get('recipient')
            recipient = User.objects.get(id = recipient , school = school)
            Notification.objects.create(
                    recipient = recipient,
                    sender = request.user,
                    school = school,
                    title = subject,
                    message = message
                )
            return Response(status=status.HTTP_201_CREATED)


        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        

@api_view(["GET"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAllExceptParent])       
def all_school_members(request):
    school =request.user.school.id
    all = User.objects.filter(school = school , is_active=True )
    serializer = UserSerializer(all , many = True)
    return Response(data=serializer.data , status=status.HTTP_200_OK)

@api_view(["GET"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAllUsers])       
def all_curriculum(request):
    all = Curriculum.objects.all()
    serializer = CurriculumSerializer(all , many = True)
    return Response(data=serializer.data , status=status.HTTP_200_OK)


class ChangePasswordView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAllUsers]
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        user = User.objects.get(id= request.user.id)
        school = School.objects.get(id = request.user.school.id)
        if serializer.is_valid():
            new_password = serializer.validated_data.get('new_password')
            user = request.user
            user.set_password(new_password)
            user.save()
            Notification.objects.create(
                    recipient = user,
                    school = school,
                    title = 'password change',
                    message = f"Hi {request.user.first_name},\nYour password change was initiated successfully. If you didn't perform any password change recently, please contact the support team for assistance.\nBy a copy of this message, an awareness as per the subject above has been made to you.\nRegards"
            )
            html_message = render_to_string('password_changed.html', {'user': user.first_name})
            subject = 'you changed your password recently'
            from_email = settings.EMAIL_HOST_USER
            to_email = user.email
            plain_message = strip_tags(html_message)
            body= plain_message
            email = EmailMultiAlternatives(subject,body, from_email, [to_email])
            email.attach_alternative(html_message, "text/html")  # Attach HTML content
            #send email
            email.send()

            return Response({"message": "Password changed successfully"}, status=status.HTTP_200_OK)
        print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


class PasswordResetRequestAPIView(APIView):
    serializer_class = PasswordResetRequestSerializer

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)  # Updated this line
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'detail': 'No user found with this email address'}, status=status.HTTP_400_BAD_REQUEST)

        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        reset_link = f"https://app.shulea.com/reset-password/confirm/?uid={uid}&token={token}"
        html_message = render_to_string('password_reset_template.html', {'reset_link': reset_link})
        subject = 'Reset your password'
        from_email = settings.EMAIL_HOST_USER
        to_email = email
        plain_message = strip_tags(html_message)
        body= plain_message
        email = EmailMultiAlternatives(subject,body, from_email, [to_email])
        email.attach_alternative(html_message, "text/html")  # Attach HTML content
        #send email
        email.send()
        user.reset_password_token = token
        user.reset_password_token_created_at = timezone.now()
        user.save()
        return Response({'detail': 'Password reset email sent'}, status=status.HTTP_200_OK)

class PasswordResetConfirmAPIView(APIView):
    serializer_class = PasswordResetConfirmSerializer
    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.validated_data['token']
        new_password = serializer.validated_data['new_password']
        uidb64 = request.query_params.get('uid')
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
        # Check if the token matches the stored token
        if (user.reset_password_token == token and
            default_token_generator.check_token(user, token) and
            user.reset_password_token_created_at and
            timezone.now() <= user.reset_password_token_created_at + timedelta(hours=5)):

            # Reset the password
            user.set_password(new_password)
            user.save()

            # Clear the token and creation time
            user.reset_password_token = None
            user.reset_password_token_created_at = None
            user.save()

            return Response({'detail': 'Password reset successfully'}, status=status.HTTP_200_OK)
        else:
            return Response({'detail': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)


#school stats
@api_view(["GET"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsHeadTeacher])
def get_users_count(request):
    user = request.user
    teachers = User.objects.filter(type='teacher', school=user.school.id , is_active=True).count()
    parents = User.objects.filter(type='parent', school=user.school.id).count()
    students = Student.objects.filter(school=user.school.id).count()
    data = {
        'teachers': teachers,
        'parents': parents,
        'students': students
    }
    return Response(data = data , status=status.HTTP_200_OK)

#teacher stats
@api_view(["GET"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsTeacher])
def get_teacher_stats(request):
    user = request.user
    subjects = TeacherSubject.objects.filter(teacher=user).count()
    reports = Report.objects.filter(teacher = user).count()
    total_earned = Payslip.objects.filter(employee=user, paid=True).aggregate(total=Sum('net_salary'))
    total_earned = total_earned['total'] if total_earned['total'] else 0
    data = {
        'subjects': subjects,
        'reports': reports,
        'total_earned': total_earned
    }
    return Response(data = data , status=status.HTTP_200_OK)

@api_view(["GET"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsFinance])
def get_revenue_items(request):
    revenue = TransactionItem.objects.filter(type='revenue')
    serializer = TransactionItemSerializer(revenue , many =True)
    return Response(data =serializer.data , status=status.HTTP_200_OK)

@api_view(["GET"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsFinance])
def get_expenses_items(request):
    expense = TransactionItem.objects.filter(type='expenditure')
    serializer = TransactionItemSerializer(expense, many=True)
    return Response(data =serializer.data , status=status.HTTP_200_OK)

from django.db.models import Sum, F, Case, When, FloatField
@api_view(["GET"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsFinance])
def calculate_transaction_item_amounts(request, start_date = None , end_date = None):
    school = request.user.school.id
    if start_date and end_date:
        transactions = Transaction.objects.filter(school_id=school, date__range=(start_date, end_date))
    else:
        transactions = Transaction.objects.filter(school_id=school)

    items = TransactionItem.objects.all()
    revenue_data = []
    expenditure_data = []

    for item in items:
        item_type_total = transactions.filter(type=item.type).aggregate(total_amount=Sum('amount'))['total_amount']
        amount = transactions.filter(head=item).aggregate(total_amount=Sum('amount'))['total_amount'] or 0
        if amount:
            percentage = (amount / item_type_total) * 100
            percentage = round(percentage, 2)
        else:
            percentage = 0

        item_data = {
            'id': item.id,
            'item_name': item.name,
            'type': item.type,
            'amount': amount,
            'item_type_total': item_type_total,
            'percentage': percentage
        }

        if item.type == 'revenue':
            revenue_data.append(item_data)
        elif item.type == 'expenditure':
            expenditure_data.append(item_data)

    response_data = {
        'revenue': revenue_data,
        'expenditure': expenditure_data
    }

    return Response(data=response_data, status=status.HTTP_200_OK)

class PayableBill(APIView):
     authentication_classes = [JWTAuthentication]
     permission_classes = [IsFinance]
     def get(self,request, academic_year = None , term=None):
            print("academic year is", academic_year , "and term is", term)
            school = School.objects.get(id=request.user.school.id)
            if academic_year and term :
                academic_year = AcademicYear.objects.get(id=academic_year)
                term = Term.objects.get(id=term)
                bills = Bill.objects.filter(school = school , term=term, Academic_year = academic_year).order_by('-id')
            else:
                bills = Bill.objects.filter(school = school).order_by('-id')
            serialized_data =BillSerializer(bills, many=True)
            return Response(data=serialized_data.data , status=status.HTTP_200_OK)
     
     def post(self, request):
            school = request.user.school.id
            school = School.objects.get(id=school)
            amount = request.data.get('amount')
            comment = request.data.get('comment')
            academic_year = request.data.get('academic_year')
            academic_year = AcademicYear.objects.get(id=academic_year)
            term = request.data.get('term')
            term = Term.objects.get(id=term)
            name = request.data.get('name')

            if amount == "":
                return Response (status=status.HTTP_400_BAD_REQUEST)
            if school == "":
                return Response (status=status.HTTP_400_BAD_REQUEST)
            if academic_year == "":
                return Response (status=status.HTTP_400_BAD_REQUEST)
            if term == "":
                return Response (status=status.HTTP_400_BAD_REQUEST)
            if name == "":
                return Response (status=status.HTTP_400_BAD_REQUEST)
            Bill.objects.create(
                school=school,
                Academic_year = academic_year,
                term = term,
                comment = comment,
                name = name,
                amount = amount
            )
            return Response(status=status.HTTP_201_CREATED)

class StudentBilled(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsFinance]

    def get(self, request, bill, grade=None):
        data = []
        if grade is not None:
            billed_bills = StudentBill.objects.filter(bill=bill, student__current_level=grade)
        else:
            billed_bills = StudentBill.objects.filter(bill=bill)

        for billed_bill in billed_bills:
            total_paid_amount = BillPayment.objects.filter(student_bill=billed_bill.id).aggregate(total_amount=Sum('amount'))['total_amount'] or 0
            if total_paid_amount < billed_bill.amount:
                serialized_data = StudentBillSerializer(billed_bill).data
                serialized_data['total_paid'] = total_paid_amount
                data.append(serialized_data)
        return Response(data=data, status=status.HTTP_200_OK)


    def post(self,request , type,bill):
        school = request.user.school.id
        school = School.objects.get(id=school)
        bill = Bill.objects.get(id=bill , school=school)
        # data = json.loads(request.body)
        amount = request.data.get('amount')
        message = request.data.get('message')
        print("comment", message)
        if type == 'all':
            students= Student.objects.filter(active = True, school=school)
            for student in students:
                StudentBill.objects.create(
                    student = student,
                    amount = amount,
                    bill = bill,
                    comment = message
                )
            return Response(status=status.HTTP_201_CREATED)
        elif type =='single':
            student = request.data.get('student')
            student = Student.objects.get(id = student , active=True, school = school)
            StudentBill.objects.create(
                    student = student,
                    amount = amount,
                    bill = bill,
                    comment = message
                )
            return Response(status=status.HTTP_201_CREATED)

@api_view(["GET"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsFinance])
def get_bill_payment_list(request, bill, grade=None):
    bill = Bill.objects.get(id=bill)
    student_bills = StudentBill.objects.filter(bill=bill)

    payments_data = []
    total_paid_sum = 0  # Initialize total_paid_sum here
    expected_amount = StudentBill.objects.filter(bill=bill).aggregate(total_amount=Sum('amount'))['total_amount'] or 0
    for student_bill in student_bills:
        total_paid_amount = BillPayment.objects.filter(student_bill=student_bill).aggregate(total_amount=Sum('amount'))['total_amount'] or 0
        if total_paid_amount == student_bill.amount:
            payment ={
                'bill': student_bill.bill.name,
                'student_name': student_bill.student.name,
                'admission_number': student_bill.student.admission_number,
                'total_paid': total_paid_amount
            }
            payments_data.append(payment)
            total_paid_sum += total_paid_amount  # This line is now correctly placed
    
    stats = {
        'total_paid_sum': total_paid_sum,
        'expected_amount': expected_amount,
        'percentage_settled': round((total_paid_sum/expected_amount)*100, 2)
    }

    response_data = {
        'payments': payments_data,
        'stats': stats
    }
    return Response(data=response_data, status=status.HTTP_200_OK)


         
from decimal import Decimal
@api_view(["POST"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsFinance])
def receipt_student_bill(request, billed_id,student, amount):
    student = Student.objects.get(admission_number=student)
    billed = StudentBill.objects.get(id=billed_id)
    paid_amount = BillPayment.objects.filter(student_bill=billed).aggregate(total_amount=Sum('amount'))['total_amount'] or Decimal('0')
    new_amount = Decimal(amount) + paid_amount
    print("you are paying", amount , "new amount is", new_amount)
    if new_amount > billed.amount:
        paid=billed.amount-paid_amount
        wallet = Decimal(amount)- Decimal(paid)
        BillPayment.objects.create(
            student_bill =billed,
            amount = paid,
            receipt_number = generate_receipt_number_for_random_use(request)
        )
        school = School.objects.get(id=request.user.school.id)
        head = TransactionItem.objects.get(id=1)
        Transaction.objects.create(
                school = school,
                type = 'revenue',
                head = head,
                amount = paid,
                receipt_number = generate_receipt_number_for_random_use(request),
                description = 'bill payment'
            )
        CarryForward.objects.create(student=student, amount=wallet)
        return Response(status=status.HTTP_201_CREATED)
        # print("Yes, overpaid")
        # print("receipting", paid, "wallet goes this",wallet )
    elif new_amount == billed.amount:
        print("Clearing bill",amount)
        BillPayment.objects.create(
            student_bill =billed,
            amount = amount,
            receipt_number = generate_receipt_number_for_random_use(request)
        )
        school = School.objects.get(id=request.user.school.id)
        head = TransactionItem.objects.get(id=1)
        Transaction.objects.create(
                school = school,
                type = 'revenue',
                head = head,
                amount = amount,
                receipt_number = generate_receipt_number_for_random_use(request),
                description = 'bill payment'
            )
        return Response(status=status.HTTP_201_CREATED)
    else:
         
         BillPayment.objects.create(
            student_bill =billed,
            amount = amount,
            receipt_number = generate_receipt_number_for_random_use(request)
        )
         school = School.objects.get(id=request.user.school.id)
         head = TransactionItem.objects.get(id=1)
         Transaction.objects.create(
                school = school,
                type = 'revenue',
                head = head,
                amount = amount,
                receipt_number = generate_receipt_number_for_random_use(request),
                description = 'bill payment'
            )
         return Response(status=status.HTTP_201_CREATED)
    

@api_view(["GET"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsFinance])
def get_bill_payment_statements(request, bill):
    bill = Bill.objects.get(id=bill)
    student_bills = StudentBill.objects.filter(bill=bill)
    data = []
    amount = 0
    for student_bill in student_bills:
        student_statements = BillPayment.objects.filter(student_bill=student_bill)
        for statement in student_statements:
            statement_data ={
                'bill' : statement.student_bill.bill.name,
                'student_admission_number': statement.student_bill.student.admission_number,
                'student_name' : statement.student_bill.student.name,
                'amount': statement.amount,
                'receipt_number':statement.receipt_number,
                'payment_date':statement.payment_date
            }
            data.append(statement_data)
            amount += statement.amount
    statements_summary ={
        'payments' : data,
        'total_amount_in_statements': amount
    }
    return Response( data=statements_summary ,status=status.HTTP_200_OK)

def get_access_token(request):
    consumer_key = "u3K648nnaMX5A9R52GUtf1fC4Z5CN84fM2bVE5sOBahILXlv"  # Fill with your app Consumer Key
    consumer_secret = "SITp1vA8MPk7jPQ9tBoOQVxu6SZcf1Ct8AP7YpZOBdXb5j2R3tG4lQy0qJKRcegF"  # Fill with your app 
    access_token_url = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'
    headers = {'Content-Type': 'application/json'}
    auth = (consumer_key, consumer_secret)
    try:
        response = requests.get(access_token_url, headers=headers, auth=auth)
        response.raise_for_status()  # Raise exception for non-2xx status codes
        result = response.json()
        access_token = result['access_token']
        return Response({'access_token': access_token}, status=status.HTTP_200_OK)
    except requests.exceptions.RequestException as e:
        return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)
    
    
    
@api_view(["POST"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAllUsers])
def initiate_stk_push(request):
    access_token_response = get_access_token(request)
    if access_token_response.status_code == status.HTTP_200_OK:
        access_token = access_token_response.data['access_token']
        amount = 1
        phone = "254714457130"
        process_request_url = 'https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest'
        callback_url = 'https://kovoschool-backend.vercel.app/api/all/financials/payments/fee/mpesa/callback'
        passkey = "bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919"
        business_short_code = '174379'
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        password = base64.b64encode((business_short_code + passkey + timestamp).encode()).decode()
        party_a = phone
        account_reference = 'AD12345'
        transaction_desc = 'payment of fees'
        stk_push_headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + access_token
        }
        
        stk_push_payload = {
            'BusinessShortCode': business_short_code,
            'Password': password,
            'Timestamp': timestamp,
            'TransactionType': 'CustomerPayBillOnline',
            'Amount': amount,
            'PartyA': party_a,
            'PartyB': business_short_code,
            'PhoneNumber': party_a,
            'CallBackURL': callback_url,
            'AccountReference': account_reference,
            'TransactionDesc': transaction_desc
        }

        try:
            response = requests.post(process_request_url, headers=stk_push_headers, json=stk_push_payload)
            response.raise_for_status()  # Raise exception for non-2xx status codes
            response_data = response.json()
            checkout_request_id = response_data['CheckoutRequestID']
            response_code = response_data['ResponseCode']
            if response_code == "0":
                return Response({'CheckoutRequestID': checkout_request_id}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'STK push failed.', 'details': response_data}, status=status.HTTP_400_BAD_REQUEST)
        except requests.exceptions.RequestException as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return Response({'error': 'Failed to retrieve access token.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["GET"])
def process_stk_callback(request):
    stk_callback_response = json.loads(request.body)
    log_file = "Mpesastkresponse.json"
    with open(log_file, "a") as log:
        json.dump(stk_callback_response, log)
    
    merchant_request_id = stk_callback_response['Body']['stkCallback']['MerchantRequestID']
    checkout_request_id = stk_callback_response['Body']['stkCallback']['CheckoutRequestID']
    result_code = stk_callback_response['Body']['stkCallback']['ResultCode']
    result_desc = stk_callback_response['Body']['stkCallback']['ResultDesc']
    amount = stk_callback_response['Body']['stkCallback']['CallbackMetadata']['Item'][0]['Value']
    transaction_id = stk_callback_response['Body']['stkCallback']['CallbackMetadata']['Item'][1]['Value']
    user_phone_number = stk_callback_response['Body']['stkCallback']['CallbackMetadata']['Item'][4]['Value']
    
    if result_code == 0:
        MpesaPayments.objects.create(
            merchant_request_id = merchant_request_id,
            checkout_request_id = checkout_request_id,
            result_code=result_code,
            result_desc = result_desc,
            amount = amount,
            transaction_id= transaction_id,
            user_phone_number=user_phone_number
            
        )



class Our_school(APIView):
    def post(self, request, format=None):
        print("Received data:", request.data)  # Log incoming data
        serializer = RegisterSchoolSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        print("Validation errors:", serializer.errors)  # Log validation errors
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)