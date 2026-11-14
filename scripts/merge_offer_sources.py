import json, os, shutil

RAW_FT_PATH = "data/offers/raw_offers.json"
JOBSPY_PATH = "data/offers/jobspy_offers.json"
MERGED_PATH = "data/offers/merged_offers.json"

def normalize_france_travail(raw_offers):
    # France Travail's raw fields, confirmed by extract_offers.py's own field
    # access below -- this project's most-tested France Travail assumptions.
    # url/date_posted are left None deliberately: no confirmed real field name
    # for either exists yet in this manual (Step 10 hadn't returned real, non-empty
    # results when this was written) -- once your own Step 10 run has real offers,
    # inspect one in data/offers/raw_offers.json yourself and add the real field
    # name here if you want working links, rather than this guessing a third time.
    normalized = []
    for o in raw_offers:
        normalized.append({
            "id": f"ft_{o['id']}",
            "source": "france_travail",
            "title": o.get("intitule"),
            "company": (o.get("entreprise") or {}).get("nom"),
            "location": (o.get("lieuTravail") or {}).get("libelle"),
            "description": o.get("description", ""),
            "url": None,
            "date_posted": None,
            "is_apprenticeship": o.get("alternance", False),
            "accessible_disability": o.get("accessibleTH", False),
            "publishable": True,  # official open government data -- safe to publish
        })
    return normalized

def load_jobspy():
    if not os.path.exists(JOBSPY_PATH):
        print(f"{JOBSPY_PATH} not found -- skipping (fine if you didn't do Step 11b).")
        return []
    with open(JOBSPY_PATH, encoding="utf-8") as f:
        data = json.load(f)
    return [
        {**o, "is_apprenticeship": False, "accessible_disability": False,
         "publishable": False}  # scraped content -- never published, see Step 11b
        for o in data["offers"]
    ]

def main():
    if os.path.exists(RAW_FT_PATH):
        with open(RAW_FT_PATH, encoding="utf-8") as f:
            ft_raw = json.load(f)
    else:
        ft_raw = {"offers": []}
        print("No France Travail API file. Checking for the explicitly labelled TD3 replacement.")
    ft_offers = normalize_france_travail(ft_raw["offers"])
    jobspy_offers = load_jobspy()
    # Keep previously normalized local JobSpy offers if their raw file is absent.
    if not os.path.exists(JOBSPY_PATH) and os.path.exists(MERGED_PATH):
        with open(MERGED_PATH, encoding="utf-8") as f:
            jobspy_offers = [o for o in json.load(f)["offers"]
                             if o.get("source") not in {"td3_sample", "france_travail"}
                             and o.get("publishable", False) is False]
    if not jobspy_offers and not os.path.exists(JOBSPY_PATH) and os.path.exists("data/offers/structured_offers.json"):
        with open("data/offers/structured_offers.json", encoding="utf-8") as f:
            jobspy_offers = [
                {**o, "description": "", "publishable": False,
                 "extraction_method": "cached_previous_extraction",
                 "extraction_note": "Extraction precedente conservee ; description brute indisponible dans la fusion actuelle."}
                for o in json.load(f)["offers"]
                if o.get("source") not in {"td3_sample", "france_travail"}
            ]
    td3_path = "data/offers/td3_offers.json"
    td3_offers = []
    if os.path.exists(td3_path):
        with open(td3_path, encoding="utf-8") as f:
            td3_offers = [{**o, "source": "td3_sample", "publishable": False}
                          for o in json.load(f)["offers"]]
    if not ft_offers and not td3_offers and not jobspy_offers:
        raise RuntimeError("No input offers: fetch France Travail or import the TD3 CSV first.")

    merged = ft_offers + jobspy_offers + td3_offers
    print(f"Merged {len(ft_offers)} France Travail + {len(jobspy_offers)} jobspy + {len(td3_offers)} TD3 = {len(merged)} total")

    os.makedirs("data/offers", exist_ok=True)
    if os.path.exists(MERGED_PATH):
        shutil.copy2(MERGED_PATH, MERGED_PATH + ".bak")
    with open(MERGED_PATH, "w", encoding="utf-8") as f:
        json.dump({"offers": merged}, f, indent=2, ensure_ascii=False)
    print(f"Wrote {MERGED_PATH} ({len(merged)} offers) -- gitignored, local only")

if __name__ == "__main__":
    main()
