from clients.unomi import Unomi
from csv import DictReader
from coolname import generate_slug
from utils.helpers import channel_token
from datetime import datetime
from tqdm import tqdm
import random
import time

unomi_client = Unomi()

def execute():
    random.seed(99)
    csvfile = open('./seeds/zipcodes_cities.csv')
    reader = DictReader(csvfile)
    cities = []
    for row in reader:
        cities.append(row)

    for i in tqdm(range(345)):
        phone_number = "+1555" + str(random.randint(1000000,9999999))
        city = random.choice(cities)

        needs = ['family-planning', 'day-care', 'transportation', 'food',
                 'perscription', 'money', 'shelter', 'shelter', 'shelter', 'legal',
                 'shelter', 'legal', 'legal', 'job', 'job', 'support-group', 'support-group', 'job', 'job']

        properties = {
            'phoneNumber': phone_number,
            'city': city['city'].upper(),
            'state': 'PA',
            'zipcode': city['zipcode'],
            'county': city['county'].upper()
        }

        channel = channel_token(phone_number)


        profile = unomi_client.create_profile(profile_id=channel,
                                          properties=properties)

        unomi_client.track_event(channel, 'engagementStarted', {})

        # # Have a conversation:
        # messages = ["Hi, Robin. My name is Julie. I’m just checking in with you after your accident. How are you doing?  I’m a recovery coach.",
        # "I’m ok, thanks for asking, but who do you work for?",
        # "Glad you doing ok. I work for the county. Judge Judy gave me your number. I hope she mentioned I would be checking in.",
        # "Oh, yes, she did. You’re helping me get into treatment or whatever so I don’t have to serve time? I can’t go to jail. I have 3 kids, and the youngest has a lot of problems. I don’t have any one else to help them, and I don’t want to have them taken away from me. I must made a mistake, a DUI.  I don’t have a real problem.",
        # "Yes, that’s what I help people with! Getting into care can be a challenge, so I help you through all the steps. Have you had an level of care assessment yet?",
        # "I don’t think so, what is that?",
        # "It is an interview you do with an assessor to figure out what level of care is appropriate for you. There are a few agencies in the area that do assessments. I can help you get that appointment. If you can come to an appointment during the work with, it will be faster, but a few places do have appointments as late as 7pm.",
        # "I’ve missed too much work already. I’d have to do something later.",
        # "Okay. Would you like to make your own appointment? Or if you’d prefer, I can figure out when there is an evening opening. Can you get to Allentown if you have to?",
        # "If you could handle that, it would be really helpful. I don’t want my kids to know about all this if possible.",
        # "I understand. I have something for you at 6pm at MARS ,Wednesday. Work for you?",
        # "Yes, thank you. Will you be there?",
        # "If you would like me to come, I can."]
        #
        # for i, message in enumerate(messages):
        #     if i % 2 == 0:
        #         unomi_client.track_inbound_message(channel, message)
        #     else:
        #         unomi_client.track_outbound_message(channel, message, 'mikeghen')
        #     time.sleep(1)

        # Have some needs
        client_needs = set(random.sample(needs, 3))
        profile["properties"]["needs"] = []
        for need in client_needs:
            _need = {
                "name": need,
                "timeStamp" : datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
            }
            profile["properties"]["needs"].append(_need)

        # Some demographics
        age = random.randint(16, 65)
        gender = random.choice(['male', 'female'])

        demographics = {
            "age": age,
            "gender": gender
        }

        if random.randint(0,100) % 20 == 0 and demographics['gender'] == 'female' and demographics['age'] < 45:
            demographics['pregnant'] = 'yes'
        elif random.randint(0,100) % 20 == 0:
            demographics['children'] = 'yes'
        if random.randint(0,100) % 20 == 0:
            demographics['criminal-record'] = 'yes'
        if random.randint(0,100) % 10 == 0:
            demographics['language'] = 'spanish'
        if random.randint(0,100) % 20 == 0:
            demographics['language'] = 'other'
        if random.randint(0,100) % 20 == 0:
            demographics['hiv'] = 'yes'
        if random.randint(0,100) % 20 == 0:
            demographics['mental-health'] = 'yes'

        profile["properties"]["demographics"] = demographics


        categories = {
            1: "intoxicationWithdrawPotential",
            2: "biomedicalConditionsComplications",
            3: "emotionalBehavioralConditionsComplications",
            4: "readinessToChange",
            5: "relapseContinuedUsePotential",
            6: "recoveryEnvironment"
        }
        scores = {}
        for key, value in categories.items():
            scores[value] = random.randint(1,4)

        profile["properties"]["scores"] = scores

        if random.randint(0,100) < 95:
            profile["properties"]["hadAssessment"] = 'yes'
            if random.randint(0,10) < 8:
                profile["properties"]["inTreatment"] = 'yes'
                profile["properties"]["timeToTreatment"] = random.randint(1,25)


        unomi_client.update_profile(channel, profile["properties"])
