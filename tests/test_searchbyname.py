from employee.models import Employee
import pytest
from decimal import Decimal


@pytest.mark.django_db
class TestSearchEmployeeByName:

    def test_search_by_first_name(self, api_client, db):
        Employee.objects.create(
            first_name="Arjun", last_name="Mehta",
            email="arjun@company.com", phone="+91-9000000001",
            job_title="Engineer", department="Engineering",
            country="India", city="Bangalore",
            salary=Decimal("95000.00"), employment_type="full_time",
            experience_years=5, joining_date="2020-01-01", skills=[],
        )
        response = api_client.get("/api/employees/?search=Arjun")
        assert response.status_code == 200
        assert response.data["count"] >= 1
        assert any("Arjun" in e["full_name"] for e in response.data["results"])

    def test_search_by_last_name(self, api_client, db):
        Employee.objects.create(
            first_name="Riya", last_name="Sharma",
            email="riya@company.com", phone="+91-9000000002",
            job_title="Designer", department="Design",
            country="India", city="Mumbai",
            salary=Decimal("80000.00"), employment_type="full_time",
            experience_years=3, joining_date="2021-01-01", skills=[],
        )
        response = api_client.get("/api/employees/?search=Sharma")
        assert response.status_code == 200
        assert response.data["count"] >= 1
        assert any("Sharma" in e["full_name"] for e in response.data["results"])

    def test_search_by_partial_name(self, api_client, db):
        Employee.objects.create(
            first_name="Priyanka", last_name="Kapoor",
            email="priyanka@company.com", phone="+91-9000000003",
            job_title="Analyst", department="Finance",
            country="India", city="Delhi",
            salary=Decimal("70000.00"), employment_type="full_time",
            experience_years=2, joining_date="2022-01-01", skills=[],
        )
        response = api_client.get("/api/employees/?search=Priya")
        assert response.status_code == 200
        assert response.data["count"] >= 1

    def test_search_returns_empty_for_no_match(self, api_client, db):
        response = api_client.get("/api/employees/?search=ZZZNoMatch")
        assert response.status_code == 200
        assert response.data["count"] == 0
        assert response.data["results"] == []

    def test_search_is_case_insensitive(self, api_client, db):
        Employee.objects.create(
            first_name="Rahul", last_name="Verma",
            email="rahul@company.com", phone="+91-9000000004",
            job_title="Manager", department="HR",
            country="India", city="Pune",
            salary=Decimal("100000.00"), employment_type="full_time",
            experience_years=6, joining_date="2019-01-01", skills=[],
        )
        response_lower = api_client.get("/api/employees/?search=rahul")
        response_upper = api_client.get("/api/employees/?search=RAHUL")
        assert response_lower.data["count"] == response_upper.data["count"]

    def test_search_excludes_inactive_employees(self, api_client, db):
        Employee.objects.create(
            first_name="Inactive", last_name="User",
            email="inactive@company.com", phone="+91-9000000005",
            job_title="Engineer", department="Engineering",
            country="India", city="Bangalore",
            salary=Decimal("90000.00"), employment_type="full_time",
            experience_years=4, joining_date="2020-01-01", skills=[],
            is_active=False,
        )
        response = api_client.get("/api/employees/?search=Inactive")
        assert response.data["count"] == 0