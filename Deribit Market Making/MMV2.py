from __future__ import print_function
import time
import openapi_client
from openapi_client.rest import ApiException
from pprint import pprint

# Setup configuration instance
conf = openapi_client.Configuration()
#conf.host = 'https://test.deribit.com'
# Setup unauthenticated client
client = openapi_client.ApiClient(conf)

# create an instance of the API class
api_instance = openapi_client.AuthenticationApi(openapi_client.ApiClient(conf))
#publicApi = public_api.PublicApi(client)
# Authenticate with API credentials
response = api_instance.public_auth_get('client_credentials', '', '', 'RLR2t3d8', 'aqW9QeFL8sEex-cXDzffu-7wVpyxXutF0X1UmSvb9Hk', '', '', '')
access_token = response['result']['access_token']

conf_authed = openapi_client.Configuration()
conf_authed.access_token = access_token
# Use retrieved authentication token to setup private endpoint client
client_authed = openapi_client.ApiClient(conf_authed)
privateApi = private_api.PrivateApi(client_authed)

response = privateApi.private_get_transfers_get(currency='BTC')
print(response['result']['data'][0]['amount'])
response = privateApi.private_get_current_deposit_address_get(currency='BTC')
print(response['result']['address'])