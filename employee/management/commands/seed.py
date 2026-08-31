"""
Seed command for Employee model with UUID primary key.
Fully driven by txt files in data/ folder.

Performance optimizations:
  - Loads all txt files once into memory
  - Pre-generates all objects before hitting DB
  - bulk_create with batch_size to minimize DB round trips
  - bulk_update for manager assignment in second pass
  - UUID PKs generated in Python (faster than DB-side generation)

Run:                        python manage.py seed
Custom count:               python manage.py seed --total 5000
Custom batch:               python manage.py seed --batch-size 1000
Skip manager assignment:    python manage.py seed --no-managers
"""

import uuid
import random
import string
import time
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path

from django.core.management.base import BaseCommand
from employee.models import Employee


# -- Paths 

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
DATA_DIR = BASE_DIR / 'data'

# -- Static pools (not in txt files) 

EMPLOYMENT_TYPES   = ['full_time', 'part_time', 'contractor']
EMPLOYMENT_WEIGHTS = [0.80, 0.10, 0.10]

CITIES_BY_COUNTRY = {
    'United States' : ['New York', 'San Francisco', 'Austin', 'Seattle', 'Chicago', 'Boston'],
    'United Kingdom': ['London', 'Manchester', 'Edinburgh', 'Birmingham', 'Bristol'],
    'India'         : ['Bangalore', 'Mumbai', 'Hyderabad', 'Pune', 'Chennai', 'Delhi'],
    'Canada'        : ['Toronto', 'Vancouver', 'Montreal', 'Calgary', 'Ottawa'],
    'Germany'       : ['Berlin', 'Munich', 'Hamburg', 'Frankfurt', 'Cologne'],
    'Australia'     : ['Sydney', 'Melbourne', 'Brisbane', 'Perth', 'Adelaide'],
    'France'        : ['Paris', 'Lyon', 'Marseille', 'Toulouse', 'Nice'],
    'Singapore'     : ['Singapore'],
    'Netherlands'   : ['Amsterdam', 'Rotterdam', 'The Hague', 'Utrecht'],
    'Brazil'        : ['São Paulo', 'Rio de Janeiro', 'Brasília', 'Curitiba'],
    'Japan'         : ['Tokyo', 'Osaka', 'Yokohama', 'Nagoya', 'Kyoto'],
    'Ireland'       : ['Dublin', 'Cork', 'Galway', 'Limerick'],
    'Poland'        : ['Warsaw', 'Kraków', 'Wrocław', 'Gdańsk'],
    'Spain'         : ['Madrid', 'Barcelona', 'Valencia', 'Seville'],
    'Sweden'        : ['Stockholm', 'Gothenburg', 'Malmö', 'Uppsala'],
    'Default'       : ['City'],
}

SALARY_RANGE_BY_TITLE = {
    'Software Engineer'            : (70_000,  120_000),
    'Senior Software Engineer'     : (110_000, 170_000),
    'Staff Engineer'               : (150_000, 220_000),
    'Principal Engineer'           : (180_000, 260_000),
    'Engineering Manager'          : (140_000, 210_000),
    'VP of Engineering'            : (200_000, 320_000),
    'CTO'                          : (250_000, 450_000),
    'Product Manager'              : (90_000,  150_000),
    'Senior Product Manager'       : (130_000, 190_000),
    'Director of Product'          : (170_000, 250_000),
    'VP of Product'                : (200_000, 300_000),
    'Data Analyst'                 : (65_000,  100_000),
    'Senior Data Analyst'          : (95_000,  140_000),
    'Data Scientist'               : (100_000, 160_000),
    'Senior Data Scientist'        : (140_000, 200_000),
    'ML Engineer'                  : (120_000, 190_000),
    'DevOps Engineer'              : (90_000,  140_000),
    'Site Reliability Engineer'    : (120_000, 180_000),
    'QA Engineer'                  : (65_000,  100_000),
    'QA Lead'                      : (100_000, 145_000),
    'UI/UX Designer'               : (70_000,  115_000),
    'Senior Designer'              : (100_000, 150_000),
    'Design Lead'                  : (130_000, 180_000),
    'HR Manager'                   : (70_000,  110_000),
    'HR Business Partner'          : (80_000,  120_000),
    'Talent Acquisition Specialist': (55_000,   90_000),
    'HR Director'                  : (120_000, 180_000),
    'Financial Analyst'            : (65_000,  100_000),
    'Senior Financial Analyst'     : (90_000,  135_000),
    'Finance Manager'              : (110_000, 160_000),
    'CFO'                          : (200_000, 400_000),
    'Marketing Manager'            : (75_000,  120_000),
    'Content Strategist'           : (60_000,   95_000),
    'Growth Manager'               : (85_000,  135_000),
    'CMO'                          : (180_000, 300_000),
    'Sales Executive'              : (55_000,  130_000),
    'Account Manager'              : (60_000,  110_000),
    'Sales Manager'                : (90_000,  150_000),
    'VP of Sales'                  : (180_000, 280_000),
    'Customer Success Manager'     : (65_000,  105_000),
    'Support Engineer'             : (55_000,   90_000),
    'Technical Writer'             : (60_000,   95_000),
    'Business Analyst'             : (65_000,  105_000),
    'Scrum Master'                 : (75_000,  115_000),
    'Security Engineer'            : (100_000, 160_000),
    'Cloud Architect'              : (140_000, 210_000),
    'Solutions Architect'          : (130_000, 195_000),
    'Database Administrator'       : (80_000,  125_000),
    'Backend Engineer'             : (80_000,  140_000),
    'Frontend Engineer'            : (75_000,  130_000),
    'Full Stack Engineer'          : (80_000,  145_000),
}

DEFAULT_SALARY_RANGE = (50_000, 100_000)
MANAGER_KEYWORDS     = ['Manager', 'Director', 'VP', 'CTO', 'CFO', 'CMO', 'Lead', 'Head', 'Architect']


# -- Helpers 

def load_txt(filename: str) -> list[str]:
    """Load a txt file from data/ — one value per line."""
    filepath = DATA_DIR / filename
    if not filepath.exists():
        raise FileNotFoundError(
            f"Missing required file: data/{filename}\n"
            f"Expected at: {filepath}"
        )
    values = [line.strip() for line in filepath.read_text(encoding='utf-8').splitlines() if line.strip()]
    if not values:
        raise ValueError(f"data/{filename} is empty — add at least one value.")
    return values


def random_salary(job_title: str) -> Decimal:
    low, high = SALARY_RANGE_BY_TITLE.get(job_title, DEFAULT_SALARY_RANGE)
    return Decimal(str(round(random.uniform(low, high), -2)))


def random_joining_date(experience_years: int) -> date:
    days_ago = experience_years * 365 + random.randint(0, 180)
    return date.today() - timedelta(days=days_ago)


def random_phone() -> str:
    return f'+1-{random.randint(200,999)}-{random.randint(100,999)}-{random.randint(1000,9999)}'


def random_city(country: str) -> str:
    cities = CITIES_BY_COUNTRY.get(country, CITIES_BY_COUNTRY['Default'])
    return random.choice(cities)


def generate_email(first: str, last: str, existing: set) -> str:
    domains = ['company.com', 'corp.io', 'enterprise.net']
    base    = ''.join(c for c in f"{first}.{last}".lower() if c.isalnum() or c == '.')
    email   = f"{base}@{random.choice(domains)}"
    if email in existing:
        suffix = ''.join(random.choices(string.digits, k=4))
        email  = f"{base}.{suffix}@{random.choice(domains)}"
    existing.add(email)
    return email


def is_manager(job_title: str) -> bool:
    return any(keyword in job_title for keyword in MANAGER_KEYWORDS)


# ── Command ───────────────────────────────────────────────────────────────────

class Command(BaseCommand):
    help = 'Seed database with 10,000 employees using UUID primary keys'

    def add_arguments(self, parser):
        parser.add_argument(
            '--total',
            type=int,
            default=10_000,
            help='Number of employees to seed (default: 10000)'
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=500,
            help='Batch size for bulk operations (default: 500)'
        )
        parser.add_argument(
            '--no-managers',
            action='store_true',
            help='Skip manager assignment step'
        )
        parser.add_argument(
        '--fresh',
        action='store_true',
        help='Clear existing employees before seeding. DANGEROUS in production.'
        )

    def handle(self, *args, **options):
        total        = options['total']
        batch_size   = options['batch_size']
        no_managers  = options['no_managers']
        fresh   = options['fresh']

        start_time   = time.perf_counter()

        self.stdout.write(f'\nSeeding {total} employees...\n')

        # -- Load all txt files once into memory 
        try:
            first_names = load_txt('first_names.txt')
            last_names  = load_txt('last_names.txt')
            job_titles  = load_txt('job_titles.txt')
            departments = load_txt('departments.txt')
            countries   = load_txt('countries.txt')
            skills_pool = load_txt('skills.txt')
        except (FileNotFoundError, ValueError) as e:
            self.stderr.write(self.style.ERROR(f'\n❌ {e}\n'))
            return

        self.stdout.write(
            f'  📂 Loaded from data/ folder:\n'
            f'     first_names : {len(first_names)}\n'
            f'     last_names  : {len(last_names)}\n'
            f'     job_titles  : {len(job_titles)}\n'
            f'     departments : {len(departments)}\n'
            f'     countries   : {len(countries)}\n'
            f'     skills      : {len(skills_pool)}\n'
        )

        # -- Clear existing data 
        deleted, _ = Employee.objects.all().delete()
        if deleted:
            self.stdout.write(f'  🗑️  Cleared {deleted} existing employees.\n')

        if fresh:
           confirm = input(
            '⚠️  WARNING: This will delete ALL existing employees. '
            'Type "yes" to continue: '
           )
           if confirm.strip().lower() != 'yes':
               self.stdout.write('Aborted.')
               return
           deleted, _ = Employee.objects.all().delete()
           self.stdout.write(f'  🗑️  Cleared {deleted} existing employees.\n')
        else:
            count = Employee.objects.count()
        if count > 0:
            self.stdout.write(
                f'  ℹ️  {count} existing employees kept — '
                f'use --fresh to clear before seeding.\n'
            )
        # -- Pre-generate all employee objects in memory 
        self.stdout.write('  ⚙️  Generating employee data...')
        existing_emails : set  = set()
        all_employees   : list = []

        for i in range(total):
            first           = random.choice(first_names)
            last            = random.choice(last_names)
            job_title       = random.choice(job_titles)
            department      = random.choice(departments)
            country         = random.choice(countries)
            employment_type = random.choices(EMPLOYMENT_TYPES, EMPLOYMENT_WEIGHTS)[0]
            experience      = random.randint(0, 20)
            n_skills        = random.randint(3, min(6, len(skills_pool)))

            all_employees.append(Employee(
                id                = uuid.uuid4(),       # ← generate UUID in Python
                first_name        = first,
                last_name         = last,
                email             = generate_email(first, last, existing_emails),
                phone             = random_phone(),
                job_title         = job_title,
                department        = department,
                country           = country,
                city              = random_city(country),
                salary            = random_salary(job_title),
                currency          = 'USD',
                employment_type   = employment_type,
                experience_years  = experience,
                joining_date      = random_joining_date(experience),
                skills            = random.sample(skills_pool, n_skills),
                is_active         = True,
                reporting_manager = None,   # assigned in second pass
            ))

            if (i + 1) % 2_000 == 0:
                self.stdout.write(f'  Generated {i + 1}/{total}...')

        # ── Bulk insert in batches ────────────────────────────────────────
        self.stdout.write('\n  💾 Inserting into database...')
        inserted = []
        for start in range(0, total, batch_size):
            batch  = all_employees[start : start + batch_size]
            result = Employee.objects.bulk_create(batch, batch_size=batch_size)
            inserted.extend(result)
            self.stdout.write(f'  Inserted {min(start + batch_size, total)}/{total}...')

        # ── Assign managers (second pass) ─────────────────────────────────
        if not no_managers:
            self.stdout.write('\n  👔 Assigning reporting managers...')
            manager_pool = [e for e in inserted if is_manager(e.job_title)]

            if manager_pool:
                updates = []
                for emp in inserted:
                    if not is_manager(emp.job_title):
                        emp.reporting_manager = random.choice(manager_pool)
                        updates.append(emp)

                for start in range(0, len(updates), batch_size):
                    Employee.objects.bulk_update(
                        updates[start : start + batch_size],
                        ['reporting_manager'],
                        batch_size=batch_size
                    )
                self.stdout.write(f'  Assigned managers to {len(updates)} employees.')
            else:
                self.stdout.write(
                    self.style.WARNING('  ⚠️  No managers found — check job_titles.txt has manager-level titles.')
                )

        # ── Summary ───────────────────────────────────────────────────────
        elapsed = time.perf_counter() - start_time
        self.stdout.write(self.style.SUCCESS(
            f'\n✅ Done! {total} employees seeded in {elapsed:.2f}s\n'
        ))