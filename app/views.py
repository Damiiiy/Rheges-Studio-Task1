from datetime import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .models import *
from .serializers import SubmissionSerializer, TaskSerializer
from django.utils import timezone

# Create a new task
# Utility function to create tokens
def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

# Sign in
@api_view(['POST'])
@permission_classes([AllowAny])
def sign_in(request):
    username = request.data.get('username')
    password = request.data.get('password')

    if not username or not password:
        return Response({"error": "Username and password are required."}, status=status.HTTP_400_BAD_REQUEST)

    user = authenticate(username=username, password=password)
    if user is None:
        return Response({"error": "Invalid username or password."}, status=status.HTTP_401_UNAUTHORIZED)

    tokens = get_tokens_for_user(user)
    return Response(tokens, status=status.HTTP_200_OK)

# Sign out
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def sign_out(request):
    try:
        refresh_token = request.data.get('refresh')
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response({"message": "Signed out successfully."}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": "Invalid or expired token."}, status=status.HTTP_400_BAD_REQUEST)




@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_task(request):
    serializer = TaskSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_submission(request):

    """
    Endpoint to allow a user to upload a submission for a specific task.
    """

    data = request.data
    task_name = data.get('task_name')

    # checks of the task exists
    try:
        task = Task.objects.get(title=task_name)
    except Task.DoesNotExist:
        return Response({"error": "Task with the given name does not exist."}, status=status.HTTP_404_NOT_FOUND)

    # Checks if the user already submitted on this task or not
    existing_submission = Submissions.objects.filter(task=task, user=request.user).first()
    if existing_submission:
        existing_submission.is_submitted = data.get("is_submitted", False)
        if existing_submission.is_submitted:
            existing_submission.completed_at = timezone.now()  # Set the completed_at timestamp
        else:
            existing_submission.completed_at = None  # Reset completed_at if not approved
        existing_submission.save()
        return Response({"error": "You have successfully updated your submission."}, status=status.HTTP_200_OK)


    # Create the submission
    submission_data = {
        "task": task.id,  
        "is_submitted": data.get("is_submitted", False), 
    }
    # if submission_data["is_approved"] == False:
    #     return Response({"error": "You have not completed the task."}, status=status.HTTP_400_BAD_REQUEST)
    # else:
    serializer = SubmissionSerializer(data=submission_data)

    if serializer.is_valid():
        submission = serializer.save(user=request.user, task=task) 

        if submission.is_submitted:
            submission.completed_at = timezone.now()
            submission.save()
         
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

   


# List all tasks
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def view_submitted_tasks(request, task_id):
    try:
        task = Task.objects.get(id=task_id)
    except Task.DoesNotExist:
        return Response({"error": "Task not found"}, status=status.HTTP_404_NOT_FOUND)
    
    # to show all submiaaion on a given task
    submissions = Submissions.objects.filter(task=task, user=request.user, is_submitted=True)
    
    if not submissions:
        return Response({"message": "No submissions are made on this tasks."}, status=status.HTTP_404_NOT_FOUND)

    serializer = SubmissionSerializer(submissions, many=True)
    return Response(serializer.data)

    # tasks = Task.objects.filter(user=request.user)
    # serializer = TaskSerializer(tasks, many=True)
    # return Response(serializer.data)

# List pending tasks
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_pending_submission(request):
    # Filter pending submissions for the authenticated user
    pending_submissions = Submissions.objects.filter(user=request.user, is_submitted=False)
    
    if not pending_submissions:
        return Response({"message": "No pending submissions."}, status=status.HTTP_404_NOT_FOUND)

    serializer = SubmissionSerializer(pending_submissions, many=True)
    return Response(serializer.data)


    # tasks = Task.objects.filter(user=request.user, is_completed=False)
    # serializer = TaskSerializer(tasks, many=True)
    # return Response(serializer.data)

# Mark a task as completed
