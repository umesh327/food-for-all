
"""
Lexbot Lambda handler.
"""
from urllib.request import Request, urlopen
from urllib.parse import quote_plus
from os import environ

import psycopg2
import logging
import traceback
import json
import boto3

endpoint=environ.get('DB_ENDPOINT')
database=environ.get('DB_NAME')
dbuser=environ.get('DB_USER')
password=environ.get('DB_PASSWORD')
port=environ.get('DB_PORT')
opencage_api_key = environ.get('OPEN_CAGE_DATA_API_KEY')

MILES_TO_METERS = 1609
DEFAULT_MILE_RADIUS = 5*MILES_TO_METERS

results = []

logger=logging.getLogger()
logger.setLevel(logging.INFO)

logger.info("Cold start complete.") 

def close(message):
    response = {
        "dialogAction": {
            "type": "Close",
            "fulfillmentState": "Fulfilled",
            "message": {
              "contentType": "SSML",
              "content": message
            },
        }
    }
    return response
    
def make_connection():
    conn_str="host={0} dbname={1} user={2} password={3} port={4} connect_timeout=5".format(
        endpoint,database,dbuser,password,port)
    conn = psycopg2.connect(conn_str)
    conn.autocommit=True
    return conn 

def exec_statement(cnx, stmt, rows=-1):
    rowcount = 0
    results = []
    try:
        cursor = cnx.cursor()
        cursor.execute(stmt)
        rowcount = cursor.rowcount
        if rows > 0:
            results = cursor.fetchmany(rows)
        cursor.close()
    except (Exception, psycopg2.DatabaseError) as error:
        logger.info(error)        
        rowcount = -1
    return (rowcount, results)

def xstr(s):
    if s is None:
        return ''
    return str(s)

def geocode(address):
    logger.info('geocode, address = ' + address)
    encoded_address = quote_plus(address)
    request = Request('https://api.opencagedata.com/geocode/v1/json?q=' + encoded_address + '&key=' + opencage_api_key + '&language=en')
    response = json.loads(urlopen(request).read())
    results = response['results']
    logger.info('geocode, result = ' + xstr(results))
    return results

def lambda_handler(event, context):
    logger.info('lambda_handler, event: ' + str(event))
    cnx = make_connection()
    intentName = event['currentIntent']['name']
    userId = event['userId']
    requestAttributes = event['requestAttributes']
    if requestAttributes is not None:
        channel_type = requestAttributes['x-amz-lex:channel-type']
    else:
        channel_type='emulator'
    logger.info('lambda_handler, intentName=' + intentName + ',requestAttributes=' + xstr(requestAttributes) + ',channel_type=' + channel_type)
    if intentName == 'FoodForAllRegistration':
        first_name = event['currentIntent']['slots']['Firstname']
        last_name = event['currentIntent']['slots']['Lastname']
        full_name = first_name + ' ' + last_name
        address = event['currentIntent']['slots']['Address']
        registrationType = event['currentIntent']['slots']['RegType'] 
        geo_result = geocode(address)
        geohash = geo_result[0]['annotations']['geohash']
        w3w = geo_result[0]['annotations']['what3words']['words']
        formatted = geo_result[0]['formatted']
        geometry = geo_result[0]['geometry']
        logger.info('formatted=' + formatted + ',geometry=' + xstr(geometry))
        geopoint = 'SRID=4326;POINT(' + str(geometry['lng']) + ' ' + str(geometry['lat']) + ')'
        dbquery = "insert into registrations values (\'{0}\',  \'{1}\',   \'{2}\', \'{3}\',      \'{4}\', \'{5}\', \'{6}\', \'{7}\')".format(
                                                       userId, full_name, address, channel_type, registrationType, geohash, w3w,  geopoint)
        ret, results = exec_statement(cnx, dbquery)
        content = "Error in saving registration"
        if ret >= 0:
            content = "Thank you {name} for registering.".format(name=full_name)
        else:
            logger.info(results)
        response = close(content)
        
    if intentName == 'CheckRegistration':
        dbquery = "select full_name from registrations where userId=\'{0}\'".format(userId)
        ret, results = exec_statement(cnx, dbquery, 1)
        if ret >= 0:
            full_name = results[0][0]
            content = "Hello {0}, you were already registered. Thank you.".format(full_name)
        else:
            content = "You are not registered" 
        response = close(content)
        
    if intentName == 'DonateFood':
        results = []
        sns = boto3.client('sns')
        food_type = event['currentIntent']['slots']['Food']
        expiry = event['currentIntent']['slots']['Expiry'] 
        newstr = ''
        if 'W' in expiry and len(expiry)==8:
            newstr = expiry.replace("W", "")
            ts_format = "YYYY-WW"
        else:
            newstr = expiry
            ts_format = "YYYY-MM-DD"
        dbquery = "insert into donations values (\'{0}\',  \'{1}\',   \'{2}\', to_timestamp(\'{3}\', \'{4}\'))".format(
                                                  userId, food_type, expiry,   newstr,            ts_format)
        ret, result = exec_statement(cnx, dbquery)
        if ret < 0:
            content = "Donor can only make one donation until a patron was matched or food expires"
        else:
            content = ""
            dbquery = "select full_name, address from registrations where userId = \'{0}\'".format(userId)
            ret, result = exec_statement(cnx, dbquery, 1)
            if ret > 0:
                donor_name = result[0][0]
                donor_address = result[0][1]
                donor_phone = userId
                logger.info('lambda_handler, intentName=' + intentName + ',donor_name=' + donor_name + ',donor_address=' + donor_address + ',donor_phone=' + donor_phone)
                dbquery = "select r1.userId, r1.full_name, r1.address, r1.channel_type from registrations r1 left join registrations r2 on ST_DWithin(r1.location, r2.location, {0}) where (r1.reg_type='patron' or r1.reg_type='both') and (r2.reg_type='donor' and r2.userId in (select userId from donations))".format(DEFAULT_MILE_RADIUS)
                ret, results = exec_statement(cnx, dbquery, 2)
                for r in results:
                    patron_phone = r[0]
                    patron_name = r[1]
                    patron_address = r[2]
                    chl = r[3]
                    logger.info('lambda_handler, intentName=' + intentName + ',patron_name=' + patron_name + ',patron_address=' + patron_address + ',patron_phone=' + patron_phone)
                    if chl == 'Twilio-SMS':
                        sns.publish(PhoneNumber='+' + patron_phone, Message="{0} is donating {1} food expires by {2} it can be picked up from {3}. You can reach them at {4}. Please confirm with the donor.".format(donor_name, food_type, expiry, donor_address, donor_phone))
                        content += "{0} at {1} will be contacted for pickup. You can reach patron at {2}".format(patron_name, patron_address, patron_phone)
        response = close(content) 

    logger.info('lambda_handler, response = ' + str(response))
    return response
    