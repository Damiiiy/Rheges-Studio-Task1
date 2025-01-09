from rest_framework import serializers
from .models import Task, Submission
from django.contrib.auth.models import User

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'

class SubmissionSerializer(serializers.ModelSerializer):
    task = serializers.PrimaryKeyRelatedField(queryset=Task.objects.all())  # Accept task ID
    
    class Meta:
        model = Submission
        fields = ['id', 'task', 'user', 'completed_at', 'is_approved']
        read_only_fields = ['user', 'completed_at']
