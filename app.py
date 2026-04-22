import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression

st.set_page_config(page_title="Analysis Tool for US Listed IT Companies", layout="wide")

df = pd.read_csv('tech_revenue_data.csv')
industry_avg = pd.read_csv('industry_avg_revenue.csv')

st.title("📊 Analysis Tool for US Listed IT Companies")
st.write("Query revenue data of US-listed IT companies (last 5 years)")

# ========== Sidebar: Filter Options ==========
st.sidebar.header("🔧 Filter Options")

# Year range slider
years = sorted(df['fyear'].unique())
year_range = st.sidebar.slider("Select Year Range", min(years), max(years), (min(years), max(years)))

# Company multiselect
company_list = df['company_name'].unique()
selected_companies = st.sidebar.multiselect("Select Companies (2-4 for comparison)", company_list, max_selections=4)

if len(selected_companies) < 1:
    st.warning("Please select at least 1 company.")
    st.stop()

# Revenue unit toggle
unit = st.sidebar.radio("Revenue Unit", ["Million USD", "Billion USD"])
unit_factor = 1 if unit == "Million USD" else 1000
unit_label = "USD mil" if unit == "Million USD" else "USD bil"

# Revenue threshold filter
threshold = st.sidebar.number_input("Revenue Threshold (Filter years with revenue >)", min_value=0, value=0, step=500)

# Forecast toggle
show_forecast = st.sidebar.checkbox("📈 Show Forecast Trend Line", value=False)
if show_forecast:
    forecast_years = st.sidebar.slider("Forecast Years", 1, 5, 2)

# ========== Data Processing ==========
filtered_data = df[df['fyear'].between(year_range[0], year_range[1])]

company_data_dict = {}
for company in selected_companies:
    company_df = filtered_data[filtered_data['company_name'] == company].copy()
    company_df = company_df.merge(industry_avg, on='fyear', how='left')
    # Convert revenue units
    company_df['revenue_converted'] = company_df['revenue_mm'] / unit_factor
    company_df['industry_avg_converted'] = company_df['industry_avg_revenue_mm'] / unit_factor
    # Apply threshold filter
    if threshold > 0:
        company_df = company_df[company_df['revenue_converted'] > threshold]
    company_data_dict[company] = company_df

# ========== Forecast Function ==========
def add_forecast_trace(fig, data, company_name, forecast_years):
    """Add linear regression forecast line"""
    if len(data) < 2:
        return fig

    # Prepare training data
    X = data['fyear'].values.reshape(-1, 1)
    y = data['revenue_converted'].values

    # Train linear regression model
    model = LinearRegression()
    model.fit(X, y)

    # Predict future years
    last_year = data['fyear'].max()
    future_years = np.arange(last_year + 1, last_year + forecast_years + 1)
    future_X = future_years.reshape(-1, 1)
    future_pred = model.predict(future_X)

    # Historical fitted values
    hist_pred = model.predict(X)

    # Add historical fitted line (dotted)
    fig.add_trace(go.Scatter(x=data['fyear'], y=hist_pred,
                             mode='lines', name=f'{company_name} (fitted)',
                             line=dict(dash='dot', width=1.5)))

    # Add future forecast line (dashed)
    fig.add_trace(go.Scatter(x=future_years, y=future_pred,
                             mode='lines+markers', name=f'{company_name} (forecast)',
                             line=dict(dash='dash', width=2)))
    return fig

# ========== Chart 1: Revenue Trend vs Industry Average ==========
st.subheader("📈 Revenue Trend vs Industry Average")

fig1 = go.Figure()
for company, data in company_data_dict.items():
    fig1.add_trace(go.Scatter(x=data['fyear'], y=data['revenue_converted'], 
                               mode='lines+markers', name=company))
    # Add forecast line
    if show_forecast and len(data) >= 2:
        fig1 = add_forecast_trace(fig1, data, company, forecast_years)

# Add industry average line
if company_data_dict:
    first_company = list(company_data_dict.values())[0]
    fig1.add_trace(go.Scatter(x=first_company['fyear'], y=first_company['industry_avg_converted'],
                               mode='lines', name='Industry Average', line=dict(dash='dash', color='gray')))

fig1.update_layout(xaxis_title="Year", yaxis_title=f"Revenue ({unit_label})", legend_title="Company")
st.plotly_chart(fig1, use_container_width=True)

# ========== Chart 2: Annual Revenue Comparison ==========
st.subheader("📊 Annual Revenue Comparison")

fig2 = go.Figure()
for company, data in company_data_dict.items():
    fig2.add_trace(go.Bar(x=data['fyear'], y=data['revenue_converted'], name=company))
fig2.update_layout(xaxis_title="Year", yaxis_title=f"Revenue ({unit_label})", barmode='group', legend_title="Company")
st.plotly_chart(fig2, use_container_width=True)

# ========== Chart 3: YoY Revenue Growth Rate ==========
st.subheader("📈 YoY Revenue Growth Rate (%)")

fig3 = go.Figure()
for company, data in company_data_dict.items():
    data['growth_rate'] = data['revenue_converted'].pct_change() * 100
    fig3.add_trace(go.Bar(x=data['fyear'], y=data['growth_rate'], name=company))
fig3.update_layout(xaxis_title="Year", yaxis_title="Growth Rate (%)", barmode='group', legend_title="Company")
st.plotly_chart(fig3, use_container_width=True)

# ========== Key Metrics Cards ==========
st.subheader("📌 Key Metrics (Latest Year)")
latest_year = year_range[1]
latest_data = {}
for company, data in company_data_dict.items():
    latest = data[data['fyear'] == latest_year]
    if not latest.empty:
        latest_data[company] = latest.iloc[0]

if latest_data:
    cols = st.columns(len(latest_data))
    for i, (company, row) in enumerate(latest_data.items()):
        with cols[i]:
            st.metric(company, f"{row['revenue_converted']:.0f} {unit_label}")

# ========== Forecast Summary ==========
if show_forecast:
    st.subheader("🔮 Forecast Summary")
    for company, data in company_data_dict.items():
        if len(data) >= 2:
            X = data['fyear'].values.reshape(-1, 1)
            y = data['revenue_converted'].values
            model = LinearRegression()
            model.fit(X, y)
            last_year = data['fyear'].max()
            next_year = last_year + 1
            next_pred = model.predict([[next_year]])[0]
            growth_rate = (next_pred / y[-1] - 1) * 100
            st.write(f"**{company}**: Predicted {next_year} revenue: {next_pred:.0f} {unit_label} (↑{growth_rate:.1f}% vs {last_year})")

# ========== Detailed Data Table ==========
st.subheader("Detailed Data")
for company, data in company_data_dict.items():
    st.write(f"**{company}**")
    display_cols = ['fyear', 'revenue_converted', 'industry_avg_converted']
    if threshold > 0:
        st.write(f"(Filtered: revenue > {threshold} {unit_label})")
    st.dataframe(data[display_cols].rename(columns={'revenue_converted': f'Revenue ({unit_label})', 
                                                     'industry_avg_converted': f'Industry Avg ({unit_label})'}))
