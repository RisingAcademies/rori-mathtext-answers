import os
from datetime import datetime, timezone
from logging import getLogger

from sqlalchemy import (
    Column,
    Text,
    Integer,
    DateTime,
    ForeignKey
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.future import select
from sqlalchemy.orm import sessionmaker

from mathtext_fastapi.constants import SUPABASE_LINK

log = getLogger(__name__)
async_engine = create_async_engine(
    SUPABASE_LINK,
    pool_size=30,
    pool_timeout=90
)
async_session = sessionmaker(
    bind=async_engine,
    autocommit=False,
    autoflush=False,
    class_=AsyncSession
)
Base = declarative_base()


async def format_datetime_in_isoformat(dt):
    return getattr(dt.now(), 'isoformat', lambda x: None)()


async def get_current_date():
    current_datetimetz = datetime.now(timezone.utc)
    formated_datetimetz = current_datetimetz.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    return datetime.strptime(formated_datetimetz, '%Y-%m-%dT%H:%M:%S.%fZ')

class Project(Base):
    __tablename__ = "project"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(Text)
    # created_at = Column(DateTime(timezone=True))
    # modified_at = Column(DateTime(timezone=True))


class Contact(Base):
    __tablename__ = "contact"
    id = Column(Integer, primary_key=True, index=True)
    project = Column(Integer, ForeignKey("project.id"))
    original_contact_id = Column(Text)
    urn = Column(Text)
    language_code = Column(Text)
    contact_inserted_at = Column(DateTime(timezone=True))
    # created_at = Column(DateTime(timezone=True))
    # modified_at = Column(DateTime(timezone=True))


class Message(Base):
    __tablename__ = "message"
    id = Column(Integer, primary_key=True, index=True)
    contact = Column(Integer, ForeignKey("contact.id"))
    original_message_id = Column(Text)
    text = Column(Text)
    direction = Column(Text)
    sender_type = Column(Text)
    channel_type = Column(Text)
    message_inserted_at = Column(DateTime(timezone=True))
    message_modified_at = Column(DateTime(timezone=True))
    message_sent_at = Column(DateTime(timezone=True))
    # created_at = Column(DateTime(timezone=True))
    # modified_at = Column(DateTime(timezone=True))
    nlu_response = Column(JSONB)
    request_object = Column(JSONB)


async def get_or_create_record(
    table_name,
    insert_data,
    check_variable=None
    ):
    # Query the database to check if the user exists
    async with async_session() as session:
        record = None
        try:
            if table_name == 'project':
                statement = select(Project).where(Project.name == insert_data['name'])
                result = await session.execute(statement)
                record = result.scalar_one_or_none()
            elif table_name == 'contact':
                statement = select(Contact).where(Contact.original_contact_id == insert_data['original_contact_id'])
                result = await session.execute(statement)
                record = result.scalar_one_or_none()
            else:
                pass
        except Exception as e:
            log.error(f'Supabase entry retrieval failed: {table_name} : {insert_data} / {e}')
            return []

        # If the user exists, return the existing record
        if record:
            return record

        # If the user doesn't exist, create a new record
        if table_name == 'project':
            new_record = Project(**insert_data)
        elif table_name == 'contact':
            new_record = Contact(**insert_data)
        elif table_name == 'message':
            new_record = Message(**insert_data)
        session.add(new_record)
        await session.commit()
        await session.refresh(new_record)

        return new_record


async def prepare_message_data_for_logging(message_data, nlu_response):
    """ Builds objects for each table and logs them to the database

    Input:
    - message_data: an object with the full message data from Turn.io/Whatsapp
    """
    project_data = {
        'name': "Rori",
        # Autogenerated fields: id, created_at, modified_at
    }
    project_data_log = await get_or_create_record(
        'project',
        project_data,
        'name'
    )
    try:
        contact_data = {
            'project': project_data_log.id,  # FK
            'original_contact_id': message_data['contact_uuid'],
            'urn': "",
            'language_code': "en",
            'contact_inserted_at': await get_current_date()
            # Autogenerated fields: id, created_at, modified_at
        }
    except AttributeError as e:
        log.error(f'Build contact_data object for Supabase failed: {project_data_log} / {message_data} / {e}')
        return False

    contact_data_log = await get_or_create_record(
        'contact',
        contact_data
    )

    del message_data['author_id']

    try:
        message_data = {
            'contact': contact_data_log.id,  # FK
            'original_message_id': message_data['message_id'],
            'text': message_data['message_body'],
            'direction': message_data['message_direction'],
            'sender_type': message_data['author_type'],
            'channel_type': "whatsapp / turn.io",
            'message_inserted_at': datetime.strptime(message_data['message_inserted_at'], '%Y-%m-%dT%H:%M:%S.%fZ'),
            'message_modified_at': datetime.strptime(message_data['message_updated_at'], '%Y-%m-%dT%H:%M:%S.%fZ'),
            'message_sent_at': await get_current_date(),
            'nlu_response': nlu_response,
            'request_object': message_data
            # Autogenerated fields: created_at, modified_at
        }
    except AttributeError as e:
        log.error(f'Build message_data object for Supabase failed: {contact_data_log} / {e}')
        return False

    message_data_log = await get_or_create_record(
        'message',
        message_data
    )
