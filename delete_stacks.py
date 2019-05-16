#!/usr/bin/env python

#get promoted stack names

import sys
import boto3
import re

domain = "cloud.mapquest.com."
hostedZoneId = "none"

def get_hosted_zone_id(dns_domain):
  global hostedZoneId
  debug = 0

  for hz in dns_domain.list_hosted_zones()['HostedZones']:
    match = re.match('/hostedzone/([A-Z0-9]+)', hz['Id'])
    if match and hz['Name'] == domain:
      hostedZoneId = match.group(1)
      if debug > 0:
        print("using hosted zone id for", z['Name'], "=", match.group(1))
      return hostedZoneId


def get_cnames(dns_domain):
  global hostedZoneId
  dname = r'navplatform-navapi-(dev|prod).*.cloud.mapquest.com'
  dval = r'(navplatform-navapi-(prod|dev)-[0-9]+).*.cloud.mapquest.com'
  startrname = "dev.navapi-sessions.cloud.mapquest.com."
  cnames = {}
  debug = 0

  rs = dns_domain.list_resource_record_sets(HostedZoneId=hostedZoneId, StartRecordName=startrname)['ResourceRecordSets']
  for r in rs:
    # look for dns name entry for navplatform-navapi prod or dev
    match = re.match(dname, r['Name'])
    if match:
       envname = match.group(1)

       # look to make sure this is CNAME
       match = re.match('CNAME', r['Type'])
       if match:
         for rr in r['ResourceRecords']:

           # get the value of the CNAME, this is active deploy
           m = re.match(dval, rr['Value'])
           if m:
             rrv = m.group(1)
             cnames[envname] = rrv
             if debug > 0:
               print(r['Name'], r['Type'], rrv, cnames[envname])
  if debug > 0:
    print(cnames)

  return cnames


def main():
  debug = 1
  r53 = boto3.client('route53')
  hostedZoneId = get_hosted_zone_id(r53)
  #print("hostedZoneId =", hostedZoneId)

  c = get_cnames(r53)

  if debug > 0:
    print(c)
    print("prod:", c['prod'])
    print("dev:", c['dev'])


if __name__ == "__main__":
  main()

### match = re.match('/hostedzone/([A-Z0-9]+)', hz['Id'])
