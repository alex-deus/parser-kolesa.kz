import threading
from typing import Any, Dict, List

from pymongo import MongoClient, UpdateOne
from scrapy import Spider
from scrapy.crawler import Crawler

__all__ = ["MongoPipeline"]


class MongoPipeline:
    def __init__(self, uri: str, db_name: str, collection: str, batch_size: int = 10):
        self.uri = uri
        self.db_name = db_name
        self.collection_name = collection
        self.batch_size = batch_size

        self.client: MongoClient | None = None
        self.collection = None
        self._buf: List[Dict[str, Any]] = []
        self._lock = threading.Lock()

    @classmethod
    def from_crawler(cls, crawler: Crawler):
        return cls(
            uri=crawler.settings.get("MONGO_URI"),
            db_name=crawler.settings.get("MONGO_DATABASE"),
            collection=crawler.settings.get("MONGO_COLLECTION"),
            batch_size=crawler.settings.getint("MONGO_BATCH_SIZE", 10),
        )

    def open_spider(self, spider: Spider):
        self.client = MongoClient(self.uri)
        self.collection = self.client[self.db_name][self.collection_name]

    def process_item(self, item: Dict[str, Any], spider):
        with self._lock:
            self._buf.append(dict(item))
            if len(self._buf) >= self.batch_size:
                self._flush()

        return item

    def close_spider(self, spider: Spider):
        with self._lock:
            if self._buf:
                self._flush()
        if self.client:
            self.client.close()

    def _flush(self):
        if not self._buf:
            return

        operations = []
        for doc in self._buf:
            if "external_id" not in doc:
                continue

            operations.append(UpdateOne({"external_id": doc["external_id"]}, {"$set": doc}, upsert=True))

        if operations:
            self.collection.bulk_write(operations, ordered=False)

        self._buf = []
