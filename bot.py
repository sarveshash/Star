import requests
from bs4 import BeautifulSoup

URL = "https://www.serebii.net/pokedex-sm/025.shtml"
HEADERS = {"User-Agent": "Mozilla/5.0"}

def scrape_serebii_basic(url):
    res = requests.get(url, headers=HEADERS)
    res.raise_for_status()
    soup = BeautifulSoup(res.text, "html.parser")

    data = {}

    dex_table = soup.find("table", class_="dextable")
    if not dex_table:
        raise ValueError("Main table not found")

    rows = dex_table.find_all("tr")

    # --- Identify header row & data row dynamically ---
    header_labels = [td.get_text(strip=True).lower() for td in rows[0].find_all("td")]
    info_cells = rows[1].find_all("td", class_="fooinfo")

    header_map = dict(zip(header_labels, info_cells))

    # Name
    name_cell = header_map.get("name")
    data["name"] = name_cell.get_text(strip=True) if name_cell else None

    # ID (Kanto)
    id_cell = header_map.get("no.")
    data["kanto_id"] = None
    if id_cell:
        id_table = id_cell.find("table")
        if id_table:
            kanto = id_table.find("b", string="Kanto")
            if kanto:
                data["kanto_id"] = kanto.find_next("td").get_text(strip=True)

    # Gender ratio
    gender_cell = header_map.get("gender ratio")
    data["gender_ratio"] = None
    if gender_cell:
        gender_table = gender_cell.find("table")
        if gender_table:
            rows_g = gender_table.find_all("tr")
            male_ratio = female_ratio = None
            if len(rows_g) >= 2:
                male_ratio = rows_g[0].find_all("td")[1].get_text(strip=True)
                female_ratio = rows_g[1].find_all("td")[1].get_text(strip=True)
            data["gender_ratio"] = {"male": male_ratio, "female": female_ratio}

    # Type(s)
    type_cell = header_map.get("type")
    types = []
    if type_cell:
        type_links = type_cell.find_all("a", href=True)
        for a in type_links:
            if "/type/" in a["href"]:
                t = a["href"].split("/")[-1].replace(".shtml", "")
                types.append(t)
    if len(types) == 1:
        types.append(None)
    data["type1"], data["type2"] = (types + [None, None])[:2]

    # --- Second section: classification etc. ---
    # Find the next header row containing “Classification”
    class_row = dex_table.find("td", string="Classification")
    if class_row:
        # The next <tr> contains values
        value_row = class_row.find_parent("tr").find_next_sibling("tr")
        vals = [td.get_text(" ", strip=True) for td in value_row.find_all("td", class_="fooinfo")]
        if len(vals) >= 5:
            data["classification"] = vals[0]
            data["height"] = vals[1]
            data["weight"] = vals[2]
            data["capture_rate"] = vals[3]
            data["base_egg_steps"] = vals[4]

    return data


if __name__ == "__main__":
    result = scrape_serebii_basic(URL)
    from pprint import pprint
    pprint(result)
