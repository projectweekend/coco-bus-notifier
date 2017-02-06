from decimal import Decimal
import json


INSERT_EVENT = 'INSERT'
DECIMAL_VALUE_TYPE = 'N'
STRING_VALUE_TYPE = 'S'


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
    for record in new_bustracker_records(records=event['Records']):
        print(record)


# if __name__ == "__main__":
#     with open('test_event.json') as f:
#         test_event = json.load(f)
#     lambda_handler(event=test_event, context=None)
