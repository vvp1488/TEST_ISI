from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Thread, Message


class UserRegisterSerializer(serializers.ModelSerializer):
    """Serializer for User model"""
    class Meta:
        model = User
        fields = ('username', 'email', 'password')


class ThreadCreateSerializer(serializers.ModelSerializer):
    """Serializer for new Thread model"""

    user = serializers.CharField()

    class Meta:
        model = Thread
        fields = ('user', )

    def validate_user(self, value):
        """validate the user field for exists in the system"""

        if value not in [x['username'] for x in User.objects.values('username')]:
            raise serializers.ValidationError(f'User {value} is not register in system')
        return value


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ('text', 'created', 'is_read')


class ThreadSerializer(serializers.ModelSerializer):
    """Serializer for the Thread model"""

    last_message = MessageSerializer(read_only=True, allow_null=True)

    class Meta:
        model = Thread
        fields = ('id', 'participants', 'created', 'updated', 'last_message')

    def to_representation(self, instance):
        """ Include last message in the serializer data"""

        representation = super().to_representation(instance)
        last_messages = self.context.get('last_messages', {})
        last_message = last_messages.get(instance.pk)
        if last_message:
            representation['last_message'] = MessageSerializer(last_message).data
        else:
            representation['last_message'] = None
        return representation

