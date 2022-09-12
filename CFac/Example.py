import time
import base64
import hashlib
import hmac
import json
import urllib.request as urllib2
import urllib.parse as urllib
import ssl
import datetime as dt
import pandas as pd



class cfApiMethods(object):
    def __init__(self, apiPath, apiPublicKey="", apiPrivateKey="", timeout=10, checkCertificate=True, useNonce=False):
        self.apiPath = apiPath
        self.apiPublicKey = apiPublicKey
        self.apiPrivateKey = apiPrivateKey
        self.timeout = timeout
        self.nonce = 0
        self.checkCertificate = checkCertificate
        self.useNonce = useNonce

    ##### public endpoints #####

    # returns all instruments with specifications
    def get_instruments(self):
        endpoint = "/api/v3/instruments"
        return self.make_request("GET", endpoint)

    # returns market data for all instruments
    def get_tickers(self):
        endpoint = "/api/v3/tickers"
        return self.make_request("GET", endpoint)

    # returns the entire order book of a futures
    def get_orderbook(self, symbol):
        endpoint = "/api/v3/orderbook"
        postUrl = "symbol=%s" % symbol
        return self.make_request("GET", endpoint, postUrl=postUrl)

    # returns historical data for futures and indices
    def get_history(self, symbol, lastTime=""):
        endpoint = "/api/v3/history"
        if lastTime != "":
            postUrl = "symbol=%s&lastTime=%s" % (symbol, lastTime)
        else:
            postUrl = "symbol=%s" % symbol
        return self.make_request("GET", endpoint, postUrl=postUrl)

    ##### private endpoints #####

    # returns key account information
    # Deprecated because it returns info about the Futures margin account
    # Use get_accounts instead
    def get_account(self):
        endpoint = "/api/v3/account"
        return self.make_request("GET", endpoint)

    # returns key account information
    def get_accounts(self):
        endpoint = "/api/v3/accounts"
        return self.make_request("GET", endpoint)

    # places an order
    def send_order(self, orderType, symbol, side, size, limitPrice, stopPrice=None, clientOrderId=None):
        endpoint = "/api/v3/sendorder"
        postBody = "orderType=%s&symbol=%s&side=%s&size=%s&limitPrice=%s" % (orderType, symbol, side, size, limitPrice)

        if orderType == "stp" and stopPrice is not None:
            postBody += "&stopPrice=%s" % stopPrice

        if clientOrderId is not None:
            postBody += "&cliOrdId=%s" % clientOrderId

        return self.make_request("POST", endpoint, postBody=postBody)

    # places an order
    def send_order_1(self, order):
        endpoint = "/api/v3/sendorder"
        postBody = urllib.urlencode(order)
        return self.make_request("POST", endpoint, postBody=postBody)

    # edit an order
    def edit_order(self, edit):
        endpoint = "/api/v3/editorder"
        postBody = urllib.urlencode(edit)
        return self.make_request("POST", endpoint, postBody=postBody)

    # cancels an order
    def cancel_order(self, order_id=None, cli_ord_id=None):
        endpoint = "/api/v3/cancelorder"

        if order_id is None:
            postBody = "cliOrdId=%s" % cli_ord_id
        else:
            postBody = "order_id=%s" % order_id

        return self.make_request("POST", endpoint, postBody=postBody)

    # cancel all orders
    def cancel_all_orders(selfs, symbol=None):
        endpoint = "/api/v3/cancelallorders"
        if symbol is not None:
            postbody = "symbol=%s" % symbol
        else:
            postbody = ""

        return selfs.make_request("POST", endpoint, postBody=postbody)

    # cancel all orders after
    def cancel_all_orders_after(selfs, timeoutInSeconds=60):
        endpoint = "/api/v3/cancelallordersafter"
        postbody = "timeout=%s" % timeoutInSeconds

        return selfs.make_request("POST", endpoint, postBody=postbody)

    # places or cancels orders in batch
    def send_batchorder(self, jsonElement):
        endpoint = "/api/v3/batchorder"
        postBody = "json=%s" % jsonElement
        return self.make_request("POST", endpoint, postBody=postBody)

    # returns all open orders
    def get_openorders(self):
        endpoint = "/api/v3/openorders"
        return self.make_request("GET", endpoint)

    # returns filled orders
    def get_fills(self, lastFillTime=""):
        endpoint = "/api/v3/fills"
        if lastFillTime != "":
            postUrl = "lastFillTime=%s" % lastFillTime
        else:
            postUrl = ""
        return self.make_request("GET", endpoint, postUrl=postUrl)

    # returns all open positions
    def get_openpositions(self):
        endpoint = "/api/v3/openpositions"
        return self.make_request("GET", endpoint)

    # return the user recent orders
    def get_recentorders(self, symbol=""):
        endpoint = "/api/v3/recentorders"
        if symbol != "":
            postUrl = "symbol=%s" % symbol
        else:
            postUrl = ""
        return self.make_request("GET", endpoint, postUrl=postUrl)

    # sends an xbt withdrawal request
    def send_withdrawal(self, targetAddress, currency, amount):
        endpoint = "/api/v3/withdrawal"
        postBody = "targetAddress=%s&currency=%s&amount=%s" % (targetAddress, currency, amount)
        return self.make_request("POST", endpoint, postBody=postBody)

    # returns xbt transfers
    def get_transfers(self, lastTransferTime=""):
        endpoint = "/api/v3/transfers"
        if lastTransferTime != "":
            postUrl = "lastTransferTime=%s" % lastTransferTime
        else:
            postUrl = ""
        return self.make_request("GET", endpoint, postUrl=postUrl)

    # returns all notifications
    def get_notifications(self):
        endpoint = "/api/v3/notifications"
        return self.make_request("GET", endpoint)

    # makes an internal transfer
    def transfer(self, fromAccount, toAccount, unit, amount):
        endpoint = "/api/v3/transfer"
        postBody = "fromAccount=%s&toAccount=%s&unit=%s&amount=%s" % (fromAccount, toAccount, unit, amount)
        return self.make_request("POST", endpoint, postBody=postBody)

    # signs a message
    def sign_message(self, endpoint, postData, nonce=""):
        # step 1: concatenate postData, nonce + endpoint                
        message = postData + nonce + endpoint

        # step 2: hash the result of step 1 with SHA256
        sha256_hash = hashlib.sha256()
        sha256_hash.update(message.encode('utf8'))
        hash_digest = sha256_hash.digest()

        # step 3: base64 decode apiPrivateKey
        secretDecoded = base64.b64decode(self.apiPrivateKey)

        # step 4: use result of step 3 to has the result of step 2 with HMAC-SHA512
        hmac_digest = hmac.new(secretDecoded, hash_digest, hashlib.sha512).digest()

        # step 5: base64 encode the result of step 4 and return
        return base64.b64encode(hmac_digest)

    # creates a unique nonce
    def get_nonce(self):
        # https://en.wikipedia.org/wiki/Modulo_operation
        self.nonce = (self.nonce + 1) & 8191
        return str(int(time.time() * 1000)) + str(self.nonce).zfill(4)

    # sends an HTTP request
    def make_request(self, requestType, endpoint, postUrl="", postBody=""):
        # create authentication headers
        postData = postUrl + postBody

        if self.useNonce:
            nonce = self.get_nonce()
            signature = self.sign_message(endpoint, postData, nonce=nonce)
            authentHeaders = {"APIKey": self.apiPublicKey, "Nonce": nonce, "Authent": signature}
        else:
            signature = self.sign_message(endpoint, postData)
            authentHeaders = {"APIKey": self.apiPublicKey, "Authent": signature}

        # create request
        url = self.apiPath + endpoint + "?" + postUrl
        request = urllib2.Request(url, str.encode(postBody), authentHeaders)
        request.get_method = lambda: requestType

        # read response
        if self.checkCertificate:
            response = urllib2.urlopen(request, timeout=self.timeout)
        else:
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            response = urllib2.urlopen(request, context=ctx, timeout=self.timeout)

        response = response.read().decode("utf-8")

        # return
        return response


apiPath = "https://www.cryptofacilities.com/derivatives"
apiPublicKey = "NiFiwZwT5L+MYjJHB46HYMRCvs6WeKO6d27ct2VxQYXpw4FTww4IMm4w"  # accessible on your Account page under Settings -> API Keys
apiPrivateKey = "g+PlW2U3gpPtG/zRXwOpK8DdoZ+kQhVGjzQtsxA8otB+JrgKproeQrkTl/tzKkpUnNet8KTt7qp+Eqfo0rSr8w+U"  # accessible on your Account page under Settings -> API Keys
timeout = 20
checkCertificate = True  # when using the test environment, this must be set to "False"
useNonce = False  # nonce is optional

cfPublic = cfApiMethods(apiPath, timeout=timeout, checkCertificate=checkCertificate)
cfPrivate = cfApiMethods(apiPath, timeout=timeout, apiPublicKey=apiPublicKey, apiPrivateKey=apiPrivateKey, checkCertificate=checkCertificate, useNonce=useNonce)


def APITester():
    ##### public endpoints #####  

    # get instruments
    result = cfPublic.get_instruments()
    print("get_instruments:\n", result)

    # get tickers
    result = cfPublic.get_tickers()
    print("get_tickers:\n", result)

    # get order book
    symbol = "PI_XBTUSD"
    result = cfPublic.get_orderbook(symbol)
    print("get_orderbook:\n", result)

    # get history
    symbol = "PI_XBTUSD"  # "PI_XBTUSD", "cf-bpi", "cf-hbpi"
    lastTime = dt.datetime.strptime("2016-01-20", "%Y-%m-%d").isoformat() + ".000Z"
    result = cfPublic.get_history(symbol, lastTime=lastTime)
    print("get_history:\n", result)

    ##### private endpoints #####

    # get account
    result = cfPrivate.get_accounts()
    print("get_accounts:\n", result)

    # send limit order
    limit_order = {
        "orderType": "lmt",
        "symbol": "PI_XBTUSD",
        "side": "buy",
        "size": 1,
        "limitPrice": 1.00,
        "reduceOnly": "true"
    }
    result = cfPrivate.send_order_1(limit_order)
    print("send_order (limit):\n", result)

    # send stop reduce-only order
    stop_order = {
        "orderType": "stp",
        "symbol": "PI_XBTUSD",
        "side": "buy",
        "size": 1,
        "limitPrice": 1.00,
        "stopPrice": 2.00,
        "cliOrdId": "my_stop_client_id"
    }
    result = cfPrivate.send_order_1(stop_order)
    print("send_order (stop):\n", result)

    edit = {
         "cliOrdId": "my_stop_client_id",
         "size": 2,
         "limitPrice": 1.50,
         "stopPrice": 2.50,
    }
    result = cfPrivate.edit_order(edit)
    print("edit_order (stop):\n", result)

    # cancel order
    order_id = "e35d61dd-8a30-4d5f-a574-b5593ef0c050"
    result = cfPrivate.cancel_order(order_id)
    print("cancel_order:\n", result)

    # cancel all orders of a margin account
    result = cfPrivate.cancel_all_orders(symbol="fi_xbtusd")
    print("cancel_all_orders:\n", result)

    # cancel all orders after a minute
    timeout_in_seconds = 60
    result = cfPrivate.cancel_all_orders_after(timeout_in_seconds)
    print("cancel_all_orders_after:\n", result)

    # batch order
    jsonElement = {
        "batchOrder":
            [
                {
                    "order": "send",
                    "order_tag": "1",
                    "orderType": "lmt",
                    "symbol": "PI_XBTUSD",
                    "side": "buy",
                    "size": 1,
                    "limitPrice": 1.00,
                    "cliOrdId": "my_another_client_id"
                },
                {
                    "order": "send",
                    "order_tag": "2",
                    "orderType": "stp",
                    "symbol": "PI_XBTUSD",
                    "side": "buy",
                    "size": 1,
                    "limitPrice": 2.00,
                    "stopPrice": 3.00,
                },
                {
                    "order": "cancel",
                    "order_id": "e35d61dd-8a30-4d5f-a574-b5593ef0c050",
                },
                {
                    "order": "cancel",
                    "cliOrdId": "my_client_id",
                },
            ],
    }
    result = cfPrivate.send_batchorder(jsonElement)
    print("send_batchorder:\n", result)

    ## get open orders
    result = cfPrivate.get_openorders()
    print("get_openorders:\n", result)

    # get fills
    lastFillTime = dt.datetime.strptime("2016-02-01", "%Y-%m-%d").isoformat() + ".000Z"
    result = cfPrivate.get_fills(lastFillTime=lastFillTime)
    print("get_fills:\n", result)

    # get open positions
    result = cfPrivate.get_openpositions()
    print("get_openpositions:\n", result)


    # get recentorders
    symbol = "pi_xbtusd"
    result = cfPrivate.get_recentorders(symbol)
    print("get_recentorders:\n", result)

    # send xbt withdrawal request
    targetAddress = "xxxxxxxxxx"
    currency = "xbt"
    amount = 0.12345678
    result = cfPrivate.send_withdrawal(targetAddress, currency, amount)
    print("send_withdrawal:\n", result)

    # get xbt transfers
    lastTransferTime = dt.datetime.strptime("2016-02-01", "%Y-%m-%d").isoformat() + ".000Z"
    result = cfPrivate.get_transfers(lastTransferTime=lastTransferTime)
    print("get_transfers:\n", result)

    # transfer
    fromAccount = "fi_ethusd"
    toAccount = "cash"
    unit = "eth"
    amount = 0.1
    result = cfPrivate.transfer(fromAccount, toAccount, unit, amount)
    print("transfer:\n", result)


APITester()

tickers = cfPublic.get_tickers()

tickers = json.loads(tickers)

tickers = pd.io.json.json_normalize(tickers['tickers'])

type(tickers)

tickers






account = cfPrivate.get_accounts()

account = json.loads(account)

account = pd.io.json.json_normalize(account['accounts'])

account = account.T

with pd.option_context('display.max_rows', None, 'display.max_columns', None):
    print(account)

transfers = cfPrivate.get_transfers()

transfers =  json.loads(transfers)

transfers = pd.io.json.json_normalize(transfers['transfers'])

with pd.option_context('display.max_rows', None, 'display.max_columns', None):
    print(transfers)

result

fills = cfPrivate.get_fills()

fills = json.loads(fills)

fills = pd.io.json.json_normalize(fills['fills'])

with pd.option_context('display.max_rows', None, 'display.max_columns', None):
    print(fills)
