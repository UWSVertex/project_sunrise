# Project Plan: Django Work Companion App

## Phase 1: Environment & Foundation
- [ ] Set up virtual environment and install dependencies (Django, Pillow, etc.)
- [ ] Initialize Django project and core application
- [ ] Configure `settings.py` (Database, Static files, Media files)
- [ ] Create initial User model (if custom) and Admin setup

## Phase 2: Database Modeling & Core Features
- [ ] **Project Model:** Name, Description, Status (Dropdown), Deadline, Progress (%)
- [ ] **Task Model:** Description, Due Date, Completed Status, Project Link (Foreign Key)
- [ ] **Server Model:** Name, IP, Status, Notes, Last Checked
- [ ] **Event Model:** Important Dates, Category, Alert Flag
- [ ] Create Migrations and populate initial test data

## Phase 3: Backend API & Views
- [ ] Create views for Dashboard summary (counting tasks, active projects)
- [ ] Implement CRUD for Projects
- [ ] Implement CRUD for Daily Tasks
- [ ] Implement CRUD for Server Tracking
- [ ] Create logic for "Important Date" reminders

## Phase 4: Frontend & Dashboard Design (Bootstrap)
- [ ] Set up Base Template with Bootstrap 5 CSS/JS
- [ ] **Main Dashboard Page:**
    - [ ] Project Progress Cards
    - [ ] Today's Task List
    - [ ] Server Status Quick-View
- [ ] Create Project Management Page (List/Detail)
- [ ] Create Task Manager Page (Checklist view)
- [ ] Create Server Registry Page
- [ ] Create "Important Dates" Calendar/List view

## Phase 5: Advanced Features & Integrations
- [ ] **Local AI Integration:**
    - [ ] Set up API endpoint for AI interaction
    - [ ] Create prompt logic for "Analyze my task list" or "Project progress"
- [ ] Add basic Notification/Alert system for overdue dates
- [ ] Add Search functionality for tasks and projects

## Phase 6: Deployment & Final Polish
- [ ] Create production configuration (Gunicorn/Nginx)
- [ ] Final UI/UX polish with CSS tweaks
- [ ] Unit testing for core logic
- [ ] Final review and deployment
