# Analysis Tool for US Listed IT Companies

## 1. Problem & User
Investors and financial analysts need a quick way to compare individual IT company revenue against the industry average. This tool provides an interactive interface to visualize revenue trends and benchmark performance.

## 2. Data
- **Source**: WRDS Compustat
- **Access Date**: April 2026
- **Key Fields**: gvkey (company ID), fyear (fiscal year), sale (revenue in USD million), company_name, gsector (GICS sector code 45 = Information Technology)
- 
## 3. Methods
- Pulled revenue data for IT sector companies from WRDS using SQL queries
- Cleaned and filtered data to keep companies with complete 5-year records
- Calculated industry average revenue per year
- Built interactive web app using Streamlit
- Visualized data with Plotly (line charts, bar charts, growth rate charts)

## 4. Key Findings
- IT industry average revenue grew from $2.5B (2020) to $5.0B (2025)
- Users can instantly compare any company's revenue against industry benchmark
- Year-over-year growth rate visualization helps identify outperforming companies
- Side-by-side company comparison reveals competitive positioning

## 5. How to Run Locally
```bash
pip install -r requirements.txt
streamlit run app.py
```

## 6. Product link / Demo
https://github.com/fsacc33/US-Listed-IT-Companies-Revenue-Analysis-Tool/tree/main

## 7. Limitations & next steps
-Limited to companies with complete 5-year data (some companies excluded)
-Industry average based on available sample, not entire IT sector
-Next steps: add profitability metrics (net income, margins), add more sectors, enable custom date range selection-Industry average based on available sample, not entire IT sector
