from decimal import Decimal
import json
import os


INSERT_EVENT = 'INSERT'
DECIMAL_VALUE_TYPE = 'N'
STRING_VALUE_TYPE = 'S'
TIME_TO_STOP = Decimal(os.getenv('TIME_TO_STOP', '0'))


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
    message = '{0}: Leave in {1} {2} for a {3} bus'
    for i, record in enumerate(new_bustracker_records(records=event['Records'])):
        time_until_leave = record['time_until_arrival'] - TIME_TO_STOP
        time_until_leave = int(time_until_leave / 60)
        if time_until_leave > 0:
            args = [i, time_until_leave, 'minutes', record['route_id']]
            args[2] = args[2][:-1] if time_until_leave == 1 else args[2]
            print(message.format(*args))
