from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import AcademicYear, Bill, CarryForward, Curriculum, Exam, ExamResult, Fee, FeeBalance, Level, Month, Notification, Payslip, Report, School, Student, StudentBill, Subject, TeacherSubject, Term, Transaction, TransactionItem, User, Week, Year
from rest_framework import serializers

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['email'] = user.email
        token['type'] =user.type
        token['school'] = user.school.id if user.school else None
        token['school_name'] = user.school.name
        token['first_name'] = user.first_name
        token['second_name'] = user.second_name
        # ...

        return token

class LevelSerializer(serializers.ModelSerializer):
        class Meta:
            model = Level
            fields = '__all__'

class AcademicYearsSerializer(serializers.ModelSerializer):
        class Meta:
            model = AcademicYear
            fields = '__all__'
class TermSerializer(serializers.ModelSerializer):
        class Meta:
            model = Term
            fields = '__all__'
class ExamSerializer(serializers.ModelSerializer):
        term_name = serializers.SerializerMethodField()
        year_name = serializers.SerializerMethodField()
        class Meta:
            model = Exam
            fields = '__all__'

        def get_term_name(self, obj):
            term = obj.term
            return term.name
        def get_year_name(self, obj):
            year = obj.year
            return year.name
        
class SubjectScoreSerializer(serializers.Serializer):
    subject_name = serializers.CharField()
    subject_score = serializers.IntegerField()

class StudentExamResultSerializer(serializers.Serializer):
    student_id = serializers.IntegerField()
    total_exam_score = serializers.IntegerField()
    subject_scores = SubjectScoreSerializer(many=True)


from rest_framework import serializers
from .models import Student, Subject

class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ('id','name')


class TransactionItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransactionItem
        fields = '__all__'

class CurriculumSerializer(serializers.ModelSerializer):
    class Meta:
        model = Curriculum
        fields = ('id','name')

class YearsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Year
        fields = '__all__'
class MonthsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Month
        fields = '__all__'

class PaySlipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payslip
        fields = '__all__'

class MyReportSerilaizer(serializers.ModelSerializer):
     class Meta:
            model = Report
            fields = '__all__'
class ReportSerializer(serializers.ModelSerializer):
     level_name = serializers.SerializerMethodField()
     teacher_name = serializers.SerializerMethodField()
     subject_name = serializers.SerializerMethodField()
     week_name = serializers.SerializerMethodField()
     student_name = serializers.SerializerMethodField()
     student_adm =  serializers.SerializerMethodField()
     class Meta:
        model = Report
        fields = '__all__'
     def get_level_name(self, obj):
        level = obj.level
        if level.stream :
             return f"{obj.level.name} {level.stream}" 
        else:
             return obj.level.name
     def get_teacher_name(self,obj):
          teacher = obj.teacher
          return f"{teacher.first_name} {teacher.second_name}"
     def get_student_name(self, obj):
            student = obj.student
            return student.name
     def get_subject_name(self,obj):
            subject = obj.subject
            return subject.name
     def get_week_name(self, obj):
            week = obj.week
            return week.name
     def get_student_adm(self, obj):
            student = obj.student
            return student.admission_number



class WeekSerializer(serializers.ModelSerializer):
    class Meta:
        model = Week
        fields = '__all__'

class FeeSerializer(serializers.ModelSerializer):
    academic_year_name = serializers.SerializerMethodField()
    level_name = serializers.SerializerMethodField()
    term_name = serializers.SerializerMethodField()
    class Meta:
        model = Fee
        fields = '__all__'
    def get_academic_year_name(self, obj):
         return obj.academic_year.name  
    def get_level_name(self, obj):
        level = obj.level
        if level.stream :
             return f"{obj.level.name} {level.stream}" 
        else:
             return obj.level.name
    def get_term_name(self, obj):
         return obj.term.name 

class FeeBalanceSerializer(serializers.ModelSerializer):
     academic_year_name = serializers.SerializerMethodField()
     student_name = serializers.SerializerMethodField()
     student_level_name = serializers.SerializerMethodField()

     class Meta:
            model = FeeBalance
            fields = '__all__'
     def get_academic_year_name(self,obj):
        return obj.academic_year.name
     def get_student_name(self,obj):
          return obj.student.name
     def get_student_level_name(self,obj):
             level = obj.student.current_level
             if level.stream :
                    return f"{level.name} {level.stream}" 
             else:
                    return f"{level.name}"
     

class PayslipsSerializer(serializers.ModelSerializer):
    year_name = serializers.SerializerMethodField()
    month_name = serializers.SerializerMethodField()
    school_name = serializers.SerializerMethodField()
    employee = serializers.StringRelatedField()
    first_name =serializers.SerializerMethodField()
    last_name =serializers.SerializerMethodField()
    class Meta:
        model = Payslip
        fields = '__all__'

    def get_year_name(self, obj):
            # Get the name of the year
        return obj.year.name  # Assuming 'name' is the field storing the year name

    def get_month_name(self, obj):
        # Get the name of the month
        return obj.month.name  
    def get_school_name(self, obj):
        # Get the name of the month
        return obj.school.name  
    def get_first_name(self, obj):
        # Get the name of the month
        return obj.employee.first_name  
    def get_last_name(self, obj):
        # Get the name of the month
        return obj.employee.second_name  

class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ('name',)
class BillSerializer(serializers.ModelSerializer):
    academic_year_name = serializers.SerializerMethodField()
    term_name = serializers.SerializerMethodField()
    class Meta:
        model = Bill
        fields = '__all__'
    def get_academic_year_name(self,obj):
         return obj.Academic_year.name
    def get_term_name(self,obj):
         return obj.term.name
    
class StudentBillSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    student_admission_number=serializers.SerializerMethodField()
    level_name =serializers.SerializerMethodField()
    bill_name = serializers.SerializerMethodField()
    class Meta:
        model = StudentBill
        fields = '__all__'
    def get_student_name (self,obj):
         return obj.student.name
    def get_student_admission_number(self, obj):
         return obj.student.admission_number
    def get_level_name(self,obj):
             level_name = obj.student.current_level
             if level_name.stream:
                    return f"{level_name.name} {level_name.stream}"
             else:
                    return level_name.name
    def get_bill_name(self,obj):
         return obj.bill.name
    

class TransactionSerializer(serializers.ModelSerializer):
    head_name = serializers.SerializerMethodField()
    class Meta:
        model = Transaction
        fields = '__all__'
    def get_head_name(self, obj):
         return obj.head.name  


class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ('id','admission_number', 'name')

class SubjectScoreSerializer(serializers.Serializer):
    student = StudentSerializer()
    subjects = serializers.SerializerMethodField()
    total_marks = serializers.IntegerField()

    def get_subjects(self, obj):
        # Extract subject names, scores, and descriptions for the student
        subjects_data = []
        for subject_name, score in obj['subject_scores'].items():
            subjects_data.append({
                'name': subject_name,
                'score': score,
                'percentage': score,  # Assuming score is already in percentage
                'description': self.get_score_description(score),
            })
        return subjects_data

    def get_score_description(self,percentage):
        if 80 <= percentage <= 100:
             return "EE"
        elif 50 <= percentage <= 79:
            return "ME"
        elif 30 <= percentage <= 49:
            return "AE"
        else:
            return "BE"
class ExamResultsSerializer(serializers.ModelSerializer):
        class Meta:
            model = ExamResult
            fields = '__all__'

class ExamQueryStudentsSerializer(serializers.ModelSerializer):
        class Meta:
            model = ExamResult
            fields = ['exam', 'year', 'term', 'level', 'subject']

class GetStudentForMarksSerializer(serializers.ModelSerializer):
        id = serializers.IntegerField()
        class Meta:
            model = Student
            fields = ['admission_number','name', 'id']
           
class SubjectSerializer(serializers.ModelSerializer):
        level_name = serializers.SerializerMethodField()
        class Meta:
            model = Subject
            fields = '__all__'
        def get_level_name(self,obj):
             level_name = obj.level
             if level_name.stream:
                    return f"{level_name.name} {level_name.stream}"
             else:
                    return level_name.name


class NewPaySlipSerializer(serializers.ModelSerializer):
        date = serializers.DateField(source='date_as_date', read_only=True)
        class Meta:
            model = Payslip
            fields = '__all__'

            
class ChangePasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(min_length=8, write_only=True)

class CarryFowardSerializer(serializers.ModelSerializer):
        class Meta:
            model = CarryForward
            fields = '__all__'
class NotificationSerializer(serializers.ModelSerializer):
        sender_name = serializers.SerializerMethodField()
        class Meta:
            model = Notification
            fields = '__all__'
        def get_sender_name(self, obj):
            return obj.sender.first_name +" "+ obj.sender.last_name if obj.sender else 'system'

class AssignedSubjectSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='subject.name', read_only=True)
    subjectIdentityId = serializers.CharField(source='subject.id', read_only=True)
    level_name = serializers.CharField(source='subject.level.name', read_only=True)
    level_id = serializers.CharField(source='subject.level.id', read_only=True)
    level_stream = serializers.CharField(source='subject.level.stream', read_only=True)
    required = serializers.BooleanField(source='subject.required', read_only=True)

    class Meta:
        model = TeacherSubject
        fields = ['id', 'name', 'level_name', 'level_stream', 'required','level_id','subjectIdentityId']

class UserSerializer(serializers.ModelSerializer):
        class Meta:
            model = User
            fields = ['id','email', 'password', 'first_name', 'last_name' ,'school','type','is_active','employee_id', 'phone_number','gross_salary']
            extra_kwargs = {'password': {'required': True , 'write_only': True}}
            


        def validate_email(self, value):
            """
            Check if the email is available.
            """
            if User.objects.filter(email=value).exists():
                raise serializers.ValidationError("This email is already in use.", code='email_in_use')
            return value

        def create(self, validated_data):
            user = User.objects.create_user(**validated_data)
            user.save()
            return user
        


class RegisterTeacherSerializer(serializers.ModelSerializer):
        class Meta:
            model = User
            fields = ['email', 'password', 'first_name', 'last_name' ,'school','type','employee_id', 'phone_number','gross_salary']
            extra_kwargs = {'password': {'required': True}}


        def validate_email(self, value):
            """
            Check if the email is available.
            """
            if User.objects.filter(email=value).exists():
                raise serializers.ValidationError("This email is already in use.", code='email_in_use')
            return value

        def create(self, validated_data):
            user = User.objects.create_user(**validated_data)
            user.set_password(validated_data['password'])
            # user.save()
            return user
        
class RegisterSchoolSerializer(serializers.ModelSerializer):
    class Meta:
        model = School
        fields = '__all__'
        
    def validate(self, data):
        # Custom validation logic
        if not data.get('name') or not data.get('head_teacher') or not data.get('school_email'):
            raise serializers.ValidationError("All fields are required.")
        return data

    def create(self, validated_data):
        # Create a new instance of the model with the validated data
        return School.objects.create(**validated_data)

class RegisterParentSerializer(serializers.ModelSerializer):
        class Meta:
            model = User
            fields = ['email', 'password', 'first_name', 'last_name' ,'school','type','phone_number','gender']
            extra_kwargs = {'email': {'required': False}, 'password': {'required': True}}


        def validate_email(self, value):
            """
            Check if the email is available.
            """
            if User.objects.filter(email=value).exists():
                raise serializers.ValidationError("This email is already in use.", code='email_in_use')
            return value

        def create(self, validated_data):
            user = User.objects.create_user(**validated_data)
            user.set_password(validated_data['password'])
            # user.save()
            return user
        
class RegisterStudentSerializer(serializers.ModelSerializer):
        parent_name = serializers.SerializerMethodField()

        class Meta:
            model = Student
            fields = ['admission_number', 'name', 'parent','parent_name', 'active', 'current_level','curriculum']

        def validate(self, data):
            admission_number = data.get('admission_number')
            school = self.context['request'].user.school.id
            
            if Student.objects.filter(admission_number=admission_number, school=school).exists():
                raise serializers.ValidationError("A student with this admission number already exists in the selected school.")

            return data

        def get_parent_name(self, obj):
            return obj.parent.first_name +" "+ obj.parent.last_name if obj.parent else None
        
        def create(self, validated_data):
            student = Student.objects.create(**validated_data)
            return student

class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

class PasswordResetConfirmSerializer(serializers.Serializer):
    token = serializers.CharField()
    new_password = serializers.CharField()
    
class TeacherSubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeacherSubject
        fields = ['teacher', 'subject']
        
    def create(self, validated_data):
        teacher = validated_data.get('teacher')
        subject = validated_data.get('subject')
        
        # Check if the subject's school matches the school associated with the logged-in user
        if subject.school != self.context['request'].user.school:
            raise serializers.ValidationError("You can only assign subjects from your school.")
        
        # Check if the subject is already assigned to the same teacher
        if TeacherSubject.objects.filter(teacher=teacher, subject=subject).exists():
            raise serializers.ValidationError("This subject is already assigned to the selected teacher.")
        
        # Check if the subject is already assigned to the teacher in the same stream
        if subject.level.stream and TeacherSubject.objects.filter(teacher=teacher, subject=subject, subject__level__stream=subject.level.stream).exists():
            raise serializers.ValidationError("This subject is already assigned to the selected teacher in the same stream.")
        
        # Create the TeacherSubject instance
        assignment = TeacherSubject.objects.create(teacher=teacher, subject=subject)
        
        # Mark the subject as assigned
        subject.assigned = True
        subject.save()
        
        return assignment

from django.db.models import Sum 
class ExamResultCompareSerializer(serializers.ModelSerializer):
    subject_name = serializers.SerializerMethodField()
    school_name = serializers.SerializerMethodField()
    year_name = serializers.SerializerMethodField()
    term_name = serializers.SerializerMethodField()
    exam_name = serializers.SerializerMethodField()
    student_name = serializers.SerializerMethodField()
    level_name = serializers.SerializerMethodField()

    class Meta:
        model = ExamResult
        fields = ['id', 'school', 'exam', 'student', 'subject', 'year', 'term', 'level', 'score', 'grade',
                  'subject_name', 'school_name', 'year_name', 'term_name', 'exam_name', 'student_name', 'level_name']

    def get_subject_name(self, obj):
        return obj.subject.name if obj.subject else ''

    def get_school_name(self, obj):
        return obj.school.name if obj.school else ''

    def get_year_name(self, obj):
        return obj.year.name if obj.year else ''

    def get_term_name(self, obj):
        return obj.term.name if obj.term else ''

    def get_exam_name(self, obj):
        return obj.exam.name if obj.exam else ''

    def get_student_name(self, obj):
        return obj.student.name if obj.student else ''

    def get_level_name(self, obj):
        if obj.level and obj.level.stream:
            return f"{obj.level.name} {obj.level.stream}"
        elif obj.level:
            return obj.level.name
        else:
            return ''

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # Retrieve previous exam result for the same subject and calculate changes
        previous_exam_result = self.get_previous_exam_result(instance)
        if previous_exam_result:
            representation['previous_score'] = previous_exam_result.score
            representation['score_change'] = instance.score - previous_exam_result.score
            representation['percentage_change'] = self.calculate_percentage_change(instance.score, previous_exam_result.score)
        else:
            representation['previous_score'] = None
            representation['score_change'] = None
            representation['percentage_change'] = None
        return representation

    def get_previous_exam_result(self, current_exam_result):
        previous_exam_result = ExamResult.objects.filter(
            student=current_exam_result.student,
            subject=current_exam_result.subject,
            year=current_exam_result.year,
            term=current_exam_result.term,
            level=current_exam_result.level,
            exam__lt=current_exam_result.exam  # Filter exams before the current exam
        ).order_by('-exam').first()
        return previous_exam_result

    def calculate_percentage_change(self, current_score, previous_score):
        if previous_score == 0:
            return None
        return ((current_score - previous_score) / previous_score) * 100

class ExamPerformanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamResult
        fields = ['exam', 'total_marks']

class StudentSubjectStatsSerializer(serializers.ModelSerializer):
    subjects = ExamResultCompareSerializer(many=True, read_only=True)
    total_marks = serializers.SerializerMethodField()
    exam_performance = serializers.SerializerMethodField()

    class Meta:
        model = Subject
        fields = ['id', 'name', 'subjects', 'total_marks', 'exam_performance']

    def get_total_marks(self, obj):
        total_marks = 0
        for subject in obj.subjects:
            total_marks += subject['score']
        return total_marks