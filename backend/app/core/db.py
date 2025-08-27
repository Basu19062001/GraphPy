import time
from threading import Lock
from typing import List, Optional, Tuple

from app.core.config import settings
from app.logger import logger
from motor.motor_asyncio import (
    AsyncIOMotorClient,
    AsyncIOMotorCollection,
    AsyncIOMotorDatabase,
)
from pymongo import ASCENDING
from pymongo.errors import OperationFailure

_lock = Lock()
_client: Optional[AsyncIOMotorClient] = None
_db: Optional[AsyncIOMotorDatabase] = None


def get_client() -> AsyncIOMotorClient:
    """
    Get or initialize the MongoDB client
    """
    global _client, _db

    if _client is None:
        with _lock:
            if _client is None:  # Double-check pattern
                try:
                    _client = AsyncIOMotorClient(settings.MONGO_DSN)
                    _db = _client[settings.MONGO_DB]
                    logger.info("Connected to MongoDB.")
                except Exception as e:
                    logger.error(f"Could not connect to MongoDB: {e}")
                    raise
    return _client


def collection(name: str) -> AsyncIOMotorCollection:
    """
    Get a collection by name
    """
    if _db is None:
        get_client()
    return _db[name]


# async def create_ttl_index():
#     """Create TTL index for jobs, questions, users and auth_tokens collections"""
#     retries = 3
#     jobs = collection("jobs")
#     questions = collection("questions")
#     auth_tokens = collection("auth_tokens")
#     users = collection("users")

#     while retries:
#         try:
#             # Get the index information for collections
#             jobs_indexes = await jobs.index_information()
#             questions_indexes = await questions.index_information()
#             auth_tokens_indexes = await auth_tokens.index_information()
#             users_indexes = await users.index_information()

#             index_key = f"expireAt_{ASCENDING}"
#             ttl_seconds = 15 * 60  # 15 minutes = 900 seconds

#             # Handle jobs collection
#             if index_key in jobs_indexes:
#                 if jobs_indexes.get(index_key, {}).get("expireAfterSeconds") == ttl_seconds:
#                     logger.info("TTL index already exists for jobs collection.")
#                 else:
#                     logger.info("Dropping existing TTL index for jobs collection.")
#                     await jobs.drop_index(index_key)
#                     await jobs.create_index(
#                         [("expireAt", ASCENDING)],
#                         name="expireAt_1",
#                         expireAfterSeconds=ttl_seconds,
#                     )
#             else:
#                 await jobs.create_index(
#                     [("expireAt", ASCENDING)],
#                     name="expireAt_1",
#                     expireAfterSeconds=ttl_seconds,
#                 )

#             # Handle questions collection
#             if index_key in questions_indexes:
#                 if questions_indexes.get(index_key, {}).get("expireAfterSeconds") == ttl_seconds:
#                     logger.info("TTL index already exists for questions collection.")
#                 else:
#                     logger.info("Dropping existing TTL index for questions collection.")
#                     await questions.drop_index(index_key)
#                     await questions.create_index(
#                         [("expireAt", ASCENDING)],
#                         name="expireAt_1",
#                         expireAfterSeconds=ttl_seconds,
#                     )
#             else:
#                 await questions.create_index(
#                     [("expireAt", ASCENDING)],
#                     name="expireAt_1",
#                     expireAfterSeconds=ttl_seconds,
#                 )

#             # Handle auth_tokens collection
#             if index_key in auth_tokens_indexes:
#                 if auth_tokens_indexes.get(index_key, {}).get("expireAfterSeconds") == 0:
#                     logger.info("TTL index already exists for auth_tokens collection.")
#                 else:
#                     logger.info("Dropping existing TTL index for auth_tokens collection.")
#                     await auth_tokens.drop_index(index_key)
#                     await auth_tokens.create_index(
#                         [("expireAt", ASCENDING)],
#                         name="expireAt_1",
#                         expireAfterSeconds=0,
#                     )
#             else:
#                 await auth_tokens.create_index(
#                     [("expireAt", ASCENDING)],
#                     name="expireAt_1",
#                     expireAfterSeconds=0,
#                 )

#             # Handle users collection
#             user_index_name = "email_verification_expire_at"
#             if user_index_name in users_indexes:
#                 if users_indexes.get(user_index_name, {}).get("expireAfterSeconds") == 0:
#                     logger.info("TTL index already exists for users collection.")
#                 else:
#                     logger.info("Dropping existing TTL index for users collection.")
#                     await users.drop_index(user_index_name)
#                     await users.create_index(
#                         [("userExpireAt", ASCENDING)],
#                         name=user_index_name,
#                         expireAfterSeconds=0,
#                     )
#             else:
#                 logger.info("Creating TTL index for users collection.")
#                 await users.create_index(
#                     [("userExpireAt", ASCENDING)],
#                     name=user_index_name,
#                     expireAfterSeconds=0,
#                 )

#             return

#         except OperationFailure as e:
#             retries -= 1
#             logger.error(f"Error while creating TTL indexes!! Retrying {3-retries+1}")
#             time.sleep(2)


# async def create_indexes(collection, indexes: List[Tuple[str, int]], **kwargs):
#     """
#     Create a single or compound index on a MongoDB collection if it doesn't exist.

#     Args:
#         collection: MongoDB collection object to create indexes on
#         indexes: List of tuples containing (field_name, sort_order) pairs
#                 where sort_order is ASCENDING (1) or DESCENDING (-1)
#         **kwargs: Additional arguments to pass to create_index()

#     Returns:
#         None

#     Raises:
#         OperationFailure: If index creation fails due to MongoDB errors

#     Example:
#         await create_indexes(
#             collection("users"),
#             [("email", ASCENDING), ("created_at", DESCENDING)]
#         )
#     """
#     try:
#         existing_indexes = await collection.list_indexes().to_list(None)
#         existing_index_keys = [tuple(idx["key"].items()) for idx in existing_indexes]

#         index_key = [(field, sort_order) for field, sort_order in indexes]
#         index_tuple = tuple(index_key)

#         if index_tuple not in existing_index_keys:
#             name = "_".join(f"{field}_{sort_order}" for field, sort_order in index_key)
#             await collection.create_index(index_key, name=name, **kwargs)
#             logger.info(f"Created index {name} on {collection.name}")
#         else:
#             logger.info(f"Index {index_tuple} already exists on {collection.name}")

#     except OperationFailure as e:
#         logger.error(f"Failed to create index on {collection.name}: {str(e)}")
#         raise


_client = get_client()
