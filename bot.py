import requests
from bs4 import BeautifulSoup

URL = "https://www.serebii.net/pokedex-sm/025.shtml"
HEADERS = {"User-Agent": "Mozilla/5.0"}

def scrape_serebii_basic(url):
    res = requests.get(url, headers=HEADERS)
    res.raise_for_status()
    soup = BeautifulSoup(res.text, "html.parser")

    data = {}

    # Find the dex table that actually has "Classification" in it (unique to main Pokémon table)
    dex_table = None
    for table in soup.find_all("table", class_="dextable"):
        if table.find(string="Classification"):
            dex_table = table
            break

    if not dex_table:
        raise ValueError("Could not find main dex table")

    all_rows = dex_table.find_all("tr")

    # --------- NAME / ID / GENDER / TYPE section -------------
    top_data_row = None
    for i, row in enumerate(all_rows):
        if row.find(string="Name"):
            top_data_row = all_rows[i + 1]  # the next row has actual data
            break

    if not top_data_row:
        raise ValueError("Main info row not found")

    top_cells = top_data_row.find_all("td")

    # Name
    name_cell = top_cells[0]
    data["name"] = name_cell.get_text(strip=True)

    # Kanto ID
    id_table = top_cells[2].find("table")
    data["kanto_id"] = None
    if id_table:
        kanto_label = id_table.find("b", string="Kanto")
        if kanto_label:
            data["kanto_id"] = kanto_label.find_next("td").get_text(strip=True)

    # Gender Ratio
    data["gender_ratio"] = None
    gender_table = top_cells[3].find("table")
    if gender_table:
        rows = gender_table.find_all("tr")
        if len(rows) >= 2:
            male = rows[0].find_all("td")[1].get_text(strip=True)
            female = rows[1].find_all("td")[1].get_text(strip=True)
            data["gender_ratio"] = {"male": male, "female": female}

    # Types
    type_links = top_data_row.find_all("a", href=True)
    types = [a["href"].split("/")[-1].replace(".shtml", "") for a in type_links if "/type/" in a["href"]]
    if len(types) == 1:
        types.append(None)
    data["type1"], data["type2"] = (types + [None, None])[:2]

    # -------- CLASSIFICATION / HEIGHT / WEIGHT etc ----------
    for i, row in enumerate(all_rows):
        if row.find(string="Classification"):
            values_row = all_rows[i + 1]
            vals = [td.get_text(" ", strip=True) for td in values_row.find_all("td", class_="fooinfo")]
            data["classification"] = vals[0]
            data["height"] = vals[1]
            data["weight"] = vals[2]
            data["capture_rate"] = vals[3]
            data["base_egg_steps"] = vals[4]
            break

    return data


if __name__ == "__main__":
    result = scrape_serebii_basic(URL)
    from pprint import pprint
    pprint(result)
