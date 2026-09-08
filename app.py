import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# ----------------------------------------------------------------------------
# PAGE CONFIG
# ----------------------------------------------------------------------------
st.set_page_config(
    page_title="Smartphone Usage & Productivity Dashboard",
    page_icon="\U0001F4F1",
    layout="wide",
    initial_sidebar_state="expanded",
)

DEFAULT_FILENAME = "Smartphone_Usage_Productivity_Dataset_50000.csv"


# ----------------------------------------------------------------------------
# DATA LOADING + CLEANING + FEATURE ENGINEERING  (mirrors Stress_Sleep.ipynb)
# ----------------------------------------------------------------------------
@st.cache_data(show_spinner="Loading and processing data...")
def load_and_process(file) -> pd.DataFrame:
    df = pd.read_csv(file)

    # normalize the index / id column if present
    if "User_ID" in df.columns:
        df = df.set_index("User_ID")

    # data cleaning
    df.columns = df.columns.str.lower().str.replace(" ", "_")
    df = df.drop_duplicates()

    required = {
        "age", "occupation", "daily_phone_hours", "sleep_hours", "stress_level",
        "work_productivity_score", "social_media_hours", "weekend_screen_time_hours",
    }
    missing = required - set(df.columns)
    if missing:
        raise ValueError(
            "This file doesn't look like the expected dataset. "
            f"Missing columns: {', '.join(sorted(missing))}"
        )

    # ---- feature engineering (identical logic to the notebook) -----------

    # phone usage - low, medium, high, very high
    df["phone_usage_category"] = pd.cut(
        df["daily_phone_hours"],
        bins=[0, 3, 6, 9, 24],
        labels=["Low", "Medium", "High", "Very High"],
    )

    # sleep health
    df["sleep_health"] = pd.cut(
        df["sleep_hours"],
        bins=[0, 6, 7, 8, 24],
        labels=["Low Sleep", "Adequate", "Healthy", "High Sleep"],
        include_lowest=True,
    )

    # age group
    df["age_group"] = pd.cut(
        df["age"],
        bins=[17, 24, 34, 44, 54, 60],
        labels=["18-24", "25-34", "35-44", "45-54", "55-60"],
    )

    # weekend behaviour - do people increase phone usage on weekends?
    df["weekend_change"] = df["weekend_screen_time_hours"] - df["daily_phone_hours"]
    df["weekend_behaviour"] = np.where(
        df["weekend_change"] > 0,
        "Higher on weekend",
        "Same or lower",
    )

    # social media usage
    df["social_media_category"] = pd.cut(
        df["social_media_hours"],
        bins=[0, 2, 4, 6, 24],
        labels=["Low", "Moderate", "High", "Very High"],
        include_lowest=True,
    )

    # productivity category
    df["productivity_level"] = pd.cut(
        df["work_productivity_score"],
        bins=[0, 4, 7, 10],
        labels=["Low", "Medium", "High"],
        include_lowest=True,
    )

    return df


@st.cache_data
def convert_df_to_csv(df: pd.DataFrame) -> bytes:
    return df.to_csv().encode("utf-8")


CAT_ORDER = {
    "phone_usage_category": ["Low", "Medium", "High", "Very High"],
    "social_media_category": ["Low", "Moderate", "High", "Very High"],
    "sleep_health": ["Low Sleep", "Adequate", "Healthy", "High Sleep"],
    "productivity_level": ["Low", "Medium", "High"],
    "age_group": ["18-24", "25-34", "35-44", "45-54", "55-60"],
}

COLOR_4 = {"Low": "#2ecc71", "Medium": "#f1c40f", "High": "#e67e22", "Very High": "#e74c3c"}
COLOR_SLEEP = {"Low Sleep": "#e74c3c", "Adequate": "#f1c40f", "Healthy": "#2ecc71", "High Sleep": "#3498db"}
COLOR_PROD = {"Low": "#e74c3c", "Medium": "#f1c40f", "High": "#2ecc71"}


# ----------------------------------------------------------------------------
# SIDEBAR — DATA SOURCE
# ----------------------------------------------------------------------------
st.sidebar.title("\U0001F4F1 Dashboard Controls")
st.sidebar.markdown("### Data source")

uploaded_file = st.sidebar.file_uploader(
    f"Upload dataset CSV (defaults to `{DEFAULT_FILENAME}` if present in the app folder)",
    type="csv",
)

data_source = uploaded_file
if data_source is None:
    import os
    if os.path.exists(DEFAULT_FILENAME):
        data_source = DEFAULT_FILENAME

if data_source is None:
    st.title("\U0001F4F1 Smartphone Usage & Productivity Dashboard")
    st.info(
        "\U0001F446 Upload the `Smartphone_Usage_Productivity_Dataset_50000.csv` file "
        "(or another dataset with the same columns) using the sidebar to get started."
    )
    st.markdown(
        """
        **Expected columns:** `age`, `gender`, `occupation`, `device_type`,
        `daily_phone_hours`, `social_media_hours`, `work_productivity_score`,
        `sleep_hours`, `stress_level`, `app_usage_count`, `caffeine_intake_cups`,
        `weekend_screen_time_hours`
        """
    )
    st.stop()

try:
    df_full = load_and_process(data_source)
except Exception as e:
    st.error(f"Couldn't load the file: {e}")
    st.stop()

# ----------------------------------------------------------------------------
# SIDEBAR — FILTERS
# ----------------------------------------------------------------------------
st.sidebar.markdown("### Filters")


def multiselect_filter(col_name, label):
    if col_name in df_full.columns:
        if col_name in CAT_ORDER:
            options = [o for o in CAT_ORDER[col_name] if o in df_full[col_name].dropna().unique().tolist()]
        else:
            options = sorted(df_full[col_name].dropna().unique().tolist())
        selected = st.sidebar.multiselect(label, options, default=options)
        return selected
    return None


gender_sel = multiselect_filter("gender", "Gender")
occupation_sel = multiselect_filter("occupation", "Occupation")
device_sel = multiselect_filter("device_type", "Device Type")
phone_cat_sel = multiselect_filter("phone_usage_category", "Phone Usage Level")
sleep_health_sel = multiselect_filter("sleep_health", "Sleep Health")

age_min, age_max = int(df_full["age"].min()), int(df_full["age"].max())
age_range = st.sidebar.slider("Age range", age_min, age_max, (age_min, age_max))

phone_hrs_min, phone_hrs_max = float(df_full["daily_phone_hours"].min()), float(df_full["daily_phone_hours"].max())
phone_range = st.sidebar.slider(
    "Daily phone hours", phone_hrs_min, phone_hrs_max, (phone_hrs_min, phone_hrs_max)
)

# apply filters
df = df_full.copy()
if gender_sel is not None:
    df = df[df["gender"].isin(gender_sel)]
if occupation_sel is not None:
    df = df[df["occupation"].isin(occupation_sel)]
if device_sel is not None:
    df = df[df["device_type"].isin(device_sel)]
if phone_cat_sel is not None:
    df = df[df["phone_usage_category"].isin(phone_cat_sel)]
if sleep_health_sel is not None:
    df = df[df["sleep_health"].isin(sleep_health_sel)]
df = df[(df["age"] >= age_range[0]) & (df["age"] <= age_range[1])]
df = df[(df["daily_phone_hours"] >= phone_range[0]) & (df["daily_phone_hours"] <= phone_range[1])]

st.sidebar.markdown("---")
st.sidebar.download_button(
    "\U0001F4E5 Download filtered data (CSV)",
    data=convert_df_to_csv(df),
    file_name="filtered_smartphone_data.csv",
    mime="text/csv",
)

if df.empty:
    st.warning("No rows match the current filters. Try widening your selection.")
    st.stop()

# ----------------------------------------------------------------------------
# HEADER + KPIs
# ----------------------------------------------------------------------------
st.title("\U0001F4F1 Smartphone Usage & Productivity Dashboard")
st.caption(f"Showing **{len(df):,}** of **{len(df_full):,}** users after filters")

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Avg. Daily Phone Use", f"{df['daily_phone_hours'].mean():.2f} hrs")
k2.metric("Avg. Productivity Score", f"{df['work_productivity_score'].mean():.1f}")
k3.metric("Avg. Sleep", f"{df['sleep_hours'].mean():.2f} hrs")
k4.metric("Avg. Stress Level", f"{df['stress_level'].mean():.1f}")
weekend_up_pct = (df["weekend_behaviour"] == "Higher on weekend").mean() * 100
k5.metric("Higher Use on Weekends", f"{weekend_up_pct:.1f}%")

st.markdown("---")

# ----------------------------------------------------------------------------
# TABS — mirror the notebook's analysis flow
# ----------------------------------------------------------------------------
(
    tab_overview,
    tab_phone,
    tab_sleep,
    tab_stress_prod,
    tab_social,
    tab_weekend,
    tab_corr,
    tab_explorer,
) = st.tabs(
    [
        "\U0001F4CA Overview",
        "\U0001F4F2 Phone Usage",
        "\U0001F634 Sleep",
        "\U0001F630 Stress & Productivity",
        "\U0001F4AC Social Media",
        "\U0001F4C5 Weekend Behaviour",
        "\U0001F517 Correlation",
        "\U0001F50D Data Explorer",
    ]
)

# ---- OVERVIEW -------------------------------------------------------------
with tab_overview:
    st.subheader("Dataset Snapshot")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Numeric summary**")
        st.dataframe(df.describe().T, use_container_width=True)
    with c2:
        st.markdown("**Age distribution**")
        fig = px.histogram(df, x="age", nbins=10, title="Age Distribution of Users")
        fig.update_layout(xaxis_title="Age", yaxis_title="Number of Users")
        st.plotly_chart(fig, use_container_width=True)

    c3, c4 = st.columns(2)
    with c3:
        st.markdown("**Distribution of users by occupation**")
        fig = px.pie(
            df["occupation"].value_counts().reset_index(),
            names="occupation", values="count",
            title="Distribution of Users by Occupation",
        )
        st.plotly_chart(fig, use_container_width=True)
    with c4:
        if "device_type" in df.columns:
            st.markdown("**Device distribution**")
            fig = px.bar(
                df["device_type"].value_counts().reset_index(),
                x="device_type", y="count", title="Device Distribution",
            )
            st.plotly_chart(fig, use_container_width=True)

# ---- PHONE USAGE ------------------------------------------------------------
with tab_phone:
    st.subheader("Smartphone Usage Patterns")

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Distribution of daily phone usage**")
        fig = px.histogram(
            df, x="daily_phone_hours", nbins=12,
            title="Distribution of Daily Phone Usage",
            labels={"daily_phone_hours": "Daily Phone Usage (Hours)"},
        )
        fig.update_layout(yaxis_title="Number of Users")
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        st.markdown("**Users by daily smartphone usage level**")
        counts = df["phone_usage_category"].value_counts().reindex(CAT_ORDER["phone_usage_category"]).reset_index()
        counts.columns = ["phone_usage_category", "count"]
        fig = px.bar(
            counts, x="phone_usage_category", y="count",
            color="phone_usage_category", color_discrete_map=COLOR_4,
            title="Users by Daily Smartphone Usage Level",
            labels={"phone_usage_category": "Phone Usage Level", "count": "Number of Users"},
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("**Daily phone usage by occupation**")
    fig = px.box(
        df, x="occupation", y="daily_phone_hours",
        title="Daily Phone Usage by Occupation",
        labels={"daily_phone_hours": "Daily Phone Usage (Hours)"},
    )
    st.plotly_chart(fig, use_container_width=True)

# ---- SLEEP -------------------------------------------------------------
with tab_sleep:
    st.subheader("Sleep Patterns & Wellbeing")

    st.markdown("**Sleep hours distribution**")
    fig = px.histogram(df, x="sleep_hours", nbins=15, title="Distribution of Sleep Hours")
    st.plotly_chart(fig, use_container_width=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Sleep health vs productivity**")
        fig = px.box(
            df, x="sleep_health", y="work_productivity_score",
            category_orders={"sleep_health": CAT_ORDER["sleep_health"]},
            color="sleep_health", color_discrete_map=COLOR_SLEEP,
            title="Productivity by Sleep Health",
            labels={"sleep_health": "Sleep Health", "work_productivity_score": "Productivity"},
        )
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        st.markdown("**Sleep health vs average stress**")
        sleep_stress = (
            df.groupby("sleep_health", observed=True)["stress_level"]
            .mean()
            .reindex(CAT_ORDER["sleep_health"])
            .reset_index()
        )
        fig = px.bar(
            sleep_stress, x="sleep_health", y="stress_level",
            color="sleep_health", color_discrete_map=COLOR_SLEEP,
            title="Average Stress Level by Sleep Health",
            labels={"sleep_health": "Sleep Health", "stress_level": "Avg. Stress Level"},
        )
        st.plotly_chart(fig, use_container_width=True)

# ---- STRESS & PRODUCTIVITY -------------------------------------------------
with tab_stress_prod:
    st.subheader("Stress, Phone Usage & Productivity")

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Productivity by stress level**")
        stress_prod = (
            df.groupby("stress_level")["work_productivity_score"]
            .mean()
            .reset_index()
        )
        fig = px.bar(
            stress_prod, x="stress_level", y="work_productivity_score",
            title="Average Productivity by Stress Level",
            labels={"stress_level": "Stress Level", "work_productivity_score": "Avg. Productivity"},
        )
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        st.markdown("**Phone usage vs productivity**")
        fig = px.box(
            df, x="phone_usage_category", y="work_productivity_score",
            category_orders={"phone_usage_category": CAT_ORDER["phone_usage_category"]},
            color="phone_usage_category", color_discrete_map=COLOR_4,
            title="Phone Usage vs Productivity",
            labels={"phone_usage_category": "Phone Usage", "work_productivity_score": "Productivity"},
        )
        st.plotly_chart(fig, use_container_width=True)

    st.info(
        "**Insight:** Medium phone users tend to show the lowest typical productivity, while "
        "Low and High/Very High users look similar at the median. There's no strong trend that "
        "higher phone usage alone lowers productivity — other factors (sleep, stress, occupation) "
        "likely play a bigger role."
    )

    st.markdown("**Productivity profile across smartphone usage levels**")
    table = (
        pd.crosstab(
            df["phone_usage_category"], df["productivity_level"], normalize="index"
        ) * 100
    ).reindex(CAT_ORDER["phone_usage_category"])[CAT_ORDER["productivity_level"]]
    fig = px.imshow(
        table, text_auto=".1f", color_continuous_scale="Blues",
        title="Productivity Profile Across Smartphone Usage Levels (% within row)",
        labels={"x": "Productivity Level", "y": "Phone Usage Level", "color": "% of users"},
    )
    st.plotly_chart(fig, use_container_width=True)

# ---- SOCIAL MEDIA -------------------------------------------------------
with tab_social:
    st.subheader("Social Media Usage vs Productivity")
    fig = px.box(
        df, x="social_media_category", y="work_productivity_score",
        category_orders={"social_media_category": CAT_ORDER["social_media_category"]},
        color="social_media_category", color_discrete_map=COLOR_4,
        title="Productivity Score Across Social Media Usage Levels",
        labels={"social_media_category": "Social Media Usage Level", "work_productivity_score": "Work Productivity Score"},
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("**Social media hours vs stress**")
    fig = px.scatter(
        df, x="social_media_hours", y="stress_level", opacity=0.35,
        labels={"social_media_hours": "Social Media Hours", "stress_level": "Stress Level"},
        title="Social Media vs Stress",
    )
    st.plotly_chart(fig, use_container_width=True)

# ---- WEEKEND BEHAVIOUR -------------------------------------------------------
with tab_weekend:
    st.subheader("Weekend vs Weekday Screen Time")
    st.caption(
        "`weekend_change` = weekend screen time \u2212 daily (weekday) phone hours. "
        "Positive values mean usage is higher on weekends."
    )

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Weekend change by occupation**")
        weekend_by_occ = df.groupby("occupation")["weekend_change"].mean().reset_index()
        fig = px.bar(
            weekend_by_occ, x="occupation", y="weekend_change",
            title="Average Weekend Change in Screen Time by Occupation",
            labels={"weekend_change": "Avg. Weekend Change (Hours)"},
        )
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        st.markdown("**Weekend behaviour distribution**")
        fig = px.pie(
            df, names="weekend_behaviour",
            title="Higher Usage on Weekends vs Same/Lower",
            color="weekend_behaviour",
            color_discrete_map={"Higher on weekend": "#e74c3c", "Same or lower": "#2ecc71"},
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("**Daily vs weekend screen time by occupation**")
    daily_vs_weekend = (
        df.groupby("occupation")[["daily_phone_hours", "weekend_screen_time_hours"]]
        .mean()
        .reset_index()
        .melt(id_vars="occupation", var_name="period", value_name="hours")
    )
    fig = px.bar(
        daily_vs_weekend, x="occupation", y="hours", color="period", barmode="group",
        title="Average Daily vs Weekend Screen Time by Occupation",
        labels={"hours": "Avg. Hours", "period": "Period"},
    )
    st.plotly_chart(fig, use_container_width=True)

# ---- CORRELATION -------------------------------------------------------------
with tab_corr:
    st.subheader("Correlation Analysis")
    numeric_df = df.select_dtypes(include=["int64", "float64"])
    corr = numeric_df.corr()
    fig = px.imshow(
        corr, text_auto=".2f", color_continuous_scale="RdBu_r", zmin=-1, zmax=1,
        title="Correlation Matrix",
    )
    fig.update_layout(height=600)
    st.plotly_chart(fig, use_container_width=True)
    st.info(
        "**Insight:** Sleep hours, daily phone usage, social media hours, and stress level show "
        "only weak pairwise correlation with each other and with productivity in this dataset — "
        "the boxplot and grouped-mean views above tend to reveal more structure (e.g. by category "
        "or occupation) than the raw linear correlations do."
    )

# ---- DATA EXPLORER ------------------------------------------------------------
with tab_explorer:
    st.subheader("Explore the filtered dataset")
    st.dataframe(df, use_container_width=True)
    st.caption(f"{len(df):,} rows \u00d7 {len(df.columns)} columns")
