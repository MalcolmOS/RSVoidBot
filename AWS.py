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
    dynamo = get_dynamo()
    return dynamo.Table('RSVoidProfiles')


def does_unique_id_exist(unique_id):
    table = get_rsvoid_table()
    resp = table.query(
        KeyConditionExpression=Key('UniqueID').eq(unique_id),
    )
    for item in resp['Items']:
        if 'Verified' in item:
            return item['Verified']
    return False


def does_profile_exist(profile):
    table = get_rsvoid_table()
    resp = table.scan()

    for item in resp['Items']:
        if "Profile" in item:
            if item["Profile"] == profile:
                return True
    return False


def get_field_from_table(unique_id, field):
    table = get_rsvoid_table()
    resp = table.query(
        KeyConditionExpression=Key('UniqueID').eq(unique_id),
    )
    for item in resp['Items']:
        if field in item:
            return item[field]


def table_scan():
    print("Checking table for new roles")
    table = get_rsvoid_table()
    return table.scan()


def update_field_in_table(unique_id, field, value):
    table = get_rsvoid_table()
    update_expression = f'set {field} = :{field}'
    update_expression_attributes = {f':{field}': value}

    table.update_item(
        Key={'UniqueID': unique_id},
        UpdateExpression=update_expression,
        ExpressionAttributeValues=update_expression_attributes
    )


def create_new_link_in_table(unique_id, token, profile):
    update_field_in_table(unique_id=unique_id, field="AuthToken", value=token)
    update_field_in_table(unique_id=unique_id, field="Profile", value=profile)
    update_field_in_table(unique_id=unique_id, field="Verified", value=False)

