# Repo Protection Webhook Module
## Description
The Repo Protection Webhook Module is an automated and scalable solution for ensuring that the default branches of created repos within an organization are protected and that developers are following prescribed rules regarding PRs, commits, reviews, etc. Any organization admins or owners who need an automated, scalable, and highly configurable way to protect repos can benefit from using this solution.
## How Does It Work?
The webhook component is a Python [Flask](https://flask.palletsprojects.com/en/2.1.x/) module that can be run on an admin's web server (or servers). It listens for organization events, namely repo creation events, from Github and makes requests to Github's REST API to perform the following actions when a request is received:  

1. Verifies that the webhooks's computed hash matches the received payload hash. See [Securing Your Webhooks](https://docs.github.com/en/developers/webhooks-and-events/webhooks/securing-your-webhooks) Github Docs for more details.
1. Gets the default branch name that was created with the repo. If there is no branch name returned, this means that an initial commit was not made upon repo creation. The component will add an initial README.md to the repo in order to create an initial commit on the default branch.
1. Add protection to the default branch. The following protections are added automatically, but can be modified by editing the protected_schema.py file:  
    <ol type="a">
    <li>enforce_admins - Enforce all configured restrictions for administrators</li>
    <li>required_pull_request_reviews - 
    <ol type="i">
    <li>dismiss_stale_reviews - Automatically dismiss approving reviews when someone pushes a new commit</li>
    <li>require_code_owner_reviews - Blocks merging pull requests until code owners review them</li>
    <li>required_approving_review_count - 2 - Number of reviewers required to approve pull requests</li>
    </ol>
    </li>
    <li>restrictions - nwhewell - Restrict who can push to the protected branch</li>
    <li>allow_force_pushes - False - Permits force pushes to the protected branch by anyone with write access to the repository</li>
    <li>allow_deletions - False - Allows deletion of the protected branch by anyone with write access to the repository</li>
    <li>block_creations - True - Blocks creation of new branches which match the branch protection pattern</li>
    <li>required_conversation_resolution - True - Requires all conversations on code to be resolved before a pull request</li>
    <li>Require signatures for commits</li>
    </ol>
1. Creates an issue in the newly created repo and tags the admin/owner, providing information on what branch protections were added to the default branch.
## How To Use
The solution provided is configurable and scalable to the needs of your organization. Follow the steps below to easily get started.
### Prereqs
This guide assumes that you are using a Linux/Mac system. Instructions/scripts may need to be tweaked for users running Windows. You will need a Python3 installation. The solution has been tested on Python 3.10.4. If you need instructions for installing Python on your system, please visit https://www.python.org/downloads/
### Steps
1. Clone the repository https://docs.github.com/en/repositories/creating-and-managing-repositories/cloning-a-repository
2. 


