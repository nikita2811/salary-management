import pytest
from decimal import Decimal
from django.utils import timezone
from employee.models import Employee
import time


# -- Fixtures 

@pytest.fixture
def valid_employee_data():
    """Minimum valid data to create an employee."""
    return {
        'first_name'      : 'John',
        'last_name'       : 'Smith',
        'email'           : 'john.smith@company.com',
        'phone'           : '+1-555-123-4567',
        'job_title'       : 'Software Engineer',
        'department'      : 'Engineering',
        'country'         : 'India',
        'city'            : 'Bangalore',
        'salary'          : Decimal('95000.00'),
        'currency'        : 'USD',
        'employment_type' : 'full_time',
        'experience_years': 5,
        'joining_date'    : '2020-01-15',
        'skills'          : ['Python', 'Django', 'AWS'],
        'is_active'       : True,
    }


@pytest.fixture
def employee(valid_employee_data):
    return Employee.objects.create(**valid_employee_data)


# -- Identity Tests 

@pytest.mark.django_db
class TestEmployeeIdentity:
    """Tests for employee identity fields."""

    def test_employee_has_first_name(self, employee):
        # RED: does first_name exist on model?
        assert employee.first_name == 'John'

    def test_employee_has_last_name(self, employee):
        assert employee.last_name == 'Smith'

    def test_full_name_combines_first_and_last(self, employee):
        # RED: does full_name property return correct value?
        assert employee.full_name == 'John Smith'

    def test_full_name_is_not_a_db_field(self):
        # RED: full_name should be a property, not stored in DB
        fields = [f.name for f in Employee._meta.get_fields()]
        assert 'full_name' not in fields

    def test_employee_has_unique_email(self, employee, valid_employee_data):
        # RED: duplicate email should raise exception
        valid_employee_data['email'] = 'john.smith@company.com'  # same email
        with pytest.raises(Exception):
            Employee.objects.create(**valid_employee_data)

    def test_employee_has_phone(self, employee):
        assert employee.phone == '+1-555-123-4567'

    def test_str_representation(self, employee):
        # RED: __str__ should return "Full Name — Job Title"
        assert str(employee) == 'John Smith — Software Engineer'


# -- Role Tests 

@pytest.mark.django_db
class TestEmployeeRole:
    """Tests for job role fields."""

    def test_employee_has_job_title(self, employee):
        assert employee.job_title == 'Software Engineer'

    def test_employee_has_department(self, employee):
        assert employee.department == 'Engineering'

    def test_employment_type_defaults_to_full_time(self, valid_employee_data):
        # RED: employment_type should default to full_time
        valid_employee_data.pop('employment_type')
        valid_employee_data['email'] = 'default@company.com'
        emp = Employee.objects.create(**valid_employee_data)
        assert emp.employment_type == 'full_time'

    def test_employment_type_accepts_valid_choices(self, valid_employee_data):
        for emp_type in ['full_time', 'part_time', 'contractor']:
            valid_employee_data['email'] = f'{emp_type}@company.com'
            valid_employee_data['employment_type'] = emp_type
            emp = Employee.objects.create(**valid_employee_data)
            assert emp.employment_type == emp_type


# -- Location Tests 

@pytest.mark.django_db
class TestEmployeeLocation:
    """Tests for location fields."""

    def test_employee_has_country(self, employee):
        assert employee.country == 'India'

    def test_employee_has_city(self, employee):
        assert employee.city == 'Bangalore'


# -- Compensation Tests 

@pytest.mark.django_db
class TestEmployeeCompensation:
    """Tests for salary and compensation fields."""

    def test_employee_has_salary(self, employee):
        assert employee.salary == Decimal('95000.00')

    def test_salary_is_decimal(self, employee):
        # RED: salary should be stored as Decimal, not float
        assert isinstance(employee.salary, Decimal)

    def test_currency_defaults_to_usd(self, valid_employee_data):
        valid_employee_data.pop('currency')
        valid_employee_data['email'] = 'nocurrency@company.com'
        emp = Employee.objects.create(**valid_employee_data)
        assert emp.currency == 'USD'

    def test_salary_supports_large_values(self, valid_employee_data):
        # RED: CEO level salary should be storable
        valid_employee_data['email']  = 'ceo@company.com'
        valid_employee_data['salary'] = Decimal('450000.00')
        emp = Employee.objects.create(**valid_employee_data)
        assert emp.salary == Decimal('450000.00')


# -- Experience & Joining Tests 

@pytest.mark.django_db
class TestEmployeeExperience:
    """Tests for experience and joining date fields."""

    def test_employee_has_experience_years(self, employee):
        assert employee.experience_years == 5

    def test_experience_defaults_to_zero(self, valid_employee_data):
        valid_employee_data.pop('experience_years')
        valid_employee_data['email'] = 'noexp@company.com'
        emp = Employee.objects.create(**valid_employee_data)
        assert emp.experience_years == 0

    def test_employee_has_joining_date(self, employee):
        assert str(employee.joining_date) == '2020-01-15'


# -- Skills Tests 

@pytest.mark.django_db
class TestEmployeeSkills:
    """Tests for skills JSONField."""

    def test_skills_is_list(self, employee):
        # RED: skills should always be a list
        assert isinstance(employee.skills, list)

    def test_skills_contains_correct_values(self, employee):
        assert 'Python' in employee.skills
        assert 'Django' in employee.skills
        assert 'AWS'    in employee.skills

    def test_skills_defaults_to_empty_list(self, valid_employee_data):
        valid_employee_data.pop('skills')
        valid_employee_data['email'] = 'noskills@company.com'
        emp = Employee.objects.create(**valid_employee_data)
        assert emp.skills == []

    def test_skills_can_be_updated(self, employee):
        employee.skills = ['Python', 'FastAPI', 'Docker']
        employee.save()
        employee.refresh_from_db()
        assert 'FastAPI' in employee.skills


# -- Org / Manager Tests 

@pytest.mark.django_db
class TestEmployeeOrg:
    """Tests for reporting manager relationship."""

    def test_reporting_manager_defaults_to_none(self, employee):
        assert employee.reporting_manager is None

    def test_can_assign_reporting_manager(self, employee, valid_employee_data):
        # RED: should be able to assign another employee as manager
        valid_employee_data['email'] = 'manager@company.com'
        manager = Employee.objects.create(**valid_employee_data)

        employee.reporting_manager = manager
        employee.save()
        employee.refresh_from_db()
        assert employee.reporting_manager == manager

    def test_manager_deletion_sets_null(self, employee, valid_employee_data):
        # RED: deleting manager should not delete employee
        valid_employee_data['email'] = 'todelete@company.com'
        manager = Employee.objects.create(**valid_employee_data)

        employee.reporting_manager = manager
        employee.save()

        manager.delete()
        employee.refresh_from_db()
        assert employee.reporting_manager is None  # SET_NULL worked


# -- Lifecycle Tests 

@pytest.mark.django_db
class TestEmployeeLifecycle:
    """Tests for is_active, created_at, updated_at fields."""

    def test_is_active_defaults_to_true(self, valid_employee_data):
        valid_employee_data.pop('is_active')
        valid_employee_data['email'] = 'active@company.com'
        emp = Employee.objects.create(**valid_employee_data)
        assert emp.is_active is True

    def test_soft_delete(self, employee):
        # RED: deleting should set is_active=False, not remove from DB
        employee.is_active = False
        employee.save()
        employee.refresh_from_db()
        assert employee.is_active is False
        assert Employee.objects.filter(id=employee.id).exists()  # still in DB

    def test_created_at_is_set_on_create(self, employee):
        assert employee.created_at is not None

    def test_updated_at_changes_on_save(self, employee):
        original_updated_at = employee.updated_at
        time.sleep(0.01) 
        employee.first_name = 'Jane'
        employee.save()
        employee.refresh_from_db()
        assert employee.updated_at > original_updated_at