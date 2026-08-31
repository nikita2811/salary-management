import pytest
from decimal import Decimal
from employee.models import Employee


# -- Fixtures 

@pytest.fixture
def insight_employees():
    employees = [
        # ── India / Software Engineer ────────────────────────────────────────
        Employee(
            first_name='Alice', last_name='Brown',
            email='alice@company.com', phone='+1-555-000-0001',
            job_title='Software Engineer', department='Engineering',
            country='India', city='Bangalore',
            salary=Decimal('80000.00'), currency='USD',
            employment_type='full_time', experience_years=2,
            joining_date='2022-01-01', skills=['Python'], is_active=True,
        ),
        Employee(
            first_name='Bob', last_name='Jones',
            email='bob@company.com', phone='+1-555-000-0002',
            job_title='Software Engineer', department='Engineering',
            country='India', city='Mumbai',
            salary=Decimal('120000.00'), currency='USD',
            employment_type='full_time', experience_years=5,
            joining_date='2019-01-01', skills=['Java'], is_active=True,
        ),
        # ── India / Product Manager ──────────────────────────────────────────
        Employee(
            first_name='Carol', last_name='White',
            email='carol@company.com', phone='+1-555-000-0003',
            job_title='Product Manager', department='Product',
            country='India', city='Hyderabad',
            salary=Decimal('110000.00'), currency='USD',
            employment_type='full_time', experience_years=8,
            joining_date='2016-01-01', skills=['Roadmapping'], is_active=True,
        ),
        # ── United States / Software Engineer ────────────────────────────────
        Employee(
            first_name='Dan', last_name='Lee',
            email='dan@company.com', phone='+1-555-000-0004',
            job_title='Software Engineer', department='Engineering',
            country='United States', city='San Francisco',
            salary=Decimal('150000.00'), currency='USD',
            employment_type='full_time', experience_years=12,
            joining_date='2012-01-01', skills=['Go'], is_active=True,
        ),
        # ── United States / Data Scientist ───────────────────────────────────
        Employee(
            first_name='Eve', last_name='Davis',
            email='eve@company.com', phone='+1-555-000-0005',
            job_title='Data Scientist', department='Data & Analytics',
            country='United States', city='New York',
            salary=Decimal('140000.00'), currency='USD',
            employment_type='contractor', experience_years=4,
            joining_date='2020-01-01', skills=['Python', 'SQL'], is_active=True,
        ),
        # ── Inactive employee — should be excluded from all insights ─────────
        Employee(
            first_name='Frank', last_name='Miller',
            email='frank@company.com', phone='+1-555-000-0006',
            job_title='Software Engineer', department='Engineering',
            country='India', city='Delhi',
            salary=Decimal('90000.00'), currency='USD',
            employment_type='full_time', experience_years=3,
            joining_date='2021-01-01', skills=['Python'], is_active=False,
        ),
    ]
    return Employee.objects.bulk_create(employees)


# -- Country Insights Tests 

@pytest.mark.django_db
class TestCountryInsights:

    def test_country_insights_returns_200(self, api_client, insight_employees):
        response = api_client.get('/api/employees/insights/country/')
        assert response.status_code == 200

    def test_country_insights_returns_all_countries(self, api_client, insight_employees):
        response = api_client.get('/api/employees/insights/country/')
        countries = [r['country'] for r in response.data]
        assert 'India' in countries
        assert 'United States' in countries

    def test_country_insights_correct_min_salary(self, api_client, insight_employees):
        response = api_client.get('/api/employees/insights/country/?country=India')
        india = response.data[0]
        assert Decimal(india['min_salary']) == Decimal('80000.00')

    def test_country_insights_correct_max_salary(self, api_client, insight_employees):
        response = api_client.get('/api/employees/insights/country/?country=India')
        india = response.data[0]
        assert Decimal(india['max_salary']) == Decimal('120000.00')

    def test_country_insights_correct_avg_salary(self, api_client, insight_employees):
        # India active employees: 80k + 120k + 110k = 310k / 3 = 103333.33
        response = api_client.get('/api/employees/insights/country/?country=India')
        india = response.data[0]
        assert Decimal(india['avg_salary']).quantize(Decimal('0.01')) == Decimal('103333.33')

    def test_country_insights_correct_headcount(self, api_client, insight_employees):
        # India has 3 active employees (Frank is inactive)
        response = api_client.get('/api/employees/insights/country/?country=India')
        india = response.data[0]
        assert india['headcount'] == 3

    def test_country_insights_excludes_inactive(self, api_client, insight_employees):
        # Frank is inactive — headcount should be 3 not 4
        response = api_client.get('/api/employees/insights/country/?country=India')
        india = response.data[0]
        assert india['headcount'] == 3

    def test_country_insights_empty_for_unknown_country(self, api_client, insight_employees):
        response = api_client.get('/api/employees/insights/country/?country=Antarctica')
        assert response.status_code == 200
        assert len(response.data) == 0


# -- Job Title Insights Tests 

@pytest.mark.django_db
class TestJobTitleInsights:

    def test_job_title_insights_returns_200(self, api_client, insight_employees):
        response = api_client.get('/api/employees/insights/job-title/')
        assert response.status_code == 200

    def test_job_title_insights_filter_by_country_and_title(self, api_client, insight_employees):
        response = api_client.get(
            '/api/employees/insights/job-title/?country=India&job_title=Software Engineer'
        )
        assert response.status_code == 200
        assert len(response.data) == 1
        result = response.data[0]
        assert result['country']   == 'India'
        assert result['job_title'] == 'Software Engineer'

    def test_job_title_insights_correct_avg_salary(self, api_client, insight_employees):
        # India Software Engineers: 80k + 120k = 200k / 2 = 100k
        response = api_client.get(
            '/api/employees/insights/job-title/?country=India&job_title=Software Engineer'
        )
        result = response.data[0]
        assert Decimal(result['avg_salary']) == Decimal('100000.00')

    def test_job_title_insights_correct_headcount(self, api_client, insight_employees):
        response = api_client.get(
            '/api/employees/insights/job-title/?country=India&job_title=Software Engineer'
        )
        result = response.data[0]
        assert result['headcount'] == 2

    def test_job_title_insights_different_countries(self, api_client, insight_employees):
        # Same job title, different country should return different avg
        india = api_client.get(
            '/api/employees/insights/job-title/?country=India&job_title=Software Engineer'
        ).data[0]
        us = api_client.get(
            '/api/employees/insights/job-title/?country=United States&job_title=Software Engineer'
        ).data[0]
        assert Decimal(india['avg_salary']) != Decimal(us['avg_salary'])
        assert Decimal(us['avg_salary']) == Decimal('150000.00')

    def test_job_title_insights_excludes_inactive(self, api_client, insight_employees):
        # Frank is inactive Software Engineer in India — should not be counted
        response = api_client.get(
            '/api/employees/insights/job-title/?country=India&job_title=Software Engineer'
        )
        result = response.data[0]
        assert result['headcount'] == 2   # not 3

    def test_job_title_insights_empty_for_unknown_title(self, api_client, insight_employees):
        response = api_client.get(
            '/api/employees/insights/job-title/?country=India&job_title=Unknown Title'
        )
        assert response.status_code == 200
        assert len(response.data) == 0


# -- Department Insights Tests 

@pytest.mark.django_db
class TestDepartmentInsights:

    def test_department_insights_returns_200(self, api_client, insight_employees):
        response = api_client.get('/api/employees/insights/department/')
        assert response.status_code == 200

    def test_department_insights_returns_all_departments(self, api_client, insight_employees):
        response = api_client.get('/api/employees/insights/department/')
        departments = [r['department'] for r in response.data]
        assert 'Engineering' in departments
        assert 'Product'     in departments

    def test_department_insights_correct_min_salary(self, api_client, insight_employees):
        response = api_client.get(
            '/api/employees/insights/department/?department=Engineering'
        )
        engineering = response.data[0]
        # active Engineering: Alice 80k, Bob 120k, Dan 150k (Frank inactive)
        assert Decimal(engineering['min_salary']) == Decimal('80000.00')

    def test_department_insights_correct_max_salary(self, api_client, insight_employees):
        response = api_client.get(
            '/api/employees/insights/department/?department=Engineering'
        )
        engineering = response.data[0]
        assert Decimal(engineering['max_salary']) == Decimal('150000.00')

    def test_department_insights_correct_salary_range(self, api_client, insight_employees):
        response = api_client.get(
            '/api/employees/insights/department/?department=Engineering'
        )
        engineering = response.data[0]
        # salary_range = max - min = 150k - 80k = 70k
        assert Decimal(engineering['salary_range']) == Decimal('70000.00')

    def test_department_insights_correct_headcount(self, api_client, insight_employees):
        response = api_client.get(
            '/api/employees/insights/department/?department=Engineering'
        )
        engineering = response.data[0]
        assert engineering['headcount'] == 3   # Alice, Bob, Dan (Frank inactive)

    def test_department_insights_excludes_inactive(self, api_client, insight_employees):
        response = api_client.get(
            '/api/employees/insights/department/?department=Engineering'
        )
        engineering = response.data[0]
        assert engineering['headcount'] == 3   # Frank excluded

    def test_department_insights_empty_for_unknown_department(self, api_client, insight_employees):
        response = api_client.get(
            '/api/employees/insights/department/?department=Unknown'
        )
        assert response.status_code == 200
        assert len(response.data) == 0


# -- Experience Band Insights Tests 

@pytest.mark.django_db
class TestExperienceBandInsights:

    def test_experience_bands_returns_200(self, api_client, insight_employees):
        response = api_client.get('/api/employees/insights/experience-bands/')
        assert response.status_code == 200

    def test_experience_bands_returns_correct_bands(self, api_client, insight_employees):
        response = api_client.get('/api/employees/insights/experience-bands/')
        bands = [r['experience_band'] for r in response.data]
        assert '0-2 years'  in bands
        assert '3-5 years'  in bands
        assert '6-10 years' in bands
        assert '10+ years'  in bands

    def test_experience_band_0_2_correct_headcount(self, api_client, insight_employees):
        response = api_client.get('/api/employees/insights/experience-bands/')
        band = next(r for r in response.data if r['experience_band'] == '0-2 years')
        # Alice has 2 years experience
        assert band['headcount'] == 1

    def test_experience_band_3_5_correct_headcount(self, api_client, insight_employees):
        response = api_client.get('/api/employees/insights/experience-bands/')
        band = next(r for r in response.data if r['experience_band'] == '3-5 years')
        # Bob(5yr) and Eve(4yr) — Frank(3yr) is inactive
        assert band['headcount'] == 2

    def test_experience_band_6_10_correct_headcount(self, api_client, insight_employees):
        response = api_client.get('/api/employees/insights/experience-bands/')
        band = next(r for r in response.data if r['experience_band'] == '6-10 years')
        # Carol has 8 years
        assert band['headcount'] == 1

    def test_experience_band_10_plus_correct_headcount(self, api_client, insight_employees):
        response = api_client.get('/api/employees/insights/experience-bands/')
        band = next(r for r in response.data if r['experience_band'] == '10+ years')
        # Dan has 12 years
        assert band['headcount'] == 1

    def test_experience_band_correct_avg_salary(self, api_client, insight_employees):
        response = api_client.get('/api/employees/insights/experience-bands/')
        band = next(r for r in response.data if r['experience_band'] == '0-2 years')
        # only Alice — 80k
        assert Decimal(band['avg_salary']) == Decimal('80000.00')

    def test_experience_bands_excludes_inactive(self, api_client, insight_employees):
        response = api_client.get('/api/employees/insights/experience-bands/')
        band = next(r for r in response.data if r['experience_band'] == '3-5 years')
        # Frank(3yr) is inactive — only Bob(5) and Eve(4)
        assert band['headcount'] == 2