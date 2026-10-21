from django.db import models

class RoutineItem(models.Model):
    CATEGORY_CHOICES = [
        ('MORNING', '1. Morning Routine & Academic Focus'),
        ('MIDDAY', '2. Midday Projects & Rest'),
        ('EVENING', '3. Evening Recreation & HSC Studies'),
        ('AGENCY', '4. Agency & Business Operations'),
        ('HEALTH', '5. Wind Down, Health & Personal Care'),
    ]

    title = models.CharField(max_length=200)       # e.g., "Diploma Studies"
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    start_time = models.TimeField()               # e.g., 07:00
    end_time = models.TimeField()                 # e.g., 09:30
    description = models.TextField(blank=True, null=True) # Details/Note
    is_completed = models.BooleanField(default=False)

    def __str__(self):
        return f"[{self.get_category_display()}] {self.title} ({self.start_time.strftime('%I:%M %p')} - {self.end_time.strftime('%I:%M %p')})"