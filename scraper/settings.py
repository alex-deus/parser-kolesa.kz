import json
import os

BOT_NAME = "kolesa"

SPIDER_MODULES = ["scraper.spiders"]
NEWSPIDER_MODULE = "scraper.spiders"

ADDONS = {}

ROBOTSTXT_OBEY = True

CONCURRENT_REQUESTS = int(os.getenv("CONCURRENT_REQUESTS", 2))
CONCURRENT_REQUESTS_PER_DOMAIN = CONCURRENT_REQUESTS
DOWNLOAD_DELAY = 1

REDIRECT_ENABLED = False

DEFAULT_REQUEST_HEADERS_FILE = os.getenv("DEFAULT_REQUEST_HEADERS_FILE")
DEFAULT_REQUEST_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
    "Alt-Used": "kolesa.kz",
    "Connection": "keep-alive",
    "Host": "kolesa.kz",
    "Priority": "u=0, i",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:139.0) Gecko/20100101 Firefox/139.0",
}
if DEFAULT_REQUEST_HEADERS_FILE and os.path.exists(DEFAULT_REQUEST_HEADERS_FILE):
    with open(DEFAULT_REQUEST_HEADERS_FILE, "r") as f:
        data = json.load(f)
    DEFAULT_REQUEST_HEADERS.update(data)

DOWNLOADER_MIDDLEWARES = {
    "scraper.middlewares.RandomUserAgentMiddleware": 400,
    "scrapy.downloadermiddlewares.retry.RetryMiddleware": 550,
}

ROTATING_PROXY_LIST_PATH = os.getenv("ROTATING_PROXY_LIST_PATH", "proxies.txt")
if os.path.exists(ROTATING_PROXY_LIST_PATH):
    DOWNLOADER_MIDDLEWARES.update(
        {
            "rotating_proxies.middlewares.RotatingProxyMiddleware": 610,
            "rotating_proxies.middlewares.BanDetectionMiddleware": 620,
        }
    )

ITEM_PIPELINES = {}

FEED_EXPORT_ENCODING = "utf-8"

S3_ENDPOINT_URL = os.getenv("S3_ENDPOINT_URL", "http://minio:9000")
S3_ACCESS_KEY = os.getenv("S3_ACCESS_KEY", "user")
S3_SECRET_KEY = os.getenv("S3_ACCESS_KEY", "pass-pass")
S3_REGION = os.getenv("S3_ACCESS_KEY", "us-east-1")
S3_BUCKET = os.getenv("S3_BUCKET", "html")
S3_PREFIX = os.getenv("S3_PREFIX", "pages")
S3_ACL = "public-read"

if all([S3_ENDPOINT_URL, S3_ACCESS_KEY, S3_SECRET_KEY, S3_REGION, S3_BUCKET]):
    ITEM_PIPELINES["scraper.pipelines.S3Pipeline"] = 200

MONGO_URI = os.getenv("MONGO_URI", "mongodb://user:pass@mongo:27017")
MONGO_DATABASE = os.getenv("MONGO_DATABASE", "kolesa")
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION", "cars")
MONGO_BATCH_SIZE = os.getenv("MONGO_BATCH_SIZE", 10)

if MONGO_URI:
    ITEM_PIPELINES["scraper.pipelines.MongoPipeline"] = 300

RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://admin:admin@rabbit:5672/")
RABBITMQ_EXCHANGE = os.getenv("RABBITMQ_EXCHANGE", "kolesa")
RABBITMQ_EX_TYPE = os.getenv("RABBITMQ_EX_TYPE", "direct")
RABBITMQ_ROUTING_KEY = os.getenv("RABBITMQ_ROUTING_KEY", "kolesa")
RABBITMQ_QUEUE = os.getenv("RABBITMQ_QUEUE", "cars")
RABBITMQ_DURABLE = True
RABBITMQ_CONFIRM = True
RABBITMQ_BUFFER = int(os.getenv("RABBITMQ_BUFFER", 10))

if RABBITMQ_URL:
    ITEM_PIPELINES["scraper.pipelines.RabbitMQPipeline"] = 400

LIST_GET_PARAMS = {}
LIST_GET_PARAMS_FILE = os.getenv("LIST_GET_PARAMS_FILE")
if LIST_GET_PARAMS_FILE and os.path.exists(LIST_GET_PARAMS_FILE):
    with open(LIST_GET_PARAMS_FILE, "r") as f:
        data = json.load(f)
    LIST_GET_PARAMS.update(data)
