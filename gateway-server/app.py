import logging
from flask import Flask, request, render_template, flash, jsonify, session, redirect, url_for
from utils.helpers import validate_number, to_E_164_number, return_facilities
from clients.slack import Slack
from clients.twilio import Twilio
from clients.unomi import Unomi
from clients.two_one_one import TwoOneOne
from clients.aunt_bertha import AuntBertha
from datetime import datetime
from utils.user import User
import sqlite3
import os

from flask_login import LoginManager, login_user, logout_user, current_user, login_required

# TODO: Set up application logging

app = Flask(__name__)
# app.secret_key = os.environ["SECRET_KEY"] or b'_5#y2L"F4Q8z\n\xec]/' # or not working!?
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
# app.config['TESTING'] = False
# app.config['LOGIN_DISABLED'] = False

slack_client = Slack()
twilio_client = Twilio()
unomi_client = Unomi()
too_client = TwoOneOne()
aunt_bertha_client = AuntBertha()

@app.errorhandler(500)
def internal_error(error):
    return jsonify(error)


# Flask-Login Manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"



@app.route('/')
def index():
    return render_template('index.html')


@app.route('/submit', methods=['POST'])
def web_submit():
    """
    Handles phone number submission coming from the website
    """
    # Look for phone number from request form or request value:
    number = request.values.get('From', None)
    if not number:
        try:
            number = request.form["number"]
            app.logger.error("Using web form submission.")
        except KeyError as e:
            app.logger.error("Invalid submission.")
    else:
        app.logger.error("Using SMS submission.")
    number = validate_number(number)
    body = request.values.get('Body', None)

    channel, phone_number = slack_client.start_engagement(number, twilio_client)
    profile = unomi_client.create_profile(profile_id=channel,
                                      properties={'phoneNumber': phone_number})
    assert(profile['itemId'] == channel) # Sanity check
    unomi_client.track_event(channel, 'engagementStarted', {})
    if body: # Case when this is a SMS submission
        slack_client.forward_twilio_message(channel, body)
        unomi_client.track_inbound_message(channel, body)
    return render_template('confirmation.html')


@app.route('/message', methods=['POST'])
def message():
    """
    Callback for Twilio. Messages posted to this route will forward the message
    to the Slack channel associated with the senders phone number.
    """
    body = request.values.get('Body', None)
    from_zip = request.values.get('FromZip', None)
    from_city = request.values.get('FromCity', None)
    from_state = request.values.get('FromState', None)

    number = to_E_164_number(request.values.get('From', None))
    channel = unomi_client.channel_from_phone_number(number)
    profile = unomi_client.profile_search(channel)
    app.logger.error("SLACK CHANNEL?: {0}".format(slack_client.does_channel_exist(channel)))
    if not slack_client.does_channel_exist(channel):
        app.logger.error("Performing Web Submit: {0} {1}".format(channel, body))
        web_submit() # Creates a profile
    else:
        app.logger.error("Channel Body: {0} {1}".format(channel, body))
        slack_client.forward_twilio_message(channel, body)
        unomi_client.track_inbound_message(channel, body)
    if "city" not in profile["properties"].keys():
        if from_city or from_state or from_zip:
            unomi_client.update_profile(
                profile_id=channel,
                properties={
                    "city": from_city,
                    "state": from_state,
                    "zipcode": from_zip
                }
            )
            body = ":world_map: Approximate Location: {0}, {1} {2}".format(from_city, from_state, from_zip)
            response = slack_client.forward_twilio_message(channel, body)

    return "200"



@app.route('/text', methods=['POST'])
def text():
    """
    Callback for Slack. /send commands in Slack will trigger a post to this
    route with parameters as defined here:
    https://api.slack.com/slash-commands#app_command_handling
    """
    channel_name = request.values.get('channel_name', None)
    body = request.values.get('text', None)
    channel_id = request.values.get('channel_id', None)
    user_name = request.values.get('user_name', None)
    app.logger.debug("Request: {0}".format(request.values))
    channel_name = slack_client.group_name_from_group_id(channel_id)
    number = unomi_client.phone_number_from_channel(channel_name)

    if number:
        text = "@" + user_name + ": " + body
        try:
            twilio_client.text(number, body)
        except Exception as e:
            return jsonify(e)
        app.logger.debug("Slack user: {0}".format(user_name))
        unomi_client.track_outbound_message(channel_name, body, user_name)

        return jsonify(
            response_type='in_channel',
            text="Message sent",
        )
    else:
        return 400



@app.route('/assessed', methods=['POST'])
def assessed():
    """
    Callback for Slack, /assessed commands in Slack will trigger a post to this
    route with parameters.
    """
    body = request.values.get('text', None)
    channel_id = request.values.get('channel_id', None)
    user_name = request.values.get('user_name', None)
    channel_name = slack_client.group_name_from_group_id(channel_id)
    profile = unomi_client.profile_search(channel_name)
    #profile["properties"]["assessed"] = datetime.today().strftime("%Y-%m-%d")
    profile["properties"]["hadAssessment"] = 'yes'
    unomi_client.update_profile(channel_name, profile["properties"])
    return jsonify(
        response_type='in_channel',
        text="Updated saved.",
    )

@app.route('/treated', methods=['POST'])
def treated():
    """
    Callback for Slack, /treated commands in Slack will trigger a post to this
    route with parameters.
    """
    body = request.values.get('text', None)
    channel_id = request.values.get('channel_id', None)
    user_name = request.values.get('user_name', None)
    channel_name = slack_client.group_name_from_group_id(channel_id)
    profile = unomi_client.profile_search(channel_name)
    #profile["properties"]["treated"] = datetime.today().strftime("%Y-%m-%d")
    profile["properties"]["inTreatment"] = 'yes'
    unomi_client.update_profile(channel_name, profile["properties"])
    return jsonify(
        response_type='in_channel',
        text="Updated saved.",
    )


@app.route('/need', methods=['POST'])
def need():
    """
    Callback for Slack, /need commands in Slack will trigger a post to this
    route with parameters.

    The usage for /need is:

    /need [name]
    ex: /need bed

    """
    app.logger.info(request.values)
    body = request.values.get('text', None)
    channel_id = request.values.get('channel_id', None)
    user_name = request.values.get('user_name', None)
    text = body.strip()
    need = {
        "name": text,
        "timeStamp" : datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
    }
    channel_name = slack_client.group_name_from_group_id(channel_id)
    app.logger.info(channel_name)
    profile = unomi_client.profile_search(channel_name)
    # Update profile property with this need
    try:
        app.logger.info(profile)
        needs = profile["properties"]["needs"]
        needs.append(need)
        needs = list(set(needs))
    except TypeError:
        # FIXME: what does unomi return if there are no needs previously?
        # If an empty array, the above section will work, and we do not need to
        # catch a TypeError exception.  Else, let's add a test for this case
        needs = [need]
    profile["properties"]["needs"] = needs
    unomi_client.update_profile(channel_name, profile["properties"])
    return jsonify(
        response_type='in_channel',
        text="Need saved: {0}".format(text),
    )


@app.route('/demographics', methods=['POST'])
def demographics():
    """
    Callback for Slack, /demographic commands in Slack will trigger a post to this
    route with parameters.

    The usage for /demographic is:

    /demographic [key] [value]
    ex: /demographic gender male

    """
    body = request.values.get('text', None)
    channel_id = request.values.get('channel_id', None)
    user_name = request.values.get('user_name', None)
    text = body.strip().split()
    key = text[0]
    value = text[1]
    demographic = {
        key: value
    }
    channel_name = slack_client.group_name_from_group_id(channel_id)
    profile = unomi_client.profile_search(channel_name)
    # Update profile property with this need
    try:
        demographics = profile["properties"]["demographics"]
        demographics[key] = value
    except KeyError:
        demographics = {key: value}

    text = "Demographic saved: {0}={1}".format(key, value)
    profile["properties"]["demographics"] = demographics
    unomi_client.update_profile(channel_name, profile["properties"])
    return jsonify(
        response_type='in_channel',
        text=text
    )


@app.route('/event', methods=['POST'])
def event():
    """
    Callback for Slack, /event commands in Slack will trigger a post to this
    route with parameters.

    The usage for /event is:

    /event [name]
    ex: /event bed

    """
    print("SLACK REQUEST: ", request.values)
    channel_name = request.values.get('channel_name', None)
    body = request.values.get('text', None)
    channel_id = request.values.get('channel_id', None)
    user_name = request.values.get('user_name', None)
    event = body.strip()
    profile = unomi_client.profile_search(channel_name) # NOTE: why is this function called?
    unomi_client.track_event(channel_name, 'userGenerated', {'value': event}, user_name)

    return jsonify(
            response_type='in_channel',
            text="Event saved: {0}".format(event))


@app.route('/stage', methods=['POST'])
def stage():
    """
    Callback for Slack, /stage commands in Slack will trigger a post to this
    route with parameters.

    The usage for /stage is:

    /stage [stage] [notes]
    ex: /stage preparation meeting scheduled with physician

    """
    print("SLACK REQUEST: ", request.values)
    channel_name = request.values.get('channel_name', None)
    body = request.values.get('text', None)
    channel_id = request.values.get('channel_id', None)
    user_name = request.values.get('user_name', None)
    stage = body.split()[0]
    notes = ' '.join(body.split()[1:])
    profile = unomi_client.profile_search(channel_name)
    unomi_client.track_event(channel_name, 'stageChange', {'value': stage, 'notes': notes}, user_name)
    profile = unomi_client.profile_search(channel_name)
    profile["properties"]["stage"] = {"name":stage,"notes":notes}
    unomi_client.update_profile(channel_name, profile["properties"])
    return jsonify(
            response_type='in_channel',
            text="Event saved")


@app.route('/facilities', methods=['POST'])
def facilities():
    zipcode = request.form["text"]
    data= return_facilities(zipcode=zipcode)
    attachments = []
    for i in range(len(data)):
        attachment = {
            "title": "Facility",
            "fields": [{
                "value": "Address: {0}".format(data[i])
            }]
        }
        attachments.append(attachment)


    return jsonify(
        response_type='in_channel',
        text="Facilities",
        attachments=attachments
    )


@app.route('/beds', methods=['POST'])
def beds():
    """
    Callback for Slack, /beds commands in Slack will trigger a post to this
    route with parameters.

    The usage for /beds is:

    /beds [county] [gender] [age]
    ex: /beds philadelphia male 21

    """
    channel_name = request.values.get('channel_name', None)
    user_name = request.values.get('user_name', None)
    row = request.form["text"].split()
    county, gender, age = None, None, None
    try:
        county = row[0]
        gender = row[1]
        age = row[2]
    except IndexError:
        # OK, only set if needed
        pass
    beds = return_beds(county, gender, age)
    attachments = []
    for bed in beds:
        attachment = {
            "title": bed["name"],
            "fields": [{
                "value": "Phone: {0}".format(bed["phone"])
            }]
        }
        attachments.append(attachment)
    if len(attachments) == 0: # No beds found
        event_info =  {'county': county, 'age': age, 'gender':gender }
        unomi_client.track_event(channel_name, 'noBeds', event_info, user_name)
        text = "No beds found, this event has been logged."
    else:
        text = "Open Beds in {county}".format(county=county)

    return jsonify(
        response_type='in_channel',
        text=text,
        attachments=attachments
    )

@app.route('/aunt_bertha', methods=['POST'])
def aunt_bertha():
    """
    Callback for Slack, /auntbertha commands in Slack will trigger a post to this
    route with parameters.

    The usage for /211 is:

    /auntbertha [zipcode] [keywords]
    ex: /auntberta 19107 women recovery

    """
    app.logger.debug("SLACK REQUEST: ", request.values)
    channel_name = request.values.get('channel_name', None)
    body = request.values.get('text', None)
    channel_id = request.values.get('channel_id', None)
    user_name = request.values.get('user_name', None)
    text = body.strip().split()
    zipcode = text[0]
    keywords = " ".join(text[1:])
    profile = unomi_client.profile_search(channel_name)
    unomi_client.track_event(channel_name, 'auntBerthaLookup', {'keywords': keywords, 'zipcode':zipcode}, user_name)
    attachments =  aunt_bertha_client.search(keywords, zipcode)
    return jsonify(
            response_type='in_channel',
            text="Aunt Bertha Results",
            attachments=attachments)



@app.route('/211', methods=['POST'])
def two_one_one():
    """
    Callback for Slack, /211 commands in Slack will trigger a post to this
    route with parameters.

    The usage for /211 is:

    /211 [keyword] [zipcode]
    ex: /211 shelter 19011

    """
    print("SLACK REQUEST: ", request.values)
    channel_name = request.values.get('channel_name', None)
    body = request.values.get('text', None)
    channel_id = request.values.get('channel_id', None)
    user_name = request.values.get('user_name', None)
    text = body.strip().split()
    keyword = text[0]
    zipcode = text[1]
    profile = unomi_client.profile_search(channel_name)
    unomi_client.track_event(channel_name, 'twoOneOneLookup', {'value': "{0} {1}".format(keyword, zipcode)}, user_name)
    attachments = too_client.search(keyword, zipcode)
    return jsonify(
            response_type='in_channel',
            text="211 Results",
            attachments=attachments)


"""
Admin User Interface
"""
@app.route('/profiles', methods=['GET'])
@login_required
def profiles_index():
    print("attempting")
    profiles = unomi_client.list_profiles()
    assessments = 0
    treatments = 0
    for profile in profiles:
        try:
            if profile["properties"]["hadAssessment"] == 'yes':
                assessments += 1
            if profile["properties"]["inTreatment"] == 'yes':
                treatments += 1
        except:
            pass

    return render_template('profiles/index.html',
            profiles=profiles,
            profiles_count=len(profiles),
            treatments=treatments,
            treatment_rate=round(treatments/len(profiles)*100,1),
            assessments=assessments,
            assessment_rate=round(assessments/len(profiles)*100,1))


@app.route('/profiles/<profile_id>', methods=['GET'])
@login_required
def profiles_show(profile_id):
    profile = unomi_client.profile_search(profile_id)
    events = unomi_client.list_events(profile_id)
    crss_messages = {} #{ ('Michael Ghen', '+12154781286'): 17,  ... }

    for event in events:
        try:
            user_name = event['source']['itemId']
            crs_name, phone_number = slack_client.get_phone_number_by_user_name(user_name)
            app.logger.debug("{0}, {1}".format(crs_name, phone_number))
            key = (crs_name, phone_number)
            if key in crss_messages.keys():
                crss_messages[key] += 1
            else:
                crss_messages[key] = 1
        # Case when there is an inbound message, no CRS involved
        except TypeError as e:
            app.logger.warning(e)
            pass # Go to the next event

    all_crs_messages = []
    for key, value in crss_messages.items():
        all_crs_messages.append([key[0], key[1], value])
    crss_messages = all_crs_messages
    return render_template('profiles/show.html', profile=profile, events=events, crss_messages=crss_messages)


@app.route('/profiles/needs', methods=['GET'])
@login_required
def profiles_needs_index():
    profiles = unomi_client.list_profiles()
    needs = []
    for profile in profiles:
        try:
            for need in profile["properties"]["needs"]:
                needs.append(
                    (profile["itemId"], need, "Philadelphia")
                )
        except KeyError:
            # No needs
            pass
    return render_template('profiles/needs/index.html', needs=needs)

@app.route('/profiles/needs/data', methods=['GET'])
@login_required
def profiles_needs_data():
    profiles = unomi_client.list_profiles()
    needs = {}
    county_needs = {}
    counties = []
    for profile in profiles:
        if 'needs' in profile["properties"].keys():
            for need in profile["properties"]["needs"]:
                if need["name"] in needs.keys():
                    needs[need["name"]] += 1
                else:
                    needs[need["name"]] = 1
                county = profile["properties"]["county"]
                if need["name"] in county_needs.keys():
                    if county in county_needs[need["name"]].keys():
                        county_needs[need["name"]][county] += 1
                    else:
                        county_needs[need["name"]][county] = 1
                        counties.append(county)
                else:
                    county_needs[need["name"]] = {}


    pie_data = []
    for key, value in needs.items():
        pie_data.append({'name': key, 'y': value})

    bar_series = [] # {name:, data:}
    for key, value in county_needs.items():
        values = list(value.values())
        bar_series.append({'name': key, 'data': values})


    return jsonify( {'pie_data': pie_data, 'bar_series': bar_series, 'counties': list(set(counties))} )







# user managment/routes
@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.validate(request.form["username"], request.form["password"])
        if user is None:
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user)

        flash('Logged in successfully.')

        next = request.args.get('next')
        # is_safe_url should check if the url is safe for redirects.
        # See http://flask.pocoo.org/snippets/62/ for an example.
        # if not is_safe_url(next):
            # return abort(400)
        return redirect(next or url_for('index'))
    else:
        if current_user.is_authenticated:
            return redirect(url_for('index'))
        return render_template('login.html')



@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))
