import streamlit as st
import pandas as pd

# Page Configuration
st.set_page_config(
    page_title="Zero-API Manual +EV Sports Line-Shopper",
    page_icon="🎯",
    layout="wide"
)

# Custom Styling for Clean, Data-Dense Dark Mode
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
        color: #fafafa;
    }
    .stMetric {
        background-color: #1f2937;
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #374151;
    }
    </style>
""", unsafe_allow_html=True)

# Helper Conversion Functions
def american_to_decimal(american):
    if american > 0:
        return (american / 100.0) + 1.0
    else:
        return (100.0 / abs(american)) + 1.0

def decimal_to_american(decimal):
    if decimal >= 2.0:
        return round((decimal - 1.0) * 100)
    else:
        return round(-100.0 / (decimal - 1.0))

def calculate_implied_probability(odds, odds_type):
    if odds_type == "American":
        if odds > 0:
            return 100.0 / (odds + 100.0)
        else:
            return abs(odds) / (abs(odds) + 100.0)
    else: # Decimal
        return 1.0 / odds

# App Header
st.title("🎯 Zero-API Manual +EV Line-Shopper & True Probability Engine")
st.markdown("Strip the vig from consensus/sharp lines across major sports, calculate fair probabilities (Decimal, American, %), and reverse-engineer your target EV odds.")
st.divider()

# Sidebar: Sport and Market Selection
st.sidebar.header("1. Sport & Market Filters")
selected_sport = st.sidebar.selectbox(
    "Select Sport",
    ["Football (NFL/CFB)", "Basketball (NBA/CBB)", "Baseball (MLB)", "Hockey (NHL)", "Soccer (EPL/MLS)"]
)

market_type = st.sidebar.selectbox(
    "Select Market Type",
    ["Moneyline (2-Way)", "Spread / Run Line / Puck Line"]
)

st.sidebar.divider()
st.sidebar.header("Bankroll & Staking")
bankroll = st.sidebar.number_input("Total Bankroll ($)", min_value=10.0, value=1000.0, step=50.0)
kelly_fraction = st.sidebar.selectbox("Kelly Multiplier", [1.0, 0.5, 0.25], index=2, format_func=lambda x: f"{int(x*100)}% Kelly (Conservative)")

# Main Layout Tabs
tab1, tab2, tab3 = st.tabs([
    "📊 1. No-Vig True Probability Engine", 
    "🧮 2. Target EV Line Calculator", 
    "📝 3. Manual Line-Shopper & Tracker"
])

# --- TAB 1: TRUE PROBABILITY ENGINE ---
with tab1:
    st.subheader(f"[{selected_sport} - {market_type}] Sharp Market Vig Stripper")
    st.markdown("Input the consensus or sharp market lines for both sides of the game to remove the juice and find the true fair probability.")
    
    matchup_title = st.text_input("Game / Matchup Description", value="Team A vs Team B")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### Selection A (e.g., Home / Favorite)")
        team_a_name = st.text_input("Team/Side A Name", value="Home Team")
        odds_a_type = st.radio("Format A", ["American", "Decimal"], key="type_a")
        odds_a_val = st.number_input("Odds A", value=-110.0 if odds_a_type=="American" else 1.91, step=1.0 if odds_a_type=="American" else 0.01, key="val_a")
        
    with col2:
        st.markdown("#### Selection B (e.g., Away / Underdog)")
        team_b_name = st.text_input("Team/Side B Name", value="Away Team")
        odds_b_type = st.radio("Format B", ["American", "Decimal"], key="type_b")
        odds_b_val = st.number_input("Odds B", value=-110.0 if odds_b_type=="American" else 1.91, step=1.0 if odds_b_type=="American" else 0.01, key="val_b")

    # Calculation logic (Multiplicative / Proportional Vig Removal)
    ip_a = calculate_implied_probability(odds_a_val, odds_a_type)
    ip_b = calculate_implied_probability(odds_b_val, odds_b_type)
    total_ip = ip_a + ip_b
    
    true_prob_a = ip_a / total_ip
    true_prob_b = ip_b / total_ip
    
    fair_dec_a = 1.0 / true_prob_a
    fair_dec_b = 1.0 / true_prob_b
    
    fair_am_a = decimal_to_american(fair_dec_a)
    fair_am_b = decimal_to_american(fair_dec_b)
    
    st.divider()
    st.markdown(f"### 📈 Fair Market Baseline for: *{matchup_title}*")
    
    res_col1, res_col2 = st.columns(2)
    with res_col1:
        st.metric(label=f"{team_a_name} True Probability", value=f"{true_prob_a*100:.2f}%")
        st.write(f"**Fair Decimal Odds:** {fair_dec_a:.2f}")
        st.write(f"**Fair American Odds:** {fair_am_a:+d}")
        
    with res_col2:
        st.metric(label=f"{team_b_name} True Probability", value=f"{true_prob_b*100:.2f}%")
        st.write(f"**Fair Decimal Odds:** {fair_dec_b:.2f}")
        st.write(f"**Fair American Odds:** {fair_am_b:+d}")

# --- TAB 2: TARGET EV LINE CALCULATOR ---
with tab2:
    st.subheader("🧮 Target EV Line Calculator ('What line do I need to find?')")
    st.markdown("Set your target profit margin (e.g., 5% EV) and feed in the true probability of your play to calculate the minimum odds required at recreational books.")
    
    calc_col1, calc_col2 = st.columns(2)
    with calc_col1:
        target_ev_pct = st.slider("Target Minimum EV (%)", min_value=1.0, max_value=25.0, value=5.0, step=0.5)
        input_true_prob = st.slider("True Probability (%)", min_value=1.0, max_value=99.0, value=50.0, step=0.5) / 100.0
        
    with calc_col2:
        target_ev_decimal = target_ev_pct / 100.0
        # Formula: Required Decimal Odds = (1 + target_ev_decimal) / true_probability
        required_dec = (1.0 + target_ev_decimal) / input_true_prob
        required_am = decimal_to_american(required_dec)
        
        st.markdown("### 🎯 Your Line-Shopping Threshold:")
        st.info(f"To lock in at least **{target_ev_pct}% EV** on a play with a **{input_true_prob*100:.1f}%** true probability:")
        st.metric(label="Minimum Required Decimal Odds", value=f"{required_dec:.2f}")
        st.metric(label="Minimum Required American Odds", value=f"{required_am:+d}")
        st.caption("If you find this line higher than this target in the market, you've beaten the threshold and secured your target EV.")

# --- TAB 3: MANUAL LINE-SHOPPER & WORKSPACE ---
with tab3:
    st.subheader("📝 Manual Line-Shopper Tracker")
    st.markdown("Log lines you discover while browsing sportsbooks manually to instantly calculate actual EV%, edge, and recommended stake.")
    
    with st.form("line_shop_form"):
        f_col1, f_col2, f_col3 = st.columns(3)
        with f_col1:
            log_match = st.text_input("Matchup", value="Team A vs Team B")
            log_book = st.text_input("Sportsbook Name", value="DraftKings / FanDuel")
        with f_col2:
            log_selection = st.text_input("Selection Backed", value="Team A -3.5")
            log_odds_type = st.selectbox("Book Odds Format", ["American", "Decimal"], key="log_fmt")
        with f_col3:
            log_odds_val = st.number_input("Available Odds at Book", value=105.0 if log_odds_type=="American" else 2.05, step=1.0 if log_odds_type=="American" else 0.01)
            log_true_prob = st.number_input("True Probability (%)", value=50.0, min_value=0.1, max_value=99.9, step=0.1) / 100.0
            
        submitted = st.form_submit_button("Calculate EV & Analyze Line")
        
    if submitted:
        book_dec = american_to_decimal(log_odds_val) if log_odds_type=="American" else log_odds_val
        ev_percent = ((log_true_prob * book_dec) - 1.0) * 100.0
        edge = log_true_prob - (1.0 / book_dec)
        
        # Kelly Criterion calculation
        q_prob = 1.0 - log_true_prob
        net_odds_decimal = book_dec - 1.0
        full_kelly = (log_true_prob * net_odds_decimal - q_prob) / net_odds_decimal
        rec_stake = max(0.0, bankroll * full_kelly * kelly_fraction)
        
        st.divider()
        st.markdown(f"### Results for: *{log_selection}* at *{log_book}*")
        
        res_c1, res_c2, res_c3, res_c4 = st.columns(4)
        res_c1.metric("Expected Value (EV%)", f"{ev_percent:+.2f}%", delta="Positive EV" if ev_percent > 0 else "Negative EV")
        res_c2.metric("Calculated Edge", f"{edge*100:+.2f}%")
        res_c3.metric("Book Implied Prob", f"{(1.0/book_dec)*100:.2f}%")
        res_c4.metric("Recommended Stake", f"${rec_stake:.2f}")
        
        if ev_percent > 0:
            st.success(f"✅ **+EV Opportunity!** This line beats your true probability baseline and yields a positive expectation.")
        else:
            st.warning("⚠️ **-EV Line.** The book's juice eliminates the value here. Keep shopping.")
          
