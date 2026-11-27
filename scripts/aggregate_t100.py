"""
Aggregate BTS T-100 Domestic Market (U.S. Carriers) downloads into small tables.

Usage (terminal):
    python aggregate_t100.py <folder_with_raw_files> <output_folder>

Usage (Jupyter / VS Code notebook cell):
    from aggregate_t100 import main
    main("raw", "out")

Reads every .csv, .csv.gz and .zip (one CSV inside) in the input folder, stacks them,
cleans them, and writes small summary CSVs that the Quarto pages read.
Raw data never needs to be loaded when rendering the site.

Cleaning rules:
  1. Keep scheduled passenger service only (CLASS == "F").
  2. Drop rows with zero passengers.
  3. Drop rows where origin == destination.
  4. Airport totals count passengers by ORIGIN only (enplanements), so a trip is not counted twice.
  5. Merged airlines are combined under the surviving brand in ALL years (see BRAND_RULES).
     Regionals owned by a major (Envoy, PSA, Piedmont, Endeavor, Comair, Mesaba, Horizon) are counted
     under that major. Independent regionals (SkyWest, Republic, etc.) are grouped as
     "Regional (independent)" because they fly for several majors.
"""
import sys
import zipfile
from pathlib import Path
import pandas as pd

BRAND_RULES = [
    ("northwest airlines", "Delta"),
    ("delta air lines", "Delta"),
    ("continental air", "United"),
    ("continental micronesia", "United"),
    ("united air lines", "United"),
    ("trans world airways", "American"),
    ("america west", "American"),
    ("us airways", "American"),
    ("usair", "American"),
    ("american airlines inc", "American"),
    ("envoy air", "American"),
    ("psa airlines", "American"),
    ("piedmont", "American"),
    ("endeavor air", "Delta"),
    ("comair", "Delta"),
    ("mesaba", "Delta"),
    ("horizon air", "Alaska"),
    ("airtran", "Southwest"),
    ("southwest airlines", "Southwest"),
    ("virgin america", "Alaska"),
    ("alaska airlines", "Alaska"),
]
REGIONAL_INDEPENDENT = ["skywest", "republic airline", "mesa airlines", "expressjet", "gojet",
                        "commuteair", "trans states", "air wisconsin", "compass airlines",
                        "shuttle america", "colgan", "chautauqua", "pinnacle", "freedom airlines",
                        "great lakes", "air midwest", "chicago express"]
MAJOR = ["Delta", "United", "American", "Southwest", "Alaska",
         "JetBlue", "Spirit", "Frontier", "Hawaiian", "Allegiant", "Regional (independent)"]
OTHER_NAMES = {"jetblue": "JetBlue", "spirit air": "Spirit", "frontier air": "Frontier",
               "hawaiian air": "Hawaiian", "allegiant": "Allegiant"}

USECOLS = ["PASSENGERS", "DISTANCE", "UNIQUE_CARRIER", "AIRLINE_ID", "UNIQUE_CARRIER_NAME",
           "ORIGIN", "ORIGIN_CITY_NAME", "ORIGIN_STATE_ABR", "DEST", "YEAR", "MONTH", "CLASS"]


def brand_of(name: str) -> str:
    n = str(name).lower()
    for key, brand in BRAND_RULES:
        if key in n:
            return brand
    if any(k in n for k in REGIONAL_INDEPENDENT):
        return "Regional (independent)"
    for key, brand in OTHER_NAMES.items():
        if key in n:
            return brand
    return str(name).strip()


OWNED_REGIONAL_RULES = [("envoy air", "American Airlines Inc."), ("psa airlines", "American Airlines Inc."),
                        ("piedmont", "American Airlines Inc."), ("endeavor air", "Delta Air Lines Inc."),
                        ("comair", "Delta Air Lines Inc."), ("horizon air", "Alaska Airlines Inc.")]


def reported_of(name: str) -> str:
    n = str(name).lower()
    for key, parent in OWNED_REGIONAL_RULES:
        if key in n:
            return parent
    if any(k in n for k in REGIONAL_INDEPENDENT):
        return "Regional (independent)"
    return str(name).strip()


def load(folder: Path) -> pd.DataFrame:
    files = sorted(p for p in folder.iterdir()
                   if p.name.endswith((".csv", ".csv.gz", ".zip")))
    if not files:
        sys.exit(f"No .csv/.csv.gz/.zip files found in {folder}")
    frames = []
    for f in files:
        if f.name.endswith(".zip"):
            with zipfile.ZipFile(f) as z:
                parts = [(f"{f.name}:{m}", z.open(m)) for m in z.namelist()
                         if m.lower().endswith(".csv") and not m.startswith("__MACOSX")
                         and not Path(m).name.startswith("._")]
        else:
            parts = [(f.name, f)]
        for label, handle in parts:
            d = pd.read_csv(handle, usecols=lambda c: c in USECOLS)
            missing = set(USECOLS) - set(d.columns)
            if missing:
                sys.exit(f"{label} is missing columns: {sorted(missing)}")
            d = d[(d["CLASS"] == "F") & (d["PASSENGERS"] > 0) & (d["ORIGIN"] != d["DEST"])]
            print(f"{label}: year(s) {sorted(int(y) for y in d.YEAR.unique())}, {len(d):,} rows kept")
            frames.append(d)
    df = pd.concat(frames, ignore_index=True)
    per_file_years = [tuple(sorted(f.YEAR.unique())) for f in frames]
    if len(per_file_years) != len(set(per_file_years)):
        sys.exit("The same year appears in more than one file; check for duplicate downloads.")
    return df


def main(src: str, out: str) -> None:
    out_dir = Path(out)
    out_dir.mkdir(parents=True, exist_ok=True)
    df = load(Path(src))
    df = df.dropna(subset=["UNIQUE_CARRIER_NAME"])

    names = df["UNIQUE_CARRIER_NAME"].drop_duplicates()
    brand_map = {n: brand_of(n) for n in names}
    df["brand"] = df["UNIQUE_CARRIER_NAME"].map(brand_map)
    df["reported"] = df["UNIQUE_CARRIER_NAME"].map({n: reported_of(n) for n in names})
    df["brand_group"] = df["brand"].where(df["brand"].isin(MAJOR), "Other")
    df = df.rename(columns={"YEAR": "year"})

    (pd.Series(brand_map, name="brand").rename_axis("carrier_name").reset_index()
       .sort_values(["brand", "carrier_name"]).to_csv(out_dir / "brand_mapping.csv", index=False))

    nat = df.groupby(["year", "brand_group"], as_index=False)["PASSENGERS"].sum()
    nat["share"] = nat["PASSENGERS"] / nat.groupby("year")["PASSENGERS"].transform("sum")
    nat.rename(columns={"PASSENGERS": "passengers"}).to_csv(out_dir / "national_share_by_group_year.csv", index=False)

    nb = df.groupby(["year", "brand"], as_index=False)["PASSENGERS"].sum()
    nb["share"] = nb["PASSENGERS"] / nb.groupby("year")["PASSENGERS"].transform("sum")
    nb.rename(columns={"PASSENGERS": "passengers"}).to_csv(out_dir / "national_share_by_brand_year.csv", index=False)

    nr = df.groupby(["year", "UNIQUE_CARRIER_NAME"], as_index=False)["PASSENGERS"].sum()
    nr["share"] = nr["PASSENGERS"] / nr.groupby("year")["PASSENGERS"].transform("sum")
    nr.rename(columns={"PASSENGERS": "passengers", "UNIQUE_CARRIER_NAME": "carrier_name"}).to_csv(
        out_dir / "national_share_as_reported.csv", index=False)

    ab = df.groupby(["year", "ORIGIN", "brand"], as_index=False)["PASSENGERS"].sum()
    tot = ab.groupby(["year", "ORIGIN"])["PASSENGERS"].transform("sum")
    ab["share"] = ab["PASSENGERS"] / tot
    ab = ab.rename(columns={"PASSENGERS": "passengers"})
    ab.rename(columns={"ORIGIN": "airport"}).to_csv(out_dir / "airport_brand_shares.csv", index=False)

    ab["sq"] = (ab["share"] * 100) ** 2
    top = ab.sort_values("share", ascending=False).drop_duplicates(["year", "ORIGIN"])
    conc = (ab.groupby(["year", "ORIGIN"], as_index=False)
              .agg(enplanements=("passengers", "sum"), hhi=("sq", "sum"), n_brands=("brand", "nunique"))
              .merge(top[["year", "ORIGIN", "brand", "share"]].rename(columns={"brand": "top_brand", "share": "top_share"}),
                     on=["year", "ORIGIN"]))
    meta = df.drop_duplicates("ORIGIN")[["ORIGIN", "ORIGIN_CITY_NAME", "ORIGIN_STATE_ABR"]]
    conc = conc.merge(meta, on="ORIGIN").rename(columns={
        "ORIGIN": "airport", "ORIGIN_CITY_NAME": "city", "ORIGIN_STATE_ABR": "state"})
    conc.to_csv(out_dir / "airport_concentration.csv", index=False)

    ar = df.groupby(["year", "ORIGIN", "reported"], as_index=False)["PASSENGERS"].sum()
    ar["share"] = ar["PASSENGERS"] / ar.groupby(["year", "ORIGIN"])["PASSENGERS"].transform("sum")
    ar["sq"] = (ar["share"] * 100) ** 2
    ar_top = ar.sort_values("share", ascending=False).drop_duplicates(["year", "ORIGIN"])
    ar_conc = (ar.groupby(["year", "ORIGIN"], as_index=False)
                 .agg(enplanements=("PASSENGERS", "sum"), hhi=("sq", "sum"),
                      n_carriers=("reported", "nunique"))
                 .merge(ar_top[["year", "ORIGIN", "reported", "share"]]
                        .rename(columns={"reported": "top_carrier", "share": "top_share"}), on=["year", "ORIGIN"])
                 .merge(meta, on="ORIGIN")
                 .rename(columns={"ORIGIN": "airport", "ORIGIN_CITY_NAME": "city", "ORIGIN_STATE_ABR": "state"}))
    ar_conc.to_csv(out_dir / "airport_concentration_as_reported.csv", index=False)

    ar_big = ar[ar.groupby(["year", "ORIGIN"])["PASSENGERS"].transform("sum") >= 250_000]
    (ar_big.drop(columns="sq")
           .rename(columns={"ORIGIN": "airport", "reported": "carrier", "PASSENGERS": "passengers"})
           .round({"share": 5})
           .to_csv(out_dir / "airport_carrier_shares_as_reported.csv", index=False))

    nar = ar.groupby(["year", "reported"], as_index=False)["PASSENGERS"].sum()
    nar["share"] = nar["PASSENGERS"] / nar.groupby("year")["PASSENGERS"].transform("sum")
    nar["sq"] = (nar["share"] * 100) ** 2
    (nar.groupby("year").agg(hhi=("sq", "sum"), carriers_5pct=("share", lambda x: int((x >= 0.05).sum())))
        .reset_index().to_csv(out_dir / "national_concentration_as_reported.csv", index=False))
    nar.drop(columns="sq").rename(columns={"reported": "carrier", "PASSENGERS": "passengers"}).to_csv(
        out_dir / "national_share_as_reported_grouped.csv", index=False)

    (df.groupby("year", as_index=False)["PASSENGERS"].sum().rename(columns={"PASSENGERS": "passengers"})
       .to_csv(out_dir / "totals_by_year.csv", index=False))

    nb["sq"] = (nb["share"] * 100) ** 2
    (nb.groupby("year", as_index=False)["sq"].sum().rename(columns={"sq": "hhi"})
       .to_csv(out_dir / "national_hhi_by_year.csv", index=False))

    print("\nWrote files to", out_dir)
    print(nat.pivot(index="year", columns="brand_group", values="share").round(3).to_string())


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
