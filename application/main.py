import asyncio
import os
import random

import requests
from elasticsearch import AsyncElasticsearch
from fastapi import FastAPI, Depends
from motor.motor_asyncio import (
    AsyncIOMotorClient,
    AsyncIOMotorDatabase,
)

word_site = "https://www.mit.edu/~ecprice/wordlist.10000"

response = requests.get(word_site)
WORDS = response.content.decode('utf-8').splitlines()
app = FastAPI()

DOCS_NUM = 100000


async def mongo_db_dep() -> AsyncIOMotorDatabase:
    return AsyncIOMotorClient(
        os.environ.get("MONGODB_HOST", "localhost"),
        int(os.environ.get("MONGODB_PORT", "27017")),
        maxConnecting=100,
        maxPoolSize=1000,
    ).test_database


async def elastic_dep() -> AsyncElasticsearch:
    return AsyncElasticsearch(
        f'http://{os.environ.get("ELASTIC_HOST", "localhost")}:{os.environ.get("ELASTIC_PORT", "9200")}',
        connections_per_node=1000,
    )


@app.get("/test")
async def say_hello(
        mongo: AsyncIOMotorDatabase = Depends(mongo_db_dep),
        elastic: AsyncElasticsearch = Depends(elastic_dep),
):
    await asyncio.gather(
        touch_mongo(mongo),
        touch_elastic(elastic),
    )
    return {}


async def touch_elastic(elastic: AsyncElasticsearch):
    await asyncio.gather(
        # elastic.search(
        #     index="foo",
        #     query={"match": {"word": {"query": r.get_random_word()}}},
        # ),
        elastic.search(
            index="foo",
            query={
                "match": {"description": {"query": random.choice(WORDS)}}
            },
        ),

    )


async def touch_mongo(mongo):
    collection = mongo.foo_collection
    id_ = random.randint(0, DOCS_NUM)
    result = await collection.find_one({f"foo{id_}": {"$gt": 0}})
    if not result:
        await collection.insert_one({f"foo{id_}": 1})
    else:
        await collection.replace_one(
            {"_id": result["_id"]},
            {f"foo{id_}": result[f"foo{id_}"] + 1, "name": random.choice(WORDS)},
        )
    return {"message": f"Hello"}
