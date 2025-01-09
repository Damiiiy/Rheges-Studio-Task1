from django.urls import path
from .views import *
urlpatterns = [
    path('tasks/view/<int:task_id>', view_submitted_tasks, name='task-list'),
    path('tasks/create', create_task, name='task-create'),
    path('tasks/upload/', upload_submission, name='task-upload'),
    path('tasks/pending/', list_pending_submission, name='pending-tasks'),
    path('sign-in/', sign_in, name='sign-in'),
    path('sign-out/', sign_out, name='sign-out'),
]
