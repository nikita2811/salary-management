from django.shortcuts import render

# Create your views here.

from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Employee
from .serializers import EmployeeSerializer, EmployeeListSerializer


# -- used modelviewset for CRUD operations
class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all().order_by('id')
    serializer_class = EmployeeSerializer
    

    def get_serializer_class(self):
        if self.action == 'list':
            return EmployeeListSerializer   # lightweight for table view
        return EmployeeSerializer

    def get_queryset(self):
        return Employee.objects.filter(is_active=True).order_by('id')
    
    # -- delete api for soft delete
    def destroy(self, request, *args, **kwargs):
        instance           = self.get_object()
        instance.is_active = False
        instance.save()
        return Response({"message": "Employee deleted."}, status=status.HTTP_204_NO_CONTENT)
    
    
