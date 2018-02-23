# Amon 7.0 Roadmap

7.0 will be the next major Amon release.

It is an almost complete rewrite of the current version, building on the already 
established foundation, going one step further in the areas that make Amon unique 
and implementing the lessons learned from working extensively with InfluxDB, 
Telegraf, Kapacitor, Grafana, Prometheus, Druid and KairosDB.


## Remove Vendor Lock-in for metrics

In Amon 6.0, you can send metrics from different collector agents, like 
CollectD and Telegraf, but the metrics coming from these sources were not 
given equal status as the ones coming from the native Amon collector agent.

In 7.0 all metrics will be equal and the idea is to make it possible
to monitor your infrastructure with 3rd party collectors only, if you choose to do so.

As an Example:

You can choose Datadog to monitor your Windows machines and Telegraf for your Docker containers. 


The reasoning behind this is that the different metrics collectors have varying levels
of support for different types of applications - one agent could be very good for collecting 
Docker metrics and subpar for Database metrics. In Amon 7.0 you should be able to choose the one
which is best for your needs.


## Prometheus Support

Amon 7.0 will have a Prometheus metrics ingest pipeline and will be able to pull metrics from your 
exporters at a specified period of time. 


## No Servers, only tagged Metrics

In Amon 6.0, servers were the main logical unit. The metrics had to come from a specific server to 
be visualized and organized properly. 

In 7.0 and beyond, metrics will be using the following format:


name | value | tags
---- | ----- | ---
cpu  | 45.0  | {"host": "server-01", "region": "eu-central-1", "provider": "digitalocean"} 
memory | 300.0  | {"host": "server-01", "region": "eu-central-1", "provider": "digitalocean"} 


The new format will give you more flexibility and make it possible to group your data in
different logical units, not only servers. For example: sensors, docker containers, etc.


## Improved alerting

Amon 7.0 alerts will add the following features to the alerts

- Alert states - Critical, Warning with separate thresholds for each.
- Option to send alerts only on state change or predefined periods of time. Example: crit, every 1 hour until resolved
- Composite alerts - the option to combine multiple metrics into a single alert
- Visual contenxt - display a graph visualizing metrics and alert conditions


## Plugable Time Series database backends 

Amon 6.0 is using MongoDB for metrics storage, which is not optimal for time series data. 
7.0 will move to PostgreSQL as a default with the possibility to use other time series backends like 
InfluxDB, Druid, KairosDB, Cassandra
