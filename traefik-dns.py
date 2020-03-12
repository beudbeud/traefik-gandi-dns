#!/usr/bin/env python

import os
import sys
import requests
from ruamel.yaml import YAML
import configparser

config = configparser.ConfigParser()
config.read('/etc/traefik-dns/gandi.cfg')

gandi = config['DEFAULT']

apikey = os.getenv('APIKEY', gandi['apikey'])
ip_traefik = os.getenv('IP_TRAEFIK', gandi['ip_traefik'])
traefik_user = gandi['traefik_user']
traefik_passwd = gandi['traefik_passwd']
zone_uuid = os.getenv('ZUUID', gandi['zone_uuid'])
dns_type = gandi.get('dns_type', 'CNAME')
dns_value = gandi['dns_value']
dns_ttl = gandi.get('dns_ttl', 3600)

traefik_endpoint = 'https://%s/api/http/routers' % (ip_traefik)
gandi_endpoint = 'https://dns.api.gandi.net/api/v5/zones/%s/records' % (zone_uuid)
headers = {'Content-type': 'application/json', 'X-Api-Key': apikey}

yaml = YAML()

try:
    r = requests.get(traefik_endpoint, auth=(traefik_user, traefik_passwd))
except requests.exceptions.RequestException as e:  # This is the correct syntax
    print(e)
    sys.exit(1)

routers = yaml.load(r.text)
hosts = []

for i in routers:
    hosts.append(i['rule'].split('`', 1)[1].split('.')[0])

for host in hosts:
    r = requests.get(gandi_endpoint + "/" + host, headers=headers)
    if r.text == "[]":
        print("Create a new entry for " + host)
        datas = {"rrset_name": host,
                 "rrset_type": dns_type,
                 "rrset_ttl": dns_ttl,
                 "rrset_values": [dns_value]}
        r = requests.post(gandi_endpoint, json=datas, headers=headers)
        print(r.text)
    else:
        print(host + " is already exist")
