from numpy import product
import keepa
from keys.keys import KEEPA as KEY
import requests
import urllib
import pandas as pd


class Keepa:
    def __init__(self) -> None:
        self.api = keepa.Keepa(KEY)
        self.domain = "1"  # com
        self.stats = "90"  # return 90 day averages in "stats" object
        self.scodes = {
            "400": "REQUEST_REJECTED",
            "402": "PAYMENT_REQUIRED",
            "405": "METHOD_NOT_ALLOWED",
            "429": "NOT_ENOUGH_TOKEN",
        }

        self.product_cols = [
            "asin",
            "imagesCSV",
            "title",
            "rootCategory",
            "variationCSV",
            "brand",
        ]

    def get_api(self, path):
        raw = requests.get(
            f"https://api.keepa.com/{path}",
        )

        status_code = str(raw.status_code)
        if status_code != "200":
            if status_code in self.scodes:
                raise Exception(self.scodes[status_code])
            else:
                raise Exception("REQUEST_FAILED")

        response = raw.json()

        if "error" in response:
            if response["error"]:
                raise Exception(response["error"]["message"])

        return response

    def search(self, keyword):
        products = self.api.query(keyword, domain=self.domain)
        return products

    def product_search(self, keyword):
        response = self.get_api(
            f"search?key={KEY}&domain={self.domain}&type=product&term={urllib.parse.quote(keyword)}&stats={self.stats}"
        )

        raw_products = pd.DataFrame(response["products"])
        products = raw_products.copy()[self.product_cols]

        products.insert(
            3,
            "salesRank",
            raw_products.apply(lambda row: row["stats"]["avg90"][3], axis=1),
        )
        products.insert(
            4,
            "rating",
            raw_products.apply(lambda row: row["stats"]["current"][16] / 10.0, axis=1),
        )
        products.insert(
            5,
            "ratingCount",
            raw_products.apply(lambda row: row["stats"]["current"][17], axis=1),
        )
        products.insert(
            6,
            "newPrice",
            raw_products.apply(lambda row: row["stats"]["avg90"][1] / 100.0, axis=1),
        )
        products.insert(
            8,
            "subCategory",
            raw_products.apply(
                lambda row: row["categories"][0] if row["categories"] else "", axis=1
            ),
        )

        return products
