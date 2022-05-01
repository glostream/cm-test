from src.gapi import Gapi
from src.keepa import Keepa


def main():
    gapi = Gapi()
    keepa = Keepa()

    master, settings = gapi.get_spreadsheet(gapi.master_id)
    template, cerebro1, cerebro2, cerebro_final, keepa_final = gapi.get_spreadsheet(
        gapi.mlk_id
    )

    min_relevance, min_sv = [int(v) for v in settings[1].values]

    # Use first row as header and delete
    master.columns = master.iloc[0]
    master = master.iloc[1:, :]

    for i, row in master.iterrows():
        if row.Status != "Done" and row.Keyword:
            # Needs to be processed
            products = keepa.product_search(row.Keyword)
            asins1, asins2 = products["asin"][:10], products["asin"][10:20]
            print("got products")


if __name__ == "__main__":
    main()
