#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.db import models
from django.conf import settings


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
    name = models.CharField(max_length=255)
    type = models.CharField(
        max_length=10,
        choices=METRIC_TYPE_CHOICES,
        default='metric'
    )
    account_id = models.IntegerField()

    def __unicode__(self):
        return u"Metric - {0}/{1}".format(self.name, self.type)

class MetricData(models.Model):
    metric = models.ForeignKey(Metric)
    timestamp = models.IntegerField()
    value = models.FloatField()

    def __unicode__(self):
        return u"Metric - {0}/{1}".format(self.metric.name)

class MetricDataChecks(models.Model):
    metric = models.ForeignKey(Metric)
    timestamp = models.IntegerField()
    value = models.CharField(
        max_length=10,
        choices=CHECK_CHOICES,
        default='unknown'
    )

    def __unicode__(self):
        return u"Metric - {0}/{1}".format(self.metric.name)