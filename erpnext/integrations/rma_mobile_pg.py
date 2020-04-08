import frappe
from frappe.utils import get_bench_path, get_request_session
#url = 'http://uatbfssecure.rma.org.bt:8080/BFSSecure/nvpapi'
url='https://bfssecure.rma.org.bt/BFSSecure/nvpapi'
#benfId = 'BE10000102'
benfId = 'BE10000099'

def get_checkSum(message, private_key_src=None):
    import os.path
    #from frappe.utils import get_bench_path
    from base64 import (
        b64encode,
        b64decode,
    )
    from Crypto.Hash import SHA256, SHA
    from Crypto.Signature import PKCS1_v1_5, PKCS1_PSS
    from Crypto.PublicKey import RSA
    import binascii
        
    private_key_src = "nrdclmobile.key" if not private_key_src else private_key_src
    private_key_src = os.path.join(str(get_bench_path()),'apps/erpnext/erpnext/integrations',str(private_key_src))
    #digest = SHA256.new()
    digest = SHA.new()
    digest.update(message)

    # Read shared key from file
    private_key = False
    with open (private_key_src, "r") as myfile:
        private_key = RSA.importKey(myfile.read())

    # Load private key and sign message
    signer = PKCS1_v1_5.new(private_key)
    #signer = PKCS1_PSS.new(private_key)
    sig = signer.sign(digest)

    verifier = PKCS1_v1_5.new(private_key.publickey())
    #verifier = PKCS1_PSS.new(private_key.publickey())
    verified = verifier.verify(digest, sig)
    assert verified, 'Signature verification failed'
    print 'Signature verified successfully with public key'
    print

    return sig.encode('hex').upper()
    #return binascii.hexlify(sig).upper()

def get_params(req_type, bfs_bfsTxnId=None):
    from datetime import datetime
    url_params = []
    
    if req_type=='AR':
        orderNo = datetime.now().strftime("%Y%m%d%H%M%S")
        url_params = [
                    {'key': 'msgType', 'value': 'AR'},
                    {'key': 'benfTxnTime', 'value': '20200122151200'},
                    {'key': 'orderNo', 'value': orderNo},
                    {'key': 'benfId', 'value': benfId},
                    {'key': 'benfBankCode', 'value': '01'},
                    {'key': 'txnCurrency', 'value': 'BTN'},
                    {'key': 'txnAmount', 'value': 1},
                    {'key': 'remitterEmail', 'value': 'sivasankar.k2003@gmail.com'},
                    {'key': 'paymentDesc', 'value': 'TestPayment'},
                    {'key': 'version', 'value': '1.0'}
        ]
    elif req_type=='AE':
        url_params = [
		{'key': 'msgType', 'value': 'AE'},
		{'key': 'bfsTxnId', 'value': bfs_bfsTxnId},
		{'key': 'benfId', 'value': benfId},
		{'key': 'remitterBankId', 'value': '1010'},
		{'key': 'remitterAccNo', 'value': '100774924'},
	]
    return url_params

def call(req_type,bfs_bfsTxnId=None):
    import urllib
    import urlparse
    import requests
    import json
    url_params = get_params(req_type,bfs_bfsTxnId)
    url_params_sorted = sorted(url_params, key=lambda k: k['key']) 
    keys = "|".join(['bfs_'+str(i['key']) for i in url_params_sorted])
    values = "|".join([str(i['value']) for i in url_params_sorted])
    temp = {'bfs_'+str(i['key']):i['value'] for i in url_params_sorted}
    checkSum = get_checkSum(values)
    temp.update({'bfs_checkSum':checkSum})
    
    final_url = url+"?"+urllib.urlencode(temp)
    print '==========', req_type, '=========='
    print final_url
    
    try:
        s = get_request_session()
        headers = {'Content-type': 'application/x-www-form-urlencoded'}
        frappe.flags.integration_request = s.post(final_url, headers=headers)
        frappe.flags.integration_request.raise_for_status()
        print frappe.flags.integration_request

        return frappe.flags.integration_request.json()
    except Exception as exc:
        frappe.log_error()
        raise exc

    '''
    with requests.Session() as s:
        data = temp
        headers = {'Content-type': 'application/x-www-form-urlencoded'}
        #res = s.post(url, data={"data":json.dumps(data)}, headers=headers)
        try:
            res = s.post(final_url, headers=headers)
        except requests.exceptions.RequestException as e:
            print 'CURSTOM_ERROR', e
            sys.exit(1)

    print 
    print '==========', 'RESPONSE', '=========='
    print res.text
    print
    return urlparse.parse_qs(res.text)
    '''

@frappe.whitelist(allow_guest=True)
def main():
    res = call('AR')
    print 'RES IN MAIN:'
    print res
    '''
    if res.get('bfs_bfsTxnId'):
        res = call('AE',res.get('bfs_bfsTxnId')[0])
    '''

if __name__ == '__main__':
    main()
