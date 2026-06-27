import pandas as pd

# ── 1. LOAD ALL FILES ──────────────────────────────────────────

# Tamil Nadu
tn_details = pd.read_excel("data/tamilnadu.xlsx")

# Assam
as_details  = pd.read_csv("data/Assam2026Election_Details.csv")
as_meta     = pd.read_csv("data/Assam2026Election_Constituency_Metadata.csv")
as_alliance = pd.read_csv("data/Assam2026Election_Alliance.csv")

# Kerala
kl_details  = pd.read_csv("data/Kerala_State_Elections_2026_Details.csv")
kl_meta     = pd.read_csv("data/Kerala_State_Elections_2026_Constituency_Metadata.csv")
kl_alliance = pd.read_csv("data/Kerala_State_Elections_2026_Alliance.csv")

print("Files loaded successfully")
print("TN shape:", tn_details.shape)
print("Assam shape:", as_details.shape)
print("Kerala shape:", kl_details.shape)
#exit()


# ── 2. STANDARDIZE TN COLUMNS ─────────────────────────────────

tn_details.rename(columns={
    "EVM Votes"   : "EVM_Votes",
    "Postal Votes": "Postal_Votes",
    "Total Votes" : "Total_Votes",
    "% Votes"     : "%_of_Votes"
}, inplace=True)

# Add missing columns so TN matches Assam/Kerala structure
tn_details["State_Name"]    = "Tamil Nadu"
tn_details["Win_Lost_Flag"] = None  # TN file has no winner flag — we'll derive it later

# Drop TN-only columns not present in other states
tn_details.drop(columns=["Code", "Round", "Last Updated Time", "Last Updated Date"], inplace=True)

print("\nTN columns after cleaning:")
print(tn_details.columns.tolist())

print("\nAssam columns:")
print(as_details.columns.tolist())


# ── 3. DERIVE MISSING TN COLUMNS ──────────────────────────────

# Tot_Constituency_votes_polled — sum of all votes in that constituency
tn_details["Tot_Constituency_votes_polled"] = tn_details.groupby("Constituency")["Total_Votes"].transform("sum")

# Tot_votes_by_parties — same as Total_Votes for each candidate
tn_details["Tot_votes_by_parties"] = tn_details["Total_Votes"]

# Winning_votes — max votes in that constituency (winner's vote count)
tn_details["Winning_votes"] = tn_details.groupby("Constituency")["Total_Votes"].transform("max")

# Win_Lost_Flag — True if candidate's votes == winning votes
tn_details["Win_Lost_Flag"] = tn_details["Total_Votes"] == tn_details["Winning_votes"]

print("TN columns now:")
print(tn_details.columns.tolist())

print("\nSample winner rows:")
print(tn_details[tn_details["Win_Lost_Flag"] == True][["Constituency", "Candidate", "Party", "Total_Votes"]].head())


# ── 4. ADD STATE_NAME TO ASSAM & KERALA ───────────────────────

as_details["State_Name"] = "Assam"
kl_details["State_Name"] = "Kerala"


# ── 5. COMBINE ALL THREE STATES ───────────────────────────────

# Reorder TN columns to match Assam/Kerala
col_order = [
    "State_Name", "Constituency", "Candidate", "Party",
    "EVM_Votes", "Postal_Votes", "Total_Votes", "%_of_Votes",
    "Tot_Constituency_votes_polled", "Tot_votes_by_parties",
    "Winning_votes", "Win_Lost_Flag"
]

tn_details = tn_details[col_order]
as_details = as_details[col_order]
kl_details = kl_details[col_order]

master_df = pd.concat([tn_details, as_details, kl_details], ignore_index=True)

print("Master DataFrame shape:", master_df.shape)
print("\nState-wise row counts:")
print(master_df["State_Name"].value_counts())

print("\nNull values:")
print(master_df.isnull().sum())


# ── 6. COMBINE METADATA FOR ALL STATES ────────────────────────

meta_combined = pd.concat([as_meta, kl_meta], ignore_index=True)

# TN has no metadata file — we'll add what we can derive
tn_meta = tn_details[["State_Name", "Constituency", "Tot_Constituency_votes_polled"]].drop_duplicates()
tn_meta["District"]                  = "Unknown"
tn_meta["Reserved"]                  = "Unknown"
tn_meta["Lok_sabha_constituency"]    = "Unknown"
tn_meta["Cons_vote_pct"]             = None
tn_meta["Tot_parties_competed"]      = tn_details.groupby("Constituency")["Candidate"].transform("count").reindex(tn_meta.index)

# Recalculate Tot_parties_competed correctly for TN
tn_party_count = tn_details.groupby("Constituency")["Candidate"].count().reset_index()
tn_party_count.columns = ["Constituency", "Tot_parties_competed"]
tn_meta = tn_meta.merge(tn_party_count, on="Constituency", how="left")
tn_meta.drop(columns=["Tot_parties_competed_x"], inplace=True)
tn_meta.rename(columns={"Tot_parties_competed_y": "Tot_parties_competed"}, inplace=True)

meta_combined = pd.concat([meta_combined, tn_meta], ignore_index=True)


# ── 7. COMBINE ALLIANCE FOR ALL STATES ────────────────────────

alliance_combined = pd.concat([as_alliance, kl_alliance], ignore_index=True).drop_duplicates(subset=["PARTY_FULL_NAME"])


# ── 8. MERGE INTO MASTER ──────────────────────────────────────

# Merge metadata
master_df = master_df.merge(
    meta_combined[["Constituency", "State_Name", "District", "Reserved", "Lok_sabha_constituency", "Cons_vote_pct", "Tot_parties_competed"]],
    on=["Constituency", "State_Name"],
    how="left"
)

# Merge alliance — keep first match only to avoid duplicate rows
master_df = master_df.merge(
    alliance_combined[["PARTY_ABBR", "PARTY_FULL_NAME", "ALLIANCE_NAME"]],
    left_on="Party",
    right_on="PARTY_FULL_NAME",
    how="left"
)

master_df["ALLIANCE_NAME"] = master_df["ALLIANCE_NAME"].fillna("Independent / Other")

# ── DEBUG: Check unmatched winners ────────────────────────────

winners = master_df[master_df["Win_Lost_Flag"] == True]
unmatched = winners[winners["ALLIANCE_NAME"] == "Independent / Other"]

print("Unmatched winner count:", len(unmatched))
print("\nUnmatched winner parties:")
print(unmatched[["State_Name", "Constituency", "Candidate", "Party"]].to_string())


# ── 9. DERIVE MARGIN COLUMN ───────────────────────────────────

# Sort by constituency and votes descending
master_df = master_df.sort_values(
    ["State_Name", "Constituency", "Total_Votes"],
    ascending=[True, True, False]
).reset_index(drop=True)

# Rank each candidate within their constituency
master_df["Rank"] = master_df.groupby(["State_Name", "Constituency"])["Total_Votes"].rank(
    method="first", ascending=False
).astype(int)

# Runner-up votes per constituency
runner_up = master_df[master_df["Rank"] == 2][["State_Name", "Constituency", "Total_Votes"]].copy()
runner_up.rename(columns={"Total_Votes": "Runner_up_votes"}, inplace=True)

master_df = master_df.merge(runner_up, on=["State_Name", "Constituency"], how="left")

# Margin = winner votes - runner-up votes (only meaningful for winner row)
master_df["Margin"] = master_df["Winning_votes"] - master_df["Runner_up_votes"]


# ── 10. EXPORT TO EXCEL ───────────────────────────────────────

master_df.to_excel("data/master_election_data.xlsx", index=False)

print("Export complete!")
print("Final shape:", master_df.shape)
print("\nSample winner rows with margin:")
print(
    master_df[master_df["Win_Lost_Flag"] == True][
        ["State_Name", "Constituency", "Candidate", "Party", "ALLIANCE_NAME", "Total_Votes", "Margin"]
    ].head(8).to_string()
)


# ── MANUAL TN ALLIANCE MAPPING ────────────────────────────────

tn_alliance_map = {
    "Dravida Munnetra Kazhagam"                    : "DMK Alliance",
    "Tamilaga Vettri Kazhagam"                     : "DMK Alliance",
    "Indian National Congress"                     : "DMK Alliance",
    "Communist Party of India (Marxist)"           : "DMK Alliance",
    "Communist Party of India"                     : "DMK Alliance",
    "Viduthalai Chiruthaigal Katchi"               : "DMK Alliance",
    "Marumalarchi Dravida Munnetra Kazhagam"       : "DMK Alliance",
    "Kongunadu Makkal Desia Katchi"                : "DMK Alliance",
    "All India Anna Dravida Munnetra Kazhagam"     : "AIADMK Alliance",
    "Pattali Makkal Katchi"                        : "AIADMK Alliance",
    "Tamil Maanila Congress (Moopanar)"            : "AIADMK Alliance",
    "Desiya Murpokku Dravida Kazhagam"             : "AIADMK Alliance",
    "Amma Makkal Munnettra Kazagam"                : "AIADMK Alliance",
}

# Apply only where ALLIANCE_NAME is still unset (TN rows)
mask = master_df["State_Name"] == "Tamil Nadu"
master_df.loc[mask, "ALLIANCE_NAME"] = master_df.loc[mask, "Party"].map(tn_alliance_map).fillna("Independent / Other")

print("Alliance distribution after TN fix:")
print(master_df[master_df["Win_Lost_Flag"] == True]["ALLIANCE_NAME"].value_counts())

# ── DEBUG: Check None of the Above and low UDF ────────────────

print("'None of the Above' winners:")
none_mask = (master_df["Win_Lost_Flag"] == True) & (master_df["ALLIANCE_NAME"] == "None of the Above")
print(master_df[none_mask][["State_Name", "Constituency", "Candidate", "Party", "ALLIANCE_NAME"]].to_string())

print("\nUDF winners:")
udf_mask = (master_df["Win_Lost_Flag"] == True) & (master_df["ALLIANCE_NAME"] == "United Democratic Front")
print(master_df[udf_mask][["State_Name", "Constituency", "Candidate", "Party"]].to_string())

# ── FINAL FIX: Clean up None of the Above ─────────────────────

master_df["ALLIANCE_NAME"] = master_df["ALLIANCE_NAME"].replace("None of the Above", "Independent / Other")
master_df["Party"] = master_df["Party"].replace("None of the Above", "Independent")

# ── FINAL EXPORT ──────────────────────────────────────────────

master_df.to_excel("data/master_election_data.xlsx", index=False)

print("✅ Phase 1 Complete!")
print("Final shape:", master_df.shape)
print("\nFinal alliance distribution (winners only):")
print(master_df[master_df["Win_Lost_Flag"] == True]["ALLIANCE_NAME"].value_counts())
print("\nState-wise seat count:")
print(master_df[master_df["Win_Lost_Flag"] == True]["State_Name"].value_counts())