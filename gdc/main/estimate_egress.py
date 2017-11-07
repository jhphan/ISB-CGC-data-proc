'''
Created on Oct 10, 2017

given a bucket path as input, estimates the egress charge for downloading hte data

@author: michael
'''
import json
import requests
from sys import argv
from urllib2 import urlopen

from google.cloud import storage

def getplace(lat, lon):
    url = "http://maps.googleapis.com/maps/api/geocode/json?"
    url += "latlng=%s,%s&sensor=false" % (lat, lon)
    v = urlopen(url).read()
    j = json.loads(v)
    components = j['results'][0]['address_components']
    country = None
    for c in components:
        if "country" in c['types']:
            country = c['long_name']
            break
    return country

def main(path):
    storage_client = storage.Client(project = 'isb-cgc')
    bucket = storage_client.get_bucket(path)
    location = bucket.location
    method = None
    try:
        for method in dir(bucket):
            print method, getattr(bucket, method)
        print 'methods:\n\t{}\n\n'.format('\n\t'.join((method) for method in dir(bucket)))
        print 'attrs:\n\t{}\n\n'.format('\n\t'.join('{}'.format(key) for key in bucket.__dict__))
    except:
        raise

    try:
        zone = None
        metadata_server = "http://metadata/computeMetadata/v1/instance/zone"
        metadata_flavor = {'Metadata-Flavor' : 'Google'}
        zone = requests.get(metadata_server, headers = metadata_flavor).text.split('/')[-1]
        if location in zone:
            pass
        country = None
    except:
        send_url = 'http://freegeoip.net/json'
        r = requests.get(send_url)
        j = json.loads(r.text)
        lat = j['latitude']
        lon = j['longitude']
        print 'location\n\tlat: {}\n\tlon: {}'.format(lat, lon)
        country = getplace(lat, lon)
        if not country:
            raise ValueError('unable to establish a zone or country to determine egress charges')
    blobs = bucket.list_blobs(max_results=None, page_token=None, prefix=None, delimiter=None, versions=None, projection='noAcl', fields=None, client=None)
    count = 0
    total_size = 0
    for blob in blobs:
        count += 1
        total_size += blob.size
    print '\n\tcountry: {}\n\tzone: {}\n\tblobs({}): combined size: {}'.format(country, zone, count, total_size)

if __name__ == '__main__':
    main(argv[1])
