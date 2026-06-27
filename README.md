# Indian Assembly Election Results Dashboard

A multi-state election results analysis project covering Tamil Nadu, Kerala, and Assam assembly elections. Built with Python (Pandas) for data cleaning and Power BI for interactive visualization.


---

## Dashboard Preview

### Page 1 — Overview
![Overview](screenshots/page1_overview.png)

### Page 2 — Constituency Details
![Constituency Details](screenshots/page2_constituency.png)

### Page 3 — Party & Alliance Battle
![Party & Alliance Battle](screenshots/page3_party.png)

---

## Project Structure

```
election-results-dashboard/
├── data/
│   ├── tamilnadu.xlsx
│   ├── Assam2026Election_Details.csv
│   ├── Assam2026Election_Constituency_Metadata.csv
│   ├── Assam2026Election_Alliance.csv
│   ├── Kerala_State_Elections_2026_Details.csv
│   ├── Kerala_State_Elections_2026_Constituency_Metadata.csv
│   ├── Kerala_State_Elections_2026_Alliance.csv
│   └── master_election_data.xlsx        ← cleaned output
├── clean_data.py                         ← data cleaning script
├── analysis.py                           ← exploratory analysis script
├── Election_Dashboard.pbix               ← Power BI dashboard
└── README.md
```

---

## Tools Used

| Tool     | Purpose                   |
|----------|---------------------------|
| Python   | Data cleaning and merging |
| Pandas   | DataFrame operations      |
| Power BI | Interactive dashboard     |
| DAX      | Custom measures           |
| Excel    | Data source               |

---

## How the Data Was Cleaned

The hardest part of this project wasn't the visualization — it was getting three inconsistently structured datasets to talk to each other.

**Tamil Nadu** came as a single Excel file with 4,257 rows but was missing key columns like total votes polled and win/loss flags — I had to derive those manually.

**Assam and Kerala** came split across three CSVs each (details, constituency metadata, and alliance info), so I had to merge them before I could even start cleaning.

The main issues I ran into:
- Column names were completely different across states, so I renamed everything to a unified schema
- Tamil Nadu had no alliance column in the raw data — I built a manual mapping for DMK Alliance and AIADMK Alliance
- After merging the alliance file, I was getting duplicate rows on party names, fixed with `drop_duplicates(subset=["PARTY_FULL_NAME"])`
- Had to derive `Runner_up_votes` and `Margin` (winner votes − runner-up votes) using `groupby + rank()`

Final output: **5,993 rows, 23 columns**, covering ~92 million votes across 3 states.

---

## Key Findings

| Insight | Finding |
|---------|---------|
| Biggest winning margin | Edappadi Palaniswami — 98,110 votes (TN) |
| Closest contest | Tiruppattur, TN — won by just 30 votes |
| Most seats won (party) | Tamilaga Vettri Kazhagam — 107 seats |
| Highest avg vote share | TVK — 40.82% |
| Most contested seat | Karur, TN — 80 candidates |
| Strongest alliance avg margin | Left Democratic Front — 31,231 votes |
| Total votes analyzed | 92 million across 3 states |

---

## Power BI Dashboard Pages

**Page 1 — Overview**
- KPI Cards: Total Seats (500), Avg Margin (22.79K), Total Votes Cast (92M)
- Donut Chart: Alliance seat share
- Stacked Bar: State-wise seats by alliance
- Slicer: Filter by state

**Page 2 — Constituency Details**
- Winner table: Constituency, Candidate, Party, Alliance, Votes, Margin
- Top 10 constituencies by winning margin (bar chart)
- Slicers: State and Alliance

**Page 3 — Party & Alliance Battle**
- Treemap: Seats won by party
- Bar chart: Average winning margin by alliance
- Bar chart: Top 10 parties by average vote share

---

## DAX Measures

```dax
Total Seats = COUNTROWS(FILTER('Sheet1', 'Sheet1'[Win_Lost_Flag] = TRUE()))

Avg Margin = AVERAGEX(FILTER('Sheet1', 'Sheet1'[Win_Lost_Flag] = TRUE()), 'Sheet1'[Margin])

Avg Vote Share = AVERAGEX(FILTER('Sheet1', 'Sheet1'[Win_Lost_Flag] = TRUE()), 'Sheet1'[%_of_Votes])

Total Votes Cast = SUM('Sheet1'[Total_Votes])
```

---

## How to Run

1. Clone the repository
2. Place all raw data files in the `data/` folder
3. Run `python clean_data.py` — generates `master_election_data.xlsx`
4. Run `python analysis.py` — prints key insights to terminal
5. Open `Election_Dashboard.pbix` in Power BI Desktop

---

## Author

**Muhammed Murshid M**  
Data Analytics Intern — Techolas Technologies  
[LinkedIn](https://www.linkedin.com/in/muhammed-murshidm)
