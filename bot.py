import requests
from bs4 import BeautifulSoup

URL = "https://www.serebii.net/pokedex-sm/025.shtml"
HEADERS = {"User-Agent": "Mozilla/5.0"}

def scrape_serebii_basic(url):
    res = requests.get(url, headers=HEADERS)
    res.raise_for_status()
    soup = BeautifulSoup(res.text, "html.parser")

    data = {}

    # Locate the main dex info table (the one you shared)
    dex_table = soup.find("table", class_="dextable")
    if not dex_table:
        raise ValueError("Main table not found.")

    rows = dex_table.find_all("tr")

    # Row 2: contains main info — name, no., gender ratio, type
    main_info_row = rows[1]
    info_cells = main_info_row.find_all("td", class_="fooinfo")

    # Name
    data["name"] = info_cells[0].get_text(strip=True)

    # Kanto ID (inside the nested table)
    id_table = info_cells[2].find("table")
    if id_table:
        kanto_row = id_table.find("b", string="Kanto")
        if kanto_row:
            data["kanto_id"] = kanto_row.find_next("td").get_text(strip=True)
        else:
            data["kanto_id"] = None

    # Gender Ratio
    gender_table = info_cells[3].find("table")
    if gender_table:
        genders = gender_table.find_all("tr")
        male_ratio = genders[0].find_all("td")[1].get_text(strip=True)
        female_ratio = genders[1].find_all("td")[1].get_text(strip=True)
        data["gender_ratio"] = {"male": male_ratio, "female": female_ratio}
    else:
        data["gender_ratio"] = None

    # Type(s)
    type_links = main_info_row.find_all("a", href=True)
    types = [a["href"].split("/")[-1].replace(".shtml", "") for a in type_links if "type" in a["href"]]
    if len(types) == 1:
        types.append(None)
    data["type1"], data["type2"] = types[:2]

    # Row 4: classification, height, weight, capture rate, egg steps
    value_row = rows[4]
    values = [td.get_text(" ", strip=True) for td in value_row.find_all("td", class_="fooinfo")]

    data["classification"] = values[0]
    data["height"] = values[1]
    data["weight"] = values[2]
    data["capture_rate"] = values[3]
    data["base_egg_steps"] = values[4]

    return data


if __name__ == "__main__":
    result = scrape_serebii_basic(URL)
    from pprint import pprint
    pprint(result)
