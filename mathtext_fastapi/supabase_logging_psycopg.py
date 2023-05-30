import os
from datetime import datetime, timezone
from logging import getLogger
from mathtext_fastapi.constants import (
    SUPABASE_LINK,
    PROD_SUPABASE_DB,
    PROD_SUPABASE_DBNAME,
    PROD_SUPABASE_USER,
    PROD_SUPABASE_PW
)
import json
import psycopg2
from psycopg2 import sql

log = getLogger(__name__)


def get_current_date():
    current_datetimetz = datetime.now(timezone.utc)
    formated_datetimetz = current_datetimetz.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    return datetime.strptime(formated_datetimetz, '%Y-%m-%dT%H:%M:%S.%fZ')


def check_for_existing_record(
    db_cursor,
    table_name,
    field_name,
    check_value
    ):
    if check_value is None:
        return ()
    db_cursor.execute(f"SELECT * FROM {table_name} WHERE {field_name} LIKE '{check_value}'")
    return db_cursor.fetchone()


def create_a_new_record(db_cursor, table_name, insert_data):

    if table_name == 'message':
        nlu_response = insert_data.pop('nlu_response')
        nlu_response_jsonb = json.dumps(nlu_response)
        insert_data['nlu_response'] = nlu_response_jsonb

        request_object = insert_data.pop('request_object')
        request_object_jsonb = json.dumps(request_object)
        insert_data['request_object'] = request_object_jsonb

    field_names = sql.SQL(', ').join(map(sql.Identifier, insert_data.keys()))
    placeholder = sql.SQL(', ').join(sql.Placeholder() * len(insert_data.keys()))
    values = insert_data.values()

    query = sql.SQL("INSERT INTO {table_name} ({field_names}) VALUES ({placeholder}) RETURNING id, {field_names}").format(
        table_name=sql.Identifier(table_name),
        field_names=field_names,
        placeholder=placeholder
    )

    db_cursor.execute(query, list(insert_data.values()))
    return db_cursor.fetchone()


def get_or_create_record(
    db_cursor,
    insert_data,
    table_name,
    field_name,
    check_value
    ):
    existing_record = check_for_existing_record(db_cursor, table_name, field_name, check_value)
    if existing_record:
        return existing_record
    new_record = create_a_new_record(db_cursor, table_name, insert_data)
    return new_record


def prepare_message_data_for_logging(message_data, nlu_response):
    db_connection = psycopg2.connect(
        host=PROD_SUPABASE_DB,
        database=PROD_SUPABASE_DBNAME,
        user=PROD_SUPABASE_USER,
        password=PROD_SUPABASE_PW
    )
    
    db_cursor = db_connection.cursor()

    try:
        project_data = {
            'name': "Rori",
            # Autogenerated fields: id, created_at, modified_at
        }
        project_record = get_or_create_record(
            db_cursor,
            project_data,
            'project',
            'name',
            project_data['name']
        )

        contact_data = {
            'project': project_record[0],  # FK
            'original_contact_id': message_data['contact_uuid'],
            'urn': "",
            'language_code': "en",
            'contact_inserted_at': get_current_date()
                # Autogenerated fields: id, created_at, modified_at
        }
        contact_record = get_or_create_record(
            db_cursor,
            contact_data,
            'contact',
            'original_contact_id',
            message_data['contact_uuid']
        )

        updated_message_data = {
            'contact': contact_record[0],  # FK
            'original_message_id': message_data['message_id'],
            'text': message_data['message_body'],
            'direction': message_data['message_direction'],
            'sender_type': message_data['author_type'],
            'channel_type': "whatsapp / turn.io",
            'message_inserted_at': datetime.strptime(message_data['message_inserted_at'], '%Y-%m-%dT%H:%M:%S.%fZ'),
            'message_modified_at': datetime.strptime(message_data['message_updated_at'], '%Y-%m-%dT%H:%M:%S.%fZ'),
            'message_sent_at': get_current_date(),
            'nlu_response': nlu_response,
            'request_object': message_data
            # Autogenerated fields: created_at, modified_at
        }
        message_record = get_or_create_record(
            db_cursor,
            updated_message_data,
            'message',
            None,
            None
        )
        db_connection.commit()
        db_connection.close()
    except Exception as e:
        log.error(f'Build failed: {e}')