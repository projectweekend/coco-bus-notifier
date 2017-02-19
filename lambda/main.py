from datetime import datetime
from decimal import Decimal
import json
import os
import boto3
from pytz import timezone


INSERT_EVENT = 'INSERT'
DECIMAL_VALUE_TYPE = 'N'
STRING_VALUE_TYPE = 'S'
TIME_TO_STOP = Decimal(os.getenv('TIME_TO_STOP', '300'))
START_HR = int(os.getenv('START_HR', '7'))
START_MIN = int(os.getenv('START_MIN', '30'))
END_HR = int(os.getenv('END_HR', '8'))
END_MIN = int(os.getenv('END_MIN', '30'))
SMS_NUMBER = os.getenv('SMS_NUMBER')
assert SMS_NUMBER
TIME_ZONE = os.getenv('TIME_ZONE')
assert TIME_ZONE


SNS = boto3.client('sns')


def _timestamp_to_tz(ts, tz):
    return timezone(tz).localize(datetime.fromtimestamp(ts))


def _is_time_to_send(dt):
    if dt.hour == START_HR and dt.minute >= START_MIN:
        return True
    if dt.hour == END_HR and dt.minute <= END_MIN:
        return True
    if dt.hour > START_HR and dt.hour < END_HR:
        return True
    return False


def parse_field_value(value_dict):
    # value_dict only has one key/value pair so just return the value
    for value_type, value_str in value_dict.iteritems():
        if value_type == DECIMAL_VALUE_TYPE:
            return Decimal(value_str)
        elif value_type == STRING_VALUE_TYPE:
            return value_str


def parse_record_from_image(image):
    record = {}
    for field_name, value_dict in image.iteritems():
        record[field_name.lower()] = parse_field_value(value_dict=value_dict)
    return record


def new_bustracker_records(records):
    for record in records:
        if record['eventName'] == INSERT_EVENT:
            yield parse_record_from_image(image=record['dynamodb']['NewImage'])


def lambda_handler(event, context):
    output = []
    for record in new_bustracker_records(records=event['Records']):
        current_dt = _timestamp_to_tz(ts=record['current_time'], tz=TIME_ZONE)
        if _is_time_to_send(dt=current_dt):
            time_until_leave = record['time_until_arrival'] - TIME_TO_STOP
            time_until_leave = int(time_until_leave / 60)
            if time_until_leave > 0:
                args = [
                    time_until_leave,
                    'minutes',
                    record['route_id'],
                    record['vehicle_id']
                ]
                args[1] = args[1][:-1] if time_until_leave == 1 else args[1]
                output.append('Leave in {0} {1} for the {2} ({3})'.format(*args))
    if output:
        SNS.publish(**{
            'PhoneNumber': SMS_NUMBER,
            'Message': output[0]
        })
