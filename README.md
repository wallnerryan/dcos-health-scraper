
# DC/OS Systemd Health Scraper

This scraper does a specific thing, that this is.

- Turn /system/health/v1/units into prometheus Gauges


##  How to use

```
docker run -d \
  -e PORT0=3456 \
  -e HEALTH_SVC_U=<user> \
  -e HEALTH_SVC_P=<pass> \
  -e DCOS_URL=https://my.dcos.com \
  -p 9091:3456 \
  wallnerryan/healthscraper:0.0.1

curl http://localhost:9091/metrics
```

## Marathon

Assuming you have the following setup

 - service user username
 - service user password in DC/OS Secrets

