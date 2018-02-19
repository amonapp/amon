from django.db import models
from django.utils import timezone

class Organization(models.Model):
    name = models.CharField(max_length=255, unique=True)
    date_created = models.DateTimeField(('date created'), default=timezone.now)


    def __unicode__(self):
        return u"Organization: {0}".format(self.name)