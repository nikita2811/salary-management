from django.db import models
import uuid

# Create your models here.



class Employee(models.Model):

    EMPLOYMENT_TYPE_CHOICES = [
        ('full_time',   'Full Time'),
        ('part_time',   'Part Time'),
        ('contractor',  'Contractor'),
    ]

    # -- Identity 
    id          = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name  = models.CharField(max_length=100)
    last_name   = models.CharField(max_length=100)
    email       = models.EmailField(unique=True)
    phone       = models.CharField(max_length=20)

    # -- Role 
    job_title        = models.CharField(max_length=255)
    department       = models.CharField(max_length=255)
    employment_type  = models.CharField(max_length=20, choices=EMPLOYMENT_TYPE_CHOICES, default='full_time')

    # -- Location 
    country = models.CharField(max_length=100)
    city    = models.CharField(max_length=100)

    # -- Compensation
    salary   = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=10, default='USD')

    # -- Experience & Joining 
    experience_years = models.PositiveIntegerField(default=0)
    joining_date     = models.DateField()

    # -- Org 
    reporting_manager = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='direct_reports'
    )

    # -- Skills 
    skills = models.JSONField(default=list)   

    # -- Lifecycle 
    is_active = models.BooleanField(default=True)

    # -- Audit 
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'employees'
        # -- Added Indexes for metrics queries
        indexes = [
            models.Index(fields=['country'],              name='idx_employees_country'),
            models.Index(fields=['job_title'],            name='idx_employees_job_title'),
            models.Index(fields=['department'],           name='idx_employees_department'),
            models.Index(fields=['country', 'job_title'], name='idx_employees_country_title'),
        ]    

    def __str__(self):
        return f"{self.first_name} {self.last_name} — {self.job_title}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
