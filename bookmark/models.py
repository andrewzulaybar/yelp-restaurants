from django.db import models


class Restaurant(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=100)
    business_id = models.CharField(max_length=100)
    visited = models.BooleanField()
    bookmark = models.BooleanField()

    def __str__(self):
        return self.name
