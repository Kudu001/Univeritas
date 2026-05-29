from rest_framework import serializers
from .models import AuditLog


class AuditLogSerializer(serializers.ModelSerializer):
    actor_email = serializers.SerializerMethodField()

    class Meta:
        model = AuditLog
        fields = ('id', 'actor', 'actor_email', 'action', 'object_repr',
                  'changes', 'ip_address', 'timestamp', 'extra')

    def get_actor_email(self, obj):
        return obj.actor.email if obj.actor else None
