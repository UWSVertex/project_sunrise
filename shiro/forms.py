from django import forms
from .models import (Project, Task, Server, Event, TaskComment, Incident, IncidentNote,
                     ChangeRequest, CRQNote,
                     PROJECT_STATUS_CHOICES, TASK_STATUS_CHOICES, 
                     SERVER_STATUS_CHOICES, EVENT_CATEGORY_CHOICES,
                     PRIORITY_CHOICES, INCIDENT_STATUS_CHOICES, INCIDENT_URGENCY_CHOICES,
                     INCIDENT_IMPACT_CHOICES, CRQ_STATUS_CHOICES, CRQ_TYPE_CHOICES,
                     CRQ_RISK_CHOICES)
from django.utils import timezone

class ProjectForm(forms.ModelForm):
    """Enhanced form for creating and editing projects"""
    start_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=False,
        label='Project Start Date'
    )
    deadline = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=False,
        label='Project Deadline'
    )
    completion_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=False,
        label='Completion Date'
    )
    budget = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'})
    )
    spent = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        initial=0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'})
    )
    servers = forms.ModelMultipleChoiceField(
        queryset=None,
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label='Linked Servers'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from inframan.models import Server as InfraServer
        self.fields['servers'].queryset = InfraServer.objects.all().order_by('name')
    
    class Meta:
        model = Project
        fields = ['name', 'description', 'status', 'priority', 'start_date', 'deadline', 
                  'completion_date', 'progress', 'budget', 'spent', 'owner', 'team_members', 
                  'client', 'category', 'tags']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Project name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Project description'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'progress': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'max': '100'}),
            'owner': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Project owner name'}),
            'team_members': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Comma-separated team members'}),
            'client': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Client name'}),
            'category': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Project category'}),
            'tags': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Comma-separated tags'}),
        }

    def save(self, commit=True):
        project = super().save(commit=commit)
        if commit:
            project.servers.set(self.cleaned_data.get('servers', []))
        return project


class TaskForm(forms.ModelForm):
    """Enhanced form for creating and editing tasks"""
    due_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        initial=timezone.now,
    )
    start_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=False,
        label='Task Start Date'
    )
    completed_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=False,
        label='Completion Date'
    )
    estimated_hours = forms.DecimalField(
        max_digits=6,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.5', 'placeholder': 'e.g., 5.5'})
    )
    actual_hours = forms.DecimalField(
        max_digits=6,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.5', 'placeholder': 'e.g., 6.0'})
    )
    
    class Meta:
        model = Task
        fields = ['project', 'title', 'description', 'status', 'priority', 'due_date', 
                  'start_date', 'completed_date', 'completed', 'assigned_to', 
                  'estimated_hours', 'actual_hours']
        widgets = {
            'project': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Task title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Task description and notes'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'completed': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'assigned_to': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Assign to team member'}),
        }


class TaskCommentForm(forms.ModelForm):
    """Form for adding comments to tasks"""
    
    class Meta:
        model = TaskComment
        fields = ['author', 'content']
        widgets = {
            'author': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your name'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Add a comment...'}),
        }


class ServerForm(forms.ModelForm):
    """Form for creating and editing servers"""
    ip_address = forms.GenericIPAddressField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '192.168.1.1'})
    )
    
    class Meta:
        model = Server
        fields = ['name', 'ip_address', 'status', 'notes']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Server name'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Server notes'}),
        }


class EventForm(forms.ModelForm):
    """Form for creating and editing events"""
    date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        initial=timezone.now,
    )
    
    class Meta:
        model = Event
        fields = ['title', 'date', 'category', 'alert', 'description']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Event title'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'alert': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Event description'}),
        }


# ===== INCIDENT FORMS =====

class IncidentForm(forms.ModelForm):
    """Form for creating and editing incidents"""
    target_resolution_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        required=False,
        label='Target Resolution Date'
    )
    resolved_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        required=False,
        label='Resolved Date'
    )
    closed_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        required=False,
        label='Closed Date'
    )
    
    class Meta:
        model = Incident
        fields = ['ticket_id', 'title', 'description', 'status', 'urgency', 'impact', 'priority',
                  'reported_by', 'assigned_to', 'assignment_group', 'affected_service', 'affected_ci',
                  'target_resolution_date', 'category', 'subcategory', 'resolution', 'root_cause', 'notes']
        widgets = {
            'ticket_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., INC0001234'}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Incident title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Detailed description'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'urgency': forms.Select(attrs={'class': 'form-select'}),
            'impact': forms.Select(attrs={'class': 'form-select'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'reported_by': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Reporter name'}),
            'assigned_to': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Assignee name'}),
            'assignment_group': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., IT Support, Database Team'}),
            'affected_service': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Service affected'}),
            'affected_ci': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Configuration Item'}),
            'category': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Category'}),
            'subcategory': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Subcategory'}),
            'resolution': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'How was it resolved?'}),
            'root_cause': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Root cause analysis'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Additional notes'}),
        }


class IncidentNoteForm(forms.ModelForm):
    """Form for adding work notes to incidents"""
    
    class Meta:
        model = IncidentNote
        fields = ['author', 'note', 'is_public']
        widgets = {
            'author': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your name'}),
            'note': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Add work note...'}),
            'is_public': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


# ===== CHANGE REQUEST FORMS =====

class ChangeRequestForm(forms.ModelForm):
    """Form for creating and editing change requests"""
    target_start_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        required=False,
        label='Target Start Date'
    )
    target_end_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        required=False,
        label='Target End Date'
    )
    actual_start_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        required=False,
        label='Actual Start Date'
    )
    actual_end_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        required=False,
        label='Actual End Date'
    )
    approved_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        required=False,
        label='Approved Date'
    )
    
    class Meta:
        model = ChangeRequest
        fields = ['ticket_id', 'title', 'description', 'status', 'crq_type', 'risk_level', 'priority',
                  'requested_by', 'assigned_to', 'approval_group', 'implementation_plan', 'rollback_plan',
                  'test_plan', 'affected_services', 'affected_ci', 'target_start_date', 'target_end_date',
                  'business_justification', 'communication_plan', 'notes']
        widgets = {
            'ticket_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., CHG0001234'}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Change request title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Detailed description of change'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'crq_type': forms.Select(attrs={'class': 'form-select'}),
            'risk_level': forms.Select(attrs={'class': 'form-select'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'requested_by': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Requester name'}),
            'assigned_to': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Assignee name'}),
            'approval_group': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., CAB (Change Advisory Board)'}),
            'implementation_plan': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Step-by-step implementation steps'}),
            'rollback_plan': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Rollback/backout procedure'}),
            'test_plan': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Testing and validation steps'}),
            'affected_services': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Comma-separated services'}),
            'affected_ci': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Affected Configuration Items'}),
            'business_justification': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Why is this change needed?'}),
            'communication_plan': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Communication to stakeholders'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Additional notes'}),
        }


class CRQNoteForm(forms.ModelForm):
    """Form for adding work notes to change requests"""
    
    class Meta:
        model = CRQNote
        fields = ['author', 'note']
        widgets = {
            'author': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your name'}),
            'note': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Add work note...'}),
        }
