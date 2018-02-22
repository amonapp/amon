from django.db import models
from django.contrib.postgres.fields import JSONField

CHECK_CHOICES = (
    ('ok', 'ok'),
    ('warn', 'warn'),
    ('crit', 'crit'),
    ('unknown', 'unknown'),
)

class Check(models.Model):
    name = models.CharField(max_length=128)
    tags = JSONField()
    organization = models.ForeignKey('organizations.Organization', on_delete=models.CASCADE)

    class Meta:
        unique_together = ("name", "tags", 'organization')

    def __unicode__(self):
        return u"Check - {0}".format(self.name)

class CheckData(models.Model):
    check = models.ForeignKey('Check', on_delete=models.CASCADE)
    timestamp = models.IntegerField()
    value = models.CharField(
        max_length=10,
        choices=CHECK_CHOICES,
        default='unknown'
    )
    message = models.TextField()

    class Meta:
        index_together = ["check", "timestamp"]


    def __unicode__(self):
        return u"Metric - {0}/{1}".format(self.metric.name)