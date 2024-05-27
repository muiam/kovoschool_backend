from datetime import timedelta, timezone, datetime
from django.db import models
from django.db.models import Q,Sum
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from coreapp.utils.manager import CustomUserManager
from django.utils import timezone as payslipTime
# Create your models here.


class School (models.Model):
    name = models.CharField(max_length = 100 , null=False , blank=False)
    head_teacher = models.CharField(max_length = 100, null=False , blank=False)
    school_email = models.EmailField(max_length=30, null=False , blank=False)
    population = models.CharField(max_length=10 , null=True , blank=True)
    curriculum = models.CharField(max_length = 100 , null=True , blank=True)
    county = models.CharField(max_length=90 , null=True , blank=True)
    constituency = models.CharField(max_length=90 , null=True , blank=True)
    ward = models.CharField(max_length=90 , null= True , blank=True)
    active = models.BooleanField(default =False)
    note = models.TextField(null=True , blank=True)

    def __str__(self) -> str:
        return self.name

class User(AbstractUser):
    username = None
    email = models.EmailField(unique =True , blank=True , null=True)
    first_name = models.CharField(max_length=30)
    second_name = models.CharField(max_length=20)
    employee_id= models.CharField(max_length=50)
    phone_number= models.CharField(max_length=50)
    gross_salary= models.CharField(max_length=50)
    gender = models.CharField(max_length=50)
    county = models.CharField(max_length=90 , null=True , blank=True)
    constituency = models.CharField(max_length=90 , null=True , blank=True)
    ward = models.CharField(max_length=90 , null= True , blank=True)

    type_Choices = (
        ('headTeacher' , 'headTeacher'),
        ('teacher', 'teacher'),
        ('parent' ,'parent'),
        ('accountant', 'accountant'),
         ('other', 'other')

    )
    type = models.CharField(max_length =20 ,choices =type_Choices, default= "teacher")
    school = models.ForeignKey(School, on_delete=models.CASCADE , null =True , blank =True)
    reset_password_token = models.CharField(max_length=255, blank=True, null=True)
    reset_password_token_created_at = models.DateTimeField(blank=True, null=True)

    objects = CustomUserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS =[]

    def __str__(self):
        if self.first_name and self.last_name and self.school : 
            return f"{self.first_name} {self.last_name} {self.school.name}"
        else :
            return f'{self.id}'

class Curriculum(models.Model):
     name = models.CharField(max_length=30 , null=True , blank=True)


class Level(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    name = models.IntegerField()
    stream = models.CharField(max_length = 50, null=True , blank = True)
    def __str__(self):
        if self.stream : 
            return f"{self.name} {self.stream}"
        else :
            return f'{self.name}'

class Subject(models.Model):
    name =models.CharField(max_length = 50)
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    required = models.BooleanField(default=True)
    level = models.ForeignKey(Level, on_delete = models.CASCADE)
    assigned=models.BooleanField(default =False)

    def __str__(self):
            return f'{self.name}'
    
class TeacherSubject(models.Model):
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to=Q(type='teacher'))
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True, editable=False, null=False, blank=False)

    class Meta:
        unique_together = ('teacher' , 'subject')

    def __str__(self):
        return f'{self.subject.id}'
     



class AcademicYear(models.Model):
    name = models.CharField(max_length=50)
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    start_date = models.DateField(default=datetime.now)  # Set the default to the current date
    duration_days = models.IntegerField()  # Field for specifying the duration in days
    end_date = models.DateField(null=True , blank=True)  # Add field for end date
    active = models.BooleanField(default=True)
    current =models.BooleanField(default=True)


    def __str__(self):
        return f'{self.name}--{self.school.name}'

    def calculate_end_date(self):
        return self.start_date + timedelta(days=self.duration_days)
    def save(self, *args, **kwargs):
        # Calculate end date based on start date and duration
        self.end_date = self.calculate_end_date()
        super().save(*args, **kwargs)
    
class Term (models.Model):
    name = models.CharField(max_length = 20)
    year = models.ForeignKey(AcademicYear , on_delete = models.CASCADE)
    status = models.BooleanField(default = True)
    current =models.BooleanField(default=True)
    def __str__(self):
            return f'{self.name}'
    
class Student(models.Model):
    admission_number = models.CharField(max_length = 20)
    name = models.CharField(max_length= 100 , null =True ,blank = True)
    gender = models.CharField(max_length=30 , null=True , blank=True)
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    parent = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'type': 'parent'})
    county = models.CharField(max_length=90 , null=True , blank=True)
    constituency = models.CharField(max_length=90 , null=True , blank=True)
    ward = models.CharField(max_length=90 , null= True , blank=True)
    active = models.BooleanField(default=True)
    curriculum = models.ForeignKey(Curriculum , on_delete=models.CharField )
    academic_year = models.ForeignKey(AcademicYear , on_delete=models.DO_NOTHING , null=True , blank=True)
    term = models.ForeignKey(Term , on_delete=models.DO_NOTHING, null=True ,blank=True)    
    current_level = models.ForeignKey(Level, on_delete = models.CASCADE)


    class Meta:
         unique_together = ('admission_number', 'school')

    def __str__(self):
        return f'{self.admission_number}'
    
class Fee(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    level = models.ForeignKey(Level, on_delete=models.CASCADE)
    term = models.ForeignKey(Term, on_delete=models.CASCADE)
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    class Meta:
        unique_together = ('school' , 'level' , 'term' , 'academic_year')

    def __str__(self):
            return f'{self.level.name} {self.term.name} {self.term.name} {self.academic_year.name} {self.amount}'
class FeeBalance(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid = models.BooleanField(default=False)
    def __str__(self):
        return f'{self.student} - {self.academic_year} --{self.amount}'

class FeePayment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    fee = models.ForeignKey(Fee, on_delete=models.CASCADE)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    date_paid = models.DateField(auto_now_add=True)
    receipt_number = models.CharField(max_length=15, null=False, unique=True)
    level = models.ForeignKey(Level, on_delete=models.CASCADE)  # Assuming you have a Level model
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)  # Assuming you have an AcademicYear model
    term = models.ForeignKey(Term, on_delete=models.CASCADE)  # Assuming you have a Term model
    overpay =models.DecimalField(max_digits=10, default=0,decimal_places=2)

class CarryForward(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date_created = models.DateTimeField(auto_now_add=True)


class Exam(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    name = models.CharField(max_length = 20)
    year = models.ForeignKey(AcademicYear, on_delete = models.CASCADE)
    term = models.ForeignKey(Term, on_delete = models.CASCADE)
    published = models.BooleanField(default=False)

    def __str__(self):
            return f'{self.name}'

class ExamResult(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    exam = models.ForeignKey(Exam, on_delete = models.CASCADE)
    student = models.ForeignKey(Student, on_delete = models.CASCADE)
    subject = models.ForeignKey(Subject , on_delete = models.CASCADE)
    year = models.ForeignKey(AcademicYear , on_delete = models.CASCADE)
    term = models.ForeignKey(Term , on_delete = models.CASCADE)
    level = models.ForeignKey(Level , on_delete = models.CASCADE)
    score = models.IntegerField()
    grade = models.CharField(max_length =2 , default ="E")
    def __str__(self):
            return f'{self.student.name ,self.school.name , self.exam.name, self.year.name, self.term.name,self.level.name,self.subject.name,self.score,self.grade}'
class Year(models.Model):
     name = models.CharField(max_length= 30 , null= False)
     def __str__(self):
            return self.name
class Month (models.Model):
     name =models.CharField(max_length= 30 , null= False)
     def __str__(self):
        return self.name
     
class Payslip(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE, null=True, blank=True)
    employee = models.ForeignKey(User, on_delete=models.CASCADE , to_field= 'email' )
    employeeID = models.CharField(max_length=50 , null=True , blank=True)
    date = models.DateTimeField(default=payslipTime.now)
    year = models.ForeignKey(Year, on_delete=models.CASCADE)
    month = models.ForeignKey(Month , on_delete=models.CASCADE)
    gross_salary = models.DecimalField(max_digits=10, decimal_places=2)
    total_allowances = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    social_security = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    health_insurance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    other_deductions = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    affordable_housing = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    advance_salary = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    net_salary = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_deductions = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    paid = models.BooleanField(default= False)

    class Meta:
         unique_together = ('employee', 'year', 'month')
    #send an email here
    @property
    def date_as_date(self):
        return self.date.date()

    # def __str__(self):
    #   
    #   return f"{self.employee.email}'s Payslip for {self.month}"

class TransactionItem(models.Model):
       name = models.CharField(max_length=30)
       type = models.CharField(max_length=20)


class Transaction(models.Model):
    school = models.ForeignKey(School ,on_delete=models.CASCADE)
    receipt_number = models.CharField(max_length=30 , default='YU87690230')
    description = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    type = models.CharField(max_length=20)
    head= models.ForeignKey(TransactionItem , on_delete=models.DO_NOTHING)
    date = models.DateField(auto_now_add=True)

class Week(models.Model):
     school = models.ForeignKey(School, on_delete=models.CASCADE)
     name = models.CharField(max_length=30)

class Report(models.Model):
     student = models.ForeignKey(Student, on_delete=models.CASCADE)
     school = models.ForeignKey(School, on_delete=models.CASCADE)
     subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
     level = models.ForeignKey(Level, on_delete=models.CASCADE)
     week = models.ForeignKey(Week , on_delete=models.CASCADE)
     teacher = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to=Q(type='teacher'))
     academic_progress = models.TextField(null=True, blank=True)
     behavior_effort = models.TextField(null=True, blank=True)
     goals_achieved = models.TextField(null=True, blank=True)
     improvement_areas = models.TextField(null=True, blank=True)
     comments = models.TextField(null=True, blank=True)
     next_week_goals = models.TextField(null=True, blank=True)
     date = models.DateField(auto_now_add=True)

     class Meta:
         unique_together = ('student', 'school', 'subject', 'level', 'week')

class Notification(models.Model):
     recipient = models.ForeignKey(User, on_delete=models.CASCADE , related_name='received_notifications')
     sender = models.ForeignKey(User , on_delete=models.CASCADE , default=None, null=True, related_name='send_notifications')
     school = models.ForeignKey(School , on_delete=models.CASCADE)
     title = models.CharField(max_length=100 , default="This is an unititled notication" )
     message = models.TextField()
     time = models.DateTimeField(auto_now_add=True)
     is_read = models.BooleanField(default=False)

class Bill(models.Model):
     name = models.CharField(max_length=100)
     Academic_year = models.ForeignKey(AcademicYear , on_delete=models.CASCADE)
     term = models.ForeignKey(Term , on_delete=models.CASCADE)
     school = models.ForeignKey(School , on_delete=models.CASCADE)
     amount = models.DecimalField(max_digits=10, decimal_places=2 , default=0)
     comment = models.TextField(null=True , blank=True)

class StudentBill(models.Model):
     student = models.ForeignKey(Student, on_delete=models.CASCADE)
     bill = models.ForeignKey(Bill, on_delete=models.CASCADE)
     amount = models.DecimalField(max_digits=10, decimal_places=2)
     comment = models.TextField(null=True , blank=True)
     
     
class BillPayment(models.Model):
     student_bill = models.ForeignKey(StudentBill, on_delete=models.CASCADE)
     amount = models.DecimalField(max_digits=10, decimal_places=2)
     receipt_number = models.CharField(max_length=100)
     payment_date = models.DateField(auto_now_add=True)


class MpesaPayments (models.Model):
     checkout_request_id = models.CharField(max_length=30)
     result_code = models.IntegerField()
     result_desc = models.CharField(max_length=30)
     amount = models.DecimalField(max_digits=10 , decimal_places=2)
     transaction_id = models.CharField(max_length=30)
     user_phone_number = models.CharField(max_length=15)

    
     
   