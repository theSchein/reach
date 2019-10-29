# Reach: Text Hotline & CRM

# Getting Started
This is a guide for deploying Reach on Google Cloud Platform (GCP). This guide is written for IT teams and covers everything you'll need to get Reach running as a proof of concept.

The guide is broken into several sections, each covering part of the deployment:

1. **Account Registration:** Covers setting up accounts with dependant services (e.g. Twilio)
2. **Google Cloud Platform Setup:** Covers setting up infrastructure on GCP using Kubernetes
3. **Twilio and Slack Setup:** Covers setting up Twilio and Slack services
4. **App Setup:** Covers how to download and configure the Reach application code
5. **Deployment:** Covers how to deploy the application to Kubernetes
6. **Dependent Service Configurations**: Covers configuring Slack and Twilio callback URLS

# 1. Account Registration
Reach requires accounts with:
* **Google Cloud Platform:** For deploying the web, app, and data services
* **Twilio:** For managing SMS messages to and from patients and specialists
* **Slack:** For managing conversations between patients and specialists

## Google Cloud Platform
1. Go to cloud.google.com and create a new account
2. After creating a new account, create a New Project and give it a unique name like "reach-example"
3. Now you will be at the dashoard for your Reach Google Cloud project

## Twilio
1. Got to https://www.twilio.com/try-twilio and create a new account with Twilio
2. After authenticating into your Twilio Account, create a New Project and give it a unique name like "reach-example"
3. In the project create wizard, select Products > Programmable SMS then click Continue to finish
4. Now you will be at the dashboard for your Reach Twilio Project
5. Next, you will need to verify the phone number you want to use to test (e.g. your phone number)
6. Click on Phone Numbers > Verify Caller ID
7. Enter the phone number to verify, and then click Call Me

## Slack
1. Go to https://slack.com/create and create a new Workspace with Slack
2. Complete the workspace creation wizard, use your email address and pick a name for your workspace like "reach-example"
3. Add additional users to the workspace by adding their email and inviting them

# 2. Kubernetes Setup
In this section, you will setup a cluster on Kubernetes Engine in GCP and install Google Cloud SDK (gcloud) and Kubernetes Command Line Interface (kubectl).

## Creating a Kubernetes Cluster
1. Log into the GCP Console using the same account used in _Account Registration_
1. Select Kubernetes Engine > Cluster from the setup
2. Click Create Cluster
3. Complete the form using the following as an example. (2 vCPU and 7.5 GB is the minimum suggested cluster size)

## Installing Google Cloud SDK (gcloud)
1. Follow the instructions in this Quickstart guide for your operating system to install the Google Cloud SDK: https://cloud.google.com/sdk/docs/quickstarts
2. Once you have the `gcloud` program installed, you will be prompted to authenticate with your Google Cloud account. If you're not prompted, run this command to authenticate with your Google Cloud account manually:
```
gcloud auth login
```
3. Follow the on-screen prompts and select the Google Cloud project you created earlier

## Install Kubernetes CLI
1. Follow the instructions in this guide from Kubernetes to install `kubectl`: https://kubernetes.io/docs/tasks/tools/install-kubectl/ (look for instructions for your operating system)

## Connect to Google Kubernetes Cluster
Once you have created your cluster and install `gcloud` and `kubectl` you can connect to  the cluster created earlier.

1. Go to your Google Cloud console and go to Kubernetes Engine
2. Click "Connect" for you cluster
3. Copy the `gcloud` command and run it in our terminal/command prompt
4. After it runs successfully, confirm `kubectl` is working by running the following command:
```
kubectl get nodes
```
This command should return statistics about the nodes in your Kubernetes cluster.

# 3. Twilio and Slack Setup
You will need to create a messaging service and purchase a phone number in Twilio. You will also need to create a new workspace in Slack.

## Creating Twilio Resources
1. Log into your Twilio project created earlier
2. Go to Programmable SMS > SMS > Messaging Services and click "Create New Messaging Service"
3. Give the Messaging Service a name like "Reach" and select the "Chat bot/2-way interactive" use case
4. Add a phone number by selecting "Numbers" and then click "Buy a Number"
5. Before returning to the Twilio Dashboard, copy the **Messaging Service SID** for your newly created messaging service and save it for _App Setup_
6. Return to the Twilio Dashboard and copy the **Account SID** and **Secret** for your account and save it for _App Setup_

## Creating Slack Resources & Getting Your Access Token
1. Log into your Slack Workspace created earlier
2. Go to https://api.slack.com and click My Apps
3. Click "Create an App"
4. Give you app a name and select the workspace you created earlier then click "Create"
5. Once created, click on "OAuth & Permissions" and allow you application
6. Under "Scopes," add the "Administer the Workspace" scope to this app
7. Copy the **OAuth Access Token** for your newly created application and save it for _App Setup_

# 4. App Setup
1. Start by cloning the project locally to your computer.
```
git clone https://github.com/mikeghen/reach
```
2. Next, fill in your Twilio and Slack credentials from the previous steps and save the file
3. Then, edit the `Makefile` and change the `GCP_PROJECT_ID` to your GCP project ID

# 5. Deployment
You will need Docker and Helm to build and deploy Reach to GCP. In this section, you will install Docker and Helm before using `make` to deploy the application to your Kubernetes cluster.

## Installing Helm CLI (TBD)
1. To install helm, follow the instructions in these guide from Helm: https://helm.sh/docs/using_helm/
2. For a script that can be used to install helm, visit: https://helm.sh/docs/using_helm/#from-script

## Installing Docker
1. To install docker, follow the instructions in this guide from Docker: https://docs.docker.com/install/

## Deploying Reach
1. Deploy the platform to Kubernetes using the following make command from the root of the reach project:
```
make build
make deploy
```
2. Go into Google Cloud Kubernetes Engine and look under "Services" and get the "External IP" for the application.

# 6. Dependent Service Configurations
This section describes how to configure Slack and Twilio AFTER your application has been deployed and you have your external IP (`IP_ADDR` below).

## Slack Configuration
1. Go back to api.slack.com and find your application from earlier
2. Create a "Slash Command" and add the following back slash command:
```
Command: /send
URL: http://IP_ADDR/text
```

## Twilio Configurations
1. Go back to Twilio console and go to Programmable SMS > SMS > Message Services
2. Under Inbound Message Settings, select Send An Incoming Message Webhook
3. Use `htttp://IP_ADDR/message` as the endpoint
