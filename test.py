import requests
from requests.auth import HTTPBasicAuth
from pprint import pprint
import json

# # /event meeting
# r = requests.post("http://127.0.0.1:5000/event?channel_id=CDF8LERL6&channel_name=vengeful-ant&command=/event&response_url=https://hooks.slack.com/commands/TD1FSS3L2/455923917874/ZFGvteZxjPcqMCMAYyWuUL0X&trigger_id=455923917970.443536887682.1a37a8ed428ba01afb3ef336befa59e8&team_domain=pa-reach&team_id=TD1FSS3L2&text=meeting&token=djAAw2ljwh0pASEClYeoS1FO&user_id=UD24L0X52&user_name=g_kip")
# print(r.content)
# assert(r.status_code == 200)
#
# # /need bed
# r = requests.post("http://127.0.0.1:5000/need?channel_id=CDF8LERL6&channel_name=vengeful-ant&command=/need&response_url=https://hooks.slack.com/commands/TD1FSS3L2/455923917874/ZFGvteZxjPcqMCMAYyWuUL0X&trigger_id=455923917970.443536887682.1a37a8ed428ba01afb3ef336befa59e8&team_domain=pa-reach&team_id=TD1FSS3L2&text=dentist&token=djAAw2ljwh0pASEClYeoS1FO&user_id=UD24L0X52&user_name=g_kip")
# print(r.content)
# assert(r.status_code == 200)
#
#
# # /stage action went to meeting
# r = requests.post("http://127.0.0.1:5000/stage?channel_id=CDF8LERL6&channel_name=vengeful-ant&command=/stage&response_url=https://hooks.slack.com/commands/TD1FSS3L2/455923917874/ZFGvteZxjPcqMCMAYyWuUL0X&trigger_id=455923917970.443536887682.1a37a8ed428ba01afb3ef336befa59e8&team_domain=pa-reach&team_id=TD1FSS3L2&text=action%20went%20to%20meeting&token=djAAw2ljwh0pASEClYeoS1FO&user_id=UD24L0X52&user_name=g_kip")
# print(r.content)
# assert(r.status_code == 200)
#
# # /demographics action went to meeting
# r = requests.post("http://127.0.0.1:5000/demographics?channel_id=CDF8LERL6&channel_name=vengeful-ant&command=/demographics&response_url=https://hooks.slack.com/commands/TD1FSS3L2/455923917874/ZFGvteZxjPcqMCMAYyWuUL0X&trigger_id=455923917970.443536887682.1a37a8ed428ba01afb3ef336befa59e8&team_domain=pa-reach&team_id=TD1FSS3L2&text=age%2026&token=djAAw2ljwh0pASEClYeoS1FO&user_id=UD24L0X52&user_name=g_kip")
# print(r.content)
# assert(r.status_code == 200)

# # /211 action went to meeting
# r = requests.post("http://127.0.0.1:5000/211?channel_id=CDF8LERL6&channel_name=brown-dear&command=/211&response_url=https://hooks.slack.com/commands/TD1FSS3L2/455923917874/ZFGvteZxjPcqMCMAYyWuUL0X&trigger_id=455923917970.443536887682.1a37a8ed428ba01afb3ef336befa59e8&team_domain=pa-reach&team_id=TD1FSS3L2&text=shelter%2018018&token=djAAw2ljwh0pASEClYeoS1FO&user_id=UD24L0X52&user_name=g_kip")
# print(r.content)
# assert(r.status_code == 200)
#
#
# #
# #
r = requests.post('http://104.196.121.238:8181/cxs/segments/',
    auth=('karaf', 'karaf'),
    json={
        "itemId":"1",
        "itemType":"segment",
        "version": 1,
        "metadata": {
             "id": "leads",
            "name": "Leads",
            "scope": "systemscope",
            "description": "You can customize the list below by editing the leads segment.",
            "readOnly":True
        },
        "condition": {
            "parameterValues": {
              "subConditions": [
                {
                  "parameterValues": {
                    "propertyName": "properties.leadAssignedTo",
                    "comparisonOperator": "exists"
                  },
                  "type": "profilePropertyCondition"
                }
              ],
              "operator" : "and"
            },
            "type": "booleanCondition"
        }
    })

pprint(r)
outfile = open('data.html','w')
outfile.write(r.content.decode())
# # #
# # # ## EXMAPLE CREATE A SESSION
# # # r = requests.post('http://104.196.121.238:8181/cxs/profiles/
# # # auth=('karaf 'karaf'),
# # # json ={
# # #         "itemId":"vengeful-ant2",
# # #         "itemType":"profile",
# # #         "version":None,
# # #         "properties": {
# # #             "phoneNumber": "555"
# # #         },
# # #         "systemProperties":{},
# # #         "segments":[],
# # #         "scores":{},
# # #         "mergedWith":None,
# # #         "consents":{}
# # #     })
# # # print(r.content)
