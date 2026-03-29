import streamlit as st
import pandas as pd
import os
import plotly.graph_objects as go

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

# Format: "Simple Name | Official Name"
RACES = {
    "Australian GP | Formula 1 Qatar Airways Australian Grand Prix": "",
    "Chinese GP | Formula 1 Heineken Chinese Grand Prix": "",
    "Japanese GP | Formula 1 Aramco Japanese Grand Prix": "",
    "Bahrain GP | Formula 1 Gulf Air Bahrain Grand Prix": "",
    "Saudi Arabian GP | Formula 1 STC Saudi Arabian Grand Prix": "",
    "Miami GP | Formula 1 Crypto.com Miami Grand Prix": "",
    "Canadian GP | Formula 1 Lenovo Grand Prix du Canada": "",
    "Monaco GP | Formula 1 Louis Vuitton Grand Prix de Monaco": "",
    "Barcelona GP | Formula 1 MSC Cruises Gran Premio de Barcelona-Catalunya": "",
    "Austrian GP | Formula 1 Lenovo Austrian Grand Prix": "",
    "British GP | Formula 1 Pirelli British Grand Prix": "",
    "Belgian GP | Formula 1 Rolex Belgian Grand Prix": "",
    "Hungarian GP | Formula 1 AWS Hungarian Grand Prix": "",
    "Dutch GP | Formula 1 Heineken Dutch Grand Prix": "",
    "Italian GP | Formula 1 Pirelli Gran Premio d’Italia": "",
    "Spanish GP | Formula 1 TAG Heuer Spanish Grand Prix (Madrid)": "",
    "Azerbaijan GP | Formula 1 Qatar Airways Azerbaijan Grand Prix": "",
    "Singapore GP | Formula 1 Singapore Airlines Singapore Grand Prix": "",
    "United States GP | Formula 1 MSC Cruises United States Grand Prix": "",
    "Mexico City GP | Formula 1 Gran Premio de la Ciudad de México": "",
    "São Paulo GP | Formula 1 MSC Cruises Grande Prêmio de São Paulo": "",
    "Las Vegas GP | Formula 1 Heineken Las Vegas Grand Prix": "",
    "Qatar GP | Formula 1 Qatar Airways Qatar Grand Prix": "",
    "Abu Dhabi GP | Formula 1 Etihad Airways Abu Dhabi Grand Prix": ""
}

SPRINT_RACES = [
    "Chinese GP | Formula 1 Heineken Chinese Grand Prix",
    "Miami GP | Formula 1 Crypto.com Miami Grand Prix",
    "Canadian GP | Formula 1 Lenovo Grand Prix du Canada",
    "British GP | Formula 1 Pirelli British Grand Prix",
    "Dutch GP | Formula 1 Heineken Dutch Grand Prix",
    "Singapore GP | Formula 1 Singapore Airlines Singapore Grand Prix"
]

PLAYERS = ["Player 1", "Player 2", "Player 3"]

# -------------------------
# CSV Filenames
# -------------------------
PREDICTIONS_FILE = "predictions.csv"
RESULTS_FILE = "results.csv"
SEASON_TOTALS_FILE = "season_totals.csv"
RACE_SCORES_FILE = "race_scores.csv"
SPRINT_RESULTS_FILE = "sprint_results.csv"

# -------------------------
# F1 official points
# -------------------------
F1_POINTS = [25, 18, 15, 12, 10, 8, 6, 4, 2, 1]

SPRINT_POINTS_SYSTEM = [8, 7, 6, 5, 4, 3, 2, 1]

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

def load_sprint_results():
    if os.path.exists(SPRINT_RESULTS_FILE):
        df = pd.read_csv(SPRINT_RESULTS_FILE)
        data = {}
        for race in df["Race"].unique():
            row = df[df["Race"] == race].iloc[0]
            data[race] = [row[f"P{i+1}"] if pd.notna(row[f"P{i+1}"]) else "" for i in range(8)]
        return data
    else:
        return {race: [""]*8 for race in SPRINT_RACES}

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
if "sprint_results" not in st.session_state:
    st.session_state.sprint_results = load_sprint_results()

# -------------------------
# Scoring function
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
                score += 3
        elif driver in podium and i < 3:
            score += 1
    return score

def calculate_sprint_points():
    totals = {driver: 0 for driver in DRIVERS}

    for race, results in st.session_state.sprint_results.items():
        for pos, driver in enumerate(results):
            if driver:
                totals[driver] += SPRINT_POINTS_SYSTEM[pos]

    return totals

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

def save_sprint_results():
    rows = []
    for race, results in st.session_state.sprint_results.items():
        row = {"Race": race}
        row.update({f"P{i+1}": driver for i, driver in enumerate(results)})
        rows.append(row)
    pd.DataFrame(rows).to_csv(SPRINT_RESULTS_FILE, index=False)

# -------------------------
# Get championship order
# -------------------------
def get_championship_order():
    driver_totals = {driver: 0 for driver in DRIVERS}
    for race, results in st.session_state.results.items():
        for pos, driver in enumerate(results):
            if driver in driver_totals:
                driver_totals[driver] += F1_POINTS[pos] if pos < 10 else 0
    return sorted(DRIVERS, key=lambda d: driver_totals[d], reverse=True)

# -------------------------
# Streamlit UI
# -------------------------
st.title("F1 Race Predictions Tracker")
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
    ["Enter Predictions", "Race Results", "Sprint Results", "Race Breakdown",
     "Season Leaderboard", "Drivers' Championship"]
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
            champ_order = get_championship_order()
            available_options = [""] + [d for d in champ_order if d not in chosen or d == selections[i]]
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
# Tab 2: Race Results
# -------------------------
with tab2:
    st.header("Enter Race Results")
    race_name_results = st.selectbox("Select Race", list(RACES.keys()), key="select_race_results")
    selections = st.session_state.results[race_name_results]

    for i in range(22):
        chosen = set(d for idx, d in enumerate(selections) if d and idx != i)
        champ_order = get_championship_order()
        available_options = [""] + [d for d in champ_order if d not in chosen or d == selections[i]]
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
# Tab 3: Sprint Results
# -------------------------
with tab3:
    st.header("Enter Sprint Results")

    sprint_race = st.selectbox("Select Sprint Race", SPRINT_RACES)

    selections = st.session_state.sprint_results[sprint_race]

    for i in range(8):
        chosen = set(d for idx, d in enumerate(selections) if d and idx != i)

        champ_order = get_championship_order()
        available = [""] + [d for d in champ_order if d not in chosen or d == selections[i]]

        selections[i] = st.selectbox(
            f"Position {i + 1}",
            options=available,
            index=available.index(selections[i]) if selections[i] in available else 0,
            key=f"sprint_{sprint_race}_{i}"
        )

    st.session_state.sprint_results[sprint_race] = selections

    if st.button("Submit Sprint Results"):
        save_sprint_results()
        st.success("Sprint results saved!")

# -------------------------
# Tab 4: Race Breakdown
# -------------------------
with tab4:
    st.header("Race Breakdown")
    race_name_breakdown = st.selectbox(
        "Select Race", list(RACES.keys()), key="select_race_breakdown"
    )

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
# Tab 5: Season Leaderboard
# -------------------------
with tab5:
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
        df_progression = pd.DataFrame(progression_data, index=races_done)

        fig = go.Figure()

        for player in df_progression.columns:
            fig.add_trace(go.Scatter(
                x=df_progression.index,
                y=df_progression[player],
                mode='lines+markers',
                name=player,
                hovertemplate="<b>%{fullData.name}</b><br>Points: %{y}<extra></extra>"
            ))

        fig.update_layout(
            height=600,
            legend=dict(
                orientation="h",
                y=-0.3
            )
        )

        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No races completed yet to show progression.")

# -------------------------
# Tab 6: Drivers' Championship
# -------------------------
with tab6:
    st.header("Drivers' Championship Standings")

    # Get completed races ONLY
    races_done = [
        race for race in RACES.keys()
        if any(driver != "" for driver in st.session_state.results.get(race, []))
    ]

    # -------------------------
    # Championship Totals
    # -------------------------
    driver_totals = {driver: 0 for driver in DRIVERS}

    for race in races_done:
        race_results = st.session_state.results[race]
        sprint_results = st.session_state.sprint_results.get(race, [""]*8)

        for driver in DRIVERS:

            # Race points
            if driver in race_results:
                pos = race_results.index(driver)
                race_pts = F1_POINTS[pos] if pos < 10 else 0
            else:
                race_pts = 0

            # Sprint points
            if race in SPRINT_RACES and driver in sprint_results:
                pos = sprint_results.index(driver)
                sprint_pts = SPRINT_POINTS_SYSTEM[pos]
            else:
                sprint_pts = 0

            driver_totals[driver] += race_pts + sprint_pts

    # Sort standings
    sorted_drivers = sorted(driver_totals.items(), key=lambda x: x[1], reverse=True)

    # Standings Table
    df_drivers_champ = pd.DataFrame({
        "Position": [f"P{i+1}" for i in range(len(sorted_drivers))],
        "Driver": [d[0] for d in sorted_drivers],
        "Points": [d[1] for d in sorted_drivers]
    }).set_index("Position")

    st.table(df_drivers_champ)

    # -------------------------
    # Progression Chart (FIXED)
    # -------------------------
    st.subheader("Drivers' Points Progression Over Season")

    if races_done:
        progression_data = {driver: [] for driver in DRIVERS}

        for race in races_done:
            race_results = st.session_state.results[race]
            sprint_results = st.session_state.sprint_results.get(race, [""]*8)

            for driver in DRIVERS:
                prev = progression_data[driver][-1] if progression_data[driver] else 0

                # Race points
                if driver in race_results:
                    pos = race_results.index(driver)
                    race_pts = F1_POINTS[pos] if pos < 10 else 0
                else:
                    race_pts = 0

                # Sprint points
                if race in SPRINT_RACES and driver in sprint_results:
                    pos = sprint_results.index(driver)
                    sprint_pts = SPRINT_POINTS_SYSTEM[pos]
                else:
                    sprint_pts = 0

                total_gain = race_pts + sprint_pts

                progression_data[driver].append(prev + total_gain)

        df_progression = pd.DataFrame(progression_data, index=races_done)

        # Plotly graph
        fig = go.Figure()

        for driver in df_progression.columns:
            fig.add_trace(go.Scatter(
                x=df_progression.index,
                y=df_progression[driver],
                mode='lines+markers',
                name=driver,
                hovertemplate="<b>%{fullData.name}</b><br>Points: %{y}<extra></extra>"
            ))

        fig.update_layout(
            height=600,
            legend=dict(
                orientation="h",
                y=-0.3
            )
        )

        st.plotly_chart(fig, use_container_width=True)

    else:
        st.info("No completed races yet.")