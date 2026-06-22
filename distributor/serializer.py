from rest_framework import serializers
from .models import Employee,Task,AssignmentHistory

class EmployeeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Employee
        fields = '__all__'

class TaskSerializer(serializers.ModelSerializer):

    class Meta:
        model = Task
        fields = "__all__"

class AssignmentHistorySerializer(serializers.ModelSerializer):

    class Meta:
        model = AssignmentHistory
        fields = "__all__"