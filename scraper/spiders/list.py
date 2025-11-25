import itertools
import re
from typing import Any, Iterator
from urllib.parse import parse_qs, urlencode, urlparse

from dateparser import parse
from scrapy import Spider
from scrapy.http import Request, Response

REGIONS = [
    "region-abaiskaya-oblast",
    "region-akmolinskaya-oblast",
    "region-aktubinskaya-oblast",
    "region-almatinskaya-oblast",
    "region-atyrauskaya-oblast",
    "region-vostochnokazakhstanskaya-oblast",
    "region-zhambilskaya-oblast",
    "region-zhetysuskaya-oblast",
    "region-zapadnokazakshstabskaya-oblast",
    "region-karagandinskaya-oblast",
    "region-kostanayskaya-oblast",
    "region-kyzylordinskaya-oblast",
    "region-mangistauskaya-oblast",
    "region-pavlodarskaya-oblast",
    "region-severokazakhstanskaya-oblast",
    "region-yuzhnokazahstanskaya-oblast",
    "region-ulytauskaya-oblast",
]

MARKS = [
    "toyota",
    "vaz",
    "hyundai",
    "mercedes-benz",
    "volkswagen",
    "kia",
    "nissan",
    "bmw",
    "audi",
    "mitsubishi",
    "lexus",
    "chevrolet",
    "gaz",
    "daewoo",
    "subaru",
    "mazda",
    "opel",
    "honda",
    "renault",
    "ford",
    "changan",
    "skoda",
    "land-rover",
    "byd",
    "geely",
    "uaz",
    "jac",
    "chery",
    "infiniti",
    "deepal",
    "haval",
    "li",
    "suzuki",
    "porsche",
    "jetour",
    "ravon",
    "ssang-yong",
    "peugeot",
    "zeekr",
    "lifan",
    "cadillac",
    "zaz",
    "jeep",
    "hongqi",
    "faw",
    "dodge",
    "exeed",
    "volvo",
    "tank",
    "jipeng",
    "chrysler",
    "tesla",
    "omoda",
    "genesis",
    "citroen",
    "hummer",
    "saab",
    "moskvich",
    "gac",
    "jaguar",
    "great-wall",
    "maybach",
    "kaiyi",
    "datsun",
    "mini",
    "isuzu",
    "voyah",
    "mg",
    "ij",
    "bentley",
    "jaecoo",
    "fiat",
    "samsung",
    "lincoln",
    "rox",
    "seat",
    "daihatsu",
    "avatr",
    "aito",
    "lynk-and-co",
    "retro-automobiles",
    "buick",
    "xiaomi",
    "mercedes-maybach",
    "eagle",
    "dong-feng",
    "gmc",
    "maserati",
    "pontiac",
    "wuling",
    "acura",
    "foton",
    "denza",
    "polar-stone",
    "zhiji",
    "smart",
    "luaz",
    "leapmotor",
    "hafei",
    "rolls-royce",
    "rover",
    "bugatti",
    "vis",
    "maxus",
    "baic",
    "lamborghini",
    "zx",
    "ram",
    "wey",
    "ferrari",
    "alfa-romeo",
    "hiphi",
    "haima",
    "jmc",
    "dfsk",
    "scion",
    "zil",
    "lotus",
    "hozon",
    "baw",
    "iran-khodro",
    "jetta",
    "eraz",
    "aston-martin",
    "huanghai",
    "mercury",
    "maextro",
    "livan",
    "kyc",
    "seres",
    "proton",
    "shuanghuan",
    "saturn",
    "baojun",
    "xpeng",
    "zotye",
    "tagaz",
    "polestar",
    "alpina",
    "jin-bei",
    "shineray",
    "leopaard",
    "fisker",
    "brilliance",
    "weltmeister",
    "plymouth",
    "vortex",
    "vinfast",
    "gonow",
    "nio",
    "koenigsegg",
    "raf",
    "lancia",
    "dadi",
    "huawei",
    "aro",
    "ora",
    "niutron",
    "ineos",
    "srm",
    "swm",
    "maple",
    "jiyue",
    "evolute",
    "alpine",
    "kg-mobility",
    "jonway",
    "venturi",
    "changfeng",
    "icar",
    "yudo",
    "dacia",
    "serpento",
    "cupra",
    "landian",
    "luxeed",
    "huansu",
    "guojin",
    "venucia",
    "im",
    "nl",
    "ds",
    "enovate",
    "skywell",
    "sol",
    "dayun",
    "hawtai",
    "roewe",
    "aurus",
    "xinkai",
    "puch",
    "derways",
    "santana",
    "lucid",
    "alha",
    "mahindra",
    "hanteng",
    "metrocab",
    "smz",
    "forthing",
    "karry",
    "tianye",
    "vgv",
    "borgward",
    "luxgen",
    "evergrande",
    "yema",
    "blaval",
    "core-power",
    "changan",
    "wanfeng",
    "oldsmobile",
    "radar",
    "farizon",
    "rivian",
    "bajaj",
    "soueast",
    "mclaren",
    "tianma",
    "arcfox",
    "hengrun",
]


class ListSpider(Spider):
    name = "list"
    start_urls = []

    GET_PARAMS = {}

    def __init__(self, start_url: str | None = None, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        for mark, region in itertools.product(MARKS, REGIONS):
            self.start_urls.append(f"https://kolesa.kz/cars/{region}/{mark}/?{urlencode(self.GET_PARAMS)}")

    def parse(self, response: Response, **kwargs: Any) -> Iterator[Request | dict]:
        elements = response.css(".row.pager-row .pager li span a")
        if not len(elements):
            return

        last_page: str = elements[-1].xpath("text()").get()
        for p in range(1, int(last_page)):
            parsed = urlparse(response.url)
            params = parse_qs(parsed.query)
            params["page"] = p

            url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}?{urlencode(params)}"

            yield response.follow(url, callback=self.parse_page)

    def parse_page(self, response: Response) -> Iterator[Request | dict]:
        for element in response.css(".a-card__info .a-card__link"):
            yield response.follow(
                f"https://kolesa.kz{element.attrib['href'].split('?')[-1]}", callback=self.parse_detail
            )

    @classmethod
    def parse_detail(cls, response: Response) -> Iterator[dict[str, Any]]:
        data: dict[str, Any] = {}

        bc = response.css(".offer__breadcrumps ol.breadcrumbs li a::text").getall()
        bc = [t.strip() for t in bc if t and t.strip()]
        if len(bc) >= 2:
            mark_name = bc[-2]
            model_full = bc[-1]

            model_name = model_full.replace(mark_name, "", 1).strip()
            data["mark"] = mark_name.capitalize()
            data["model"] = model_name.capitalize()

        data["year"] = cls._txt(response.css("span.year::text")) or None

        price_raw = cls._txt(response.css("div.offer__price::text")) or ""
        data["price"] = re.sub(r"\D", "", price_raw) or None

        for dl in response.css(".offer__parameters dl"):
            key = cls._txt(dl.css("dt::text")).lower() or cls._txt(dl.css("dt span::text")).lower()
            value = cls._txt(dl.css("dd::text")).lower()

            if not key:
                continue

            if key == "город":
                data["city"] = value.capitalize()

            elif key == "поколение":
                data["generation"] = value

            elif key == "кузов":
                data["body_type"] = value

            elif "объем двигателя" in key:
                m = re.search(r"(\d+(?:[.,]\d+)?)", value)
                if m:
                    data["engine_volume"] = m.group(1).replace(",", ".")

                mf = re.search(r"\(([^)]+)\)", value)
                if mf:
                    data["fuel_type"] = mf.group(1).strip().lower()

            elif key == "пробег":
                data["mileage"] = re.sub(r"\D", "", value) or None

            elif key == "коробка передач":
                data["transmission"] = value

            elif key == "привод":
                data["wheel_drive"] = value.replace(" привод", "").strip()

            elif key == "руль":
                data["rudder"] = value

            elif key == "цвет":
                data["body_color_metallic"] = "металлик" in value
                data["body_color"] = value.replace("металлик", "").strip() or None

            elif "растаможен" in key:
                data["customs_cleared"] = {"да": True, "нет": False}.get(value)

        data["images"] = [
            href.strip()
            for href in response.css(".offer__gallery ul.gallery__thumbs-list button::attr(data-href)").getall()
            if href and href.strip()
        ]

        data["options"] = [
            t.strip().capitalize()
            for t in response.css(".text .offer__options span.offer__option-label::text").getall()
            if t and t.strip()
        ]

        data["comment"] = cls._txt(response.css(".a-description .a-description__text p::text")) or None

        try:
            views_text = cls._txt(response.css(".offer__content-block.offer__info .offer__info-views::text"))
            if " c " in views_text:
                date_str = views_text.split(" c ", 1)[1].strip()
                data["published"] = parse(date_str, dayfirst=True).isoformat()
        except Exception:
            ...

        data["is_damaged"] = bool(response.xpath("//div[contains(text(), 'Аварийная')]").get())

        m = re.search(r"/a/show/(\d+)", response.url)
        if m:
            data["external_id"] = int(m.group(1))

        data["html"] = response.text.strip()

        yield data

    @staticmethod
    def _txt(sel, default: str = "") -> str:
        v = sel.get()

        return v.strip() if v else default
