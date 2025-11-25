import json
from typing import Any, Dict

import boto3
from botocore.client import Config
from scrapy import Spider
from scrapy.crawler import Crawler
from twisted.internet.threads import deferToThread

__all__ = ["S3Pipeline"]


class S3Pipeline:
    def __init__(
        self,
        endpoint_url: str,
        access_key: str,
        secret_key: str,
        region: str,
        bucket: str,
        prefix: str = "",
        acl: str | None = None,
        public_url_base: str | None = None,
    ) -> None:
        self.endpoint_url = endpoint_url
        self.access_key = access_key
        self.secret_key = secret_key
        self.region = region or "us-east-1"
        self.bucket = bucket
        self.prefix = (prefix or "").lstrip("/").rstrip("/")
        self.acl = acl
        self.public_url_base = public_url_base.rstrip("/") if public_url_base else None

        self.s3 = None

    @classmethod
    def from_crawler(cls, crawler: Crawler) -> None:
        g = crawler.settings.get

        return cls(
            endpoint_url=g("S3_ENDPOINT_URL"),
            access_key=g("S3_ACCESS_KEY"),
            secret_key=g("S3_SECRET_KEY"),
            region=g("S3_REGION"),
            bucket=g("S3_BUCKET"),
            prefix=g("S3_PREFIX"),
            acl=g("S3_ACL"),
            public_url_base=g("S3_PUBLIC_URL_BASE"),
        )

    def open_spider(self, spider: Spider) -> None:
        if not (self.endpoint_url and self.bucket and self.access_key and self.secret_key):
            raise RuntimeError("S3 settings are incomplete (need endpoint, bucket, access/secret keys).")

        self.s3 = boto3.client(
            "s3",
            endpoint_url=self.endpoint_url,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            region_name=self.region,
            config=Config(signature_version="s3v4"),
        )

    def close_spider(self, spider: Spider) -> None:
        ...

    def process_item(self, item: Dict[str, Any], spider: Spider) -> dict:
        html = item.pop("html", None)
        external_id = item.get("external_id")
        if not all([html, external_id]):
            spider.logger.warning("S3HtmlPipeline: skip item (no html or external_id): %s", json.dumps(item)[:200])

            return item

        key = f"{external_id}.html"
        if self.prefix:
            key = f"{self.prefix}/{key}"

        item["s3_bucket"] = self.bucket
        item["s3_key"] = key

        deferToThread(self._upload, item, key, html)

        return item

    def _upload(self, item: Dict[str, Any], key: str, html: str) -> None:
        put_kwargs = {
            "Bucket": self.bucket,
            "Key": key,
            "Body": html.encode("utf-8"),
            "ContentType": "text/html; charset=utf-8",
        }

        if self.acl:
            put_kwargs["ACL"] = self.acl

        self.s3.put_object(**put_kwargs)
