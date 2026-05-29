from rest_framework import serializers
from ..models import PlagiarismReport


class PlagiarismReportSerializer(serializers.ModelSerializer):
    matches = serializers.SerializerMethodField()

    class Meta:
        model = PlagiarismReport
        fields = ('version_id', 'overall_score', 'flagged', 'status', 'completed_at', 'matches')

    def get_matches(self, obj):
        from .match import PlagiarismMatchSerializer
        return PlagiarismMatchSerializer(obj.matches.all(), many=True).data
