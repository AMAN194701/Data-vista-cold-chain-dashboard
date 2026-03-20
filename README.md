# FreshGuard Solutions — Cold Chain Profit Leakage Dashboard
Built for Data Vista Hackathon — An interactive analytics dashboard that diagnoses profit leakage in cold chain logistics across 100,000 transactions, 5 regions, 50 stores, and 15 suppliers.


📸 Demo
🔗 Live App: https://data-vista-cold-chain-dashboard-ckxmfi3komk7txvzlntowk.streamlit.app/

🧩 Problem Statement
Cold chain logistics (food, pharma, dairy) loses billions annually due to spoilage, temperature abuse, and poor handling. The challenge: identify where profit is leaking across the supply chain — from supplier to store — and give decision-makers actionable insights.

📊 What This Dashboard Analyzes
The dashboard is split into 7 analytical sections, each answering a real business question:
SectionQuestion Answered1. Executive OverviewHow bad is the waste problem overall?2. Hot Zone AnalysisWhich stores and temperature bands have the worst spoilage?3. Financial Leak AnalysisWhere exactly is profit bleeding — by category and discount?4. Supply Chain FragilityWhat operational factors (distribution time, handling) drive spoilage?5. Demand & SeasonalityAre there seasonal patterns in waste we can predict?6. Supplier RiskWhich vendors are costing us the most?7. Strategic RecommendationsWhat should the business actually do about it?

## 🛠 Tech Stack
- Python
- Streamlit
- Pandas
- Plotly
- Statsmodels

⚙️ Installation & Running Locally
bash# 1. Clone the repository
git clone https://github.com/AMAN194701/Data-vista-cold-chain-dashboard
cd Data-vista-cold-chain-dashboard

## Install dependencies
pip install -r requirements.txt

## Run the app
streamlit run app.py

Make sure Dataset.csv is in the same directory as app.py.


📌 Key Features

> Sidebar Filters — Filter by Region, Category, Supplier, Month, and Store dynamically
> 
> 6 KPI Cards — Revenue, Profit, Margin, Waste Cost, Waste Rate, Units Wasted
> 
> 15 Interactive Charts — Bar, Line, Scatter, Treemap, Pie, Waterfall, and Dual-Axis charts
> 
> Auto-generated Insights — Each section surfaces a data-driven insight box
> 
> Strategic Recommendations — 5 actionable business recommendations derived from the data
> 
> Dark Professional Theme — Custom CSS with gradient cards and Inter font




## 📈 Key Findings (from the data)

Temperature deviations above 3°C dramatically increase spoilage risk

Distribution times beyond 48 hours cause a sharp spike in waste rates

Deep discounting (>40%) destroys margins more than the spoilage itself

Handling Score is one of the strongest predictors of spoilage — every 1-point drop matters

The top waste category alone accounts for the majority of total waste cost

