#!/usr/bin/env python
# create_webhook.py 
# --------------------------- 
# Python script that creates an Organization webhook for the application
# using GitHub REST API. The file "config.ini" must be configured properly
# before using this script
# ---------------------------
import configparser
import argparse
import requests
from requests.auth import HTTPBasicAuth

# Get input arg
parser = argparse.ArgumentParser("create_webhook.py")
parser.add_argument("url",
                    help="""The URL of the web server. Must be appended with the /createRepo route. 
                         For example, "https://7434-108-51-128-227.ngrok.io/createRepo" """,
                    type=str)
args = parser.parse_args()

# Read values from config.ini
config = configparser.ConfigParser()
config.read('config.ini')
try:
    if 'https://api.github.com' in config:
        user = config['https://api.github.com'].get('User')
        auth = config['https://api.github.com'].get('AuthToken')
        organization = config['https://api.github.com'].get('Organization')
        secret = config['https://api.github.com'].get('WebhookSecret')
        if None in [user, auth, organization, secret]:
            raise Exception("User, AuthToken, Organization and Secret values in config.ini must be valid.")
    else:
        raise Exception("Config file must include 'https://api.github.com' section.")
except Exception as e:
    print(e)

basic = HTTPBasicAuth(user, auth)

api_url = 'https://api.github.com/orgs'

send_data = {
    "name" : "web",
    "config" : {
        "url" : f"{args.url}",
        "content_type" : "json",
        "secret" : f"{secret}",
    },
    "events" : ["repository"],
    "active" : True,
    
}
response = requests.post(f'{api_url}/{organization}/hooks', auth=basic, json=send_data)

if response.status_code != 200:
    print(response.text)

