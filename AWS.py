import Utils
import boto3
from boto3.dynamodb.conditions import Key

ACCESS_KEY = ''
SECRET_KEY = ''


class DynamoDB:
    def __init__(self):
        Utils.log("Loading DynamoDB...")
        self.table = self.get_rsvoid_table()
        Utils.log("Successfully loaded DynamoDB...")

    @staticmethod
    def get_dynamo():
        access_key = ACCESS_KEY
        secret_key = SECRET_KEY
        session = boto3.Session(
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
        )
        return session.resource('dynamodb', region_name='us-west-1')

    def get_rsvoid_table(self):
        Utils.log("Accessing RSVoid table")
        dynamo = self.get_dynamo()
        return dynamo.Table('RSVoidProfiles')

    def does_unique_id_exist(self, unique_id):
        Utils.log(f'Checking table for verification for user: {unique_id}')
        resp = self.table.query(
            KeyConditionExpression=Key('UniqueID').eq(unique_id),
        )
        for item in resp['Items']:
            if 'Verified' in item:
                Utils.log(f'User {unique_id} verification returned {item["Verified"]}')
                return item['Verified']
        Utils.log(f'User {unique_id} is not in the table.')
        return False

    def does_profile_exist(self, profile):
        resp = self.table_scan()
        Utils.log(f'Checking if {profile} exists in table')
        for item in resp['Items']:
            if "Profile" in item:
                if item["Profile"] == profile:
                    Utils.log(f'Profile exists.')
                    return True
        Utils.log(f'Profile does not exist.')
        return False

    def get_auth_token_from_table(self, unique_id):
        Utils.log(f'Grabbing AuthToken from table for {unique_id}')
        resp = self.table.query(
            KeyConditionExpression=Key('UniqueID').eq(unique_id),
        )
        for item in resp['Items']:
            if "AuthToken" in item:
                return item["AuthToken"]

    def get_field_from_table(self, unique_id, field):
        Utils.log(f'Grabbing {field} from table for {unique_id}')
        resp = self.table.query(
            KeyConditionExpression=Key('UniqueID').eq(unique_id),
        )
        for item in resp['Items']:
            if 'Verified' in item and item['Verified']:
                Utils.log(f'Verification for {unique_id} returned {item["Verified"]}')
                if field in item:
                    Utils.log(f'Returning {field} from table for {unique_id}')
                    return item[field]
        Utils.log(f'{field} does not exist for user - {unique_id}')

    def table_scan(self):
        Utils.log("Scanning RSVoid table...")
        return self.table.scan()

    def update_field_in_table(self, unique_id, field, value):
        update_expression = f'set {field} = :{field}'
        update_expression_attributes = {f':{field}': value}
        Utils.log(f'Setting {field} to {value} for {unique_id}')
        self.table.update_item(
            Key={'UniqueID': unique_id},
            UpdateExpression=update_expression,
            ExpressionAttributeValues=update_expression_attributes
        )

    def create_new_link_in_table(self, unique_id, token, profile):
        self.update_field_in_table(unique_id=unique_id, field="AuthToken", value=token)
        self.update_field_in_table(unique_id=unique_id, field="Profile", value=profile)
        self.update_field_in_table(unique_id=unique_id, field="Verified", value=False)

