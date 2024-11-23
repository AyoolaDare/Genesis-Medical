from app import dynamodb, bcrypt
from datetime import datetime
import uuid

class User:
    table = dynamodb.Table('Users')

    @staticmethod
    def create(username, password, role):
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        User.table.put_item(Item={
            'id': str(uuid.uuid4()),
            'username': username,
            'password': hashed_password,
            'role': role
        })

    @staticmethod
    def get_by_username(username):
        response = User.table.get_item(Key={'username': username})
        return response.get('Item')

    @staticmethod
    def check_password(user, password):
        return bcrypt.check_password_hash(user['password'], password)

class Patient:
    table = dynamodb.Table('Patients')

    @staticmethod
    def create(first_name, last_name, phone_number):
        patient_id = str(uuid.uuid4())
        Patient.table.put_item(Item={
            'id': patient_id,
            'first_name': first_name,
            'last_name': last_name,
            'phone_number': phone_number,
            'medical_records': [],
            'created_at': datetime.utcnow().isoformat()
        })
        return patient_id

    @staticmethod
    def get_all():
        response = Patient.table.scan()
        return response['Items']

    @staticmethod
    def get_by_id(patient_id):
        response = Patient.table.get_item(Key={'id': patient_id})
        return response.get('Item')

    @staticmethod
    def update(patient_id, data):
        update_expression = "set "
        expression_attribute_values = {}
        for key, value in data.items():
            update_expression += f"{key} = :{key}, "
            expression_attribute_values[f":{key}"] = value
        update_expression = update_expression.rstrip(", ")

        Patient.table.update_item(
            Key={'id': patient_id},
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_attribute_values
        )

    @staticmethod
    def add_medical_record(patient_id, record):
        record['id'] = str(uuid.uuid4())
        record['timestamp'] = datetime.utcnow().isoformat()
        Patient.table.update_item(
            Key={'id': patient_id},
            UpdateExpression="SET medical_records = list_append(if_not_exists(medical_records, :empty_list), :record)",
            ExpressionAttributeValues={
                ':record': [record],
                ':empty_list': []
            }
        )

    @staticmethod
    def search(query):
        response = Patient.table.scan(
            FilterExpression='contains(first_name, :query) or contains(last_name, :query) or contains(phone_number, :query)',
            ExpressionAttributeValues={':query': query}
        )
        return response['Items']

class Activity:
    table = dynamodb.Table('Activities')

    @staticmethod
    def create(patient_id, patient_name, action, admin_name, admin_role):
        Activity.table.put_item(Item={
            'id': str(uuid.uuid4()),
            'patient_id': patient_id,
            'patient_name': patient_name,
            'action': action,
            'admin_name': admin_name,
            'admin_role': admin_role,
            'timestamp': datetime.utcnow().isoformat()
        })

    @staticmethod
    def get_recent(limit=10):
        response = Activity.table.scan(Limit=limit)
        return sorted(response['Items'], key=lambda x: x['timestamp'], reverse=True)

    @staticmethod
    def get_all():
        response = Activity.table.scan()
        return sorted(response['Items'], key=lambda x: x['timestamp'], reverse=True)