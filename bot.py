import requests
from bs4 import BeautifulSoup

URL = "https://www.serebii.net/pokedex-sm/025.shtml"
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible)"}

def scrape_pokemon(url):
    resp = requests.get(url, headers=HEADERS)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    data = {}

    # Name & No.
    # Assuming the “name box” is something like <div class="pokedex-title">Pikachu</div>
    title = soup.select_one("div#content h1")  # example selector
    if title:
        data["name"] = title.get_text(strip=True)
    # Kanto No: maybe inside a table with “No.” label
    no_label = soup.find(string="No.")
    if no_label:
        data["kanto_no"] = no_label.find_next().get_text(strip=True)

    # Gender ratio & Type(s)
    # Example: a table row with “Gender Ratio” and then something like “♂ 50% ♀ 50%”
    gender_label = soup.find(string="Gender Ratio")
    if gender_label:
        data["gender_ratio"] = gender_label.find_next().get_text(strip=True)
    types = soup.select("td a[href*='/type/']")
    # types might list one or two
    if types:
        data["type1"] = types[0].get_text(strip=True)
        data["type2"] = types[1].get_text(strip=True) if len(types) > 1 else None

    # Classification, Height, Weight, Capture Rate, Base Egg Steps
    for field in ["Classification", "Height", "Weight", "Capture Rate", "Base Egg Steps"]:
        lbl = soup.find(string=field)
        if lbl:
            data[field.lower().replace(" ", "_")] = lbl.find_next().get_text(strip=True)

    # Abilities + description
    data["abilities"] = []
    abil_section = soup.find(string="Ability")
    if abil_section:
        # Example cells for each ability
        abil_cells = abil_section.find_next("table").select("tr")
        for row in abil_cells:
            # parse ability name and description from row
            cols = row.select("td")
            if len(cols) >= 2:
                name = cols[0].get_text(strip=True)
                desc = cols[1].get_text(strip=True)
                data["abilities"].append({"name": name, "description": desc})

    # Exp growth + Base happiness
    exp_lbl = soup.find(string="EXP Growth")
    if exp_lbl:
        data["exp_growth"] = exp_lbl.find_next().get_text(strip=True)

    happ_lbl = soup.find(string="Base Happiness")
    if happ_lbl:
        data["base_happiness"] = happ_lbl.find_next().get_text(strip=True)

    # Effort values
    ev_lbl = soup.find(string="Effort Values")
    if ev_lbl:
        data["effort_values"] = ev_lbl.find_next().get_text(strip=True)

    # Egg groups
    egg_lbl = soup.find(string="Egg Group(s)")
    if egg_lbl:
        data["egg_groups"] = egg_lbl.find_next().get_text(strip=True)

    return data

if __name__ == "__main__":
    result = scrape_pokemon(URL)
    import pprint
    pprint.pprint(result)
