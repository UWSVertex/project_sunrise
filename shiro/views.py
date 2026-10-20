from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib import messages
from .models import Project, Task, Server, Event, TaskComment, Incident, IncidentNote, ChangeRequest, CRQNote
from .forms import ProjectForm, TaskForm, ServerForm, EventForm, TaskCommentForm, IncidentForm, IncidentNoteForm, ChangeRequestForm, CRQNoteForm
from inframan.models import Server as InfraServer
from django.utils import timezone
from datetime import timedelta

# Dashboard View
def dashboard(request):
    """Main dashboard with summary cards"""
    context = {
        'total_projects': Project.objects.count(),
        'active_projects': Project.objects.filter(status='in_progress').count(),
        'today_tasks': Task.objects.filter(due_date=timezone.now().date()),
        'servers': Server.objects.all(),
        'upcoming_events': Event.objects.filter(date__gte=timezone.now().date()).order_by('date')[:5],
        'overdue_tasks': Task.objects.filter(due_date__lt=timezone.now().date(), completed=False),
        # Incident stats
        'total_incidents': Incident.objects.count(),
        'open_incidents': Incident.objects.filter(status__in=['new', 'assigned', 'in_progress']).count(),
        'critical_incidents': Incident.objects.filter(urgency='critical', status__in=['new', 'assigned', 'in_progress']).count(),
        'recent_incidents': Incident.objects.order_by('-reported_date')[:5],
        # CRQ stats
        'total_crqs': ChangeRequest.objects.count(),
        'pending_crqs': ChangeRequest.objects.filter(status__in=['draft', 'submitted', 'approved']).count(),
        'recent_crqs': ChangeRequest.objects.order_by('-requested_date')[:5],
    }
    return render(request, 'shiro/dashboard.html', context)

# ===== PROJECT VIEWS =====
def project_list(request):
    """List all projects with filtering"""
    projects = Project.objects.all().order_by('-created_at')
    status_filter = request.GET.get('status')
    priority_filter = request.GET.get('priority')
    
    if status_filter:
        projects = projects.filter(status=status_filter)
    if priority_filter:
        projects = projects.filter(priority=priority_filter)
    
    return render(request, 'shiro/project_list.html', {
        'projects': projects,
        'status_filter': status_filter,
        'priority_filter': priority_filter
    })

def project_detail(request, pk):
    """Project detail view with tasks"""
    project = get_object_or_404(Project, pk=pk)
    tasks = project.tasks.all()
    budget_remaining = project.get_budget_remaining()
    days_until_deadline = project.get_days_until_deadline()
    
    return render(request, 'shiro/project_detail.html', {
        'project': project,
        'tasks': tasks,
        'budget_remaining': budget_remaining,
        'days_until_deadline': days_until_deadline,
        'is_overdue': project.is_overdue()
    })

def project_create(request):
    """Create new project"""
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save()
            messages.success(request, f'Project "{project.name}" created successfully!')
            return redirect('shiro:project_detail', pk=project.pk)
    else:
        form = ProjectForm()
    return render(request, 'shiro/project_form.html', {'form': form, 'title': 'Create Project'})

def project_edit(request, pk):
    """Edit project"""
    project = get_object_or_404(Project, pk=pk)
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            messages.success(request, f'Project "{project.name}" updated successfully!')
            return redirect('shiro:project_detail', pk=project.pk)
    else:
        form = ProjectForm(instance=project)
        form.fields['servers'].initial = project.servers.all()
    return render(request, 'shiro/project_form.html', {'form': form, 'project': project, 'title': 'Edit Project'})

def project_delete(request, pk):
    """Delete project"""
    project = get_object_or_404(Project, pk=pk)
    if request.method == 'POST':
        project_name = project.name
        project.delete()
        messages.success(request, f'Project "{project_name}" deleted successfully!')
        return redirect('shiro:project_list')
    return render(request, 'shiro/confirm_delete.html', {'object': project, 'type': 'Project'})

def project_remove_server(request, pk, server_pk):
    """Detach an infrastructure server from a project"""
    project = get_object_or_404(Project, pk=pk)
    server = get_object_or_404(InfraServer, pk=server_pk)
    project.servers.remove(server)
    messages.success(request, f'{server.name} removed from {project.name}.')
    return redirect('shiro:project_detail', pk=project.pk)


# ===== TASK VIEWS =====
def task_list(request):
    """List all tasks with filtering"""
    tasks = Task.objects.all().order_by('due_date')
    status_filter = request.GET.get('status')
    priority_filter = request.GET.get('priority')
    project_filter = request.GET.get('project')
    
    if status_filter:
        tasks = tasks.filter(status=status_filter)
    if priority_filter:
        tasks = tasks.filter(priority=priority_filter)
    if project_filter:
        tasks = tasks.filter(project_id=project_filter)
    
    return render(request, 'shiro/task_list.html', {
        'tasks': tasks,
        'status_filter': status_filter,
        'priority_filter': priority_filter,
        'project_filter': project_filter
    })

def task_detail(request, pk):
    """Task detail view with comments"""
    task = get_object_or_404(Task, pk=pk)
    comments = task.comments.all()
    
    if request.method == 'POST':
        comment_form = TaskCommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.task = task
            comment.save()
            messages.success(request, 'Comment added successfully!')
            return redirect('shiro:task_detail', pk=pk)
    else:
        comment_form = TaskCommentForm()
    
    return render(request, 'shiro/task_detail.html', {
        'task': task,
        'comments': comments,
        'comment_form': comment_form,
        'is_overdue': task.is_overdue(),
        'days_until_due': task.get_days_until_due()
    })

def task_create(request):
    """Create new task"""
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save()
            messages.success(request, f'Task "{task.title}" created successfully!')
            return redirect('shiro:task_detail', pk=task.pk)
    else:
        form = TaskForm()
    return render(request, 'shiro/task_form.html', {'form': form, 'title': 'Create Task'})

def task_edit(request, pk):
    """Edit task"""
    task = get_object_or_404(Task, pk=pk)
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            messages.success(request, f'Task "{task.title}" updated successfully!')
            return redirect('shiro:task_detail', pk=task.pk)
    else:
        form = TaskForm(instance=task)
    return render(request, 'shiro/task_form.html', {'form': form, 'task': task, 'title': 'Edit Task'})

def task_delete(request, pk):
    """Delete task"""
    task = get_object_or_404(Task, pk=pk)
    if request.method == 'POST':
        task.delete()
        messages.success(request, f'Task deleted successfully!')
        return redirect('shiro:task_list')
    return render(request, 'shiro/confirm_delete.html', {'object': task, 'type': 'Task'})

def task_toggle(request, pk):
    """Toggle task completion status"""
    task = get_object_or_404(Task, pk=pk)
    task.completed = not task.completed
    task.status = 'completed' if task.completed else 'in_progress'
    task.completed_date = timezone.now().date() if task.completed else None
    task.save()
    messages.success(request, f'Task marked as {"completed" if task.completed else "incomplete"}!')
    return redirect('shiro:task_detail', pk=pk)

# ===== SERVER VIEWS =====
def server_list(request):
    """List all servers"""
    servers = Server.objects.all().order_by('name')
    status_filter = request.GET.get('status')
    
    if status_filter:
        servers = servers.filter(status=status_filter)
    
    return render(request, 'shiro/server_list.html', {
        'servers': servers,
        'status_filter': status_filter
    })

def server_detail(request, pk):
    """Server detail view"""
    server = get_object_or_404(Server, pk=pk)
    return render(request, 'shiro/server_detail.html', {'server': server})

def server_create(request):
    """Create new server"""
    if request.method == 'POST':
        form = ServerForm(request.POST)
        if form.is_valid():
            server = form.save()
            messages.success(request, f'Server "{server.name}" added successfully!')
            return redirect('shiro:server_detail', pk=server.pk)
    else:
        form = ServerForm()
    return render(request, 'shiro/server_form.html', {'form': form, 'title': 'Add Server'})

def server_edit(request, pk):
    """Edit server"""
    server = get_object_or_404(Server, pk=pk)
    if request.method == 'POST':
        form = ServerForm(request.POST, instance=server)
        if form.is_valid():
            form.save()
            messages.success(request, f'Server "{server.name}" updated successfully!')
            return redirect('shiro:server_detail', pk=server.pk)
    else:
        form = ServerForm(instance=server)
    return render(request, 'shiro/server_form.html', {'form': form, 'server': server, 'title': 'Edit Server'})

def server_delete(request, pk):
    """Delete server"""
    server = get_object_or_404(Server, pk=pk)
    if request.method == 'POST':
        server_name = server.name
        server.delete()
        messages.success(request, f'Server "{server_name}" deleted successfully!')
        return redirect('shiro:server_list')
    return render(request, 'shiro/confirm_delete.html', {'object': server, 'type': 'Server'})

# ===== EVENT VIEWS =====
def event_list(request):
    """List all events"""
    events = Event.objects.all().order_by('date')
    category_filter = request.GET.get('category')
    
    if category_filter:
        events = events.filter(category=category_filter)
    
    return render(request, 'shiro/event_list.html', {
        'events': events,
        'category_filter': category_filter
    })

def event_detail(request, pk):
    """Event detail view"""
    event = get_object_or_404(Event, pk=pk)
    return render(request, 'shiro/event_detail.html', {'event': event})

def event_create(request):
    """Create new event"""
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save()
            messages.success(request, f'Event "{event.title}" created successfully!')
            return redirect('shiro:event_detail', pk=event.pk)
    else:
        form = EventForm()
    return render(request, 'shiro/event_form.html', {'form': form, 'title': 'Create Event'})

def event_edit(request, pk):
    """Edit event"""
    event = get_object_or_404(Event, pk=pk)
    if request.method == 'POST':
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, f'Event "{event.title}" updated successfully!')
            return redirect('shiro:event_detail', pk=event.pk)
    else:
        form = EventForm(instance=event)
    return render(request, 'shiro/event_form.html', {'form': form, 'event': event, 'title': 'Edit Event'})

def event_delete(request, pk):
    """Delete event"""
    event = get_object_or_404(Event, pk=pk)
    if request.method == 'POST':
        event_title = event.title
        event.delete()
        messages.success(request, f'Event "{event_title}" deleted successfully!')
        return redirect('shiro:event_list')
    return render(request, 'shiro/confirm_delete.html', {'object': event, 'type': 'Event'})

# ===== INCIDENT VIEWS =====
def incident_list(request):
    """List all incidents"""
    incidents = Incident.objects.all().order_by('-reported_date')
    status_filter = request.GET.get('status')
    urgency_filter = request.GET.get('urgency')
    
    if status_filter:
        incidents = incidents.filter(status=status_filter)
    if urgency_filter:
        incidents = incidents.filter(urgency=urgency_filter)
    
    return render(request, 'shiro/incident_list.html', {
        'incidents': incidents,
        'status_filter': status_filter,
        'urgency_filter': urgency_filter
    })

def incident_detail(request, pk):
    """Incident detail view with work notes"""
    incident = get_object_or_404(Incident, pk=pk)
    notes = incident.work_notes.all()
    
    if request.method == 'POST':
        note_form = IncidentNoteForm(request.POST)
        if note_form.is_valid():
            note = note_form.save(commit=False)
            note.incident = incident
            note.save()
            messages.success(request, 'Work note added successfully!')
            return redirect('shiro:incident_detail', pk=pk)
    else:
        note_form = IncidentNoteForm()
    
    return render(request, 'shiro/incident_detail.html', {
        'incident': incident,
        'notes': notes,
        'note_form': note_form,
        'is_overdue': incident.is_overdue(),
        'age_in_hours': incident.get_age_in_hours()
    })

def incident_create(request):
    """Create new incident"""
    if request.method == 'POST':
        form = IncidentForm(request.POST)
        if form.is_valid():
            incident = form.save()
            messages.success(request, f'Incident "{incident.ticket_id}" created successfully!')
            return redirect('shiro:incident_detail', pk=incident.pk)
    else:
        form = IncidentForm()
    return render(request, 'shiro/incident_form.html', {'form': form, 'title': 'Create Incident'})

def incident_edit(request, pk):
    """Edit incident"""
    incident = get_object_or_404(Incident, pk=pk)
    if request.method == 'POST':
        form = IncidentForm(request.POST, instance=incident)
        if form.is_valid():
            form.save()
            messages.success(request, f'Incident "{incident.ticket_id}" updated successfully!')
            return redirect('shiro:incident_detail', pk=incident.pk)
    else:
        form = IncidentForm(instance=incident)
    return render(request, 'shiro/incident_form.html', {'form': form, 'incident': incident, 'title': 'Edit Incident'})

def incident_delete(request, pk):
    """Delete incident"""
    incident = get_object_or_404(Incident, pk=pk)
    if request.method == 'POST':
        ticket_id = incident.ticket_id
        incident.delete()
        messages.success(request, f'Incident "{ticket_id}" deleted successfully!')
        return redirect('shiro:incident_list')
    return render(request, 'shiro/confirm_delete.html', {'object': incident, 'type': 'Incident'})

# ===== CHANGE REQUEST VIEWS =====
def crq_list(request):
    """List all change requests"""
    crqs = ChangeRequest.objects.all().order_by('-requested_date')
    status_filter = request.GET.get('status')
    risk_filter = request.GET.get('risk_level')
    
    if status_filter:
        crqs = crqs.filter(status=status_filter)
    if risk_filter:
        crqs = crqs.filter(risk_level=risk_filter)
    
    return render(request, 'shiro/crq_list.html', {
        'crqs': crqs,
        'status_filter': status_filter,
        'risk_filter': risk_filter
    })

def crq_detail(request, pk):
    """Change request detail view with work notes"""
    crq = get_object_or_404(ChangeRequest, pk=pk)
    notes = crq.work_notes.all()
    
    if request.method == 'POST':
        note_form = CRQNoteForm(request.POST)
        if note_form.is_valid():
            note = note_form.save(commit=False)
            note.crq = crq
            note.save()
            messages.success(request, 'Work note added successfully!')
            return redirect('shiro:crq_detail', pk=pk)
    else:
        note_form = CRQNoteForm()
    
    return render(request, 'shiro/crq_detail.html', {
        'crq': crq,
        'notes': notes,
        'note_form': note_form,
        'is_overdue': crq.is_overdue(),
        'status_percentage': crq.get_status_percentage()
    })

def crq_create(request):
    """Create new change request"""
    if request.method == 'POST':
        form = ChangeRequestForm(request.POST)
        if form.is_valid():
            crq = form.save()
            messages.success(request, f'Change Request "{crq.ticket_id}" created successfully!')
            return redirect('shiro:crq_detail', pk=crq.pk)
    else:
        form = ChangeRequestForm()
    return render(request, 'shiro/crq_form.html', {'form': form, 'title': 'Create Change Request'})

def crq_edit(request, pk):
    """Edit change request"""
    crq = get_object_or_404(ChangeRequest, pk=pk)
    if request.method == 'POST':
        form = ChangeRequestForm(request.POST, instance=crq)
        if form.is_valid():
            form.save()
            messages.success(request, f'Change Request "{crq.ticket_id}" updated successfully!')
            return redirect('shiro:crq_detail', pk=crq.pk)
    else:
        form = ChangeRequestForm(instance=crq)
    return render(request, 'shiro/crq_form.html', {'form': form, 'crq': crq, 'title': 'Edit Change Request'})

def crq_delete(request, pk):
    """Delete change request"""
    crq = get_object_or_404(ChangeRequest, pk=pk)
    if request.method == 'POST':
        ticket_id = crq.ticket_id
        crq.delete()
        messages.success(request, f'Change Request "{ticket_id}" deleted successfully!')
        return redirect('shiro:crq_list')
    return render(request, 'shiro/confirm_delete.html', {'object': crq, 'type': 'Change Request'})
