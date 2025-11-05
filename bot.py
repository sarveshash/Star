import requests
from bs4 import BeautifulSoup
import re

URL = "https://www.serebii.net/pokedex-sm/025.shtml"
HEADERS = {"User-Agent": "Mozilla/5.0"}

def scrape_serebii_basic(url):
    res = requests.get(url, headers=HEADERS)
    res.raise_for_status()
    soup = BeautifulSoup(res.text, "html.parser")

    data = {}

    # Find the dex table that has "Classification"
    dex_table = None
    for table in soup.find_all("table", class_="dextable"):
        if table.find(string="Classification"):
            dex_table = table
            break
    if not dex_table:
        raise ValueError("Main Pokémon table not found.")

    rows = dex_table.find_all("tr")

    # ---- NAME / ID / GENDER / TYPE ----
    top_data_row = None
    for i, row in enumerate(rows):
        if row.find(string="Name"):
            top_data_row = rows[i + 1]
            break

    if not top_data_row:
        raise ValueError("Top info row not found.")

    top_cells = top_data_row.find_all("td")

    # Name
    data["name"] = top_cells[0].get_text(strip=True)

    # Kanto ID
    data["kanto_id"] = None
    id_table = top_cells[2].find("table")
    if id_table:
        kanto_label = id_table.find("b", string=re.compile("Kanto", re.I))
        if kanto_label:
            data["kanto_id"] = kanto_label.find_next("td").get_text(strip=True)

    # Gender Ratio
    data["gender_ratio"] = None
    gender_table = top_cells[3].find("table")
    if gender_table:
        rows_g = gender_table.find_all("tr")
        if len(rows_g) >= 2:
            male = rows_g[0].find_all("td")[1].get_text(strip=True)
            female = rows_g[1].find_all("td")[1].get_text(strip=True)
            data["gender_ratio"] = {"male": male, "female": female}

    # Types (last <td> in this row)
    type_cell = top_data_row.find("td", class_="cen")
    if type_cell:
        type_links = type_cell.find_all("a", href=True)
        types = [
            a["href"].split("/")[-1].replace(".shtml", "")
            for a in type_links
            if "/type/" in a["href"]
        ]
        if len(types) == 1:
            types.append(None)
        data["type1"], data["type2"] = (types + [None, None])[:2]
    else:
        data["type1"], data["type2"] = None, None

    # ---- CLASSIFICATION / HEIGHT / WEIGHT / CAPTURE RATE / EGG ----
    for i, row in enumerate(rows):
        if row.find(string="Classification"):
            value_row = rows[i + 1]
            vals = [td.get_text(" ", strip=True) for td in value_row.find_all("td", class_="fooinfo")]
            data["classification"] = vals[0]
            
            # Parse Height (imperial + metric)
            height_text = vals[1].split()
            imperial = None
            metric = None
            for part in height_text:
                if "'" in part or '"' in part:
                    imperial = part.strip()
                elif "m" in part:
                    metric = part.strip()
            data["height"] = {"imperial": imperial, "metric": metric}
            
            # Parse Weight (lbs + kg)
            weight_text = vals[2].split()
            lbs = kg = None
            for part in weight_text:
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
