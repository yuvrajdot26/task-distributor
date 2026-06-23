import json
from django.shortcuts import render,redirect,get_object_or_404
from distributor.models import Employee,Task,AssignmentHistory
from django.utils import timezone
from django.contrib.auth import login,logout,authenticate
from django.contrib.auth.decorators import login_required
from django.db.models import Q,F
from django.core.paginator import Paginator

MAX_TASKS_PER_EMPLOYEE = 5  # shared threshold used by dashboard + assignment logic

# Create your views here.
@login_required
def dashboard(request):

    context = {
    "total_employees": Employee.objects.count(),
    "available_employees": Employee.objects.filter(
        current_task_count__lt=MAX_TASKS_PER_EMPLOYEE
    ).count(),

    "total_tasks": Task.objects.count(),

    "pending_tasks": Task.objects.filter(
        status=Task.StatusChoice.PENDING
    ).count(),

    "in_progress_tasks": Task.objects.filter(
        status=Task.StatusChoice.IN_PROGRESS
    ).count(),

    "completed_tasks": Task.objects.filter(
        status=Task.StatusChoice.COMPLETED
    ).count(),

    "recent_tasks": Task.objects.order_by(
        "-created_at"
    )[:5],

    "top_employees": Employee.objects.order_by(
        "-current_task_count"
    )[:5],
}

    context["task_chart_labels"] = json.dumps([
        "Pending",
        "In Progress",
        "Completed"
    ])

    context["task_chart_data"] = json.dumps([
        context["pending_tasks"],
        context["in_progress_tasks"],
        context["completed_tasks"]
    ])

    context["employee_chart_labels"] = json.dumps([
        emp.full_name for emp in context["top_employees"]
    ])

    context["employee_chart_data"] = json.dumps([
        emp.current_task_count for emp in context["top_employees"]
    ])
    
    return render(request,"frontend/dashboard.html",context)

@login_required
def employees(request):

    # explicit ordering so pagination is stable across requests
    employees = Employee.objects.all().order_by("id")

    query = request.GET.get("q")

    if query:
        employees=employees.filter(
            Q(full_name__icontains=query) | Q(email__icontains=query)
        )

    paginator = Paginator(employees,12)
    page_number=request.GET.get("page")
    employees=paginator.get_page(page_number)

    context = {
        "employees":employees
    }

    return render(request,"frontend/employees.html",context)

@login_required
def tasks(request):

    # explicit ordering so pagination is stable across requests
    tasks = Task.objects.all().order_by("-created_at")

    query = request.GET.get("q")
    status_filter = request.GET.get("status")
    skill_filter = request.GET.get("skill")

    if query:
        tasks = tasks.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )

    if status_filter:
        tasks = tasks.filter(
            status=status_filter
        )

    if skill_filter:
        tasks=tasks.filter(
            required_skills=skill_filter
        )

    paginator = Paginator(tasks,12)
    page_number=request.GET.get("page")
    tasks=paginator.get_page(page_number)

    context = {"tasks":tasks}

    return render(request,"frontend/tasks.html",context)

@login_required
def history(request):

    # explicit ordering so pagination is stable across requests
    history_records = AssignmentHistory.objects.all().order_by("-assigned_at")

    query = request.GET.get("q")
    if query:
        history_records=history_records.filter(
            # NOTE: was "Employee__full_name__icontains" (capital E) — the FK
            # field is named "employee" (lowercase), so this used to raise
            # FieldError on every search that reached this branch.
            Q(task__title__icontains=query) | Q(employee__full_name__icontains=query)
        )

    paginator = Paginator(history_records,12)
    page_number=request.GET.get("page")
    history_records=paginator.get_page(page_number)

    context = {"history_records":history_records}

    return render(request,"frontend/history.html",context)
@login_required
def employee_create(request):
    
    if request.method == "POST":

        Employee.objects.create(
            full_name=request.POST.get("full_name"),
            email=request.POST.get("email"),
            skills=request.POST.get("skills"),
            experience_level=request.POST.get("experience_level"),
            
        )

        return redirect("/employees/")
    return render(request,"frontend/employee_form.html")
@login_required
def employee_edit(request,pk):
    employee = get_object_or_404(Employee,id=pk) 

    if request.method == "POST":
        employee.full_name=request.POST.get("full_name")
        employee.email=request.POST.get("email")
        employee.skills=request.POST.get("skills")
        employee.experience_level=request.POST.get("experience_level")

        employee.save()

        return redirect("/employees/")
    return render(request,"frontend/employee_edit.html",{"employee":employee})
@login_required
def employee_delete(request,pk):

    employee = get_object_or_404(Employee,id=pk)

    employee.delete()

    return redirect("/employees/")

@login_required
def task_create(request):

    if request.method == "POST":
        Task.objects.create(
            title=request.POST.get("title"),
            description=request.POST.get("description"),
            priority=request.POST.get("priority"),
            required_skills=request.POST.get("required_skills"),
            estimate_hours=request.POST.get("estimate_hours"),
            deadline=request.POST.get("deadline")
        )

        return redirect("/tasks/")
    return render(request,"frontend/task_create.html") 
@login_required
def task_edit(request,pk):

    task = get_object_or_404(Task,id=pk)

    if request.method=="POST":
        task.title=request.POST.get("title")
        task.description=request.POST.get("description")
        task.priority=request.POST.get("priority")
        task.required_skills=request.POST.get("required_skills")
        task.estimate_hours=request.POST.get("estimate_hours")
        task.deadline=request.POST.get("deadline")

        task.save()

        return redirect("/tasks/")
    return render(request,"frontend/task_edit.html",{"task":task})
@login_required
def task_delete(request,pk):

    task = get_object_or_404(Task,id=pk)

    task.delete()

    return redirect("/tasks/")

@login_required
def assign_task(request, pk):

    # was Task.objects.get(id=pk) — raised an unhandled 500 on a bad/stale id
    task = get_object_or_404(Task, id=pk)

    if task.assign_to:
        return redirect("/tasks/")

    # only employees under the per-person task cap
    employees = Employee.objects.filter(
        skills=task.required_skills,
        current_task_count__lt=MAX_TASKS_PER_EMPLOYEE
    ).order_by("current_task_count", "id")

    employee = employees.first()

    if employee:

        task.assign_to = employee
        task.status = Task.StatusChoice.IN_PROGRESS
        task.save()

        Employee.objects.filter(id=employee.id).update(
        current_task_count=F('current_task_count') + 1
        )

        AssignmentHistory.objects.create(
            task=task,
            employee=employee
        )

    return redirect("/tasks/")

@login_required
def complete_task(request, pk):

    # was Task.objects.get(id=pk) — raised an unhandled 500 on a bad/stale id
    task = get_object_or_404(Task, id=pk)

    if task.status == Task.StatusChoice.COMPLETED:
        return redirect("/tasks/")

    employee = task.assign_to

    task.status = Task.StatusChoice.COMPLETED
    task.save()

    if employee:

        Employee.objects.filter(id=employee.id).update(
            current_task_count=F('current_task_count') - 1
        )

        employee.refresh_from_db()

        if employee.current_task_count < 0:
            employee.current_task_count = 0
            employee.save()

        history = AssignmentHistory.objects.filter(
            task=task,
            employee=employee
        ).last()

        if history:
            history.complete_at = timezone.now()
            history.save()

    return redirect("/tasks/")

@login_required
def history_delete(request,pk):
    # was AssignmentHistory.objects.get(id=pk) — raised an unhandled 500 on a bad/stale id
    history = get_object_or_404(AssignmentHistory, id=pk)

    history.delete()

    return redirect("/history/")

@login_required
def workload(request):

    employees = Employee.objects.all().order_by("id")

    return render(
        request,
        "frontend/workload.html",
        {"employees": employees}
    )

def login_view(request):

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user:
            login(request,user)

            return redirect("/")
        
        return render (
            request,
            "frontend/login.html",
            {"error":"Invalid credentials"}
        )
    return render(request,"frontend/login.html")

def logout_view(request):

    logout(request)

    return redirect("/login/")