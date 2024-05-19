from django.contrib import admin
from .models import Bill, BillPayment, Curriculum, MpesaPayments, Notification, School,User,Level,Student,AcademicYear, Term, Exam, ExamResult,Subject,TeacherSubject,Payslip,Year,Month,Fee,FeePayment,CarryForward, Transaction,FeeBalance,Week,Report , TransactionItem,StudentBill
# Register your models here.

admin.site.register(School)
admin.site.register(User)
admin.site.register(Level)
admin.site.register(Student)
admin.site.register(AcademicYear)
admin.site.register(Term)
admin.site.register(Exam)
admin.site.register(ExamResult)
admin.site.register(Subject)
admin.site.register(TeacherSubject)
admin.site.register(Payslip)
admin.site.register(Year)
admin.site.register(Month)
admin.site.register(Fee)
admin.site.register(FeePayment)
admin.site.register(CarryForward)
admin.site.register(Transaction)
admin.site.register(FeeBalance)
admin.site.register(Week)
admin.site.register(Report)
admin.site.register(Notification)
admin.site.register(Curriculum)
admin.site.register(TransactionItem)
admin.site.register(StudentBill)
admin.site.register(Bill)
admin.site.register(BillPayment)
admin.site.register(MpesaPayments)


