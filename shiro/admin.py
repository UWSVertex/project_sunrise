from django.contrib import admin
from .models import Project, Task, TaskComment, Server, Event, Incident, IncidentNote, ChangeRequest, CRQNote

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'status', 'priority', 'progress', 'deadline', 'owner', 'created_at')
    list_filter = ('status', 'priority', 'created_at')
    search_fields = ('name', 'description', 'owner', 'client')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'category', 'client')
        }),
        ('Status & Priority', {
            'fields': ('status', 'priority', 'progress')
        }),
        ('Dates', {
            'fields': ('start_date', 'deadline', 'completion_date')
        }),
        ('Budget', {
            'fields': ('budget', 'spent')
        }),
        ('Team', {
            'fields': ('owner', 'team_members')
        }),
        ('Tags & Metadata', {
            'fields': ('tags', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'project', 'status', 'priority', 'due_date', 'assigned_to', 'completed')
    list_filter = ('status', 'priority', 'completed', 'due_date')
    search_fields = ('title', 'description', 'assigned_to')
    date_hierarchy = 'due_date'
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Basic Information', {
            'fields': ('project', 'title', 'description')
        }),
        ('Status & Priority', {
            'fields': ('status', 'priority', 'completed')
        }),
        ('Dates', {
            'fields': ('due_date', 'start_date', 'completed_date')
        }),
        ('Assignment & Tracking', {
            'fields': ('assigned_to', 'estimated_hours', 'actual_hours')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(TaskComment)
class TaskCommentAdmin(admin.ModelAdmin):
    list_display = ('task', 'author', 'created_at')
    list_filter = ('created_at', 'task')
    search_fields = ('content', 'author')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'

@admin.register(Server)
class ServerAdmin(admin.ModelAdmin):
    list_display = ('name', 'ip_address', 'status', 'last_checked')
    list_filter = ('status', 'created_at')
    search_fields = ('name', 'ip_address')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'category', 'alert')
    list_filter = ('category', 'alert', 'date')
    search_fields = ('title', 'description')
    date_hierarchy = 'date'
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Incident)
class IncidentAdmin(admin.ModelAdmin):
    list_display = ('ticket_id', 'title', 'status', 'urgency', 'impact', 'assigned_to', 'reported_date')
    list_filter = ('status', 'urgency', 'impact', 'reported_date')
    search_fields = ('ticket_id', 'title', 'description', 'assigned_to', 'affected_service')
    date_hierarchy = 'reported_date'
    readonly_fields = ('ticket_id', 'created_at', 'updated_at')
    fieldsets = (
        ('Identification', {
            'fields': ('ticket_id', 'title', 'description')
        }),
        ('Status & Priority', {
            'fields': ('status', 'urgency', 'impact', 'priority')
        }),
        ('Assignment', {
            'fields': ('reported_by', 'assigned_to', 'assignment_group')
        }),
        ('Affected Items', {
            'fields': ('affected_service', 'affected_ci', 'category', 'subcategory')
        }),
        ('Dates', {
            'fields': ('reported_date', 'target_resolution_date', 'resolved_date', 'closed_date')
        }),
        ('Resolution', {
            'fields': ('resolution', 'root_cause', 'notes')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(IncidentNote)
class IncidentNoteAdmin(admin.ModelAdmin):
    list_display = ('incident', 'author', 'is_public', 'created_at')
    list_filter = ('is_public', 'created_at', 'incident')
    search_fields = ('note', 'author', 'incident__ticket_id')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'

@admin.register(ChangeRequest)
class ChangeRequestAdmin(admin.ModelAdmin):
    list_display = ('ticket_id', 'title', 'status', 'risk_level', 'priority', 'assigned_to', 'requested_date')
    list_filter = ('status', 'risk_level', 'priority', 'crq_type', 'requested_date')
    search_fields = ('ticket_id', 'title', 'description', 'assigned_to', 'affected_services')
    date_hierarchy = 'requested_date'
    readonly_fields = ('ticket_id', 'created_at', 'updated_at')
    fieldsets = (
        ('Identification', {
            'fields': ('ticket_id', 'title', 'description')
        }),
        ('Status & Type', {
            'fields': ('status', 'crq_type', 'risk_level', 'priority')
        }),
        ('Assignment & Approval', {
            'fields': ('requested_by', 'assigned_to', 'approval_group', 'approved_date')
        }),
        ('Implementation', {
            'fields': ('implementation_plan', 'rollback_plan', 'test_plan')
        }),
        ('Affected Items', {
            'fields': ('affected_services', 'affected_ci')
        }),
        ('Scheduling', {
            'fields': ('target_start_date', 'target_end_date', 'actual_start_date', 'actual_end_date')
        }),
        ('Planning', {
            'fields': ('business_justification', 'communication_plan')
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(CRQNote)
class CRQNoteAdmin(admin.ModelAdmin):
    list_display = ('crq', 'author', 'created_at')
    list_filter = ('created_at', 'crq')
    search_fields = ('note', 'author', 'crq__ticket_id')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'
