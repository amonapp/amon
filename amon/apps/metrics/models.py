from django.db import models
from django.contrib.postgres.fields import JSONField


class Metric(models.Model):
    name = models.CharField(max_length=128)
    tags = JSONField()
    retention = models.IntegerField()
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


class MetricDataSummary(models.Model):
    metric = models.ForeignKey('Metric', on_delete=models.CASCADE)
    timestamp = models.IntegerField()
    sum = models.FloatField()
    upper = models.FloatField()
    lower = models.FloatField()
    mean = models.FloatField()

    # TODO 
    # upper_90 = models.FloatField()
    # lower_90 = models.FloatField()
    # mean_90 = models.FloatField()
    # sum_90 = models.FloatField()

    count = models.FloatField()

