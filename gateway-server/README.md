# Gateway Server

## TODO:
- [ ] Confirmation page, after someone puts in a phone number, display what's supposed to happen next
- [ ] /send command sends message back to client's number
- [ ] When recieving incoming text message from client, check for geolocation data and forward that to slack (or database)


![architecture](../img/reach-arch-gateway-server.png)

## Overview
This application connects clients with providers through SMS and web chat. Conversations are routed through Twilio to Slack. Providers in Slack can directly chat with the clients. The Gateway Server manages this interaction by:

1. Creates channels in Slack for each client
2. Routing incoming SMS/web chat to Slack channels
3. Routing messages from the Slack channel to the client SMS/web chat

## Setup
1. Install Python 3
2. Install Python packages:
```
pip3 install -r requirements.txt
```
2. Export the environmental variables for Slack and Twilio:
```
export SLACK_TOKEN=xoxp-443536887682-442805332144-445502414465-15b59a514de786c697d02014262f3b9f
export TWILIO_ACCOUNT_SID=AC7dcae26ab02956b94cd9418b21d00a29
export TWILIO_AUTH_TOKEN=f620989294ab4c35f2d2158c1de471c6
export FLASK_APP=app.py
```
3. Run the application:
```
FLASK_ENV=development flask run
```
