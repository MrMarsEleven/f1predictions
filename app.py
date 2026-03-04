import streamlit as st
import pandas as pd
import os

# -------------------------
# Drivers and Races
# -------------------------
DRIVERS = [
    "Pierre Gasly", "Franco Colapinto", "Fernando Alonso", "Lance Stroll",
    "Alexander Albon", "Carlos Sainz Jr.", "Gabriel Bortoleto", "Nico Hülkenberg",
    "Sergio Pérez", "Valtteri Bottas", "Charles Leclerc", "Lewis Hamilton",
    "Esteban Ocon", "Oliver Bearman", "Lando Norris", "Oscar Piastri",
    "Kimi Antonelli", "George Russell", "Liam Lawson", "Arvid Lindblad",
    "Max Verstappen", "Isack Hadjar"
]

RACES = {
    "Australian Grand Prix": "8 March",
    "Chinese Grand Prix": "15 March",
    "Japanese Grand Prix": "29 March",
    "Bahrain Grand Prix": "12 April",
    "Saudi Arabian Grand Prix": "19 April",
    "Miami Grand Prix": "3 May",
    "Canadian Grand Prix": "24 May",
    "Monaco Grand Prix": "7 June",
    "Barcelona-Catalunya Grand Prix": "14 June",
    "Austrian Grand Prix": "28 June",
    "British Grand Prix": "5 July",
    "Belgian Grand Prix": "19 July",
    "Hungarian Grand Prix": "26 July",
    "Dutch Grand Prix": "23 August",
    "Italian Grand Prix": "6 September",
    "Spanish Grand Prix": "13 September",
    "Azerbaijan Grand Prix": "26 September",
    "Singapore Grand Prix": "11 October",
    "United States Grand Prix": "25 October",
    "Mexico City Grand Prix": "1 November",
    "São Paulo Grand Prix": "8 November",
    "Las Vegas Grand Prix": "21 November",
    "Qatar Grand Prix": "29 November",
    "Abu Dhabi Grand Prix": "6 December"
}

PLAYERS = ["Player 1", "Player 2", "Player 3"]

# -------------------------
# Session State Initialization
# -------------------------
if 'predictions' not in st.session_state:
    st.session_state.predictions = {}
if 'results' not in st.session_state:
    st.session_state.results = {}
if 'season_totals' not in st.session_state:
    st.session_state.season_totals = {player: 0 for player in PLAYERS}


# -------------------------
# Scoring function
# -------------------------
def calculate_scores(predictions, results):
    score = 0
    podium = results[:3]
    for i, driver in enumerate(predictions):
        if driver == results[i]:
            score += 3
            if i == 0:
                score += 3
        elif driver in podium and i < 3:
            score += 1
    return score


# -------------------------
# Save CSV function
# -------------------------
def save_data(data, filename):
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False)


# -------------------------
# Streamlit UI
# -------------------------
st.title("F1 Race Predictions Tracker")
tab1, tab2, tab3, tab4 = st.tabs(
    ["Enter Predictions", "Enter Results", "Race Breakdown", "Season Leaderboard"]
)

# -------------------------
# Tab 1: Enter Predictions (one player at a time)
# -------------------------
with tab1:
    st.header("Enter Predictions")
    race_name = st.selectbox("Select Race", list(RACES.keys()), key="select_race_predictions_safe")

    if race_name not in st.session_state.predictions:
        st.session_state.predictions[race_name] = {}

    for player in PLAYERS:
        st.subheader(player)
        if player not in st.session_state.predictions[race_name]:
            st.session_state.predictions[race_name][player] = [""] * 22  # start empty

        selections = st.session_state.predictions[race_name][player].copy()
        chosen_drivers = []

        for i in range(22):
            available = [""] + [d for d in DRIVERS if d not in chosen_drivers or d == selections[i]]
            selected_driver = st.selectbox(
                f"Position {i + 1}",
                options=available,
                index=available.index(selections[i]) if selections[i] else 0,
                key=f"pred_{race_name}_{player}_{i}"
            )
            selections[i] = selected_driver
            if selected_driver:
                chosen_drivers.append(selected_driver)

        st.session_state.predictions[race_name][player] = selections

        if st.button(f"Submit {player}'s Predictions", key=f"submit_{race_name}_{player}"):
            if "" in st.session_state.predictions[race_name][player]:
                st.error("Please fill all 22 positions before submitting.")
            else:
                st.success(f"{player}'s predictions submitted successfully!")

# -------------------------
# Tab 2: Enter Results
# -------------------------
with tab2:
    st.header("Enter Results")
    race_name_results = st.selectbox(
        "Select Race", list(RACES.keys()), key="select_race_results_safe"
    )

    if race_name_results not in st.session_state.results:
        st.session_state.results[race_name_results] = [""] * 22

    selections = st.session_state.results[race_name_results].copy()
    chosen_drivers = []

    for i in range(22):
        available = [""] + [d for d in DRIVERS if d not in chosen_drivers or d == selections[i]]
        selected_driver = st.selectbox(
            f"Position {i + 1}",
            options=available,
            index=available.index(selections[i]) if selections[i] else 0,
            key=f"result_{race_name_results}_{i}"
        )
        selections[i] = selected_driver
        if selected_driver:
            chosen_drivers.append(selected_driver)

    st.session_state.results[race_name_results] = selections

    if st.button("Submit Results", key=f"submit_results_{race_name_results}"):
        if "" in selections:
            st.error("Please fill all 22 positions before submitting.")
        elif race_name_results not in st.session_state.predictions:
            st.error("Predictions for this race have not been submitted yet.")
        else:
            for player, pred in st.session_state.predictions[race_name_results].items():
                st.session_state.season_totals[player] += calculate_scores(pred, selections)
            st.success("Results submitted successfully!")

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

        results_table = pd.DataFrame({
            "Position": [f"P{i + 1}" for i in range(22)],
            "Result": results
        })
        st.subheader("Official Results")
        st.table(results_table)

        st.subheader("Predictions & Points")
        predictions_data = {}
        for player in PLAYERS:
            predictions = st.session_state.predictions[race_name_breakdown].get(player, [""] * 22)
            points = []
            for i, driver in enumerate(predictions):
                if driver == results[i]:
                    pts = 3 + (3 if i == 0 else 0)
                elif driver in results[:3] and i < 3:
                    pts = 1
                else:
                    pts = 0
                points.append(pts)
            predictions_data[player] = [f"{driver} ({pt} pts)" for driver, pt in zip(predictions, points)]

        predictions_table = pd.DataFrame(predictions_data, index=[f"P{i + 1}" for i in range(22)])
        st.table(predictions_table)
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
    leaderboard_df = pd.DataFrame(leaderboard, columns=["Player", "Points"])
    st.dataframe(leaderboard_df, use_container_width=True)

    st.subheader("Points Progression Over Season")
    races_done = [race for race in RACES.keys() if race in st.session_state.results]
    if races_done:
        progression_data = {player: [] for player in PLAYERS}
        for race in races_done:
            for player in PLAYERS:
                pred = st.session_state.predictions[race].get(player, [""] * 22)
                race_points = calculate_scores(pred, st.session_state.results[race])
                last_points = progression_data[player][-1] if progression_data[player] else 0
                progression_data[player].append(last_points + race_points)
        progression_df = pd.DataFrame(progression_data, index=races_done)
        st.line_chart(progression_df)
    else:
        st.info("No races completed yet to show progression.")

# -------------------------
# Save CSVs
# -------------------------
save_data(st.session_state.predictions, "predictions.csv")
save_data(st.session_state.results, "results.csv")
save_data(
    {"Player": list(st.session_state.season_totals.keys()),
     "Points": list(st.session_state.season_totals.values())},
    "season_totals.csv"
)