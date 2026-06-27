import pandas as pd

df = pd.read_excel("data/master_election_data.xlsx")
winners = df[df["Win_Lost_Flag"] == True].copy()

# ── Q1: Alliance seats per state ──────────────────────────────
print("=" * 55)
print("Q1: Alliance-wise seats per state")
print("=" * 55)
print(winners.groupby(["State_Name", "ALLIANCE_NAME"])["Constituency"].count().to_string())

# ── Q2: Top 10 winners by margin ──────────────────────────────
print("\n" + "=" * 55)
print("Q2: Top 10 winners by margin")
print("=" * 55)
top_margin = winners.nlargest(10, "Margin")[["State_Name", "Constituency", "Candidate", "Party", "Margin"]]
print(top_margin.to_string())

# ── Q3: Closest contests (smallest margin) ────────────────────
print("\n" + "=" * 55)
print("Q3: Top 10 closest contests")
print("=" * 55)
close = winners.nsmallest(10, "Margin")[["State_Name", "Constituency", "Candidate", "Party", "Margin"]]
print(close.to_string())

# ── Q4: Party-wise average vote share ─────────────────────────
print("\n" + "=" * 55)
print("Q4: Top 10 parties by avg vote share (winners only)")
print("=" * 55)
avg_vs = winners.groupby("Party")["%_of_Votes"].mean().nlargest(10).round(2)
print(avg_vs.to_string())

# ── Q5: Voter turnout by state ────────────────────────────────
print("\n" + "=" * 55)
print("Q5: Average voter turnout by state")
print("=" * 55)
turnout = df.groupby("State_Name")["Tot_Constituency_votes_polled"].mean().round(0)
print(turnout.to_string())


# ── Q6: Top 10 parties by total seats won ─────────────────────
print("=" * 55)
print("Q6: Top 10 parties by seats won")
print("=" * 55)
party_seats = winners.groupby("Party")["Constituency"].count().nlargest(10)
print(party_seats.to_string())

# ── Q7: Reserved seat wins by alliance ────────────────────────
print("\n" + "=" * 55)
print("Q7: Reserved seat wins by alliance (Assam & Kerala)")
print("=" * 55)
reserved = winners[winners["Reserved"].isin(["SC", "ST", "GEN", "GENERAL"])].copy()
print(reserved.groupby(["State_Name", "Reserved", "ALLIANCE_NAME"])["Constituency"].count().to_string())

# ── Q8: Constituencies with most candidates ───────────────────
print("\n" + "=" * 55)
print("Q8: Top 10 most contested constituencies")
print("=" * 55)
most_contested = df.groupby(["State_Name", "Constituency"])["Candidate"].count().nlargest(10)
print(most_contested.to_string())

# ── Q9: Average margin by alliance ────────────────────────────
print("\n" + "=" * 55)
print("Q9: Average winning margin by alliance")
print("=" * 55)
avg_margin = winners.groupby("ALLIANCE_NAME")["Margin"].mean().sort_values(ascending=False).round(0)
print(avg_margin.to_string())

# ── Q10: State-wise gender count in winners (name-based proxy) ─
print("\n" + "=" * 55)
print("Q10: Postal votes contribution % by state")
print("=" * 55)
df["Postal_pct"] = (df["Postal_Votes"] / df["Total_Votes"] * 100).round(2)
postal = df.groupby("State_Name")["Postal_pct"].mean().round(2)
print(postal.to_string())