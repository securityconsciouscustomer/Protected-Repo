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
This guide assumes that you are using a Linux/Mac system and have a web server set up for serving the application. Instructions/scripts may need to be tweaked for users running Windows. You will need a Python3 installation. The solution has been tested on Python 3.10.4. If you need instructions for installing Python on your system, please visit https://www.python.org/downloads/
### Steps
1. Clone the repository https://docs.github.com/en/repositories/creating-and-managing-repositories/cloning-a-repository
1. Copy the file called "config_example.ini" to a new file called "config.ini" in the same directory. From a terminal, you can run the following:

    ```cp config_example.ini config.ini```

    WARNING - Skipping this step or putting in incorrect values in the next step can lead to application errors.
1. Edit the config.ini file with the correct values for your environment. 

    a. Logging - set to `True` if you would like to enable Debug level logging for the module or `False` otherwise. Output will be directed to "webhook_listener.log". 
    
    WARNING - Output will be appended to this file while the application is running, which means that there is a potential for a large log file that fills up memory. It's only advised that you enable logging for testing or debugging the application or frequently archive/remove the log file. 

    b. Organization - Enter the Github organization name for the repo owner. Must match Github Organization name exactly.

    c. User - This is the admin or owner user name responsible for setting up the webhook server/protection module. Must match Github user name exactly.

    d. AuthToken - Admin's auth token for making Github API calls. See https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token for more information on setting this up.

    e. WebhookSecret - Enter the high-entropy value to be used for setting up the Webhook. See https://docs.github.com/en/developers/webhooks-and-events/webhooks/securing-your-webhooks for help setting one up. 

    f. Port - The port used for serving content on your web server.

    g. Host - The server's host address.
1. Run the run.sh script. This will install start a Python virtual environment, install application dependencies, and start the application using the host and port provided in the config.ini file. If using a bash emulator such as MINGW or Git Bash on a Windows system, edit run.sh by following the directions in the comments. Run the script by entering the following in a terminal program:
```./run.sh```
1. Set up a webhook for your organization. This can be done either through the Github Web UI or the API. Make sure that the paylod URL is your server address, followed by "/createRepo". For example, the payload URL could look something like "https://623a-108-51-128-227.ngrok.io/createRepo". Also make sure that the content type is `application/json`, the secret matches the WebhookSecret found in your config.ini file from step #3.e, and the webhook is triggered on "Repositories" type events. You can follow the instructions found here: https://docs.github.com/en/developers/webhooks-and-events/webhooks/creating-webhooks
1. At this point, the application should be operating. To test, create a new repo in the organization. Verify operation by checking that all of the steps enumerated in the "How Does It Work?" section were completed. To debug, check the Webhooks console in your Organization Settings and view the Recent Deliveries tab. Successful delivery should be marked by a Status 200 code. 


