import datetime
import json
import os
import dotenv
import string
import requests
from bs4 import BeautifulSoup

import gspread
from oauth2client.service_account import ServiceAccountCredentials

dotenv.load_dotenv()

def get_nemzet_headers(soup):
    return soup.find_all("div", class_="enews-article-offerer-title")


def get_index_headers(soup):
    return soup.find_all("h1")


MAX_TITLES = 10

sites = [
    ("https://index.hu/", get_index_headers),
    ("https://magyarnemzet.hu/", get_nemzet_headers),
]


if __name__ == "__main__":

    out = []
    for site_url, site_header_getter in sites:

        resp = requests.get(site_url)
        soup = BeautifulSoup(resp.content, "html5lib")
        current_time = datetime.datetime.now().isoformat()
        for i, header in enumerate(site_header_getter(soup)[:MAX_TITLES]):
            a_tag = header.find("a")
            if a_tag is None:
                a_tag = header.find_parent("a")

            if a_tag:
                link = a_tag["href"]
            else:
                link = None
            out.append(
                {
                    "title": header.text.strip(),
                    "link": link,
                    "time": current_time,
                    "site": site_url,
                    "ind": i + 1,
                }
            )

    spread_id = "1ti4e4rHKi_6WV4pYccY1YvX0t17dgyXwSBdoiZH2i8M"
    d = json.load(open("creds.json"))
    d["private_key"] = os.environ["GSPREAD_PRIVATE_KEY"]
    scope = ["https://spreadsheets.google.com/feeds"]
    credentials = ServiceAccountCredentials.from_json_keyfile_dict(d, scope)
    gc = gspread.authorize(credentials)
    sheet = gc.open_by_key(spread_id).sheet1
    record = out[0]
    col_headers = list(record.keys())
    end_letter = string.ascii_uppercase[len(col_headers) - 1]
    end_of_sheet = sheet.row_count
    rows = [list(d.values()) for d in out]
    sheet.add_rows(len(rows))
    sheet_range_name = f"A{end_of_sheet + 1}:{end_letter}{len(rows)+end_of_sheet}"
    sheet.update(sheet_range_name, rows)
