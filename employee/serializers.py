from rest_framework import serializers
from .models import Employee


class EmployeeSerializer(serializers.ModelSerializer):

    full_name         = serializers.SerializerMethodField()
    reporting_manager = serializers.PrimaryKeyRelatedField(
        queryset=Employee.objects.all(),
        allow_null=True,
        required=False
    )

    class Meta:
        model  = Employee
        fields = [
            # -- Identity 
            'id',
            'first_name',
            'last_name',
            'full_name',
            'email',
            'phone',

            # -- Role 
            'job_title',
            'department',
            'employment_type',

            # -- Location 
            'country',
            'city',

            # -- Compensation 
            'salary',
            'currency',

            # -- Experience & Joining 
            'experience_years',
            'joining_date',

            # -- Org 
            'reporting_manager',

            # -- Skills 
            'skills',

            # -- Lifecycle 
            'is_active',

            # -- Audit 
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'full_name', 'created_at', 'updated_at']

    def get_full_name(self, obj):
        return obj.full_name

    def validate_salary(self, value):
        if value <= 0:
            raise serializers.ValidationError("Salary must be a positive value.")
        return value

    def validate_skills(self, value):
        if not isinstance(value, list):
            raise serializers.ValidationError("Skills must be a list.")
        if not all(isinstance(s, str) for s in value):
            raise serializers.ValidationError("Each skill must be a string.")
        return value

    def validate_experience_years(self, value):
        if value < 0:
            raise serializers.ValidationError("Experience years cannot be negative.")
        return value


class EmployeeListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views — avoids fetching unnecessary fields."""

    full_name = serializers.SerializerMethodField()

    class Meta:
        model  = Employee
        fields = [
            'id', 'full_name', 'job_title',
            'department', 'country', 'city',
            'salary', 'employment_type', 'is_active',
        ]

    def get_full_name(self, obj):
        return obj.full_name