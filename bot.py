import requests
from bs4 import BeautifulSoup
import re

URL = "https://www.serebii.net/pokedex-sm/025.shtml"
HEADERS = {"User-Agent": "Mozilla/5.0"}

def scrape_serebii_basic(url):
    res = requests.get(url, headers=HEADERS)
    res.raise_for_status()
    soup = BeautifulSoup(res.text, "html.parser")

    data = {
        "name": None,
        "kanto_id": None,
        "gender_ratio": None,
        "type1": None,
        "type2": None,
        "classification": None,
        "height": None,
        "weight": None,
        "capture_rate": None,
        "base_egg_steps": None,
    }

    # --- locate the correct dex table ---
    dex_table = None
    for table in soup.find_all("table", class_="dextable"):
        if table.find(string=re.compile("Classification")):
            dex_table = table
            break
    if not dex_table:
        print("❌ Main dex table not found.")
        return data

    rows = dex_table.find_all("tr")

    # --- Find Name row header ---
    name_header_row = None
    for i, row in enumerate(rows):
        if row.find(string=re.compile(r"\bName\b", re.I)):
            name_header_row = i
            break
    if name_header_row is None:
        print("❌ Couldn't find 'Name' header row.")
        return data

    # Next row contains actual data
    info_row = rows[name_header_row + 1]
    info_cells = info_row.find_all("td")

    # Name
    if len(info_cells) >= 1:
        name = info_cells[0].get_text(strip=True)
        if name:
            data["name"] = name

    # ID (look for the nested table with “Kanto”)
    if len(info_cells) >= 3:
        id_table = info_cells[2].find("table")
        if id_table:
            kanto_label = id_table.find("b", string=re.compile("Kanto", re.I))
            if kanto_label:
                id_val = kanto_label.find_next("td")
                if id_val:
                    data["kanto_id"] = id_val.get_text(strip=True)

    # Gender Ratio
    if len(info_cells) >= 4:
        gender_table = info_cells[3].find("table")
        if gender_table:
            tr_list = gender_table.find_all("tr")
            if len(tr_list) >= 2:
                male = tr_list[0].find_all("td")[1].get_text(strip=True)
                female = tr_list[1].find_all("td")[1].get_text(strip=True)
                data["gender_ratio"] = {"male": male, "female": female}

    # Type(s)
    type_cell = info_row.find("td", class_="cen")
    if type_cell:
        type_links = type_cell.find_all("a", href=True)
        types = [a["href"].split("/")[-1].replace(".shtml", "") for a in type_links if "/type/" in a["href"]]
        if len(types) == 1:
            types.append(None)
        data["type1"], data["type2"] = (types + [None, None])[:2]

    # --- Second part: Classification / Height / Weight / Capture Rate / Egg Steps ---
    for i, row in enumerate(rows):
        if row.find(string=re.compile("Classification")):
            vals_row = rows[i + 1]
            vals = [td.get_text(" ", strip=True) for td in vals_row.find_all("td", class_="fooinfo")]
            if len(vals) >= 5:
                data["classification"] = vals[0]

                # height
                imperial, metric = None, None
                for part in vals[1].split():
                    if "'" in part or '"' in part:
                        imperial = part.strip()
                    elif "m" in part:
                        metric = part.strip()
                data["height"] = {"imperial": imperial, "metric": metric}

                # weight
                lbs, kg = None, None
                for part in vals[2].split():
                    if "lbs" in part:
                        lbs = part.replace("lbs", "").strip()
                    elif "kg" in part:
                        kg = part.replace("kg", "").strip()
                data["weight"] = {"lbs": lbs, "kg": kg}

                data["capture_rate"] = vals[3]
                data["base_egg_steps"] = vals[4]
            break

    return data


if __name__ == "__main__":
    result = scrape_serebii_basic(URL)
    from pprint import pprint
    pprint(result)
