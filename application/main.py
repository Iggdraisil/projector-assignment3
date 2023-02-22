import asyncio
import os

from fastapi import FastAPI, Depends
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase, AsyncIOMotorCollection
from elasticsearch import AsyncElasticsearch
from pymongo.collection import Collection

app = FastAPI()


def mongo_db_dep() -> AsyncIOMotorDatabase:
    return AsyncIOMotorClient(
        os.environ.get("MONGODB_HOST", "localhost"),
        os.environ.get("MONGODB_PORT", 27017),
    ).test_database


async def elastic_dep() -> AsyncElasticsearch:
    elasticsearch = AsyncElasticsearch(
        f'http://{os.environ.get("ELASTIC_HOST", "localhost")}:{os.environ.get("ELASTIC_PORT", "9200")}'
    )
    bar = not await elasticsearch.indices.get(index="foo", ignore_unavailable=True)
    if bar:
        await elasticsearch.indices.create(index="foo")
    await elasticsearch.update(index="foo", id="bar", doc={"baz": 1}, upsert={"baz": 1})
    return elasticsearch


@app.get("/test")
async def say_hello(
        name: str = 'Pizza',
        mongo: AsyncIOMotorDatabase = Depends(mongo_db_dep),
        elastic: AsyncElasticsearch = Depends(elastic_dep),
):
    result, _ = await asyncio.gather(
        touch_mongo(mongo, name),
        touch_elastic(elastic, name)
    )
    return result


async def touch_elastic(elastic: AsyncElasticsearch, name: str):
    result = await elastic.get(index="foo", id="bar") or {'baz': 1}
    result['_source']['baz'] += 1
    await elastic.update(index="foo", id="bar", doc=result['_source'] | {'name': name})


async def touch_mongo(mongo, name):
    collection = mongo.foo_collection
    result = await collection.find_one({'foo': {'$gt': 0}})
    if not result:
        await collection.insert_one({"foo": 1})
    else:
        await collection.replace_one({'_id': result['_id']}, {'foo': result['foo'] + 1, 'name': name})
    return {"message": f"Hello"}
