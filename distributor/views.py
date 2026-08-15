from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from django.utils import timezone
from distributor.services.ai_task_analyzer import analyze_task

# from django.shortcuts import render
from .serializer import EmployeeSerializer,TaskSerializer,AssignmentHistorySerializer
from .models import Employee,Task,AssignmentHistory
# Create your views here.

class EmployeeListCreateView(APIView):

    def get(self,request):
        
        employee = Employee.objects.all()
        search = request.GET.get("search")
        skill = request.GET.get("skill")

        if search:
            employee = employee.filter(
                full_name__icontains=search
            )
        
        if skill:
            employee=employee.filter(
                skills = skill
            )

        serializer = EmployeeSerializer(
            employee,
            many = True
        )

        return Response(serializer.data)
    
    def post(self,request):

        serializer = EmployeeSerializer(
            data = request.data
        )

        if serializer.is_valid():
            serializer.save()
        
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        
class EmployeeDetailView(APIView):

    def get_object(self,pk):

        try :
            return Employee.objects.get(id=pk)
        except Employee.DoesNotExist:
            return None

    def get(self,request,pk):

        employee = self.get_object(pk)
        
        if not employee:
            return Response(
                {"error":"Employee not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = EmployeeSerializer(employee)
        return Response (serializer.data)
    
    def patch(self,request,pk):

        employee = self.get_object(pk)

        serializer = EmployeeSerializer(
            employee,
            data = request.data,
            partial = True
        )

        if serializer.is_valid():
            serializer.save()

            return Response(
                serializer.data,
            )
        
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
    
    def delete(self,request,pk):

        employee = self.get_object(pk)

        if not employee:
            return Response(
                {"error":"Nothing To Delete"},
                status=status.HTTP_404_NOT_FOUND
            )
        employee.delete()
        return Response(
            {"message":"Deleted Successfully"},
            status=status.HTTP_204_NO_CONTENT
        )
    
class TaskListView(APIView):

    def get(self,request):

        task = Task.objects.all()

        status_filter = request.GET.get("status")
        priority_filter = request.GET.get("priority")
        assign_filter = request.GET.get("assigned")

        if status_filter:
            task = task.filter(
                status = status_filter
            )
        if priority_filter:
            task = task.filter(
                priority = priority_filter 
            )
        if assign_filter=="true":
            task = task.filter(
                assign_to__isnull = False
            )
        elif assign_filter=="false":
            task = task.filter(
                assign_to__isnull = True
            )

        serializer = TaskSerializer(
            task,
            many = True
        )
        
        return Response(serializer.data)
    
    def post(self,request):

        data = request.data.copy()
        title = data.get("title")
        description = data.get("description")

        if not title or not description:
            return Response(
            {"error":"Title and description is required"},
            status=status.HTTP_400_BAD_REQUEST)

        try :
            ai_result = analyze_task(title,description)
        except Exception as e :
            return Response(
                {
                 "error":"AI analysis failed",
                 "details":str(e)   
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        data["required_skills"] = ai_result["required_skills"]
        data["priority"] = ai_result["priority"]
        data["estimate_hours"] = ai_result["estimate_hours"]

        serializer = TaskSerializer(
            data=data
        )
        if serializer.is_valid():
            serializer.save()

            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
    
class TaskDetailView(APIView):

    def get_object(self,pk):

        try:
            return Task.objects.get(id=pk)
        except Task.DoesNotExist:
            return None
        
    def get(self,request,pk):

        task = self.get_object(pk)

        if not task:
            return Response(
                {"error":"Task Dosen't Exist"},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = TaskSerializer(task)
        return Response(serializer.data)
    
    def patch(self,request,pk):

        task = self.get_object(pk)

        serializer = TaskSerializer(
            task,
            data = request.data,
            partial = True
        )

        if serializer.is_valid():
            serializer.save()

            return Response(serializer.data)
        
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
    
    def delete(self, request , pk):

        task = self.get_object(pk)

        if not task:
            return Response(
                {"error":"Nothing To Delete"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        task.delete()
        return Response(
            {"message":"Deleted Successfully"},
            status=status.HTTP_204_NO_CONTENT
        )

class AutoAssignTaskView(APIView):
    
    def post(self,request,pk,):
        
        try:
            task = Task.objects.get(id=pk)
        
        except Task.DoesNotExist:
            return Response(
                {"error":"Task not found"},
                status=status.HTTP_404_NOT_FOUND
            )
       
        if task.status == Task.StatusChoice.COMPLETED:
            return Response(
                {"error": "Completed tasks cannot be assigned"},
                status=status.HTTP_400_BAD_REQUEST
            )
        if task.assign_to:

            return Response(
                {"error":"Task Already Assigned"},
                status=status.HTTP_400_BAD_REQUEST
            )
        MAX_TASKS=5
        employee = Employee.objects.filter(
            skills = task.required_skills,
            availbility = True,
            current_task_count__lt=MAX_TASKS
        ).order_by('current_task_count')

        best_employee = employee.first()

        if not best_employee:
            return Response(
                {"message":"No suitable employee exists"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        task.assign_to = best_employee
        task.status = Task.StatusChoice.IN_PROGRESS
        task.save()

        best_employee.current_task_count+=1
        best_employee.save()

        AssignmentHistory.objects.create(
            task = task,
            employee = best_employee
        )

        return Response(
            {
            "message":"Task Assigned",
            "employee": best_employee.full_name 
            },
            status=status.HTTP_202_ACCEPTED
        )

class AssignmentHistoryView(APIView):

    def get(self,request):

        history = AssignmentHistory.objects.order_by("-assigned_at")

        serializer = AssignmentHistorySerializer(
            history,
            many = True
        )

        return Response(serializer.data)

class AnalyticsView(APIView):

    def get(self,request):

        data = {
            "total_employees" : Employee.objects.count(),
            "available_employees":Employee.objects.filter(availbility=True).count(),
            "total_tasks": Task.objects.count(),
            "pending_tasks": Task.objects.filter(status=Task.StatusChoice.PENDING).count(),
            "in-progress_task":Task.objects.filter(status=Task.StatusChoice.IN_PROGRESS).count(),
            "completed_task":Task.objects.filter(status=Task.StatusChoice.COMPLETED).count()
        }

        return Response(data)   
    
class BusiestEmployeeView(APIView):

    def get(self,request):

        employee = Employee.objects.order_by(
            "-current_task_count",
            "full_name"
        )[:5]

        data = []

        for i in employee:
            data.append({
                "id":i.id,
                "name" : i.full_name,
                "task_count":i.current_task_count
            })
        
        return Response(data)
    
class CompletedTaskView(APIView):

    def post(self,request,pk):

        try :
            task=Task.objects.get(id=pk)
        except Task.DoesNotExist:
            return Response(
                {"error":"No Task Found"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if task.status == task.StatusChoice.COMPLETED:

            return Response(
                {"message":"Task Already Completed "},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not task.assign_to:
            return Response(
                {"error": "Task is not assigned"},
                status=status.HTTP_400_BAD_REQUEST
            )

        employee = task.assign_to

        if employee:

            if employee.current_task_count > 0:
                employee.current_task_count-=1
                employee.save()

        task.status = Task.StatusChoice.COMPLETED
        task.save()

        history = AssignmentHistory.objects.filter(
            task=task,
            employee=employee
        ).last()

        if history:
            history.complete_at = timezone.now()
            history.save()
            print("Updated:", history.id, history.complete_at)
        else:
            print("History NOT FOUND")
        return Response(
            {"message":"Task completed successfully"}
        )
    
class WorkloadDashboardView(APIView):

    def get(self,request):

        employee = Employee.objects.all()

        data = []

        for i in employee:
            data.append({
                "id":i.id,
                "name":i.full_name,
                "active_task":i.current_task_count,
                 "available":i.availbility
            })

        return Response(data)