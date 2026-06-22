from django.contrib import admin
from .models import Employee,Task,AssignmentHistory
# Register your models here.
admin.site.register(Employee)
admin.site.register(Task)
admin.site.register(AssignmentHistory)