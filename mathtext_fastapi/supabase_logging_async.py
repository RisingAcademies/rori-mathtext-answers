import asyncio
from asyncpg.exceptions import ConnectionDoesNotExistError
from collections import deque
from datetime import datetime, timezone
from logging import getLogger
from typing import Deque

from mathtext_fastapi.constants import SUPABASE_LINK
from sqlalchemy import Column, Integer
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.future import select
from sqlalchemy.orm import sessionmaker

async def pre_ping_function(conn):
    await conn.execute("SELECT 1")

log = getLogger(__name__)
async_engine = create_async_engine(
    SUPABASE_LINK,
    pool_size=20,
    pool_timeout=30,
    pool_pre_ping=True,
    pool_recycle=1800
)
async_session = sessionmaker(
    bind=async_engine,
    autocommit=False,
    autoflush=False,
    class_=AsyncSession
)

# Just used for seeing how many connections are in the pool
pool = async_session().get_bind().pool
Base = declarative_base()

# Database logging will happen when the batch reaches this value
BATCH_SIZE = 30


class RequestBatch:
    """ Manages a double-ended queue (d e que) that stores request objects and the nlu evaluation results """
    def __init__(self):
        self.requests: Deque[dict] = deque()

    def add_request(self, request: dict):
        self.requests.append(request)

    def is_full(self) -> bool:
        return len(self.requests) >= BATCH_SIZE

    def empty_requests(self):
        self.requests.clear()


request_batch = RequestBatch()


class Message(Base):
    """ A minimal example of the 'message' table in the db.  
    
    Decomposition of the request_object to otherfields happens during ETL outside of API """
    __tablename__ = "message"
    id = Column(Integer, primary_key=True, index=True)
    nlu_response = Column(JSONB)
    request_object = Column(JSONB)


async def log_batch(batch, retry_attempts=0):
    """ Bulk uploads a set of request/response entries to the database """
    async with async_session() as session:
        for request in batch:
            # Add the request data to the db session
            log_entry = Message(
                nlu_response=request["nlu_response"],
                request_object=request["request_object"]
            )
            session.add(log_entry)
        try:
            # Commit the changes to the db and close the async session
            await session.commit()
        except ConnectionDoesNotExistError as e:
            retry_limit = 3
            if retry_attempts < retry_limit:
                await log_batch(batch, retry_attempts + 1)
            else:
                log.error(f'Retry attempts for logging failed --- {e}')
                # Add the data back to preserve it
                request_batch.requests.extend(batch)
        except Exception as e:
            # Undo changes to the database session
            await session.rollback()
            # Add the data back to preserve it
            request_batch.requests.extend(batch)
        finally:
            await session.close()


async def prepare_message_data_for_logging(message_data, nlu_response):
    """ Builds objects for each table and logs them to the database

    Input:
    - message_data: an object with the full message data from Turn.io/Whatsapp
    """
    # Remove phone number from logging
    del message_data['author_id']

    try:
        message_data = {
            'nlu_response': nlu_response,
            'request_object': message_data
        }
    except AttributeError as e:
        log.error(f'Build message_data object for Supabase failed: {message_data} / {e}')
        return False

    request_batch.add_request(message_data)
    if request_batch.is_full():
        batch = request_batch.requests.copy()
        request_batch.empty_requests()
        asyncio.create_task(log_batch(batch))
    # print("Current number of connections:", pool.checkedin())

