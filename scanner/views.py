import celery.exceptions
import redis.exceptions
import socket
from celery.result import AsyncResult

from scanner.models import Scan, CheckInfo, Finding
from scanner.serializers import ScanSerializer, CheckSerializer, FindingSerializer

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.utils import timezone

from .redis_provider import RedisProvider
from .tasks import run_scan_task


class ScanViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Scan objects.
    Supports standard CRUD operations plus:
    - GET /scans/{id}/status/ : retrieve real-time status of scan
    - POST /scans/{id}/run/ : trigger async scan execution
    """
    queryset = Scan.objects.all()
    serializer_class = ScanSerializer

    @swagger_auto_schema(
        method='get',
        operation_description='Retrieve real-time status of a specific scan.',
        responses={200: openapi.Response('Scan Status', schema=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                'status': openapi.Schema(type=openapi.TYPE_STRING),
                'started_at': openapi.Schema(type=openapi.FORMAT_DATETIME),
                'ended_at': openapi.Schema(type=openapi.FORMAT_DATETIME, nullable=True),
            }
        ))}
    )
    @action(detail=True, methods=['get'], url_path='status')
    def status(self, request, pk=None):
        scan = self.get_object()
        data = {
            'id': scan.id,
            'status': scan.status,
            'started_at': scan.started_at,
            'ended_at': scan.ended_at,
        }
        return Response(data)

    @swagger_auto_schema(
        method='post',
        operation_description='Trigger scan execution asynchronously.',
        responses={
            202: openapi.Response('Scan triggered successfully.'),
            400: 'Scan is already in progress.'
        }
    )
    @action(detail=True, methods=['post'], url_path='run')
    def run_scan(self, request, pk=None):
        scan = self.get_object()
        if scan.status == 'in_progress':
            return Response({'detail': 'Scan is already in progress.'}, status=status.HTTP_400_BAD_REQUEST)

        scan.status = 'in_progress'
        scan.started_at = timezone.now()
        scan.ended_at = None

        # Enqueue async scan task with Celery
        task = run_scan_task.delay(scan.id)

        scan.celery_task_id = task.id
        scan.save()

        return Response({'detail': f'Scan {scan.id} has started.'}, status=status.HTTP_202_ACCEPTED)

    @action(detail=True, methods=['get'])
    def celery_task_status(self, request, pk=None):
        """
        Returns the status of the Celery task
        :param request:
        :param pk:
        :return:
        """
        scan = self.get_object()
        task_id = scan.celery_task_id

        if not task_id:
            return Response({'error': 'the scan is not initiated yet'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            result = AsyncResult(task_id)
        except (celery.exceptions.CeleryError, redis.exceptions.RedisError, ConnectionError, socket.error) as e:
            # Catch common connection issues to Redis or Celery backend
            return Response(
                {'error': 'Failed to connect to Celery backend: ' + str(e)},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        except Exception as e:
            return Response(
                {'error': 'Unexpected error: ' + str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        return Response({
            'task_id': task_id,
            'state': result.state,
            'info': result.info,
        })

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        scan = self.get_object()
        task_id = scan.celery_task_id

        if task_id:
            result = AsyncResult(task_id)
            result.revoke(terminate=True, signal='SIGTERM')

            scan.status = 'failed'
            scan.ended_at = timezone.now()
            scan.save()

            redis_conn = RedisProvider()
            redis_conn.delete(scan.id)

            return Response({'status': 'cancelled', 'task_id': task_id})
        else:
            return Response({'error': 'No task running'}, status=400)


class CheckInfoViewSet(viewsets.ModelViewSet):
    queryset = CheckInfo.objects.all()
    serializer_class = CheckSerializer


class FindingViewSet(viewsets.ModelViewSet):
    queryset = Finding.objects.all()
    serializer_class = FindingSerializer
