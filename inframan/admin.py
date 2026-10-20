from django.contrib import admin
from .models import Region, Country, Site, Location, Server, ServerMaintenance, ServerMonitoring

@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ('name', 'code')
    search_fields = ('name', 'code')

@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'region')
    list_filter = ('region',)
    search_fields = ('name', 'code')

@admin.register(Site)
class SiteAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'country', 'city')
    list_filter = ('country', 'created_at')
    search_fields = ('name', 'code', 'city')
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'code', 'country', 'city')
        }),
        ('Contact Information', {
            'fields': ('address', 'phone', 'contact_person', 'contact_email')
        }),
        ('Additional Info', {
            'fields': ('notes',)
        }),
    )

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'site', 'location_type', 'row', 'number')
    list_filter = ('site', 'location_type')
    search_fields = ('name', 'site__name')

@admin.register(Server)
class ServerAdmin(admin.ModelAdmin):
    list_display = ('name', 'ip_address', 'site', 'environment', 'status', 'os')
    list_filter = ('status', 'environment', 'site', 'os', 'server_type')
    search_fields = ('name', 'ip_address', 'serial_number', 'hostname')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Identification', {
            'fields': ('name', 'serial_number', 'asset_tag')
        }),
        ('Network', {
            'fields': ('ip_address', 'hostname', 'mac_address')
        }),
        ('Location', {
            'fields': ('site', 'location')
        }),
        ('Type & Status', {
            'fields': ('server_type', 'status', 'environment')
        }),
        ('Operating System', {
            'fields': ('os', 'os_version')
        }),
        ('Hardware - CPU', {
            'fields': ('cpu_model', 'cpu_cores', 'cpu_threads')
        }),
        ('Hardware - Memory', {
            'fields': ('memory_gb',)
        }),
        ('Hardware - Storage', {
            'fields': ('storage_total_gb', 'storage_type', 'storage_info')
        }),
        ('iDRAC (Dell)', {
            'fields': ('idrac_ip', 'idrac_username', 'idrac_password'),
            'classes': ('collapse',)
        }),
        ('Power & Connectivity', {
            'fields': ('power_supply_count', 'network_interfaces'),
            'classes': ('collapse',)
        }),
        ('Manufacturer', {
            'fields': ('manufacturer', 'model')
        }),
        ('Lifecycle', {
            'fields': ('purchase_date', 'warranty_expiry', 'last_maintenance', 'decommission_date')
        }),
        ('Assignment & Notes', {
            'fields': ('assigned_to', 'notes')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(ServerMaintenance)
class ServerMaintenanceAdmin(admin.ModelAdmin):
    list_display = ('server', 'maintenance_type', 'maintenance_date', 'performed_by')
    list_filter = ('maintenance_type', 'maintenance_date', 'server__site')
    search_fields = ('server__name', 'performed_by')
    date_hierarchy = 'maintenance_date'
    readonly_fields = ('created_at', 'updated_at')

@admin.register(ServerMonitoring)
class ServerMonitoringAdmin(admin.ModelAdmin):
    list_display = ('server', 'health_status', 'cpu_usage_percent', 'memory_usage_percent', 'disk_usage_percent')
    list_filter = ('health_status', 'is_monitored')
    search_fields = ('server__name',)
    readonly_fields = ('created_at', 'updated_at', 'last_check_time')
    fieldsets = (
        ('Server & Monitoring', {
            'fields': ('server', 'is_monitored', 'monitoring_tool', 'health_status')
        }),
        ('Current Metrics', {
            'fields': ('cpu_usage_percent', 'memory_usage_percent', 'disk_usage_percent', 'last_check_time')
        }),
        ('Thresholds', {
            'fields': ('cpu_warning_threshold', 'memory_warning_threshold', 'disk_warning_threshold')
        }),
        ('Notes & Metadata', {
            'fields': ('notes', 'created_at', 'updated_at')
        }),
    )
