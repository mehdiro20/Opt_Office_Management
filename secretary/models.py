from django.db import models
from django.utils import timezone
import jdatetime


class Patient(models.Model):
    STATUS_CHOICES = [
        ("waiting", "Waiting (Secretary list)"),
        ("accepted", "Accepted (Doctor list)"),
        ("done", "Done (Removed from both lists)"),
    ]

    patient_id = models.CharField(max_length=20, unique=True, editable=False)
    name = models.CharField(max_length=100)
    
    phone = models.CharField(max_length=15, blank=True, null=True)
    age = models.PositiveIntegerField()
    gender = models.CharField(max_length=1, choices=[('M', 'Male'), ('F', 'Female')])
    melli_code = models.CharField(max_length=10, unique=True, blank=True, null=True)
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='waiting')
    created_at = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        if not self.patient_id:
            now_jalali = jdatetime.datetime.now()
            year = now_jalali.year
            month = now_jalali.month

            # Determine season
            if 1 <= month <= 3:
                season_number = 1
            elif 4 <= month <= 6:
                season_number = 2
            elif 7 <= month <= 9:
                season_number = 3
            else:
                season_number = 4

            # Start of season (first day of first month in season)
            start_of_season = jdatetime.datetime(
                year, (season_number - 1) * 3 + 1, 1
            ).togregorian()

            # End of season (last day of last month in season)
            end_month = season_number * 3
            if end_month == 12:
                # next year, month 1
                next_month = jdatetime.datetime(year + 1, 1, 1)
            else:
                next_month = jdatetime.datetime(year, end_month + 1, 1)

            end_of_season = (next_month - jdatetime.timedelta(days=1)).togregorian()

            # Count patients in this season
            count_season = (
                Patient.objects.filter(
                    created_at__gte=start_of_season,
                    created_at__lte=end_of_season
                ).count()
                + 1
            )

            # Generate patient_id
            self.patient_id = f"P{year}S{season_number}{count_season:03d}"

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.patient_id})"
