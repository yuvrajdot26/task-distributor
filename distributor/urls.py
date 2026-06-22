from django.urls import path

from .views import EmployeeListCreateView,EmployeeDetailView,TaskListView,TaskDetailView,AutoAssignTaskView,AssignmentHistoryView,AnalyticsView,BusiestEmployeeView,CompletedTaskView,WorkloadDashboardView

urlpatterns = [
    path("employees/",EmployeeListCreateView.as_view(),name="Employee_list"),
    path("employees/<int:pk>/",EmployeeDetailView.as_view(),name="Employee_Detail"),
    path("tasks/",TaskListView.as_view(),name="Task_List"),
    path("tasks/<int:pk>/",TaskDetailView.as_view(),name="Task_Detail"),
    path("tasks/<int:pk>/assign/",AutoAssignTaskView.as_view(),name="Auto_assign_task"),
    path("history/",AssignmentHistoryView.as_view(),name="History"),
    path("analytics/",AnalyticsView.as_view(),name="Analytics"),
    path("analytics/busiest/",BusiestEmployeeView.as_view(),name="Analytics-busiest"),
    path("tasks/<int:pk>/complete/",CompletedTaskView.as_view(),name="Complete-Task"),
    path("workload/",WorkloadDashboardView.as_view(),name="Workload-dashboard"),
]
