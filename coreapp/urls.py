from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('actions/teacher' , views.RegisterTeacher.as_view()),
    path('actions/parent' , views.RegisterParent.as_view()),
    path('actions/student',views.RegisterStudent.as_view()),
    path('actions/student/all',views.get_my_school_students_all),
    path('actions/student/level/<int:level>',views.get_my_school_students),
    path('actions/subject/level/<int:level>' , views.get_my_subject_per_level),
    path('actions/subject' , views.Subjects.as_view()),
    path('actions/assignSubject' ,views.AssignSubject.as_view()),
    path('actions/free/subjects', views.FreeSubjects.as_view()),
    path('actions/my/student/level/<int:level>',views.get_my_kid),
    path('actions/my/student/',views.get_my_kid),
    path('actions/all/my/students', views.get_all_my_kid),
    path('actions/all/school/staff/',views.all_school_members),
    path('actions/stats/all/members/count' , views.get_users_count),
    path('actions/stats/all/teacher/items' , views.get_teacher_stats),
    path('actions/all/financials/items/revenue' ,views.get_revenue_items ),
    path('actions/all/financials/items/expense' , views.get_expenses_items),
    path('actions/school' , views.Our_school.as_view()),
   

   
   
    #token
    path('auth/token/', views.MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    #register
    path('auth/logout' , views.LogoutView.as_view()),
    path('teachers/search/', views.searchTeachers, name='search_teachers'),
    path('parents/search/', views.searchParents, name='search_Parents'),
    path('actions/levels',views.Levels.as_view() ),
    path('actions/allYears' , views.AcademicYears.as_view()),
    path('actions/allTerms', views.Terms.as_view()),
    path('actions/allExams', views.Exams.as_view()),
    path("actions/fetch/exam/students", views.StudentsMarksFetch.as_view()),
    #teacher subjects
    path('teacher/mysubjects/', views.TeacherSubjects.as_view(), name='teacher_subjects'),
    path('teacher/enter/marks', views.BulkInsertMarksView.as_view()),
    path('exams/rank_students/<int:year_id>/<int:term_id>/<int:exam_id>/<int:level_id>/', views.RankStudentsAPIView.as_view()),
    path('exams/exam_stats/<int:year_id>/<int:term_id>/<int:exam_id>/<int:level_id>/', views.calculate_average_percentage),
    path('exams/subject_stats/<int:year_id>/<int:term_id>/<int:exam_id>/<int:level_id>/', views.find_most_improved_students),
    path('exams/subject_drop_stats/<int:year_id>/<int:term_id>/<int:exam_id>/<int:level_id>/', views.find_least_improved_students),
    path('exam-results/compare/<int:year_id>/<int:term_id>/<int:exam_id>/<int:level_id>/<int:student_id>/', 
         views.find_student_scores, name='find-student-scores'),

    path('exam-results/academic/year/recent/analysis/<str:student_id>', views.get_my_learner_year_achievement),
    path('exam-results/academic/year/recent/analysis/default/student', views.get_my_learner_year_achievement),

    path('students/level/<int:level_id>', views.get_students_per_level),
    path('all/financial/years', views.get_year),
    path('all/financial/months', views.get_month),
    path('all/financial/payrolls/<int:year>/<int:month>', views.Payroll.as_view()),
    path('all/financial/employees', views.all_employees),
    path('all/financial/employees/<str:id>', views.employee),
    path('all/financial/payrolls/new', views.NewPayslip.as_view()),
    path('all/financial/my/payslips/', views.my_payslip),
    path('all/financial/my/payslips/<int:year>/', views.my_payslip),
    path('all/financial/my/payslip/<int:payslip>/', views.my_single_payslip),
    path('all/financial/our/school/fee', views.all_school_fees),
    path('all/financial/our/school/fee/<int:year>/', views.all_school_fees),
    path('all/financial/our/school/fee/<int:year>/<str:term>/', views.all_school_fees),
    path('all/financial/our/school/fee/<int:year>/<str:term>/<str:grade>/', views.all_school_fees),
    path('all/financial/students/fee/unpaid/<str:year_id>/<str:term_id>/<str:level_id>/<str:fee_id>/', views.get_unpaid_fee_students),
    path('all/financial/our/school/fee/overpaid/<str:student>/', views.fetch_student_carry_foward),
    path('all/financial/our/school/generate/receipt/', views.generate_receipt_number),
    path('all/financial/our/school/receive/fee/overpay/', views.fee_payment_over),
    path('all/financial/our/school/receive/fee/direct/', views.fee_payment_direct),
    path('all/financial/our/school/total/wallet', views.calculate_total_carryforward),
    path('all/financial/our/school/fee/paid/list/<str:year_id>/<str:term_id>/<str:level_id>/<str:fee_id>/', views.display_student_balances),
    path('all/financial/our/school/transactions/', views.get_transactions_summary),
    path('all/financial/our/school/transactions/<str:start_date>/<str:end_date>', views.get_transactions_summary),
    path('all/financial/our/school/fee/balances/<int:year>', views.all_get_fee_balances),
    path('all/financial/our/school/fee/balances/<int:year>/<int:level>', views.all_get_fee_balances),
    path('all/financial/our/school/save/revenue' , views.save_revenue),
    path('all/financial/our/school/save/expenditure' , views.save_expenditure),
    path('all/financial/our/school/save/new/fee' , views.get_add_school_fee),
    path('all/financial/our/school/stats/revenues-expenditure/for/year/<int:year>' , views.revenue_vs_expenditure),
    path('all/financial/mykid/fee/statements/<str:year>/<str:term>/<str:fee>/<str:grade>/<str:student>', views.get_my_kid_fee_statements),
    path('all/financials/our/school/ledger/items/stats' , views.calculate_transaction_item_amounts),
    path('all/financials/our/school/ledger/items/stats/<str:start_date>/<str:end_date>' , views.calculate_transaction_item_amounts),
    path('all/financials/our/school/ledger/items/sort/ranges/dates' , views.get_transaction_dates),
    path('all/financials/our/school/bills/' , views.PayableBill.as_view()),
    path('all/financials/our/school/bills/<str:academic_year>/<str:term>' , views.PayableBill.as_view()),
    path('all/financials/our/school/bills/<str:bill>' , views.get_my_school_student_bill),
    path('all/financials/our/school/students/billed/<str:bill>/<str:grade>' , views.StudentBilled.as_view()),
    path('all/financials/our/school/students/billed/<str:bill>' , views.StudentBilled.as_view()),
    path('all/financials/our/school/students/billed/<str:type>/<str:bill>/' , views.StudentBilled.as_view()),
    path('all/financials/our/school/students/pay/bills/<str:billed_id>/<str:student>/<str:amount>' , views.receipt_student_bill),
    path('all/financials/our/school/students/bill/payment/list/<str:bill>/<str:grade>/' , views.get_bill_payment_list),
    path('all/financials/our/school/students/bill/payment/list/<str:bill>/' , views.get_bill_payment_list),
    path('all/financials/our/school/students/bill/payment/statements/<str:bill>/' , views.get_bill_payment_statements),
    path('all/financials/payments/fee/pay/get_access_token', views.get_access_token),
    path('all/financials/payments/fee/pay/stk-push', views.initiate_stk_push),
     path('all/financials/payments/fee/mpesa/callback', views.process_stk_callback),
    


    #others
    path('app/weeks/all-weeks', views.all_weeks) ,
    path('app/weeks/all-weeks-data', views.all_weeks_data) ,
    path('app/weeks/new/week', views.save_current_week) ,
    path('app/student/progress/weekly/reports' , views.StudentReport.as_view()),
    path('app/student/progress/weekly/reports/<int:level>/<int:week>' , views.StudentReport.as_view()),
    path('app/student/progress/weekly/reports/level/<int:level>/' , views.StudentReport.as_view()),
    path('app/student/progress/weekly/reports/week/<int:week>/' , views.StudentReport.as_view()),
    path('app/student/progress/weekly/single/report/<int:id>/' , views.single_report),
    # 
    path('app/student/my/progress/weekly/reports' , views.MyStudentReport.as_view()),
    path('app/student/my/progress/weekly/reports/<int:level>/<int:week>' , views.MyStudentReport.as_view()),
    path('app/student/my/progress/weekly/reports/level/<int:level>/' , views.MyStudentReport.as_view()),
    path('app/student/my/progress/weekly/reports/week/<int:week>/' , views.MyStudentReport.as_view()),
    path('app/student/my/progress/weekly/single/report/details/<int:id>' , views.my_single_report),
    path('app/student/my/progress/weekly/single/report/<int:id>/' , views.single_report),

    #

    path('app/kid/my/progress/weekly/reports' , views.MyKidReport.as_view()),
    path('app/kid/my/progress/weekly/reports/<int:level>/<int:week>' ,views.MyKidReport.as_view()),
    path('app/kid/my/progress/weekly/reports/level/<int:level>/' , views.MyKidReport.as_view()),
    path('app/kid/my/progress/weekly/reports/week/<int:week>/' , views.MyKidReport.as_view()),
    path('app/kid/my/progress/weekly/reports/kid/<int:student>/' , views.MyKidReport.as_view()),
    path('app/kid/my/progress/weekly/single/report/details/<int:id>' , views.my_kid_single_report),
    path('app/kid/my/data/summary' , views.my_kids_data),
    

    path('actions/deactivate/user/' , views.deactivateUser),
    path('actions/pay/payslip/', views.pay_pasyslip),


    #notications
    path('app/notifications/for/users/status/unread/count' , views.get_unread_notifications),
    path('app/notifications/for/users/read/<str:id>' , views.update_unread_notifications),
    path('app/notifications/for/users/create/<str:type>' , views.Notifications.as_view()),
    path('app/notifications/for/users/all/' , views.Notifications.as_view()),
    

    #passwords

    path('reset-password/', views.PasswordResetRequestAPIView.as_view()),
    path('reset-password/confirm/', views.PasswordResetConfirmAPIView.as_view()),
    path('app/auth/change/password' , views.ChangePasswordView.as_view()),

    #curriclulum
    path('app/fetch/curriculum/all' , views.all_curriculum),




]
