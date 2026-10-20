from django.urls import path
from . import views

app_name = 'shiro'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Project URLs
    path('projects/', views.project_list, name='project_list'),
    path('projects/<int:pk>/', views.project_detail, name='project_detail'),
    path('projects/create/', views.project_create, name='project_create'),
    path('projects/<int:pk>/edit/', views.project_edit, name='project_edit'),
    path('projects/<int:pk>/delete/', views.project_delete, name='project_delete'),
    path('projects/<int:pk>/remove-server/<int:server_pk>/', views.project_remove_server, name='project_remove_server'),
    
    # Task URLs
    path('tasks/', views.task_list, name='task_list'),
    path('tasks/<int:pk>/', views.task_detail, name='task_detail'),
    path('tasks/create/', views.task_create, name='task_create'),
    path('tasks/<int:pk>/edit/', views.task_edit, name='task_edit'),
    path('tasks/<int:pk>/delete/', views.task_delete, name='task_delete'),
    path('tasks/<int:pk>/toggle/', views.task_toggle, name='task_toggle'),
    
    # Server URLs
    path('servers/', views.server_list, name='server_list'),
    path('servers/<int:pk>/', views.server_detail, name='server_detail'),
    path('servers/create/', views.server_create, name='server_create'),
    path('servers/<int:pk>/edit/', views.server_edit, name='server_edit'),
    path('servers/<int:pk>/delete/', views.server_delete, name='server_delete'),
    
    # Event URLs
    path('events/', views.event_list, name='event_list'),
    path('events/<int:pk>/', views.event_detail, name='event_detail'),
    path('events/create/', views.event_create, name='event_create'),
    path('events/<int:pk>/edit/', views.event_edit, name='event_edit'),
    path('events/<int:pk>/delete/', views.event_delete, name='event_delete'),
    
    # Incident URLs
    path('incidents/', views.incident_list, name='incident_list'),
    path('incidents/<int:pk>/', views.incident_detail, name='incident_detail'),
    path('incidents/create/', views.incident_create, name='incident_create'),
    path('incidents/<int:pk>/edit/', views.incident_edit, name='incident_edit'),
    path('incidents/<int:pk>/delete/', views.incident_delete, name='incident_delete'),
    
    # Change Request URLs
    path('crqs/', views.crq_list, name='crq_list'),
    path('crqs/<int:pk>/', views.crq_detail, name='crq_detail'),
    path('crqs/create/', views.crq_create, name='crq_create'),
    path('crqs/<int:pk>/edit/', views.crq_edit, name='crq_edit'),
    path('crqs/<int:pk>/delete/', views.crq_delete, name='crq_delete'),
]
