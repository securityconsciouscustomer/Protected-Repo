from protected_schema import protection_data
from flask import Flask, request, abort
from flask_cors import CORS
from waitress import serve
import requests
from requests.auth import HTTPBasicAuth
import configparser
import base64
import logging
import hmac

# Set up Flask app and get values from configuration file
app = Flask(__name__)
CORS(app)
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

#Set up logging
if config['DEFAULT'].get('Logging').lower() == 'true':
    logging.basicConfig(filename='webhook_listener.log', encoding='utf-8', level=logging.DEBUG)

basic = HTTPBasicAuth(user, auth)

@app.route('/')
def hello():
    return 'Test Page for Webhooks Listener'

@app.route('/createRepo',methods=['POST'])
def createRepo():

    api_url = 'https://api.github.com/repos'

    # Get the json data that corresponds with the POST request
    byte_data = request.get_data()
    data = request.json
    headers = request.headers
    sig = hmac.new(key=secret.encode(), msg=byte_data, digestmod="sha256").hexdigest()
    logging.debug("Calculated hash: " + str(sig))
    if not hmac.compare_digest('sha256=' + str(sig), headers['X-Hub-Signature-256']):
        abort(500)

    # There are many actions that correspond to POST requests for repository-related
    # webhooks. We are interested in repository creation, rather than deletion or others
    if data['action'] == 'created':
        repo_name = data['repository']['name']
        branches = requests.get(f'{api_url}/{organization}/{repo_name}/branches', auth=basic)
        if branches.status_code != 200:
            logging.error(branches.text)
            return branches.text
        if not branches.json():
            with open('initialreadme.md', 'r') as file:
                encoded_string = base64.b64encode(file.read().encode()).decode()
            send_data = {
                "message" : "Initial commit",
                "content" : encoded_string
            }
            response = requests.put(f'{api_url}/{organization}/{repo_name}/contents/README.md', auth=basic, json=send_data)
            if response.status_code == 201:
                branches = requests.get(f'{api_url}/{organization}/{repo_name}/branches', auth=basic)
            else:
                logging.error(response.text)
                return response.text
            logging.debug(response.text)
            logging.info("Created README and added to default branch")

        default_branch = branches.json()[0]['name']

        protection = requests.put(f'{api_url}/{organization}/{repo_name}/branches/{default_branch}/protection', auth=basic, json=protection_data)

        if protection.status_code != 200:
            logging.error(protection.text)
            return protection.text
        logging.debug(protection.text)

        sig_protection = requests.post(f'{api_url}/{organization}/{repo_name}/branches/{default_branch}/protection/required_signatures', auth=basic)
        if sig_protection.status_code != 200:
            logging.error(sig_protection.text)
            return sig_protection.text
        logging.debug(sig_protection.text)

        issue_data = {
            "title" : "Protection Added to Default Branch",
            "body" : f"""@{user}
                        Added the following branch protection rules to the default branch: 
                        1) enforce_admins - Enforce all configured restrictions for administrators
                        2) required_pull_request_reviews - 
                            a. dismiss_stale_reviews - Automatically dismiss approving reviews when someone pushes a new commit
                            b. require_code_owner_reviews - Blocks merging pull requests until code owners review them
                            c. required_approving_review_count - 2 - Number of reviewers required to approve pull requests
                        3) restrictions - nwhewell - Restrict who can push to the protected branch
                        4) allow_force_pushes - False - Permits force pushes to the protected branch by anyone with write access to the repository
                        5) allow_deletions - False - Allows deletion of the protected branch by anyone with write access to the repository
                        6) block_creations - True - Blocks creation of new branches which match the branch protection pattern
                        7) required_conversation_resolution - True - Requires all conversations on code to be resolved before a pull request
                        8) Require signatures for commits"""
        }
        issue = requests.post(f'{api_url}/{organization}/{repo_name}/issues', auth=basic, json=issue_data)
        if issue.status_code != 201:
            logging.error(issue.text)
            return issue.text
        logging.debug(issue.text)

    logging.info("Webhook listener successfully created repository protections")
    return "Protected repo created"

# Set defaults
host = '127.0.0.1'
port = 8080
if config['webhook_server']:
    host = config['webhook_server'].get('Host', '127.0.0.1')
    port = config['webhook_server'].get('Port', 8080)
else:
    logging.debug("Config.ini does not contain information on port and host of webhook server...Using default values")

serve(app, host=host, port=port)

