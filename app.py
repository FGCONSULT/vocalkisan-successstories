import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests
import json

# Set Streamlit Page Config
st.set_page_config(
    page_title="Dairy Green-Wealth Evaluator",
    page_icon="🐄",
    layout="wide"
)

# Application Theme / Styling (FIXED: Clean HTML layout)
st.markdown("""
    <style>
    .main-header { font-size:36px !important; font-weight: bold; color: #1E3A8A; }
    .sub-header { font-size:20px !important; color: #10B981; margin-bottom: 20px; }
    .card { background-color: #F3F4F6; padding: 20px; border-radius: 10px; border-left: 5px solid #2563EB; margin-bottom: 15px; }
    </style>
""", unsafe_allow_html=True)

# Corrected Header Markdown Blocks
st.markdown('<div class="main-header">🐄 Dairy Farm Sustainability & Translation Platform</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Bilingual Article Translation (via Sarvam AI) & NDP-I Benchmark Analysis</div>', unsafe_allow_html=True)
st.write("---")

# Helper function to calculate IRR without external library dependencies (avoids np.irr deprecation)
def calculate_irr(cash_flows):
    def npv(r, cfs):
        return sum(cf / (1 + r)**t for t, cf in enumerate(cfs))
    
    # Simple bisection method to find IRR
    low, high = -0.99, 2.0
    for _ in range(100):
        mid = (low + high) / 2
        npv_mid = npv(mid, cash_flows)
        if abs(npv_mid) < 1e-4:
            return mid * 100
        
        # Determine the direction of the NPV curve
        if npv(high, cash_flows) < npv(low, cash_flows):
            if npv_mid > 0:
                low = mid
            else:
                high = mid
        else:
            if npv_mid > 0:
                high = mid
            else:
                low = mid
    # Fallback to simple compound return estimate if bisection limits fail
    total_returns = sum(cash_flows[1:])
    initial = abs(cash_flows[0])
    return ((total_returns / initial) ** (1 / max(len(cash_flows) - 1, 1)) - 1) * 100

# Retrieve API keys securely from sidebar or Streamlit Secrets
with st.sidebar:
    st.header("🔑 API Configurations")
    sarvam_key = st.text_input("Sarvam AI Subscription Key", type="password", value=st.secrets.get("SARVAM_API_KEY", ""))
    groq_key = st.text_input("Groq API Key (for Analysis)", type="password", value=st.secrets.get("GROQ_API_KEY", ""))
    st.info("Retrieve your keys from the respective platform dashboards to run translation & advisory models.")

# Create Core Application Tabs
tab1, tab2, tab3 = st.tabs(["📝 Sarvam AI Article Translator", "📊 Farm Data Input & Calculation", "🎯 Benchmark Performance Dashboard"])

# ==========================================
# TAB 1: SARVAM AI TRANSLATION SYSTEM
# ==========================================
with tab1:
    st.header("Translate Dairy Articles to English")
    st.write("Use **Sarvam AI's Translate API** (optimized for Indian context) to translate local success stories (like Mrs. Renu Mishra's Hindi section in the chronicle) back to English.")
    
    sample_text = """श्रीमती रेणु मिश्रा, पत्नी श्री उपेंद्र कुमार मिश्रा, जिनकी आयु लगभग 40 वर्ष है और मिश्रोलिया गाँव की निवासी हैं। वह अपने पति, सास और तीन बच्चों के साथ रहती हैं। इनके परिवार की आजीविका का आधार कृषि और पशुपालन है। कुछ साल पहले इन्होंने, एक देशी और एक संकर नस्ल की गाय खरीदी थी, जिससे लगभग 15 लीटर दूध का उत्पादन होता था। बापूधाम मिल्क प्रोड्यूसर कंपनी से जुड़ने के बाद अब उन्हें यकीन है कि अपनी गायों से उत्पादित दूध की कीमत का निर्धारण अब उनके सामने स्वचालित मशीन से होता है। वह इस बात से भी बहुत खुश है कि अब दूध का मूल्य सीधे उनके बैंक खाते में आता है।"""
    
    input_text = st.text_area("Paste Hindi Article Here", value=sample_text, height=200)
    
    if st.button("Translate using Sarvam AI"):
        if not sarvam_key:
            st.warning("Please configure your Sarvam AI API Key in the sidebar.")
        else:
            with st.spinner("Translating using sarvam-translate:v1..."):
                try:
                    # Direct REST API post request
                    url = "https://api.sarvam.ai/translate"
                    payload = {
                        "input": input_text,
                        "source_language_code": "hi-IN",
                        "target_language_code": "en-IN",
                        "model": "sarvam-translate:v1",
                        "mode": "formal"
                    }
                    headers = {
                        "api-subscription-key": sarvam_key,
                        "Content-Type": "application/json"
                    }
                    response = requests.post(url, json=payload, headers=headers)
                    
                    if response.status_code == 200:
                        translated_text = response.json().get("translated_text", "")
                        st.success("### Translated Text (English)")
                        st.info(translated_text)
                    else:
                        st.error(f"Error {response.status_code}: {response.text}")
                except Exception as e:
                    st.error(f"API Connection Failed: {e}")

# ==========================================
# TAB 2: INDICATOR DESIGN, INPUTS & CALCULATIONS
# ==========================================
with tab2:
    st.header("Enter Farm Sustainability Parameters")
    st.write("Provide your dairy farm's operational values to dynamically calculate liquidity, profitability, solvency, economic returns, and carbon index.")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("🏦 Financial Parameters")
        revenue = st.number_input("Monthly Milk Revenue (₹)", value=35000, step=1000)
        current_assets = st.number_input("Current Liquid Assets (₹)", value=25000, step=1000)
        current_liabilities = st.number_input("Current Liabilities (Short-term debt) (₹)", value=12000, step=500)
        total_assets = st.number_input("Total Farm Value (Cows, Land, etc.) (₹)", value=250000, step=5000)
        total_liabilities = st.number_input("Outstanding Long-term Loans (₹)", value=80000, step=5000)
        
    with col2:
        st.subheader("📈 Economic Parameters")
        feed_cost = st.number_input("Monthly Feed Cost (₹)", value=15000, step=500)
        vet_misc_cost = st.number_input("Monthly Vet & Misc Operational Costs (₹)", value=3000, step=100)
        initial_investment = st.number_input("Initial Herd Expansion Investment (₹)", value=100000, step=5000)
        est_annual_growth = st.slider("Estimated Annual Income Growth (%)", min_value=0, max_value=50, value=15)
        
    with col3:
        st.subheader("🌱 Environmental Parameters")
        methane_reduc = st.slider("Cattle Methane Emission Reduction (%)", min_value=0, max_value=30, value=12)
        total_energy = st.number_input("Total Monthly Energy Usage (kWh)", value=500, step=10)
        renewable_energy = st.number_input("Solar/Biogas Energy Generated (kWh)", value=110, step=5)
        water_intensity = st.number_input("Water Consumed per Liter of Milk (Liters)", value=4.5, step=0.1)

    # Calculations
    net_monthly_income = revenue - (feed_cost + vet_misc_cost)
    current_ratio = current_assets / max(current_liabilities, 1)
    net_profit_margin = (net_monthly_income / max(revenue, 1)) * 100
    debt_to_asset = total_liabilities / max(total_assets, 1)
    
    # Benefit Cost Ratio (BCR)
    total_costs = feed_cost + vet_misc_cost
    bcr = revenue / max(total_costs, 1)
    
    # 5-Year Projected Cash Flows for custom IRR
    annual_net_benefit = net_monthly_income * 12
    cash_flows = [-initial_investment] + [annual_net_benefit * ((1 + est_annual_growth/100)**t) for t in range(1, 6)]
    irr = calculate_irr(cash_flows)
    
    renewable_share = (renewable_energy / max(total_energy, 1)) * 100

    st.success("### Derived Indicator Calculations")
    res_col1, res_col2, res_col3 = st.columns(3)
    with res_col1:
        st.metric("Net Monthly Income", f"₹{net_monthly_income:,.2f}")
        st.metric("Current Ratio (Liquidity)", f"{current_ratio:.2f}x")
        st.metric("Solvency (Debt-to-Asset)", f"{debt_to_asset:.2%}")
    with res_col2:
        st.metric("Benefit-Cost Ratio (BCR)", f"{bcr:.2f}")
        st.metric("Estimated 5-Year IRR", f"{irr:.2f}%")
        st.metric("Net Profit Margin (%)", f"{net_profit_margin:.1f}%")
    with res_col3:
        st.metric("Renewable Energy Share (%)", f"{renewable_share:.1f}%")
        st.metric("Methane Reduction Rate", f"{methane_reduc:.1f}%")
        st.metric("Water Usage / Liter Milk", f"{water_intensity:.1f} Liters")

# ==========================================
# TAB 3: VISUAL BENCHMARK COMPARISONS
# ==========================================
with tab3:
    st.header("Comparative Performance Dashboard")
    st.write("Compare your computed metrics directly with case-study benchmarks from the **National Dairy Plan Phase-I (NDP-I)**.")

    # Data Structuring for Plotting
    metrics = ['Net Profit Margin (%)', 'Benefit-Cost Ratio (BCR)', 'Methane Reduction (%)', 'Renewable Energy Share (%)']
    user_vals = [net_profit_margin, bcr * 10, methane_reduc, renewable_share] # Scaling BCR to visual scale (x10)
    bench_vals = [25.0, 1.25 * 10, 14.0, 20.0]  # Standardized case-study metrics

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=metrics,
        y=user_vals,
        name='Your Farm Indicators',
        marker_color='#10B981'
    ))
    fig.add_trace(go.Bar(
        x=metrics,
        y=bench_vals,
        name='NDP-I/Case Benchmarks',
        marker_color='#3B82F6'
    ))

    fig.update_layout(
        barmode='group',
        title='Farm Performance vs. Case Study Benchmarks',
        yaxis_title='Normalized Percentage / Scale Values',
        legend_title='Data Category',
        template='plotly_white'
    )

    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("""
    > **Visual Scale Notes**: 
    > * **Benefit-Cost Ratio (BCR)** is scaled up by a factor of 10 on this chart for visual clarity.
    > * **Target Profit Margin (25%)** is modeled on successful producer operations.
    > * **Methane reduction benchmarks (14%)** and **Renewable energy targets (20%)** are derived from the [NDDB Mission Milk Chronicle](https://www.nddb.coop/sites/default/files/pdfs/ndpi/Mission_Milk_Chronicle_Vol_4_April_2019.pdf).
    """, unsafe_allow_html=True)

    # AI Diagnostic Generation via Groq
    st.write("---")
    st.subheader("💡 GenAI Advisory Performance Diagnostics")
    
    if st.button("Generate Performance Growth Strategy"):
        if not groq_key:
            st.warning("Provide your Groq API Key in the sidebar to generate custom Advisory Reports.")
        else:
            with st.spinner("Analyzing parameters and drafting strategy..."):
                try:
                    headers = {
                        "Authorization": f"Bearer {groq_key}",
                        "Content-Type": "application/json"
                    }
                    prompt = f"""
                    You are a dairy development consultant evaluating a smallholder farm with the following profiles:
                    - Monthly Revenue: INR {revenue}
                    - Net Income: INR {net_monthly_income}
                    - Current Liquidity Ratio: {current_ratio}x (Benchmark: 1.5)
                    - Solvency Ratio (Debt/Asset): {debt_to_asset:.2f} (Benchmark: <0.4)
                    - Benefit-Cost Ratio: {bcr:.2f} (Benchmark: 1.25)
                    - Estimated 5-Yr IRR: {irr:.1f}%
                    - Environmental: {renewable_share:.1f}% renewable energy share (Benchmark: 20%), Methane Reduction of {methane_reduc}% (Benchmark: 14%).
                    
                    Draft an actionable 3-part strategic expansion plan based on NDP-I success stories (Ration Balancing, Automated Cashless payment, and solar adoption). Write concisely.
                    """
                    data = {
                        "model": "llama-3.3-70b-versatile",
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0.3
                    }
                    response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=data)
                    
                    if response.status_code == 200:
                        report = response.json()['choices'][0]['message']['content']
                        st.info("### AI Consultation Report & Action Plan")
                        st.markdown(report)
                    else:
                        st.error(f"Error contacting Groq API: {response.text}")
                except Exception as e:
                    st.error(f"Groq API connection failure: {e}")
