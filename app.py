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
# Session State Initialization
# -------------------------
if 'predictions' not in st.session_state:
    st.session_state.predictions = {race: {p: [""]*22 for p in PLAYERS} for race in RACES}
if 'results' not in st.session_state:
    st.session_state.results = {race: [""]*22 for race in RACES}
if 'season_totals' not in st.session_state:
    st.session_state.season_totals = {player: 0 for player in PLAYERS}
if 'race_scores' not in st.session_state:
    st.session_state.race_scores = {}

# -------------------------
# Load saved CSVs if they exist
# -------------------------
if os.path.exists("predictions.csv"):
    df = pd.read_csv("predictions.csv")
    for _, row in df.iterrows():
        race = row["Race"]
        player = row["Player"]
        preds = [row[f"P{i+1}"] for i in range(22)]
        if race not in st.session_state.predictions:
            st.session_state.predictions[race] = {}
        st.session_state.predictions[race][player] = preds

if os.path.exists("results.csv"):
    df = pd.read_csv("results.csv")
    for _, row in df.iterrows():
        race = row["Race"]
        results = [row[f"P{i+1}"] for i in range(22)]
        st.session_state.results[race] = results

if os.path.exists("race_scores.csv"):
    df = pd.read_csv("race_scores.csv")
    for _, row in df.iterrows():
        race = row["Race"]
        scores = {player: row[player] for player in PLAYERS}
        st.session_state.race_scores[race] = scores

# Recalculate season totals
for player in PLAYERS:
    st.session_state.season_totals[player] = sum(
        st.session_state.race_scores[race].get(player, 0)
        for race in st.session_state.race_scores
    )

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
    pd.DataFrame(rows).to_csv("predictions.csv", index=False)

def save_results_csv():
    rows = []
    for race, results in st.session_state.results.items():
        row = {"Race": race}
        row.update({f"P{i+1}": driver for i, driver in enumerate(results)})
        rows.append(row)
    pd.DataFrame(rows).to_csv("results.csv", index=False)

def save_season_totals_csv():
    rows = []
    for player, total in st.session_state.season_totals.items():
        rows.append({"Player": player, "Points": total})
    pd.DataFrame(rows).to_csv("season_totals.csv", index=False)

def save_race_scores_csv():
    rows = []
    for race, scores in st.session_state.race_scores.items():
        row = {"Race": race}
        row.update(scores)
        rows.append(row)
    pd.DataFrame(rows).to_csv("race_scores.csv", index=False)

# -------------------------
# Streamlit UI
# -------------------------
st.title("F1 Race Predictions Tracker")
tab1, tab2, tab3, tab4 = st.tabs(
    ["Enter Predictions", "Enter Results", "Race Breakdown", "Season Leaderboard"]
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
            available_options = [""] + [d for d in DRIVERS if d not in chosen]
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
        available_options = [""] + [d for d in DRIVERS if d not in chosen]
        selections[i] = st.selectbox(
            f"Position {i+1}",
            options=available_options,
            index=available_options.index(selections[i]) if selections[i] in available_options else 0,
            key=f"result_{race_name_results}_{i}"
        )

    st.session_state.results[race_name_results] = selections

    if st.button("Submit Results"):
        # Remove old points if race already scored
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
# Tab 4: Season Leaderboard
# -------------------------
with tab4:
    st.header("Season Leaderboard")
    leaderboard = sorted(
        st.session_state.season_totals.items(), key=lambda x: x[1], reverse=True
    )
    st.dataframe(pd.DataFrame(
        {player: points for player, points in leaderboard}, index=[0]
    ).T.rename(columns={0:"Points"}), use_container_width=True)

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