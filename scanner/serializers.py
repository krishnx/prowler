from rest_framework import serializers
from .models import Scan, CheckInfo, Finding


class FindingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Finding
        fields = ['id', 'check_info', 'severity', 'description']
        read_only_fields = ('id',)


class CheckSerializer(serializers.ModelSerializer):
    findings = FindingSerializer(many=True, read_only=True)

    class Meta:
        model = CheckInfo
        fields = ['id', 'scan', 'name', 'description', 'findings']
        read_only_fields = ('id',)


class ScanSerializer(serializers.ModelSerializer):
    checks = CheckSerializer(many=True, read_only=True)
    celery_task_id = serializers.CharField(read_only=True)

    class Meta:
        model = Scan
        fields = ['id', 'celery_task_id', 'status', 'started_at', 'ended_at', 'checks']
        read_only_fields = ('id',)
