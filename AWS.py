import Utils
import boto3
from boto3.dynamodb.conditions import Key

ACCESS_KEY = ''
SECRET_KEY = ''


def get_dynamo():
    access_key = ACCESS_KEY
    secret_key = SECRET_KEY
    session = boto3.Session(
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
    )
    return session.resource('dynamodb', region_name='us-west-1')


def get_rsvoid_table():
    Utils.log("Accessing RSVoid table")
    dynamo = get_dynamo()
    return dynamo.Table('RSVoidProfiles')

"""
def does_unique_id_exist(unique_id):
    table = get_rsvoid_table()
    Utils.log(f'Checking table for verification for user: {unique_id}')
    resp = table.query(
        KeyConditionExpression=Key('UniqueID').eq(unique_id),
    )
    for item in resp['Items']:
        if 'Verified' in item:
            Utils.log(f'User {unique_id} verification returned {item["Verified"]}')
            return item['Verified']
    Utils.log(f'User {unique_id} is not in the table.')
    return False
"""

def does_profile_exist(profile):
    resp = table_scan()
    Utils.log(f'Checking if {profile} exists in table')
    for item in resp['Items']:
        if "Profile" in item:
            if item["Profile"] == profile:
                Utils.log(f'Profile exists.')
                return True
    Utils.log(f'Profile does not exist.')
    return False


def get_field_from_table(unique_id, field):
    table = get_rsvoid_table()
    Utils.log(f'Grabbing {field} from table for {unique_id}')
    resp = table.query(
        KeyConditionExpression=Key('UniqueID').eq(unique_id),
    )
    for item in resp['Items']:
        if 'Verified' in item and item['Verified']:
            Utils.log(f'Verification for {unique_id} returned {item["Verified"]}')
            if field in item:
                return item[field]


def table_scan():
    Utils.log("Scanning RSVoid table...")
    table = get_rsvoid_table()
    return table.scan()


def update_field_in_table(unique_id, field, value):
    table = get_rsvoid_table()
    update_expression = f'set {field} = :{field}'
    update_expression_attributes = {f':{field}': value}
    Utils.log(f'Setting {field} to {value} for {unique_id}')
    table.update_item(
        Key={'UniqueID': unique_id},
        UpdateExpression=update_expression,
        ExpressionAttributeValues=update_expression_attributes
    )


def create_new_link_in_table(unique_id, token, profile):
    update_field_in_table(unique_id=unique_id, field="AuthToken", value=token)
    update_field_in_table(unique_id=unique_id, field="Profile", value=profile)
    update_field_in_table(unique_id=unique_id, field="Verified", value=False)

