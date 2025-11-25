import json
import queue
import threading
import time
from typing import Any, Dict

import pika
from pika.adapters.blocking_connection import BlockingConnection
from scrapy import Spider
from scrapy.crawler import Crawler

__all__ = ["RabbitMQPipeline"]


class RabbitMQPipeline:
    def __init__(
        self,
        url: str,
        exchange: str = "",
        ex_type: str | None = None,
        routing_key: str = "",
        queue_name: str | None = None,
        durable: bool = True,
        use_confirms: bool = True,
        buffer_size: int = 1000,
    ) -> None:
        self.url = url
        self.exchange = exchange or ""
        self.ex_type = ex_type
        self.routing_key = routing_key or ""
        self.queue_name = queue_name
        self.durable = bool(durable)
        self.use_confirms = bool(use_confirms)
        self.buffer_size = int(buffer_size)

        self._conn: BlockingConnection | None = None
        self._ch = None
        self._buf: "queue.Queue[bytes]" = queue.Queue(self.buffer_size)
        self._stop = threading.Event()
        self._worker_thread: threading.Thread | None = None

    @classmethod
    def from_crawler(cls, crawler: Crawler):
        g = crawler.settings.get
        return cls(
            url=g("RABBITMQ_URL"),
            exchange=g("RABBITMQ_EXCHANGE", ""),
            ex_type=g("RABBITMQ_EX_TYPE"),
            routing_key=g("RABBITMQ_ROUTING_KEY", ""),
            queue_name=g("RABBITMQ_QUEUE"),
            durable=g("RABBITMQ_DURABLE", True),
            use_confirms=g("RABBITMQ_CONFIRM", True),
            buffer_size=g("RABBITMQ_BUFFER", 100),
        )

    def open_spider(self, spider: Spider) -> None:
        if not self.url:
            raise RuntimeError("RABBITMQ_URL is required")

        self._stop.clear()
        self._worker_thread = threading.Thread(target=self._worker, name="rabbitmq-publisher", daemon=True)
        self._worker_thread.start()

    def close_spider(self, spider: Spider) -> None:
        self._stop.set()
        if self._worker_thread:
            self._worker_thread.join(timeout=5)

        try:
            if self._conn and self._conn.is_open:
                self._conn.close()
        except Exception:
            spider.logger.exception("RabbitMQ connection is closed")

        self._conn = None
        self._ch = None

    def process_item(self, item: Dict[str, Any], spider):
        body = json.dumps(dict(item), ensure_ascii=False).encode("utf-8")
        try:
            self._buf.put(body, timeout=2)
        except queue.Full:
            spider.logger.error("RabbitMQ buffer is full: dropping message")

        return item

    def _worker(self):
        backoff = 1.0
        while not self._stop.is_set():
            if not self._ensure_channel():
                time.sleep(min(backoff, 15))
                backoff *= 2
                continue

            backoff = 1.0

            try:
                body = self._buf.get(timeout=0.5)
            except queue.Empty:
                continue

            try:
                props = pika.BasicProperties(
                    delivery_mode=2 if self.durable else 1, content_type="application/json; charset=utf-8"
                )
                self._ch.basic_publish(
                    exchange=self.exchange,
                    routing_key=self.routing_key if self.exchange else (self.queue_name or self.routing_key),
                    body=body,
                    properties=props,
                    mandatory=False,
                )
                if self.use_confirms:
                    ...

            except Exception:
                self._safe_close()

                try:
                    self._buf.put_nowait(body)
                except queue.Full:
                    ...

                time.sleep(1)

    def _ensure_channel(self) -> bool:
        try:
            if not self._conn or not self._conn.is_open:
                params = pika.URLParameters(self.url)
                params.heartbeat = params.heartbeat or 30
                params.blocked_connection_timeout = params.blocked_connection_timeout or 30

                self._conn = pika.BlockingConnection(params)

            if not self._ch or self._ch.is_closed:
                self._ch = self._conn.channel()

                if self.use_confirms:
                    self._ch.confirm_delivery()

                if self.exchange:
                    ex_type = (self.ex_type or "direct").lower()
                    self._ch.exchange_declare(exchange=self.exchange, exchange_type=ex_type, durable=self.durable)
                    if self.queue_name:
                        self._ch.queue_declare(queue=self.queue_name, durable=self.durable)
                        self._ch.queue_bind(queue=self.queue_name, exchange=self.exchange, routing_key=self.routing_key)
                else:
                    qname = self.queue_name or self.routing_key
                    if not qname:
                        raise RuntimeError("queue name (RABBITMQ_QUEUE) or routing key must be set when exchange=''")

                    self._ch.queue_declare(queue=qname, durable=self.durable)

            return True
        except Exception:
            self._safe_close()

            return False

    def _safe_close(self):
        try:
            if self._ch and self._ch.is_open:
                self._ch.close()
        except Exception:
            ...

        try:
            if self._conn and self._conn.is_open:
                self._conn.close()
        except Exception:
            ...

        self._ch = None
        self._conn = None
