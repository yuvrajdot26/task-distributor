from django.db import models

# Create your models here.

class Employee(models.Model):
    class SkillChoices(models.TextChoices):
        BACKEND = "BACKEND", "Backend"
        FRONTEND = "FRONTEND", "Frontend"
        TESTING = "TESTING", "Testing"
        DEVOPS = "DEVOPS", "DevOps"
    
    class ExperienceChoice(models.TextChoices):
        JUNIOR = "Junior","Junior"
        MID = "Mid","Mid"
        SENIOR = "Senior","Senior"

    full_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    skills = models.CharField(max_length=30,choices=SkillChoices.choices)
    experience_level = models.CharField(max_length=10,choices=ExperienceChoice.choices)
    availbility = models.BooleanField(default=True)
    current_task_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.full_name
    
class Task(models.Model):
    class PriorityChoices(models.TextChoices):
        LOW="LOW","Low"
        MEDIUM="MEDIUM","Medium"
        HIGH="HIGH","High"

    class StatusChoice(models.TextChoices):
        PENDING = "PENDING","Pending"
        IN_PROGRESS = "IN_PROGRESS","In_Progress"
        COMPLETED = "COMPLETED","Completed"
    
    title = models.CharField(max_length=200)

    description = models.TextField()
    
    priority = models.CharField(
        max_length=20,
        choices=PriorityChoices.choices,
        default=PriorityChoices.MEDIUM
        )
    
    required_skills = models.CharField(
        max_length=30,
        choices=Employee.SkillChoices.choices
    )
    
    estimate_hours = models.PositiveIntegerField()

    status = models.CharField(
        max_length=30,
        choices=StatusChoice.choices,
        default=StatusChoice.PENDING
    )

    assign_to = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tasks'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    deadline = models.DateTimeField(
        null=True,
        blank=True
    )

    def __str__(self):
        return self.title
    
class AssignmentHistory(models.Model):

    class Meta:
        verbose_name = "Assignment History"
        verbose_name_plural = "Assignment Histories"

    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='assignment_history'
    )

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='assignment_history'
    )

    assigned_at = models.DateTimeField(auto_now_add=True)

    complete_at = models.DateTimeField(null=True,blank=True)


    def __str__(self):
        return f"{self.task.title}-->{self.employee.full_name}"