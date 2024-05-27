from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import AcademicYear, Fee, FeeBalance, FeePayment, Student, Level
from django.db.models import Sum

@receiver(post_save, sender=AcademicYear)
def close_academic_year(sender, instance, **kwargs):
    if not instance.active:
        # Get the school associated with the closed academic year
        school = instance.school

        # Get all active students of the school
        students = Student.objects.filter(school=school, active=True)
        
        # Promote the students
        for student in students:
            current_level = student.current_level
            next_level = get_next_level(current_level, school)
            if next_level:
                student.current_level = next_level
                try:
                    student.save()
                except Exception as e:
                    print(f"Failed to promote student: {student}. Error: {e}")
            else:
                print("Failed to promote student:", student)

def get_next_level(current_level, school):
    current_level_name = current_level.name
    current_level_number = current_level_name
    current_stream = current_level.stream

    try:
        # Try to get the next level with the same stream as the current level
        if current_stream:
            print(f"Looking for next level with same stream: {current_level_number + 1} {current_stream} at {school}")
            next_level = Level.objects.get(name=current_level_number + 1, stream=current_stream, school=school)
        else:
            # If the current level has no stream, try to get the next level with any stream
            print(f"Current level has no stream, looking for next level with any stream: {current_level_number + 1} at {school}")
            next_level = Level.objects.filter(name=current_level_number + 1, school=school).exclude(stream='').first()
            if not next_level:
                print(f"No next level with any stream found, keeping student in current level: {current_level}")
                return current_level

        if next_level:
            print(f"Next level found: {next_level}")
            return next_level
        else:
            print(f"No next level found, keeping student in current level: {current_level}")
            return current_level
    except Level.DoesNotExist:
        print(f"Current level has no corresponsing level, looking for next level with any stream: {current_level_number + 1} at {school}")
        next_level = Level.objects.filter(name=current_level_number + 1, school=school).exclude(stream='').first()
        if not next_level:
            print(f"No next level with any stream found, keeping student in current level: {current_level}")
            return current_level
        else:
            return next_level