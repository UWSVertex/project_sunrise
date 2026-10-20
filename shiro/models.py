from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

# Status choices for Project and Task
PROJECT_STATUS_CHOICES = [
    ('not_started', 'Not Started'),
    ('in_progress', 'In Progress'),
    ('blocked', 'Blocked'),
    ('completed', 'Completed'),
    ('archived', 'Archived'),
]

TASK_STATUS_CHOICES = [
    ('todo', 'To Do'),
    ('in_progress', 'In Progress'),
    ('completed', 'Completed'),
    ('cancelled', 'Cancelled'),
]

PRIORITY_CHOICES = [
    ('low', 'Low'),
    ('medium', 'Medium'),
    ('high', 'High'),
    ('critical', 'Critical'),
]

SERVER_STATUS_CHOICES = [
    ('online', 'Online'),
    ('offline', 'Offline'),
    ('maintenance', 'Maintenance'),
    ('unknown', 'Unknown'),
]

EVENT_CATEGORY_CHOICES = [
    ('deadline', 'Deadline'),
    ('meeting', 'Meeting'),
    ('release', 'Release'),
    ('maintenance', 'Maintenance'),
    ('other', 'Other'),
]


class Project(models.Model):
    """Enhanced project model for comprehensive project management"""
    # Basic Info
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    
    # Status & Priority
    status = models.CharField(max_length=20, choices=PROJECT_STATUS_CHOICES, default='not_started')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    
    # Dates
    start_date = models.DateField(blank=True, null=True)
    deadline = models.DateField(blank=True, null=True)
    completion_date = models.DateField(blank=True, null=True)
    
    # Progress & Budget
    progress = models.IntegerField(default=0, help_text="Progress percentage (0-100)")
    budget = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    spent = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    
    # Team & Ownership
    owner = models.CharField(max_length=255, blank=True, null=True)
    team_members = models.TextField(blank=True, null=True, help_text="Comma-separated list of team members")
    
    # Additional Info
    client = models.CharField(max_length=255, blank=True, null=True)
    category = models.CharField(max_length=100, blank=True, null=True)
    tags = models.TextField(blank=True, null=True, help_text="Comma-separated tags")
    
    # Infrastructure
    servers = models.ManyToManyField('inframan.Server', blank=True, related_name='projects', help_text="Servers used by this project")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Project'
        verbose_name_plural = 'Projects'
        indexes = [
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['priority', '-deadline']),
        ]

    def __str__(self):
        return self.name
    
    @staticmethod
    def _split_csv(value):
        return [item.strip() for item in (value or '').split(',') if item.strip()]

    @property
    def team_list(self):
        return self._split_csv(self.team_members)

    @property
    def tag_list(self):
        return self._split_csv(self.tags)

    def get_days_until_deadline(self):
        """Calculate days remaining until deadline"""
        if self.deadline:
            delta = self.deadline - timezone.now().date()
            return delta.days
        return None
    
    def is_overdue(self):
        """Check if project is overdue"""
        if self.deadline and self.status != 'completed':
            return timezone.now().date() > self.deadline
        return False
    
    def get_budget_remaining(self):
        """Calculate remaining budget"""
        if self.budget:
            return self.budget - self.spent
        return None


class Task(models.Model):
    """Enhanced task model with comments"""
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks', blank=True, null=True)
    
    # Task Info
    title = models.CharField(max_length=255, default='Untitled Task')
    description = models.TextField(blank=True, null=True)
    
    # Status & Priority
    status = models.CharField(max_length=20, choices=TASK_STATUS_CHOICES, default='todo')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    
    # Dates
    due_date = models.DateField()
    start_date = models.DateField(blank=True, null=True)
    completed_date = models.DateField(blank=True, null=True)
    
    # Tracking
    completed = models.BooleanField(default=False)
    assigned_to = models.CharField(max_length=255, blank=True, null=True)
    estimated_hours = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    actual_hours = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['due_date', '-created_at']
        verbose_name = 'Task'
        verbose_name_plural = 'Tasks'
        indexes = [
            models.Index(fields=['status', 'due_date']),
            models.Index(fields=['project', 'completed']),
        ]

    def __str__(self):
        return self.title
    
    def is_overdue(self):
        """Check if task is overdue"""
        if not self.completed and self.due_date < timezone.now().date():
            return True
        return False
    
    def get_days_until_due(self):
        """Calculate days until due"""
        delta = self.due_date - timezone.now().date()
        return delta.days


class TaskComment(models.Model):
    """Comments on tasks for discussion and tracking"""
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='comments')
    
    author = models.CharField(max_length=255)
    content = models.TextField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']
        verbose_name = 'Task Comment'
        verbose_name_plural = 'Task Comments'

    def __str__(self):
        return f"Comment by {self.author} on {self.task.title}"


class Server(models.Model):
    """Server registry for tracking infrastructure"""
    name = models.CharField(max_length=255)
    ip_address = models.GenericIPAddressField()
    status = models.CharField(max_length=20, choices=SERVER_STATUS_CHOICES, default='unknown')
    notes = models.TextField(blank=True, null=True)
    last_checked = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Server'
        verbose_name_plural = 'Servers'

    def __str__(self):
        return f"{self.name} ({self.ip_address})"


class Event(models.Model):
    """Important dates and events"""
    title = models.CharField(max_length=255)
    date = models.DateField()
    category = models.CharField(max_length=20, choices=EVENT_CATEGORY_CHOICES, default='other')
    alert = models.BooleanField(default=True, help_text="Send alert for this event")
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['date']
        verbose_name = 'Event'
        verbose_name_plural = 'Events'

    def __str__(self):
        return f"{self.title} - {self.date}"


# ===== INCIDENT & CRQ MODELS =====

INCIDENT_STATUS_CHOICES = [
    ('new', 'New'),
    ('assigned', 'Assigned'),
    ('in_progress', 'In Progress'),
    ('pending', 'Pending'),
    ('resolved', 'Resolved'),
    ('closed', 'Closed'),
]

INCIDENT_URGENCY_CHOICES = [
    ('low', 'Low'),
    ('medium', 'Medium'),
    ('high', 'High'),
    ('critical', 'Critical'),
]

INCIDENT_IMPACT_CHOICES = [
    ('low', 'Low - One user'),
    ('medium', 'Medium - Department'),
    ('high', 'High - Multiple Departments'),
    ('critical', 'Critical - Entire Organization'),
]

CRQ_STATUS_CHOICES = [
    ('draft', 'Draft'),
    ('submitted', 'Submitted'),
    ('approved', 'Approved'),
    ('in_progress', 'In Progress'),
    ('completed', 'Completed'),
    ('rejected', 'Rejected'),
    ('cancelled', 'Cancelled'),
]

CRQ_TYPE_CHOICES = [
    ('standard', 'Standard'),
    ('emergency', 'Emergency'),
    ('urgent', 'Urgent'),
]

CRQ_RISK_CHOICES = [
    ('low', 'Low'),
    ('medium', 'Medium'),
    ('high', 'High'),
    ('critical', 'Critical'),
]


class Incident(models.Model):
    """Incident tracking model (similar to Remedy Incident)"""
    # Identification
    ticket_id = models.CharField(max_length=50, unique=True)  # Auto-generated like INC0001234
    title = models.CharField(max_length=255)
    description = models.TextField()
    
    # Status & Priority
    status = models.CharField(max_length=20, choices=INCIDENT_STATUS_CHOICES, default='new')
    urgency = models.CharField(max_length=20, choices=INCIDENT_URGENCY_CHOICES, default='medium')
    impact = models.CharField(max_length=20, choices=INCIDENT_IMPACT_CHOICES, default='low')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    
    # Assignment
    reported_by = models.CharField(max_length=255)
    assigned_to = models.CharField(max_length=255, blank=True, null=True)
    assignment_group = models.CharField(max_length=255, blank=True, null=True)
    
    # Affected Items
    affected_service = models.CharField(max_length=255, blank=True, null=True)
    affected_ci = models.CharField(max_length=255, blank=True, null=True, help_text="Affected Configuration Item")
    
    # Dates
    reported_date = models.DateTimeField(auto_now_add=True)
    assigned_date = models.DateTimeField(blank=True, null=True)
    target_resolution_date = models.DateTimeField(blank=True, null=True)
    resolved_date = models.DateTimeField(blank=True, null=True)
    closed_date = models.DateTimeField(blank=True, null=True)
    
    # Additional Info
    category = models.CharField(max_length=100, blank=True, null=True)
    subcategory = models.CharField(max_length=100, blank=True, null=True)
    resolution = models.TextField(blank=True, null=True)
    root_cause = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    
    # Tracking
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-reported_date']
        verbose_name = 'Incident'
        verbose_name_plural = 'Incidents'
        indexes = [
            models.Index(fields=['status', '-reported_date']),
            models.Index(fields=['urgency', 'impact']),
            models.Index(fields=['ticket_id']),
        ]

    def __str__(self):
        return f"{self.ticket_id} - {self.title}"
    
    def is_overdue(self):
        """Check if incident is overdue based on target resolution date"""
        if self.target_resolution_date and self.status not in ['resolved', 'closed']:
            return timezone.now() > self.target_resolution_date
        return False
    
    def get_age_in_hours(self):
        """Calculate incident age in hours"""
        delta = timezone.now() - self.reported_date
        return delta.total_seconds() / 3600


class IncidentNote(models.Model):
    """Work notes for incidents"""
    incident = models.ForeignKey(Incident, on_delete=models.CASCADE, related_name='work_notes')
    
    author = models.CharField(max_length=255)
    note = models.TextField()
    is_public = models.BooleanField(default=False, help_text="Visible to requester")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Incident Note'
        verbose_name_plural = 'Incident Notes'

    def __str__(self):
        return f"Note on {self.incident.ticket_id}"


class ChangeRequest(models.Model):
    """Change Request tracking model (similar to Remedy CRQ)"""
    # Identification
    ticket_id = models.CharField(max_length=50, unique=True)  # Auto-generated like CHG0001234
    title = models.CharField(max_length=255)
    description = models.TextField()
    
    # Status & Type
    status = models.CharField(max_length=20, choices=CRQ_STATUS_CHOICES, default='draft')
    crq_type = models.CharField(max_length=20, choices=CRQ_TYPE_CHOICES, default='standard', verbose_name='Type')
    risk_level = models.CharField(max_length=20, choices=CRQ_RISK_CHOICES, default='medium')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    
    # Assignment
    requested_by = models.CharField(max_length=255)
    assigned_to = models.CharField(max_length=255, blank=True, null=True)
    approval_group = models.CharField(max_length=255, blank=True, null=True)
    
    # Implementation
    implementation_plan = models.TextField(blank=True, null=True)
    rollback_plan = models.TextField(blank=True, null=True)
    test_plan = models.TextField(blank=True, null=True)
    
    # Affected Items
    affected_services = models.TextField(blank=True, null=True, help_text="Comma-separated services")
    affected_ci = models.TextField(blank=True, null=True, help_text="Affected Configuration Items")
    
    # Dates
    requested_date = models.DateTimeField(auto_now_add=True)
    approved_date = models.DateTimeField(blank=True, null=True)
    target_start_date = models.DateTimeField(blank=True, null=True)
    target_end_date = models.DateTimeField(blank=True, null=True)
    actual_start_date = models.DateTimeField(blank=True, null=True)
    actual_end_date = models.DateTimeField(blank=True, null=True)
    
    # Additional Info
    business_justification = models.TextField(blank=True, null=True)
    communication_plan = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    
    # Tracking
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-requested_date']
        verbose_name = 'Change Request'
        verbose_name_plural = 'Change Requests'
        indexes = [
            models.Index(fields=['status', '-requested_date']),
            models.Index(fields=['risk_level', 'priority']),
            models.Index(fields=['ticket_id']),
        ]

    def __str__(self):
        return f"{self.ticket_id} - {self.title}"
    
    def is_overdue(self):
        """Check if CRQ is overdue"""
        if self.target_end_date and self.status not in ['completed', 'cancelled']:
            return timezone.now() > self.target_end_date
        return False
    
    def get_status_percentage(self):
        """Calculate completion percentage based on status"""
        status_map = {
            'draft': 10,
            'submitted': 25,
            'approved': 50,
            'in_progress': 75,
            'completed': 100,
            'rejected': 0,
            'cancelled': 0,
        }
        return status_map.get(self.status, 0)


class CRQNote(models.Model):
    """Work notes for change requests"""
    crq = models.ForeignKey(ChangeRequest, on_delete=models.CASCADE, related_name='work_notes')
    
    author = models.CharField(max_length=255)
    note = models.TextField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'CRQ Note'
        verbose_name_plural = 'CRQ Notes'

    def __str__(self):
        return f"Note on {self.crq.ticket_id}"
