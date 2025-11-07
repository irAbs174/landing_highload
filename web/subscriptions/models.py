from django.db import models

class Subscriber(models.Model):
    phone = models.CharField(max_length=24, unique=True, db_index=True)
    raw_phone = models.CharField(max_length=32, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'subscribers'

    def __str__(self):
        return self.phone
