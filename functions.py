__author__ = 'Andrew'
import math
import urllib2
import os
import time
from xml.dom import minidom as DOM


def calculate_distance(origin, destination):
    lat1, lon1 = origin
    lat2, lon2 = destination
    radius = 6371  # km

    latitude = math.radians(lat2 - lat1)
    longitude = math.radians(lon2 - lon1)
    a = (math.sin(latitude / 2) * math.sin(latitude / 2) + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(longitude / 2)
         * math.sin(longitude / 2))
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    destination = radius * c

    return destination


def get_closest_servers(client, complete=False):
    connection = urllib2.urlopen('http://speedtest.net/speedtest-servers.php')
    server_xml = connection.read()
    if int(connection.code) != 200:
        return None
    connection.close()
    root = DOM.parseString(server_xml)
    servers = {}
    for server in root.getElementsByTagName('server'):
        attrib = dict(server.attributes.items())
        d = calculate_distance([float(client['lat']), float(client['lon'])],
                               [float(attrib.get('lat')), float(attrib.get('lon'))])
        attrib['d'] = d
        if d not in servers:
            servers[d] = [attrib]
        else:
            servers[d].append(attrib)

    closest = []
    for d in sorted(servers.keys()):
        for s in servers[d]:
            closest.append(s)
            if len(closest) == 5 and not complete:
                break
        else:
            continue
        break

    del servers
    del root
    return closest


def get_best_server(servers):
    results = {}
    for server in servers:
        cum = 0
        url = os.path.dirname(server['url'])
        for i in xrange(0, 3):
            uh = urllib2.urlopen('%s/latency.txt' % url)
            start = time.time()
            text = uh.read().strip()
            total = time.time() - start
            if int(uh.code) == 200 and text == 'test=test':
                cum += total
            else:
                cum += 3600
            uh.close()
        avg = round((cum / 3) * 1000000, 3)
        results[avg] = server

    fastest = sorted(results.keys())[0]
    best = results[fastest]
    best['latency'] = fastest

    return best


def get_config():
    uh = urllib2.urlopen('http://www.speedtest.net/speedtest-config.php')
    config_xml = uh.read()
    if int(uh.code) != 200:
        return None
    uh.close()
    root = DOM.parseString(config_xml)
    config = {
        'client': extract_tag_name(root, 'client'),
        'times': extract_tag_name(root, 'times'),
        'download': extract_tag_name(root, 'download'),
        'upload': extract_tag_name(root, 'upload')}

    del root
    return config


def extract_tag_name(dom, tag_name):
    elem = dom.getElementsByTagName(tag_name)[0]
    return dict(elem.attributes.items())


def setup():
    print 'Configuring server, one moment.'
    configs = get_config()
    closest_server = get_closest_servers(configs['client'])
    best = get_best_server(closest_server)
    return best['id']
