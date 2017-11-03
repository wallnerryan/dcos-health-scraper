#!/usr/bin/env python

from prometheus_client import start_http_server, Metric, REGISTRY
import requests
requests.packages.urllib3.disable_warnings()
import json
import commands
import sys, os
import time
import logging
logging.basicConfig(level=logging.DEBUG)

class HealthJsonCollector(object):
  def __init__(self, url, svc_u, svc_p):
    self._url = url
    self._svc_u = svc_u
    self._svc_p = svc_p
    self._token = "none"

  def get_token(self):
     logging.info("Getting New Auth Token")
     payload={"uid": self._svc_u, "password": self._svc_p }
     token_r = requests.post('%s/acs/api/v1/auth/login' % self._url, 
                             data=json.dumps(payload), 
                             headers={'Content-Type': 'application/json'},
                             verify=False)
     if token_r.status_code == 200:
       token_json=json.loads(token_r.content)
       self._token = token_json['token']

  def collect(self):

     r = requests.get('%s/system/health/v1/units' % self._url,
                      headers={'Authorization': 'token='+self._token},
                      verify=False)

     # if failed, refresh token
     if r.status_code == 401:
         logging.info("Failed auth, getting new auth token")
         self.get_token()
         self.collect()
     else:
         healthmetrics=r.json()
         for hm in healthmetrics['units']:
            logging.info(hm)           
            hm_removed_periods = hm[u'id'].replace(".", "_")
            hm_removed_dashes = hm_removed_periods.replace("-", "_")
            metric = Metric( hm_removed_dashes,'', 'gauge')
            metric.add_sample(hm_removed_dashes, value=hm[u'health'],
                              labels={'name': hm[u'name'],
                                      'desc': hm[u'description']})
            yield metric
            logging.info("%s:%d" % (hm[u'id'], hm[u'health']))

if __name__ == "__main__":
   if len(sys.argv) > 1:
     if sys.argv[1] == "--help" or sys.argv[1] == "help" or sys.argv[1] == "-help":
       print """
            Make sure HEALTH_SVC_U, HEALTH_SVC_P, and DCOS_URL are set in the environment
            LOGGING_SVC_U: service user used to login to dcos
            LOGGING_SVC_P: service user password used to login to dcos
       
       USAGE:
       %s 
       """ % sys.argv[0]
       exit(0)

   uid = os.environ['HEALTH_SVC_U']
   uid_p = os.environ['HEALTH_SVC_P']
   dcos_url = os.environ['DCOS_URL']

   start_http_server(int(os.environ['PORT0']))
   REGISTRY.register(HealthJsonCollector(dcos_url, uid, uid_p))

   while True: time.sleep(1)
