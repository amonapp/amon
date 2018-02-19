from django.db import models
from django.contrib.postgres.fields import JSONField

CHECK_CHOICES = (
    ('ok', 'ok'),
    ('warn', 'warn'),
    ('crit', 'crit'),
    ('unknown', 'unknown'),
)

METRIC_TYPE_CHOICES = (
    ('metric', 'metric'),
    ('check', 'check'),
)

class Metric(models.Model):
    name = models.CharField(max_length=128)
    type = models.CharField(
        max_length=10,
        choices=METRIC_TYPE_CHOICES,
        default='metric'
    )
    tags = JSONField()
    organization = models.ForeignKey('organizations.Organization', on_delete=models.CASCADE)

    class Meta:
        unique_together = ("name", "tags", 'organization')

    def __unicode__(self):
        return u"Metric - {0}/{1}".format(self.name, self.type)

class MetricData(models.Model):
    metric = models.ForeignKey('Metric', on_delete=models.CASCADE)
    timestamp = models.IntegerField()
    value = models.FloatField()


    class Meta:
        index_together = ["metric", "timestamp"]

    def __unicode__(self):
        return u"Metric - {0}/{1}".format(self.metric.name)

class MetricDataChecks(models.Model):
    metric = models.ForeignKey('Metric', on_delete=models.CASCADE)
    timestamp = models.IntegerField()
    value = models.CharField(
        max_length=10,
        choices=CHECK_CHOICES,
        default='unknown'
    )
    message = models.TextField()

    class Meta:
        index_together = ["metric", "timestamp"]


    def __unicode__(self):
        return u"Metric - {0}/{1}".format(self.metric.name)