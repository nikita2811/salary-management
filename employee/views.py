from django.shortcuts import render

# Create your views here.

from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Employee
from .serializers import EmployeeSerializer, EmployeeListSerializer
from rest_framework.decorators import action
from django.db.models import Case, When, Value, CharField
from django.db.models import Min, Max, Avg, Count, F, ExpressionWrapper, DecimalField
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters


# -- used modelviewset for CRUD operations
class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all().order_by('id')
    serializer_class = EmployeeSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields   = ['first_name', 'last_name', 'email'] 
    

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

    
    @action(detail=False, methods=['get'], url_path='insights/country')
    def salary_by_country(self, request):
        country = request.query_params.get('country', None)

        queryset = Employee.objects.filter(is_active=True)

        if country:
            queryset = queryset.filter(country=country)

        data = (
            queryset
            .values('country')
            .annotate(
                min_salary = Min('salary'),
                max_salary = Max('salary'),
                avg_salary = Avg('salary'),
                headcount  = Count('id'),
            )
            .order_by('country')
        )

        return Response(data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'], url_path='insights/job-title')
    def salary_by_job_title(self, request):
      country   = request.query_params.get('country', None)
      job_title = request.query_params.get('job_title', None)
  
      queryset = Employee.objects.filter(is_active=True)
  
      if country:
          queryset = queryset.filter(country=country)
  
      if job_title:
          queryset = queryset.filter(job_title=job_title)
  
      data = (
          queryset
          .values('country', 'job_title')
          .annotate(
              avg_salary = Avg('salary'),
              min_salary = Min('salary'),
              max_salary = Max('salary'),
              headcount  = Count('id'),
          )
          .order_by('country', 'job_title')
      )
  
      return Response(data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'], url_path='insights/department')
    def salary_by_department(self, request):
        department = request.query_params.get('department', None)
    
        queryset = Employee.objects.filter(is_active=True)
    
        if department:
            queryset = queryset.filter(department=department)
    
        data = (
            queryset
            .values('department')
            .annotate(
                min_salary    = Min('salary'),
                max_salary    = Max('salary'),
                avg_salary    = Avg('salary'),
                headcount     = Count('id'),
                salary_range  = Max('salary') - Min('salary'),
            )
            .order_by('department')
        )
    
        return Response(data, status=status.HTTP_200_OK)




    @action(detail=False, methods=['get'], url_path='insights/experience-bands')
    def salary_by_experience_band(self, request):

        queryset = Employee.objects.filter(is_active=True)
    
        data = (
            queryset
            .annotate(
                experience_band=Case(
                    When(experience_years__lte=2,  then=Value('0-2 years')),
                    When(experience_years__lte=5,  then=Value('3-5 years')),
                    When(experience_years__lte=10, then=Value('6-10 years')),
                    default=Value('10+ years'),
                    output_field=CharField(),
                )
            )
            .values('experience_band')
            .annotate(
                avg_salary = Avg('salary'),
                min_salary = Min('salary'),
                max_salary = Max('salary'),
                headcount  = Count('id'),
            )
            .order_by('experience_band')
        )
    
        return Response(data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='count')
    def employee_count(self, request):
            count = Employee.objects.filter(is_active=True).count()
            return Response({"count": count}, status=status.HTTP_200_OK)
      
    
