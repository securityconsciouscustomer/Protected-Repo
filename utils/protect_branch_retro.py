#!/usr/bin/env python
# protect_branch_retro.py 
# --------------------------- 
# Python script that retroactively enforces branch protection on
# the default branches in repositories
# ---------------------------
import configparser
import requests
import re
import base64
from requests.auth import HTTPBasicAuth
from protected_schema import protection_data

# Read values from config.ini
config = configparser.ConfigParser()
config.read('config.ini')
try:
    if 'https://api.github.com' in config:
        user = config['https://api.github.com'].get('User')
        auth = config['https://api.github.com'].get('AuthToken')
        organization = config['https://api.github.com'].get('Organization')
        if None in [user, auth, organization]:
            raise Exception("User, AuthToken, and Organization values in config.ini must be valid.")
    else:
        raise Exception("Config file must include 'https://api.github.com' section.")
except Exception as e:
    print(e)

basic = HTTPBasicAuth(user, auth)

api_url = 'https://api.github.com/orgs'

response = requests.get(f'{api_url}/{organization}/repos?per_page=1', auth=basic)

if response.status_code != 200:
    print(response.text)

pattern = '&page={}>; rel="last"'
page_num = int(re.findall(re.escape(pattern).replace(r'\{\}', r'(\S+)'), str(response.headers))[0])

for page in range(1, page_num+1):
    response = requests.get(f'{api_url}/{organization}/repos?per_page=1;page={page}', auth=basic)
    print(response.text)
    print('****************************************************')
    repo_list = response.json()
    for repo in repo_list:

        repo_name = repo.get('name')
        print(f"Name: {repo.get('name')}")
        branches = requests.get(f'{api_url}/{organization}/{repo_name}/branches', auth=basic)
        if branches.status_code != 200:
            print(branches.text)
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
                print(response.text)
            print("Created README and added to default branch")

        default_branch = branches.json()[0]['name']

        protection = requests.put(f'{api_url}/{organization}/{repo_name}/branches/{default_branch}/protection', auth=basic, json=protection_data)

        if protection.status_code != 200:
            print(protection.text)

        sig_protection = requests.post(f'{api_url}/{organization}/{repo_name}/branches/{default_branch}/protection/required_signatures', auth=basic)
        if sig_protection.status_code != 200:
            print(sig_protection.text)

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
            print(issue.text)

# print(response.headers)
# print(response.text)