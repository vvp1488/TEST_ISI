from rest_framework.pagination import LimitOffsetPagination
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .serializers import (
    UserRegisterSerializer,
    ThreadCreateSerializer,
    MessageSerializer, ThreadSerializer,
)
from .models import Thread, Message
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.response import Response


class RegisterUserAPIView(APIView):
    """Register new user in system with post request """

    serializer_class = UserRegisterSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = User.objects.create_user(
                username=serializer.validated_data['username'],
                email=serializer.validated_data['email'],
                password=serializer.validated_data['password']
            )
            user.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ThreadCreateAPIView(APIView):
    """Create new Thread with post request"""

    serializer_class = ThreadCreateSerializer
    permission_classes = [IsAuthenticated, ]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            participant = User.objects.get(username=serializer.validated_data['user'])
            thread = Thread.objects.filter(participants__in=[request.user.id]).filter(participants__in=[participant.id]).first()
            if thread:
                return Response(status=status.HTTP_400_BAD_REQUEST, data={
                        "status": "failure",
                        "detail": f"Thread with  {thread.get_participants()} already exist"
                    }
                )
            else:
                new_thread = Thread.objects.create()
                new_thread.participants.add(request.user, participant)
                return Response(status=status.HTTP_201_CREATED, data={
                    "status": "success",
                    "detail": f"Thread with id={new_thread.id} with participants {new_thread.get_participants()} was completely added"
                })

        else:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={
                "status": "failure",
                "detail": serializer.errors
            })


class MessageListAPIView(APIView):
    """API view for creating or receiving a list of messages for a thread.
    get request - list of messages
    post request - new message for specific thread
    patch request - mark messages as read
    """

    permission_classes = [IsAuthenticated, ]
    pagination_class = LimitOffsetPagination

    def get(self, request, thread_id):
        try:
            thread = Thread.objects.get(pk=thread_id, participants=request.user)
        except Thread.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND, data={
                "status": "failure",
                "detail": 'Thread is not available'
            })
        messages = thread.messages.all()
        paginator = self.pagination_class()
        paginated_messages = paginator.paginate_queryset(messages, request)
        serializer = MessageSerializer(paginated_messages, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request, thread_id):
        """Create a new message for the given thread ID"""

        try:
            thread = Thread.objects.get(pk=thread_id, participants=request.user)
        except Thread.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND, data={
                "status": "failure",
                "detail": 'Thread is not available'
            })
        serializer = MessageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(sender=request.user, thread=thread)
            return Response(status=status.HTTP_201_CREATED, data={
                "status": "success",
                "detail": serializer.data
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, thread_id):
        """For change messages status is_read=True"""

        queryset = Message.objects.filter(thread=thread_id)
        queryset.update(is_read=True)
        return Response(status=status.HTTP_200_OK, data={
            "status": "success",
            "detail": "Messages from thread is read"
        })


class ThreadListAPIView(APIView):
    """List thread for specific user with last message"""

    permission_classes = [IsAuthenticated, ]
    pagination_class = LimitOffsetPagination

    def get(self, request):
        threads = Thread.objects.filter(participants=request.user.id)
        last_messages = {}
        for thread in threads:
            last_message = thread.messages.last()
            if last_message:
                last_messages[thread.pk] = last_message
        paginator = self.pagination_class()
        paginated_threads = paginator.paginate_queryset(threads, request)
        serializer = ThreadSerializer(paginated_threads, many=True, context={'last_messages': last_messages})
        return paginator.get_paginated_response(serializer.data)


class UnreadMessagesCountAPIView(APIView):
    """getting the number of unread messages for the user (not for the thread)"""

    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return Message.objects.filter(
            thread__participants=self.request.user,
            is_read=False
        ).exclude(sender=self.request.user)

    def get(self, request):
        unread_messages_count = self.get_queryset().count()
        return Response(status=status.HTTP_200_OK, data={
            "status": "success",
            "detail": f'Unread messages for {request.user.username} - {unread_messages_count}'
        })


