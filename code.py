import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# --- CONFIGURATION & GAME CONSTANTS ---
MAX_PERIODS = 8  # 8 Quarters (2 Years)
STARTING_CASH = 500  # in Crores
STARTING_SHARE = 59.0  # Percentage
BIRLA_SHARE = 5.0     # Percentage
DEMAND_BASE = 1000    # Base units

# --- INITIALIZATION ---
def init_game():
    if 'period' not in st.session_state:
        st.session_state['period'] = 1
        st.session_state['cash'] = STARTING_CASH
        st.session_state['market_share'] = STARTING_SHARE
        st.session_state['birla_share'] = BIRLA_SHARE
        st.session_state['history'] = []
        st.session_state['game_over'] = False
        st.session_state['last_feedback'] = "Welcome, Vikram. Birla Opus has just launched. Your dealers are anxious. Make your Q1 decisions."

def reset_game():
    st.session_state.clear()
    init_game()

# --- THE SIMULATION ENGINE ---
def calculate_results(delivery_freq, inventory_policy, dealer_incentive, demand_type):
    
    # 1. Base Costs (Efficiency Levers)
    # 4x delivery is expensive, 1x is cheap
    logistics_cost = 80 if delivery_freq == "4x Daily (Responsive)" else 30
    
    # High buffer is expensive, Lean is cheap
    inventory_cost = 50 if inventory_policy == "High Buffer (Responsive)" else 20
    
    # Matching Birla's margins is expensive
    incentive_cost = 60 if dealer_incentive == "Match Birla (High)" else 20
    
    total_opex = logistics_cost + inventory_cost + incentive_cost

    # 2. Service Level Calculation (The Trap)
    # The market demands High Responsiveness. Efficiency hurts service level.
    service_score = 0
    
    if delivery_freq == "4x Daily (Responsive)":
        service_score += 40
    else:
        service_score += 10 # Penalty for slow delivery
        
    if inventory_policy == "High Buffer (Responsive)":
        service_score += 40
    else:
        service_score += 10 # Penalty for stockouts
        
    if dealer_incentive == "Match Birla (High)":
        service_score += 20
    else:
        service_score += 5 # Penalty for unhappy dealers

    # 3. Apply Volatility (The Difficulty Multiplier)
    # If demand is "Festival" or "Volatile", 'Efficiency' choices are penalized double
    if demand_type != "Stable":
        if inventory_policy == "Lean (Efficient)":
            service_score -= 30 # Massive stockout penalty
        if delivery_freq == "1x Daily (Efficient)":
            service_score -= 20 # Customers won't wait

    # Clamp score 0-100
    service_score = max(0, min(100, service_score))

    # 4. Market Share Impact (The Permanent Damage)
    # If Service Score < 70, you lose share to Birla PERMANENTLY
    share_change = 0
    if service_score >= 85:
        share_change = 0.5 # Small gain
        feedback = "Dealers are happy. Availability is high."
    elif service_score >= 60:
        share_change = -1.5 # Slow bleed
        feedback = "Dealers are grumbling. Some are stocking Birla Opus alongside yours."
    else:
        share_change = -5.0 # Hemorrhage
        feedback = "DISASTER! Stockouts during peak demand. Dealers are furious and aggressively pushing Birla Opus."

    # 5. Financials
    # Revenue depends on Market Share and Demand
    demand_multiplier = 1.5 if demand_type == "Festival Season" else 1.0
    actual_revenue = (DEMAND_BASE * demand_multiplier) * (st.session_state['market_share'] / 100) * (service_score / 100) * 0.5
    
    net_profit = actual_revenue - total_opex

    return net_profit, share_change, feedback, total_opex, actual_revenue

# --- MAIN APP UI ---
st.set_page_config(page_title="Asian Paints Strategy Sim", layout="wide")

init_game()

st.title("🏭 The Colour of Competition: Strategy Simulation")
st.markdown("""
**Role:** You are Vikram Malhotra, CSCO of Asian Paints.
**Objective:** Survive 8 Quarters against Birla Opus. Maximize Profit while protecting Market Share.
**The Trap:** Your CFO wants you to cut costs (Efficiency). Your Dealers want Paint NOW (Responsiveness).
""")

# Sidebar Stats
with st.sidebar:
    st.header(f"Quarter: {st.session_state['period']} / {MAX_PERIODS}")
    
    share_delta = 0
    if len(st.session_state['history']) > 0:
        share_delta = st.session_state['market_share'] - st.session_state['history'][-1]['market_share_end']
        
    st.metric("💰 Cash Reserve", f"₹{st.session_state['cash']:.0f} Cr")
    st.metric("📈 Market Share", f"{st.session_state['market_share']:.1f}%", delta=f"{share_delta:.1f}%")
    st.metric("😈 Birla Opus Share", f"{st.session_state['birla_share']:.1f}%")
    
    st.divider()
    if st.button("Restart Simulation"):
        reset_game()
        st.rerun()

# --- GAME OVER SCREEN ---
if st.session_state['game_over']:
    st.error("GAME OVER")
    if st.session_state['market_share'] < 40:
        st.write("❌ You lost your dominance. Birla Opus has commoditized the market.")
    elif st.session_state['cash'] < 0:
        st.write("❌ You went bankrupt trying to fight a price war.")
    else:
        st.success(f"✅ Simulation Complete! Final Cash: ₹{st.session_state['cash']:.0f} Cr. Final Share: {st.session_state['market_share']:.1f}%")
    
    # Show History Data
    df = pd.DataFrame(st.session_state['history'])
    st.dataframe(df)
    st.stop()

# --- SCENARIO GENERATOR ---
# Randomize environment for the current period
np.random.seed(st.session_state['period'] * 99)
scenario_roll = np.random.random()
if scenario_roll < 0.3:
    scenario = "Stable"
    context = "Demand is flat. A quiet quarter."
elif scenario_roll < 0.7:
    scenario = "Volatile"
    context = "Competitor Price War! Birla is undercutting prices aggressively."
else:
    scenario = "Festival Season"
    context = "Diwali Peak! Demand is skyrocketing and highly unpredictable."

st.info(f"**Market Conditions for Q{st.session_state['period']}: {scenario}** - {context}")

# --- INPUT FORM ---
with st.form("decision_form"):
    c1, c2, c3 = st.columns(3)
    
    with c1:
        st.subheader("1. Logistics")
        delivery = st.radio("Delivery Frequency", ["4x Daily (Responsive)", "1x Daily (Efficient)"], help="4x costs more but guarantees availability.")
        
    with c2:
        st.subheader("2. Inventory")
        inventory = st.radio("Stocking Policy", ["High Buffer (Responsive)", "Lean (Efficient)"], help="High Buffer prevents stockouts during spikes.")
        
    with c3:
        st.subheader("3. Dealer Relations")
        incentive = st.radio("Commissions", ["Match Birla (High)", "Standard (Low)"], help="Paying dealers more reduces profit but keeps loyalty.")
        
    submitted = st.form_submit_button("Run Quarter")

if submitted:
    # Run Calculation
    profit, share_change, feedback, opex, rev = calculate_results(delivery, inventory, incentive, scenario)
    
    # Update State
    st.session_state['cash'] += profit
    prev_share = st.session_state['market_share']
    st.session_state['market_share'] += share_change
    st.session_state['birla_share'] -= share_change # Zero sum game mostly
    st.session_state['last_feedback'] = feedback
    
    # Record History
    st.session_state['history'].append({
        "Quarter": st.session_state['period'],
        "Scenario": scenario,
        "Strategy": "Responsive" if delivery.startswith("4x") else "Efficient",
        "Profit": round(profit, 2),
        "Market_Share_End": round(st.session_state['market_share'], 2)
    })
    
    # Check Game Over
    st.session_state['period'] += 1
    if st.session_state['period'] > MAX_PERIODS or st.session_state['cash'] < 0 or st.session_state['market_share'] < 40:
        st.session_state['game_over'] = True
        
    st.rerun()

# --- DASHBOARD & GRAPHS ---
st.divider()
st.subheader("Analyst Report")

# Feedback Box
if st.session_state['history']:
    last_round = st.session_state['history'][-1]
    profit_color = "green" if last_round['Profit'] > 0 else "red"
    
    st.markdown(f"**Last Quarter Feedback:** {st.session_state['last_feedback']}")
    st.markdown(f"**Net Profit:** :{profit_color}[₹{last_round['Profit']} Cr]")

    # Graphs
    if len(st.session_state['history']) > 0:
        hist_df = pd.DataFrame(st.session_state['history'])
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("##### Market Share Trend")
            st.line_chart(hist_df.set_index("Quarter")['Market_Share_End'])
        with col2:
            st.markdown("##### Profit Trend")
            st.bar_chart(hist_df.set_index("Quarter")['Profit'])
