from flask import request, jsonify, redirect, session
import requests, hashlib, base64, json, random, datetime
import urllib.parse
import urllib.request

##data_as = json.loads(base64.b64decode(encoded_payload.encode()).decode())
def sha_generator(str_to_convert):
    str_to_convert_bytes = str_to_convert.encode('utf-8')
    hash_object = hashlib.sha256(str_to_convert_bytes)
    return hash_object.hexdigest()

def payment_test():
    if request.method == 'GET':
        host_url = "https://api-preprod.phonepe.com/apis/pg-sandbox/pg/v1/pay"
        api_endpoint = "/pg/v1/pay"
        salt_key = "695d0547-3728-4b1c-825d-996479133615"
        salt_index = '1'

        merchantId = 'PGTESTPAYUAT139'
        merchantTransactionId = "MS"+datetime.datetime.now().strftime("%Y%m%d_%H%M%S%f")+"_"+str(random.randint(1,1000)).zfill(4)
        ##merchantUserId = session['id']        
        return jsonify(session['id'])
        payload = {
          "merchantId": merchantId,
          "merchantTransactionId": merchantTransactionId,
          "merchantUserId": "MUID123",
          "amount": 1000,
          "redirectUrl": "https://www.google.com",
          "redirectMode": "REDIRECT",
          "callbackUrl": "https://www.google.com",
          "mobileNumber": "9999999999",
          "paymentInstrument": {
            "type": "PAY_PAGE"
          }
        }
        encoded_payload = base64.b64encode(json.dumps(payload).encode()).decode()
        payload = { "request" : encoded_payload}
        x_verify_value = sha_generator(encoded_payload+api_endpoint+salt_key)+"###"+salt_index
        return x_verify_value
        headers = {
            "accept": "text/plain",            
            "Content-Type" : "application/json",
            "X-VERIFY" : x_verify_value  
        }
        response = requests.post(host_url+api_endpoint, json=payload, headers=headers)
        return jsonify(response.text)
        
        response = {
            "success": 'true',
            "code": "PAYMENT_INITIATED",
            "message": "Payment Iniiated",
            "data": {
                "merchantId": "PGTESTPAYUAT",
                "merchantTransactionId": "MT7850590068188104",
                "instrumentResponse": {
                    "type": "PAY_PAGE",
                    "redirectInfo": {
                        "url": "https://mercury-uat.phonepe.com/transact?token=MjdkNmQ0NjM2MTk5ZTlmNDcxYjY3NTAxNTY5MDFhZDk2ZjFjMDY0YTRiN2VhMjgzNjIwMjBmNzUwN2JiNTkxOWUwNDVkMTM2YTllOTpkNzNkNmM2NWQ2MWNiZjVhM2MwOWMzODU0ZGEzMDczNA",
                        "url_2": "https://www.google.com",
                        "method": "GET"
                    }
                }
            }
        }
        return redirect(response['data']['instrumentResponse']['redirectInfo']['url_2'], 307)


        base_url = 'http://www.google.com/search'
        params = {'q': 'science123'}

        url = '{}?{}'.format(base_url, urllib.parse.urlencode(params))

        #data = urllib.request.urlopen(url).read()
        return redirect(url)
    else:
        return jsonify(['Not Working'])


