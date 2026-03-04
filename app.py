import streamlit as st
import pandas as pd
import os

# -------------------------
# Drivers and Races
# -------------------------
DRIVERS = [
    "Lando Norris", "Oscar Piastri", "George Russell", "Kimi Antonelli",
    "Max Verstappen", "Isack Hadjar", "Charles Leclerc", "Lewis Hamilton",
    "Carlos Sainz Jr.", "Alexander Albon", "Liam Lawson", "Arvid Lindblad",
    "Fernando Alonso", "Lance Stroll", "Esteban Ocon", "Oliver Bearman",
    "Nico Hülkenberg", "Gabriel Bortoleto", "Pierre Gasly", "Franco Colapinto",
    "Valtteri Bottas", "Sergio Pérez"
]

RACES = {
    "Australian GP | Albert Park Grand Prix Circuit": "Melbourne, Australia",
    "Chinese GP | Shanghai International Circuit": "Shanghai, China",
    "Japanese GP | Suzuka International Racing Course": "Suzuka, Japan",
    "Bahrain GP | Bahrain International Circuit": "Sakhir, Bahrain",
    "Saudi Arabian GP | Jeddah Corniche Circuit": "Jeddah, Saudi Arabia",
    "Miami GP | Miami International Autodrome": "Miami, USA",
    "Canadian GP | Circuit Gilles-Villeneuve": "Montreal, Canada",
    "Monaco GP | Circuit de Monaco": "Monte Carlo, Monaco",
    "Barcelona-Catalunya GP | Circuit de Barcelona-Catalunya": "Montmeló, Spain",
    "Austrian GP | Red Bull Ring": "Spielberg, Austria",
    "British GP | Silverstone Circuit": "Silverstone, UK",
    "Belgian GP | Circuit de Spa-Francorchamps": "Stavelot, Belgium",
    "Hungarian GP | Hungaroring": "Mogyoród, Hungary",
    "Dutch GP | Circuit Zandvoort": "Zandvoort, Netherlands",
    "Italian GP | Autodromo Nazionale Monza": "Monza, Italy",
    "Spanish GP | Madrid Street Circuit (IFEMA)": "Madrid, Spain",
    "Azerbaijan GP | Baku City Circuit": "Baku, Azerbaijan",
    "Singapore GP | Marina Bay Street Circuit": "Singapore",
    "United States GP | Circuit of the Americas": "Austin, USA",
    "Mexico City GP | Autódromo Hermanos Rodríguez": "Mexico City, Mexico",
    "São Paulo GP | Autódromo José Carlos Pace (Interlagos)": "São Paulo, Brazil",
    "Las Vegas GP | Las Vegas Strip Circuit": "Las Vegas, USA",
    "Qatar GP | Lusail International Circuit": "Lusail, Qatar",
    "Abu Dhabi GP | Yas Marina Circuit": "Abu Dhabi, UAE"
}

PLAYERS = ["Player 1", "Player 2", "Player 3"]

# -------------------------
# CSV Filenames
# -------------------------
PREDICTIONS_FILE = "predictions.csv"
RESULTS_FILE = "results.csv"
SEASON_TOTALS_FILE = "season_totals.csv"
RACE_SCORES_FILE = "race_scores.csv"

# -------------------------
# Helper functions to load CSVs
# -------------------------
def load_predictions():
    if os.path.exists(PREDICTIONS_FILE):
        df = pd.read_csv(PREDICTIONS_FILE)
        data = {}
        for race in df["Race"].unique():
            data[race] = {}
            race_df = df[df["Race"] == race]
            for player in PLAYERS:
                player_row = race_df[race_df["Player"] == player]
                if not player_row.empty:
                    data[race][player] = [player_row[f"P{i+1}"].values[0] if pd.notna(player_row[f"P{i+1}"].values[0]) else "" for i in range(22)]
                else:
                    data[race][player] = [""]*22
        return data
    else:
        return {race: {p: [""]*22 for p in PLAYERS} for race in RACES}

def load_results():
    if os.path.exists(RESULTS_FILE):
        df = pd.read_csv(RESULTS_FILE)
        data = {}
        for race in df["Race"].unique():
            row = df[df["Race"] == race].iloc[0]
            data[race] = [row[f"P{i+1}"] if pd.notna(row[f"P{i+1}"]) else "" for i in range(22)]
        return data
    else:
        return {race: [""]*22 for race in RACES}

def load_season_totals():
    if os.path.exists(SEASON_TOTALS_FILE):
        df = pd.read_csv(SEASON_TOTALS_FILE)
        return {row["Player"]: row["Points"] for _, row in df.iterrows()}
    else:
        return {player: 0 for player in PLAYERS}

def load_race_scores():
    if os.path.exists(RACE_SCORES_FILE):
        df = pd.read_csv(RACE_SCORES_FILE)
        data = {}
        for race in df["Race"].unique():
            row = df[df["Race"] == race].iloc[0]
            data[race] = {player: row[player] for player in PLAYERS}
        return data
    else:
        return {}

# -------------------------
# Session State Initialization
# -------------------------
if 'predictions' not in st.session_state:
    st.session_state.predictions = load_predictions()
if 'results' not in st.session_state:
    st.session_state.results = load_results()
if 'season_totals' not in st.session_state:
    st.session_state.season_totals = load_season_totals()
if 'race_scores' not in st.session_state:
    st.session_state.race_scores = load_race_scores()

# -------------------------
# Scoring function (partial submissions supported)
# -------------------------
def calculate_scores(predictions, results):
    score = 0
    podium = results[:3]
    for i, driver in enumerate(predictions):
        if not driver:
            continue
        if driver == results[i]:
            score += 3
            if i == 0:
                score += 3  # bonus for exact winner
        elif driver in podium and i < 3:
            score += 1
    return score

# -------------------------
# CSV Saving Helpers
# -------------------------
def save_predictions_csv():
    rows = []
    for race, race_preds in st.session_state.predictions.items():
        for player, preds in race_preds.items():
            row = {"Race": race, "Player": player}
            row.update({f"P{i+1}": driver for i, driver in enumerate(preds)})
            rows.append(row)
    pd.DataFrame(rows).to_csv(PREDICTIONS_FILE, index=False)

def save_results_csv():
    rows = []
    for race, results in st.session_state.results.items():
        row = {"Race": race}
        row.update({f"P{i+1}": driver for i, driver in enumerate(results)})
        rows.append(row)
    pd.DataFrame(rows).to_csv(RESULTS_FILE, index=False)

def save_season_totals_csv():
    rows = []
    for player, total in st.session_state.season_totals.items():
        rows.append({"Player": player, "Points": total})
    pd.DataFrame(rows).to_csv(SEASON_TOTALS_FILE, index=False)

def save_race_scores_csv():
    rows = []
    for race, scores in st.session_state.race_scores.items():
        row = {"Race": race}
        row.update(scores)
        rows.append(row)
    pd.DataFrame(rows).to_csv(RACE_SCORES_FILE, index=False)

# -------------------------
# Streamlit UI
# -------------------------
st.title("F1 Race Predictions Tracker")
tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["Enter Predictions", "Enter Results", "Race Breakdown", "Season Leaderboard", "Drivers' Championship"]
)

# -------------------------
# Tab 1: Enter Predictions
# -------------------------
with tab1:
    st.header("Enter Predictions")
    race_name = st.selectbox("Select Race", list(RACES.keys()), key="select_race_predictions")

    for player in PLAYERS:
        st.subheader(player)
        selections = st.session_state.predictions[race_name][player]

        for i in range(22):
            chosen = set(d for idx, d in enumerate(selections) if d and idx != i)
            available_options = [""] + [d for d in DRIVERS if d not in chosen or d == selections[i]]
            selections[i] = st.selectbox(
                f"Position {i+1}",
                options=available_options,
                index=available_options.index(selections[i]) if selections[i] in available_options else 0,
                key=f"pred_{race_name}_{player}_{i}"
            )

        st.session_state.predictions[race_name][player] = selections

        if st.button(f"Submit {player}'s Predictions", key=f"submit_{race_name}_{player}"):
            st.success(f"{player}'s predictions submitted!")
            save_predictions_csv()

# -------------------------
# Tab 2: Enter Results
# -------------------------
with tab2:
    st.header("Enter Results")
    race_name_results = st.selectbox("Select Race", list(RACES.keys()), key="select_race_results")
    selections = st.session_state.results[race_name_results]

    for i in range(22):
        chosen = set(d for idx, d in enumerate(selections) if d and idx != i)
        available_options = [""] + [d for d in DRIVERS if d not in chosen or d == selections[i]]
        selections[i] = st.selectbox(
            f"Position {i+1}",
            options=available_options,
            index=available_options.index(selections[i]) if selections[i] in available_options else 0,
            key=f"result_{race_name_results}_{i}"
        )

    st.session_state.results[race_name_results] = selections

    if st.button("Submit Results"):
        if race_name_results in st.session_state.race_scores:
            old_scores = st.session_state.race_scores[race_name_results]
            for player, pts in old_scores.items():
                st.session_state.season_totals[player] -= pts

        race_points = {}
        for player in PLAYERS:
            pred = st.session_state.predictions.get(race_name_results, {}).get(player, [""]*22)
            points = calculate_scores(pred, selections)
            race_points[player] = points
            st.session_state.season_totals[player] += points

        st.session_state.race_scores[race_name_results] = race_points
        st.success("Results submitted successfully!")

        save_results_csv()
        save_season_totals_csv()
        save_race_scores_csv()

# -------------------------
# Tab 3: Race Breakdown
# -------------------------
with tab3:
    st.header("Race Breakdown")
    race_name_breakdown = st.selectbox("Select Race", list(RACES.keys()), key="select_race_breakdown")

    if race_name_breakdown in st.session_state.results:
        results = st.session_state.results[race_name_breakdown]

        st.subheader("Official Results")
        df_results = pd.DataFrame({
            "Position": [f"P{i+1}" for i in range(22)],
            "Driver": results
        }).set_index("Position")
        st.table(df_results)

        st.subheader("Predictions & Points")
        predictions_data = {}
        for player in PLAYERS:
            preds = st.session_state.predictions.get(race_name_breakdown, {}).get(player, [""]*22)
            points = []
            for i, driver in enumerate(preds):
                if not driver:
                    pts = 0
                elif driver == results[i]:
                    pts = 3 + (3 if i == 0 else 0)
                elif driver in results[:3] and i < 3:
                    pts = 1
                else:
                    pts = 0
                points.append(f"{driver} ({pts} pts)" if driver else "")
            predictions_data[player] = points

        st.table(pd.DataFrame(predictions_data, index=[f"P{i+1}" for i in range(22)]).rename_axis(index=None))
    else:
        st.info("No results for this race yet.")

# -------------------------
# Tab 4: Season Leaderboard
# -------------------------
with tab4:
    st.header("Season Leaderboard")
    leaderboard = sorted(
        st.session_state.season_totals.items(), key=lambda x: x[1], reverse=True
    )
    df_leaderboard = pd.DataFrame({
        "Player": [player for player, _ in leaderboard],
        "Points": [points for _, points in leaderboard]
    })
    st.dataframe(df_leaderboard.set_index("Player"), use_container_width=True)

    st.subheader("Points Progression Over Season")
    races_done = [race for race in RACES.keys() if race in st.session_state.race_scores]
    if races_done:
        progression_data = {player: [] for player in PLAYERS}
        for race in races_done:
            for player in PLAYERS:
                last_points = progression_data[player][-1] if progression_data[player] else 0
                progression_data[player].append(last_points + st.session_state.race_scores[race].get(player, 0))
        st.line_chart(pd.DataFrame(progression_data, index=races_done))
    else:
        st.info("No races completed yet to show progression.")

# -------------------------
# Tab 5: Drivers' Championship
# -------------------------
with tab5:
    st.header("Drivers' Championship Standings")

    F1_POINTS = [25, 18, 15, 12, 10, 8, 6, 4, 2, 1]
    driver_totals = {driver: 0 for driver in DRIVERS}

    for race, results in st.session_state.results.items():
        for pos, driver in enumerate(results):
            if driver in driver_totals:
                driver_totals[driver] += F1_POINTS[pos] if pos < 10 else 0

    df_drivers_champ = pd.DataFrame({
        "Driver": list(driver_totals.keys()),
        "Points": list(driver_totals.values())
    }).sort_values(by="Points", ascending=False).reset_index(drop=True)

    # Set index as P1, P2, P3 …
    df_drivers_champ.index = [f"P{i+1}" for i in range(len(df_drivers_champ))]

    st.table(df_drivers_champ)

    st.subheader("Drivers' Points Progression Over Season")
    races_done = [race for race in RACES.keys() if race in st.session_state.results]
    if races_done:
        progression_data = {driver: [] for driver in DRIVERS}
        for race in races_done:
            for driver in DRIVERS:
                last_points = progression_data[driver][-1] if progression_data[driver] else 0
                results = st.session_state.results[race]
                if driver in results:
                    pos = results.index(driver)
                    points = F1_POINTS[pos] if pos < 10 else 0
                else:
                    points = 0
                progression_data[driver].append(last_points + points)
        st.line_chart(pd.DataFrame(progression_data, index=races_done))
    else:
        st.info("No races completed yet to show progression.")