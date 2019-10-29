import re
import uuid
import random
import sqlite3
# TODO: Setup a custom corpus for this so it doesn't pick sketchy names
from coolname import generate_slug


def channel_token(number):
  """
  Encodes a phone number to a Slack channel name
  of the form is a two word slug. Repeats the same slug for
  the same number
  """
  random.seed("999" + str(number))
  return generate_slug(2)


def sanitize_number(number):
  return re.sub('\D', '', str(number))


def validate_number(number):
  """
  Returns a valid phone number or False if number is invalid
  """
  number = sanitize_number(number)
  l = len(number)
  if l == 10:
    return number
  elif l >= 11:
    return number[-10:]
  else:
    return False


def to_E_164_number(number):
  """
  Validates and formats phone numbers to the E.164 international format
  adopted by Twilio: https://www.twilio.com/docs/glossary/what-e164
  Raises an error for invalid numbers
  """
  number = validate_number(number)
  if not number:
      raise ValueError
  return "+1" + str(number)


def return_facilities(zipcode=None):
    """
    Returns facilities for a zipcode
    """
    data=[]
    database = "./utils/facilities.db"
    db = sqlite3.connect(database)
    cursor= db.cursor()
    sql="""SELECT * FROM (SELECT
    name_of_doctor || " " || street1 || " " ||  street2 || " " || city ||  " " || state || " " || zip || " " ||  phone as address
    FROM facilities where zip=?) where address is not null"""
    result = cursor.execute(sql, zipcode)
    for row in result:
        data.append(row)
    return data


def return_beds(county, gender, age):
    """
    Looks in the openbeds.csv file and finds any open beds based on
    county, gender, and age
    """
    csvfile = open(open_beds.csv)
    reader = csv.DictReader(csvfile)
    beds = []
    for row in reader:
        if county:
            if row["county"].upper() != county.upper():
                is_match = False
        if age:
            if int(row["max_age"]) < age:
                is_match = False
        if gender:
            if row["gender"].upper() != gender.upper():
                is_match = False
        if is_match:
            beds.append(row)

    return beds
