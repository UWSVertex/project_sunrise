from django.urls import path
from . import views

app_name = 'inframan'

urlpatterns = [
    # Dashboard
    path('', views.infrastructure_dashboard, name='dashboard'),
    
    # Server URLs
    path('servers/', views.server_list, name='server_list'),
    path('servers/import/', views.server_import_upload, name='server_import_upload'),
    path('servers/import/<str:token>/confirm/', views.server_import_confirm, name='server_import_confirm'),
    path('servers/import/<str:token>/cancel/', views.server_import_cancel, name='server_import_cancel'),
    path('servers/create/', views.server_create, name='server_create'),
    path('servers/<int:pk>/', views.server_detail, name='server_detail'),
    path('servers/<int:pk>/edit/', views.server_edit, name='server_edit'),
    path('servers/<int:pk>/delete/', views.server_delete, name='server_delete'),
    path('servers/bulk-delete/', views.server_bulk_delete, name='server_bulk_delete'),
    
    # Rack URLs
    path('racks/', views.rack_list, name='rack_list'),
    path('racks/create/', views.rack_create, name='rack_create'),
    path('racks/<int:pk>/', views.rack_detail, name='rack_detail'),

    # Country URLs
    path('countries/', views.country_list, name='country_list'),
    path('countries/create/', views.country_create, name='country_create'),
    path('countries/<int:pk>/edit/', views.country_edit, name='country_edit'),
    path('countries/<int:pk>/delete/', views.country_delete, name='country_delete'),

    # Site URLs
    path('sites/', views.site_list, name='site_list'),
    path('sites/create/', views.site_create, name='site_create'),
    path('sites/<int:pk>/', views.site_detail, name='site_detail'),
    path('sites/<int:pk>/edit/', views.site_edit, name='site_edit'),
    
    # Region URLs
    path('regions/', views.region_list, name='region_list'),
    path('regions/create/', views.region_create, name='region_create'),
    path('regions/<int:pk>/edit/', views.region_edit, name='region_edit'),
    path('regions/<int:pk>/delete/', views.region_delete, name='region_delete'),
    
    # Maintenance URLs
    path('maintenance/', views.maintenance_list, name='maintenance_list'),
    path('maintenance/create/', views.maintenance_create, name='maintenance_create'),
]
