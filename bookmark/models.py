from django.db import models


class Restaurant(models.Model):
    business_id = models.CharField(max_length=100)
    visited = models.BooleanField()
    bookmark = models.BooleanField()
