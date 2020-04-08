import requests
import json
import urllib

def sendsms():
	#headers = {'Content-type': 'application/x-www-form-urlencoded'}
	#headers = { 'User-Agent': 'Mozilla/5.0 (Windows NT 6.0; WOW64; rv:24.0) Gecko/20100101 Firefox/24.0' }
	headers = {}
	host = '119.2.115.41'
	port = '9000'
	#port = '8080'
	username = 'nrdcl'
	password = 'nrdcl@btl'
	protocol = 'SMPP'
	usertype = 'transceiver'
	data = {"request_type": "SUBMIT_SM", 
		"username": username, 
		"password": password, 
		"seqno":"123",
		"oa": "NRDCL",
		"da": "97517115380",
		"ud":"Test from new smsc"}
	url = 'http://{0}:{1}/Messaging/'.format(host,port)
	#print urllib.urlencode(data)
	url = 'http://{}:{}/Messaging?{}'.format(host,port,urllib.urlencode(data))
	with requests.Session() as s:
		try:
			print url
			print json.dumps(data)
			#res = s.post(url, headers=headers, data=data, timeout=10)
			res = s.post(url, headers=headers,timeout=10)
			print 'RES'
			print res.text
		except requests.exceptions.Timeout as e:
			print 'EXCEPTION requests.exceptions.Timeout'
			print str(e)
			print 'EXCEPTION RES===>'
		except requests.exceptions.RequestException as e:
			print 'EXCEPTION requests.exceptions.RequestException'
			print str(e)
			#sys.exit(1)

sendsms()
