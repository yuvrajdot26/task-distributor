from django.urls import path,include
from . import views
urlpatterns = [
    path("",views.dashboard,name='dashboard'),
    path("employees/",views.employees,name='employees'),
    path("tasks/",views.tasks,name='tasks'),
    path("history/",views.history,name='history'),
    path("employees/create/",views.employee_create,name='employee_create'),
    path("employees/<int:pk>/edit/",views.employee_edit,name='employee_edit'),
    path("employees/<int:pk>/delete/",views.employee_delete,name='employee_delete'),
    path("tasks/create/",views.task_create,name='task_create'),
    # path("tasks/<int:pk>/edit/",views.task_edit,name='task_edit'),
    path("tasks/<int:pk>/delete/",views.task_delete,name='task_delete'),
    path("tasks/<int:pk>/assign/",views.assign_task,name='task_assign'),
    path("tasks/<int:pk>/complete/",views.complete_task,name='task_complete'),
    path("history/<int:pk>/delete/",views.history_delete,name='history_delete'),
    path("workload/",views.workload,name='workload'),
    path("login/",views.login_view,name='login'),
    path("logout/",views.logout_view,name='logout'),

]
