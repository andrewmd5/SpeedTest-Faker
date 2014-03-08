__author__ = 'Andrew'
from hashlib import md5
import urllib2
import sys
from urlparse import parse_qs
import functions

ping = 16
accuracy = 8
server = functions.setup()


def speed_test(up, down):
    get_data = [
        'download=%s' % down,
        'ping=%s' % ping,
        'upload=%s' % up,
        'promo=',
        'startmode=%s' % 'pingselect',
        'recommendedserverid=%s' % server,
        'accuracy=%s' % 8,
        'serverid=%s' % server,
        'hash=%s' % md5('%s-%s-%s-%s' %
                        (ping, up, down, '297aae72')
                        ).hexdigest()]
    request = urllib2.Request('http://www.speedtest.net/api/api.php',
                              data='&'.join(get_data))
    request.add_header('Referer', 'http://c.speedtest.net/flash/speedtest.swf')
    connection = urllib2.urlopen(request)
    response = connection.read()
    response_code = connection.code
    connection.close()

    if int(response_code) != 200:
        print 'There was an issue submitting data'
        sys.exit(1)

    qs_args = parse_qs(response)
    result_id = qs_args.get('resultid')
    if not result_id or len(result_id) != 1:
        print 'No speedtest image found?'
        sys.exit(1)

    print ('Speedtest Results: http://www.speedtest.net/result/%s.png' % result_id[0])


down_input = raw_input("Please enter your download speed (EX: 375.520): ")
down_input = down_input.replace(".", "")

up_input = raw_input("Please enter your upload speed (EX: 375.520): ")
up_input = up_input.replace(".", "")

speed_test(up_input, down_input)