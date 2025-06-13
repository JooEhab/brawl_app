import streamlit as st
import requests
from bs4 import BeautifulSoup

# === Rarity Map ===
rarity_map = {
    "Shelly": "starter", "Nita": "starter", "Colt": "starter", "Bull": "starter",
    "Brock": "starter", "El primo": "starter", "Barley": "starter", "Poco": "starter",
    "Rosa": "starter", "Jessie": "starter", "Dynamike": "starter", "Tick": "starter",
    "8-bit": "starter", "Rico": "starter", "Darryl": "starter", "Penny": "starter",
    "Carl": "starter", "Jacky": "starter", "Gus": "starter", "Bo": "starter",
    "Emz": "starter", "Stu": "starter", "Piper": "starter", "Pam": "starter",
    "Frank": "starter", "Bibi": "starter", "Bea": "starter", "Nani": "starter",
    "Edgar": "starter", "Griff": "starter", "Grom": "starter", "Bonnie": "starter",
    "Gale": "starter", "Colette": "starter", "Belle": "starter", "Ash": "starter",
    "Lola": "starter", "Sam": "starter", "Mandy": "starter", "Maisie": "starter",
    "Hank": "starter", "Pearl": "starter", "Larry & lawrie": "starter",
    "Angelo": "starter", "Berry": "starter", "Shade": "starter", "Meeple": "starter",
    "Mortis": "mythic", "Tara": "mythic", "Gene": "mythic", "Max": "mythic",
    "Mr. p": "mythic", "Sprout": "mythic", "Byron": "mythic", "Squeak": "mythic",
    "Lou": "mythic", "Ruffs": "mythic", "Buzz": "mythic", "Fang": "mythic",
    "Eve": "mythic", "Janet": "mythic", "Otis": "mythic", "Buster": "mythic",
    "Gray": "mythic", "R-t": "mythic", "Willow": "mythic", "Doug": "mythic",
    "Charlie": "mythic", "Mico": "mythic", "Melodie": "mythic", "Clancy": "mythic",
    "Moe": "mythic", "Juju": "mythic", "Lumi": "mythic", "Finx": "mythic",
    "Ollie": "mythic", "Chuck": "mythic", "Lily": "mythic", "Jae-yong": "mythic",
    "Spike": "mythic", "Crow": "mythic", "Leon": "mythic", "Sandy": "mythic",
    "Amber": "mythic", "Meg": "mythic", "Chester": "mythic", "Surge": "mythic",
    "Kit": "mythic", "Cordelius": "mythic", "Draco": "mythic", "Kenji": "mythic",
    "Kaze": "ultra_legendary"
}

# === Mastery Rewards ===
mastery_rewards = {
    "starter": {300: {"coins": 750}, 800: {"PowerPoints": 100}, 1500: {"credits": 75},
                2600: {"PowerPoints": 200}, 4000: {"coins": 1250}, 5800: {"credits": 150}},
    "mythic": {300: {"coins": 1000}, 800: {"PowerPoints": 150}, 1500: {"credits": 100},
               2600: {"PowerPoints": 300}, 4000: {"coins": 2000}, 5800: {"credits": 200}},
    "ultra_legendary": {300: {"coins": 1500}, 800: {"PowerPoints": 200}, 1500: {"credits": 150},
                         2600: {"PowerPoints": 400}, 4000: {"coins": 3000}, 5800: {"credits": 300}}
}

# === Mastery Rank Tiers ===
mastery_ranks = [
    (24800, "Gold III"), (16800, "Gold II"), (10300, "Gold I"),
    (5800, "Silver III"), (4000, "Silver II"), (2600, "Silver I"),
    (1500, "Bronze III"), (800, "Bronze II"), (300, "Bronze I"), (0, "Unranked")
]

def get_rank(points):
    for threshold, rank in mastery_ranks:
        if points >= threshold:
            return rank
    return "Unranked"

def fetch_mastery(tag):
    url = f"https://brawlytix.com/profile/{tag}"
    resp = requests.get(url)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    data = {}
    rows = soup.select("#brawlersContainer .brawler-row")
    for row in rows:
        name_elem = row.select_one(".brawler-name")
        pts_elem = row.select_one(".brawler-mastery span")
        if not name_elem or not pts_elem:
            continue
        name = name_elem.text.strip().capitalize()
        pts_text = pts_elem.get_text(strip=True).replace(",", "").split()[0]
        try:
            pts = int(pts_text)
        except:
            continue
        data[name] = pts
    return data

def compute_rewards(points):
    total = {"coins": 0, "PowerPoints": 0, "credits": 0}
    brawler_data = []
    for name, pts in points.items():
        tier = rarity_map.get(name)
        rank = get_rank(pts)
        earned = {"coins": 0, "PowerPoints": 0, "credits": 0}
        if tier:
            for thr, reward in mastery_rewards[tier].items():
                if pts >= thr:
                    for k, v in reward.items():
                        earned[k] += v
                        total[k] += v
        brawler_data.append((name, pts, rank, earned))
    return total, brawler_data

def compute_remaining_rewards(points):
    remaining = {"coins": 0, "PowerPoints": 0, "credits": 0}
    for name, pts in points.items():
        tier = rarity_map.get(name)
        if not tier:
            continue
        for thr, reward in mastery_rewards[tier].items():
            if pts < thr:
                for k, v in reward.items():
                    remaining[k] += v
    return remaining

# === Streamlit App ===
st.title("🟡 Brawl Stars Mastery Reward Tracker")
tag = st.text_input("Enter your Brawl Stars tag (without #):")

if tag:
    with st.spinner("Fetching mastery data..."):
        try:
            pts = fetch_mastery(tag)
            rewards, brawler_data = compute_rewards(pts)
            remaining = compute_remaining_rewards(pts)

            st.success("Data loaded!")

            st.subheader("🎯 Total Rewards Earned")
            st.write(rewards)

            st.subheader("🧾 Remaining Rewards to Earn")
            st.write(remaining)

            st.subheader("📋 Brawler Mastery Details")
            sort_by = st.selectbox("Sort brawlers by:", ["Points", "Name"])
            if sort_by == "Points":
                brawler_data.sort(key=lambda x: x[1], reverse=True)
            else:
                brawler_data.sort(key=lambda x: x[0])

            for name, pts, rank, earned in brawler_data:
                st.markdown(f"**{name}** — {pts} pts | Rank: {rank}")
        except Exception as e:
            st.error(f"Failed to fetch data: {e}")
