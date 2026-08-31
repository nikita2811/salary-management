import pytest
from decimal import Decimal
from employee.models import Employee
from employee.serializers import EmployeeSerializer, EmployeeListSerializer


# -- Fixtures 

@pytest.fixture
def valid_data():
    """Minimum valid payload to create an employee."""
    return {
        'first_name'      : 'John',
        'last_name'       : 'Smith',
        'email'           : 'john.smith@company.com',
        'phone'           : '+1-555-123-4567',
        'job_title'       : 'Software Engineer',
        'department'      : 'Engineering',
        'country'         : 'India',
        'city'            : 'Bangalore',
        'salary'          : '95000.00',
        'currency'        : 'USD',
        'employment_type' : 'full_time',
        'experience_years': 5,
        'joining_date'    : '2020-01-15',
        'skills'          : ['Python', 'Django', 'AWS'],
        'is_active'       : True,
    }


@pytest.fixture
def employee(valid_data):
    return Employee.objects.create(**{
        **valid_data,
        'salary': Decimal('95000.00'),
    })


# -- Valid Data Tests 

@pytest.mark.django_db
class TestEmployeeSerializerValid:
    """Tests for valid data serialization and deserialization."""

    def test_serializer_with_valid_data_is_valid(self, valid_data):
        serializer = EmployeeSerializer(data=valid_data)
        assert serializer.is_valid(), serializer.errors

    def test_serializer_saves_employee(self, valid_data):
        serializer = EmployeeSerializer(data=valid_data)
        assert serializer.is_valid()
        emp = serializer.save()
        assert Employee.objects.filter(email='john.smith@company.com').exists()

    def test_serializer_returns_full_name(self, employee):
        serializer = EmployeeSerializer(employee)
        assert serializer.data['full_name'] == 'John Smith'

    def test_serializer_returns_all_fields(self, employee):
        serializer = EmployeeSerializer(employee)
        expected_fields = [
            'id', 'first_name', 'last_name', 'full_name', 'email', 'phone',
            'job_title', 'department', 'employment_type', 'country', 'city',
            'salary', 'currency', 'experience_years', 'joining_date',
            'reporting_manager', 'skills', 'is_active', 'created_at', 'updated_at',
        ]
        for field in expected_fields:
            assert field in serializer.data

    def test_serializer_returns_correct_salary(self, employee):
        serializer = EmployeeSerializer(employee)
        assert Decimal(serializer.data['salary']) == Decimal('95000.00')

    def test_serializer_returns_skills_as_list(self, employee):
        serializer = EmployeeSerializer(employee)
        assert isinstance(serializer.data['skills'], list)
        assert 'Python' in serializer.data['skills']

    def test_serializer_read_only_fields(self, valid_data):
        # id, full_name, created_at, updated_at should be read only
        serializer = EmployeeSerializer(data=valid_data)
        assert serializer.is_valid()
        assert 'id'         in serializer.Meta.read_only_fields
        assert 'full_name'  in serializer.Meta.read_only_fields
        assert 'created_at' in serializer.Meta.read_only_fields
        assert 'updated_at' in serializer.Meta.read_only_fields


# -- Salary Validation Tests 

@pytest.mark.django_db
class TestSalaryValidation:
    """Tests for salary field validation."""

    def test_negative_salary_is_invalid(self, valid_data):
        valid_data['salary'] = '-5000.00'
        serializer = EmployeeSerializer(data=valid_data)
        assert not serializer.is_valid()
        assert 'salary' in serializer.errors

    def test_zero_salary_is_invalid(self, valid_data):
        valid_data['salary'] = '0.00'
        serializer = EmployeeSerializer(data=valid_data)
        assert not serializer.is_valid()
        assert 'salary' in serializer.errors

    def test_valid_salary_passes(self, valid_data):
        valid_data['salary'] = '150000.00'
        serializer = EmployeeSerializer(data=valid_data)
        assert serializer.is_valid(), serializer.errors

    def test_large_salary_passes(self, valid_data):
        valid_data['salary'] = '450000.00'
        serializer = EmployeeSerializer(data=valid_data)
        assert serializer.is_valid(), serializer.errors

    def test_salary_stored_as_decimal(self, valid_data):
        serializer = EmployeeSerializer(data=valid_data)
        assert serializer.is_valid()
        emp = serializer.save()
        assert isinstance(emp.salary, Decimal)


# -- Skills Validation Tests 

@pytest.mark.django_db
class TestSkillsValidation:
    """Tests for skills JSONField validation."""

    def test_skills_as_string_is_invalid(self, valid_data):
        valid_data['skills'] = 'Python'   # should be list not string
        serializer = EmployeeSerializer(data=valid_data)
        assert not serializer.is_valid()
        assert 'skills' in serializer.errors

    def test_skills_as_dict_is_invalid(self, valid_data):
        valid_data['skills'] = {'skill': 'Python'}   # should be list
        serializer = EmployeeSerializer(data=valid_data)
        assert not serializer.is_valid()
        assert 'skills' in serializer.errors

    def test_skills_as_empty_list_is_valid(self, valid_data):
        valid_data['skills'] = []
        serializer = EmployeeSerializer(data=valid_data)
        assert serializer.is_valid(), serializer.errors

    def test_skills_with_non_string_items_is_invalid(self, valid_data):
        valid_data['skills'] = ['Python', 123, True]  # items must be strings
        serializer = EmployeeSerializer(data=valid_data)
        assert not serializer.is_valid()
        assert 'skills' in serializer.errors

    def test_skills_as_valid_list_passes(self, valid_data):
        valid_data['skills'] = ['Python', 'Django', 'AWS']
        serializer = EmployeeSerializer(data=valid_data)
        assert serializer.is_valid(), serializer.errors


# -- Experience Validation Tests 

@pytest.mark.django_db
class TestExperienceValidation:
    """Tests for experience_years field validation."""

    def test_negative_experience_is_invalid(self, valid_data):
        valid_data['experience_years'] = -1
        serializer = EmployeeSerializer(data=valid_data)
        assert not serializer.is_valid()
        assert 'experience_years' in serializer.errors

    def test_zero_experience_is_valid(self, valid_data):
        valid_data['experience_years'] = 0
        serializer = EmployeeSerializer(data=valid_data)
        assert serializer.is_valid(), serializer.errors

    def test_valid_experience_passes(self, valid_data):
        valid_data['experience_years'] = 10
        serializer = EmployeeSerializer(data=valid_data)
        assert serializer.is_valid(), serializer.errors


# -- Required Field Tests 

@pytest.mark.django_db
class TestRequiredFields:
    """Tests that required fields are enforced."""

    def test_missing_first_name_is_invalid(self, valid_data):
        valid_data.pop('first_name')
        serializer = EmployeeSerializer(data=valid_data)
        assert not serializer.is_valid()
        assert 'first_name' in serializer.errors

    def test_missing_last_name_is_invalid(self, valid_data):
        valid_data.pop('last_name')
        serializer = EmployeeSerializer(data=valid_data)
        assert not serializer.is_valid()
        assert 'last_name' in serializer.errors

    def test_missing_email_is_invalid(self, valid_data):
        valid_data.pop('email')
        serializer = EmployeeSerializer(data=valid_data)
        assert not serializer.is_valid()
        assert 'email' in serializer.errors

    def test_missing_salary_is_invalid(self, valid_data):
        valid_data.pop('salary')
        serializer = EmployeeSerializer(data=valid_data)
        assert not serializer.is_valid()
        assert 'salary' in serializer.errors

    def test_missing_job_title_is_invalid(self, valid_data):
        valid_data.pop('job_title')
        serializer = EmployeeSerializer(data=valid_data)
        assert not serializer.is_valid()
        assert 'job_title' in serializer.errors

    def test_missing_country_is_invalid(self, valid_data):
        valid_data.pop('country')
        serializer = EmployeeSerializer(data=valid_data)
        assert not serializer.is_valid()
        assert 'country' in serializer.errors

    def test_invalid_email_format(self, valid_data):
        valid_data['email'] = 'not-an-email'
        serializer = EmployeeSerializer(data=valid_data)
        assert not serializer.is_valid()
        assert 'email' in serializer.errors

    def test_duplicate_email_is_invalid(self, valid_data, employee):
        valid_data['email'] = 'john.smith@company.com'  # already exists
        serializer = EmployeeSerializer(data=valid_data)
        assert not serializer.is_valid()
        assert 'email' in serializer.errors


# -- Partial Update Tests 

@pytest.mark.django_db
class TestPartialUpdate:
    """Tests for PATCH — partial updates."""

    def test_partial_update_salary(self, employee):
        serializer = EmployeeSerializer(
            employee,
            data={'salary': '110000.00'},
            partial=True
        )
        assert serializer.is_valid(), serializer.errors
        updated = serializer.save()
        assert updated.salary == Decimal('110000.00')

    def test_partial_update_skills(self, employee):
        serializer = EmployeeSerializer(
            employee,
            data={'skills': ['Python', 'FastAPI']},
            partial=True
        )
        assert serializer.is_valid(), serializer.errors
        updated = serializer.save()
        assert 'FastAPI' in updated.skills

    def test_partial_update_does_not_affect_other_fields(self, employee):
        original_email = employee.email
        serializer = EmployeeSerializer(
            employee,
            data={'first_name': 'Jane'},
            partial=True
        )
        assert serializer.is_valid(), serializer.errors
        updated = serializer.save()
        assert updated.email == original_email  # untouched


# -- List Serializer Tests 

@pytest.mark.django_db
class TestEmployeeListSerializer:
    """Tests for lightweight list serializer."""

    def test_list_serializer_returns_limited_fields(self, employee):
        serializer = EmployeeListSerializer(employee)
        expected_fields = [
            'id', 'full_name', 'job_title',
            'department', 'country', 'city',
            'salary', 'employment_type', 'is_active',
        ]
        for field in expected_fields:
            assert field in serializer.data

    def test_list_serializer_excludes_sensitive_fields(self, employee):
        serializer = EmployeeListSerializer(employee)
        assert 'email'            not in serializer.data
        assert 'phone'            not in serializer.data
        assert 'reporting_manager' not in serializer.data

    def test_list_serializer_returns_full_name(self, employee):
        serializer = EmployeeListSerializer(employee)
        assert serializer.data['full_name'] == 'Nikita Saxena'