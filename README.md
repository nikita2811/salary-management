# Salary Management Tool — Artifacts & Engineering Decisions

## 1. Development Approach: TDD

I followed the **Test-Driven Development (TDD)** lifecycle throughout the project:

- Tests were written **before** the implementation code
- Each feature followed the Red → Green → Refactor cycle
- Used **pytest** and **pytest-django** as the testing framework, with **factory-boy** and **model-bakery** for test data factories
- **pytest-cov** was used to track test coverage

**Continuous Integration** was set up via **GitHub Actions** — on every push, the CI pipeline runs the full test suite automatically, ensuring no regressions are introduced.

---

## 2. Planning & Design Notes

### Database Design

- Kept the schema intentionally simple: **a single `Employee` table** covering all required fields
- This avoids unnecessary joins for a dataset of 10,000 employees and keeps queries fast and predictable
- Added **database indexes** on the following columns to optimise the most common query patterns:
  - `country`
  - `job_title`
  - `department`
- These are the primary filter and aggregation axes for salary insights (min/max/avg by country, avg by job title in a country, etc.), so indexing them directly translates to query performance at scale

### API Design

- Used **Django REST Framework ModelViewSets** for CRUD operations — this gave full CRUD with minimal boilerplate and a consistent, RESTful URL structure
- Created **two serializers** to avoid over-fetching:
  - `EmployeeSerializer` — full detail serializer used for create, update, and retrieve operations
  - `EmployeeListSerializer` — lightweight serializer used for list views, returning only the fields needed for the table UI (avoids sending heavy fields across large paginated responses)
- Used **django-filter** for server-side filtering by country, job title, and department

### Salary Insights

Aggregation endpoints compute the following metrics directly in the database (using Django ORM `aggregate` / `annotate`):

- Minimum, maximum, and average salary per country
- Average salary for a given job title within a country
- Additional meaningful metrics surfaced for the HR Manager persona

---

## 3. Seeding Script

The seed script (`python manage.py seed`) is designed to be **re-runnable and performant**:

| Flag | Purpose |
|---|---|
| `--total` | Set the number of employees to generate (default: 10,000) |
| `--fresh` | Wipe existing data before seeding (idempotent re-seeding) |
| `--batch-size` | Control the number of rows inserted per database transaction (bulk insert batching) |

**Design decisions:**
- First and last names are sourced from separate `first_names.txt` and `last_names.txt` files, making the name data easy to swap or extend without touching code
- `bulk_create` is used with configurable batch sizes to significantly reduce the number of database round-trips — critical for inserting 10,000 rows efficiently
- The script is safe to run repeatedly in dev/CI environments

---

## 4. Infrastructure & Deployment

- **Docker** is used for containerisation — a `Dockerfile` and `docker-compose.yml` are provided for local development
- **Backend** deployed on **https://salary-management-b8pb.onrender.com**
- **Frontend** deployed on **https://salary-frontend-nine.vercel.app/**
- **SQLite** is used as the relational database, persisted via a Docker named volume in local environments and via Render's persistent disk in production
- **Gunicorn** is used as the production WSGI server
## Demo Video
[watch Demo Video][https://drive.google.com/file/d/1Wnj56-qbfTCXxgS6wN4y5gi7LJi63tmn/view?usp=sharing]

---

## 5. AI-Assisted Development

As a backend developer, I used AI tooling specifically to bridge my weaker area — **UI/frontend design** — rather than to generate core backend logic.

**How I prompted AI:**

I followed a consistent prompt structure for reliable, targeted output:

| Element | Purpose |
|---|---|
| **Role** | Set the context — e.g. *"You are a senior React developer"* |
| **Task** | State exactly what to build — e.g. *"Build a salary insights dashboard component"* |
| **Objective** | Explain the goal — e.g. *"The HR manager needs to compare salaries across countries at a glance"* |
| **Output format** | Specify constraints — e.g. *"Return a single React functional component using Tailwind, no external state library"* |

**Where AI was used:**
- Frontend component design and layout (React/Next.js) — my primary use case
- UI decisions like component structure, data display patterns, and responsive layout

**Where AI was NOT used:**
- Backend architecture — models, serializers, viewsets, and query design were written and reasoned through manually
- Test cases — written by hand following TDD practice, before implementation
- Database and indexing decisions — made based on the scale requirement (10,000 employees)

---

## 6. Trade-off Explanations

### Single Table vs. Normalised Schema

**What was done:** All employee data lives in a single `Employee` table with `country`, `department`, and `job_title` stored as plain text fields.

**Why:** For a demonstration/MVP scope, this is the fastest path to a working product. It avoids joins, keeps queries simple, and is easy to reason about.

**The trade-off:** Without lookup tables enforced by foreign key constraints, the data is vulnerable to:
- **Typos** — e.g. `"Enginering"` vs `"Engineering"` would be treated as two distinct departments
- **Inconsistent casing** — `"india"` vs `"India"` vs `"INDIA"` become separate countries in aggregation queries
- **Garbage values** — any free-text string is accepted, so invalid entries silently pollute salary insight calculations

**Production approach:** In a production system, `country`, `department`, and `job_title` would each be their own lookup table with a foreign key on `Employee`. This enforces referential integrity at the database level — a value that doesn't exist in the lookup table simply cannot be inserted — eliminating the entire class of typo/garbage-value bugs. The trade-off there is slightly more complex queries (joins) and a more involved seed/onboarding flow to pre-populate the lookup tables.

---

## 7. Tech Stack Summary

| Layer | Choice |
|---|---|
| Backend framework | Django + Django REST Framework |
| Database | SQLite |
| Testing | pytest, pytest-django, factory-boy, model-bakery |
| Linting | ruff |
| CI | GitHub Actions |
| Containerisation | Docker + docker-compose |
| Deployment | Render |
