import pytest
from decimal import Decimal
from employee.models import Employee
import uuid


#test cases for CRUD operations

# -- Fixtures 

@pytest.fixture
def valid_payload():
    return {
        'first_name'      : 'Nikita',
        'last_name'       : 'Saxena',
        'email'           : 'nikitasaxena43@company.com',
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
def employee(valid_payload):
    return Employee.objects.create(**{
        **valid_payload,
        'salary': Decimal('95000.00'),
    })


@pytest.fixture
def multiple_employees():
    employees = [
        Employee(
            first_name='Alice', last_name='Brown',
            email='alice@company.com', phone='+1-555-000-0001',
            job_title='Software Engineer', department='Engineering',
            country='India', city='Bangalore',
            salary=Decimal('80000.00'), currency='USD',
            employment_type='full_time', experience_years=3,
            joining_date='2021-01-01', skills=['Python'], is_active=True,
        ),
        Employee(
            first_name='Bob', last_name='Jones',
            email='bob@company.com', phone='+1-555-000-0002',
            job_title='Data Scientist', department='Data & Analytics',
            country='United States', city='New York',
            salary=Decimal('120000.00'), currency='USD',
            employment_type='full_time', experience_years=7,
            joining_date='2018-06-01', skills=['Python', 'SQL'], is_active=True,
        ),
        Employee(
            first_name='Carol', last_name='White',
            email='carol@company.com', phone='+1-555-000-0003',
            job_title='Product Manager', department='Product',
            country='India', city='Mumbai',
            salary=Decimal('110000.00'), currency='USD',
            employment_type='contractor', experience_years=6,
            joining_date='2019-03-01', skills=['Roadmapping'], is_active=True,
        ),
        Employee(
            first_name='Dan', last_name='Lee',
            email='dan@company.com', phone='+1-555-000-0004',
            job_title='DevOps Engineer', department='Engineering',
            country='India', city='Hyderabad',
            salary=Decimal('90000.00'), currency='USD',
            employment_type='full_time', experience_years=4,
            joining_date='2020-07-01', skills=['Docker', 'AWS'], is_active=False,  # inactive
        ),
    ]
    return Employee.objects.bulk_create(employees)


# -- CREATE Tests

@pytest.mark.django_db
class TestCreateEmployee:

    def test_create_employee_returns_201(self, api_client, valid_payload):
        response = api_client.post('/api/employees/', valid_payload, format='json')
        assert response.status_code == 201

    def test_create_employee_saves_to_db(self, api_client, valid_payload):
        api_client.post('/api/employees/', valid_payload, format='json')
        assert Employee.objects.filter(email='nikitasaxena43@company.com').exists()

    def test_create_employee_returns_correct_data(self, api_client, valid_payload):
        response = api_client.post('/api/employees/', valid_payload, format='json')
        assert response.data['email']      == 'nikitasaxena43@company.com'
        assert response.data['first_name'] == 'Nikita'
        assert response.data['last_name']  == 'Saxena'
        assert response.data['full_name']  == 'Nikita Saxena'

    def test_create_employee_returns_id(self, api_client, valid_payload):
        response = api_client.post('/api/employees/', valid_payload, format='json')
        assert 'id' in response.data
        assert response.data['id'] is not None

    def test_create_employee_missing_required_field(self, api_client, valid_payload):
        valid_payload.pop('email')
        response = api_client.post('/api/employees/', valid_payload, format='json')
        assert response.status_code == 400
        assert 'email' in response.data

    def test_create_employee_invalid_email(self, api_client, valid_payload):
        valid_payload['email'] = 'not-an-email'
        response = api_client.post('/api/employees/', valid_payload, format='json')
        assert response.status_code == 400
        assert 'email' in response.data

    def test_create_employee_duplicate_email(self, api_client, valid_payload, employee):
        response = api_client.post('/api/employees/', valid_payload, format='json')
        assert response.status_code == 400
        assert 'email' in response.data

    def test_create_employee_negative_salary(self, api_client, valid_payload):
        valid_payload['salary'] = '-5000.00'
        response = api_client.post('/api/employees/', valid_payload, format='json')
        assert response.status_code == 400
        assert 'salary' in response.data

    def test_create_employee_invalid_skills(self, api_client, valid_payload):
        valid_payload['skills'] = 'Python'   # should be list
        response = api_client.post('/api/employees/', valid_payload, format='json')
        assert response.status_code == 400
        assert 'skills' in response.data

    def test_create_employee_invalid_employment_type(self, api_client, valid_payload):
        valid_payload['employment_type'] = 'intern'   # not a valid choice
        response = api_client.post('/api/employees/', valid_payload, format='json')
        assert response.status_code == 400
        assert 'employment_type' in response.data


# -- READ Tests 

@pytest.mark.django_db
class TestListEmployees:

    def test_list_returns_200(self, api_client, employee):
        response = api_client.get('/api/employees/')
        assert response.status_code == 200

    def test_list_returns_paginated_response(self, api_client, employee):
        response = api_client.get('/api/employees/')
        assert 'count'    in response.data
        assert 'next'     in response.data
        assert 'previous' in response.data
        assert 'results'  in response.data

   
       

   

   
    


# -- RETRIEVE Tests 

@pytest.mark.django_db
class TestRetrieveEmployee:

    def test_retrieve_returns_200(self, api_client, employee):
        response = api_client.get(f'/api/employees/{employee.id}/')
        assert response.status_code == 200

    def test_retrieve_returns_correct_employee(self, api_client, employee):
        response = api_client.get(f'/api/employees/{employee.id}/')
        assert response.data['email']     == employee.email
        assert response.data['full_name'] == 'Nikita Saxena'

    def test_retrieve_returns_all_fields(self, api_client, employee):
        response = api_client.get(f'/api/employees/{employee.id}/')
        assert 'email'             in response.data
        assert 'phone'             in response.data
        assert 'skills'            in response.data
        assert 'reporting_manager' in response.data

    def test_retrieve_nonexistent_employee_returns_404(self, api_client):
        response = api_client.get(f'/api/employees/{uuid.uuid4()}/')
        assert response.status_code == 404


# -- UPDATE Tests 

@pytest.mark.django_db
class TestUpdateEmployee:

    def test_partial_update_salary_returns_200(self, api_client, employee):
        response = api_client.patch(
            f'/api/employees/{employee.id}/',
            {'salary': '110000.00'},
            format='json'
        )
        assert response.status_code == 200

    def test_partial_update_salary_persists(self, api_client, employee):
        api_client.patch(
            f'/api/employees/{employee.id}/',
            {'salary': '110000.00'},
            format='json'
        )
        employee.refresh_from_db()
        assert employee.salary == Decimal('110000.00')

    def test_partial_update_skills(self, api_client, employee):
        api_client.patch(
            f'/api/employees/{employee.id}/',
            {'skills': ['Python', 'FastAPI', 'Docker']},
            format='json'
        )
        employee.refresh_from_db()
        assert 'FastAPI' in employee.skills

    def test_partial_update_does_not_affect_other_fields(self, api_client, employee):
        original_email = employee.email
        api_client.patch(
            f'/api/employees/{employee.id}/',
            {'first_name': 'Jane'},
            format='json'
        )
        employee.refresh_from_db()
        assert employee.email == original_email

    def test_full_update_returns_200(self, api_client, employee, valid_payload):
        valid_payload['email'] = 'nikitasaxena43@company.com'  # same email
        response = api_client.put(
            f'/api/employees/{employee.id}/',
            valid_payload,
            format='json'
        )
        assert response.status_code == 200

    def test_update_with_invalid_salary_returns_400(self, api_client, employee):
        response = api_client.patch(
            f'/api/employees/{employee.id}/',
            {'salary': '-1000.00'},
            format='json'
        )
        assert response.status_code == 400

    def test_update_nonexistent_employee_returns_404(self, api_client, valid_payload):
        response = api_client.patch(
            f'/api/employees/{uuid.uuid4()}/',
            {'salary': '110000.00'},
            format='json'
        )
        assert response.status_code == 404


# -- DELETE Tests 

@pytest.mark.django_db
class TestDeleteEmployee:

    def test_delete_returns_204(self, api_client, employee):
        response = api_client.delete(f'/api/employees/{employee.id}/')
        assert response.status_code == 204

    def test_delete_soft_deletes_employee(self, api_client, employee):
        api_client.delete(f'/api/employees/{employee.id}/')
        employee.refresh_from_db()
        assert employee.is_active is False

    def test_delete_keeps_record_in_db(self, api_client, employee):
        api_client.delete(f'/api/employees/{employee.id}/')
        assert Employee.objects.filter(id=employee.id).exists()

    def test_deleted_employee_not_in_list(self, api_client, employee):
        api_client.delete(f'/api/employees/{employee.id}/')
        response = api_client.get('/api/employees/')
        ids = [e['id'] for e in response.data['results']]
        assert employee.id not in ids

    def test_delete_nonexistent_employee_returns_404(self, api_client):
        response = api_client.delete(f'/api/employees/{uuid.uuid4()}/')
        assert response.status_code == 404