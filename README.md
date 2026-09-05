<<<<<<< HEAD
# Smartphone Usage & Productivity — Streamlit Dashboard

An interactive rebuild of the `Smartphone-Usage-Productivity-Analysis.ipynb` notebook.

## Setup

```bash
pip install -r requirements.txt
```

## Run

Put `Smartphone_Usage_Productivity_Dataset_50000.csv` in the same folder as `app.py`
(or upload any CSV with the same columns from the sidebar), then:

```bash
streamlit run app.py
```

## What it does

- Recreates the notebook's cleaning + feature engineering: dedup, `phone_usage_category`
  (Low/Medium/High), `sleep_health` (Good/Poor), `risk_score`, `risk_level`, and `high_risk` flag.
- Sidebar filters: gender, occupation, device type, risk level, age range, daily phone hours.
- Tabs mirroring the notebook's EDA: Overview, Phone Usage vs Productivity, Sleep vs Stress,
  Social Media vs Stress, Risk Analysis, Correlation, and a raw Data Explorer.
- KPI cards, interactive Plotly charts (hover/zoom), and a "download filtered data" button.
=======
# 📊 Smartphone Usage & Productivity Analysis

## 🔍 Project Overview
This project analyzes how smartphone usage habits impact **productivity, sleep, and stress levels**.  
Using a dataset of **50,000 user records**, we explore behavioral patterns, engineer risk features, and build a predictive model to understand the real-world impact of digital lifestyles.

---

## 🎯 Business Problem
With increasing screen time, organizations and individuals are facing:
- Reduced productivity  
- Poor sleep quality  
- Rising stress levels  

**Goal:**  
Identify the relationship between smartphone behavior and mental well-being, and provide data-driven insights for better lifestyle and workplace policies.

---

## ❓ Key Questions
1. Does higher phone usage reduce productivity?  
2. Is sleep duration related to stress levels?  
3. Do social media and gaming increase stress?  
4. Who are the high-risk users?  
5. Can stress be predicted from usage behavior?

---

## 📁 Dataset
- **Rows:** 50,000  
- **Features:**  
  - daily_phone_hours  
  - social_media_hours  
  - gaming_hours  
  - sleep_hours  
  - stress_level  
  - work_productivity_score  
  - app_usage_count  
  - caffeine_intake_cups  
  - weekend_screen_time_hours  
  - age, gender, occupation, device_type  

---

## 🛠️ Tools & Technologies
- Python  
- Pandas & NumPy  
- Seaborn & Matplotlib  
- Scikit-learn  
- Jupyter Notebook  

---

## 🔄 Workflow
1. Data Loading & Inspection  
2. Data Cleaning  
3. Feature Engineering  
4. Exploratory Data Analysis (EDA)  
5. Correlation Analysis  
6. Risk Segmentation  
7. Stress Prediction Model  

---

## 📈 Key Insights
- High phone usage reduces productivity  
- Poor sleep increases stress  
- Social media & gaming correlate with stress  
- High-risk users show low sleep and high phone usage  

---

## 🧠 Risk Scoring
A composite risk score was created using normalized:
- Daily phone hours  
- Sleep hours (inverted)  
- Stress levels  

Users were segmented into **Low, Medium, and High Risk** groups.

---

## 🤖 Predictive Modeling
A Linear Regression model was trained using:
- Phone usage  
- Sleep hours  
- Social media & gaming time  

to predict **stress levels**.

---

## 📊 Visualizations
- Phone Usage vs Productivity  
- Sleep vs Stress  
- Social Media vs Stress  
- Correlation Heatma
>>>>>>> 9fd0f6ba31d89ce576e5a1a2180ff21fe7ede062
