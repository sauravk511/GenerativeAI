from datetime import datetime
import streamlit as st
import altair as alt
import vega_datasets

full_df = vega_datasets.data("seattle_weather")

st.set_page_config(
    #Title and Icon of the browsers tab bar: 
    page_title="Seattle Weather",
    page_icon="🌧️",
    #Make the content take up thw width of the page:
    # layout="wide",
)

"""
## Seattle Weather

Lets explore the [ classic Seattle weather 
dataset](https://altair-viz.github.io/case_studies/exploring-weather.html)
"""

"" # Add a little vertical space. Same as st.write("").
""

"""
## 2015 Summary
"""

""

df_2015 = full_df[full_df["date"].dt.year == 2015]
df_2014 = full_df[full_df["date"].dt.year == 2014]

max_temp_2015 = df_2015["temp_max"].max()
max_temp_2014 = df_2014["temp_max"].max()

min_temp_2015 = df_2015["temp_min"].min()
min_temp_2014 = df_2014["temp_min"].min()

max_wind_2015 = df_2015["wind"].max()
max_wind_2014 = df_2014["wind"].max()

min_wind_2015 = df_2015["wind"].min()
min_wind_2014 = df_2014["wind"].min()

max_prec_2015 = df_2015["precipitation"].max()
max_prec_2014 = df_2014["precipitation"].max()  

min_prec_2015 = df_2015["precipitation"].min()
min_prec_2014 = df_2014["precipitation"].min()

with st.container(horizontal=True, gap="medium"):
    cols = st.columns(2, gap="medium", width=300)

    with cols[0]:
        st.metric(
            "Max Temperature",
            f"{max_temp_2015:0.1f}C",
            delta=f"{max_temp_2015 - max_temp_2014:0.1f}C",
            width="content",
        )
    
    with cols[1]:
        st.metric(
            "Min Temperature",
            f"{min_temp_2015:0.1f}C",
            delta=f"{min_temp_2015 - min_temp_2014:0.1f}C",
            width="content"
        )
    cols = st.columns(2, gap="medium", width=300)

    with cols[0]:
        st.metric(
            "Max precipitation",
            f"{max_prec_2015:0.1f}C",
            delta=f"{max_prec_2015 - max_prec_2014:0.1f}C",
            width="content",
        )

    with cols[1]:
        st.metric(
            "Min precipitation",
            f"{min_prec_2015:0.1f}C",
            delta=f"{min_prec_2015 - min_prec_2014:0.1f}C",
            width="content"
        )

    cols = st.columns(2, gap="medium", width=300)

    with cols[0]:
        st.metric(
            "Max wind",
            f"{max_wind_2015:0.1f}m/s",
            delta=f"{max_wind_2015 - max_wind_2014:0.1f}m/s",
            width="content"
        )

    with cols[1]:
        st.metric(
            "Min wind",
            f"{min_wind_2015:0.1f}m/s",
            delta=f"{min_wind_2015 - min_wind_2014:0.1f}m/s",
            width="content"
        )

    cols = st.columns(2, gap="medium", width=300)

    weather_icons = {
        "sun": "☀️",
        "snow": "❄️",
        "rain": "🌧️",
        "fog": "🌫️ ",
        "drizzle": "🌦️",
    }

    with cols[1]:
        weather_name = (
            full_df["weather"].value_counts().head(1).reset_index()["weather"][0]
        )
        st.metric(
            "Most common weather",
            f"{weather_icons[weather_name]} {weather_name.upper()}",
        )

    with cols[1]:
        weather_name = (
            full_df["weather"].value_counts().tail(1).reset_index()["weather"][0]
        )
        st.metric(
            "Least common weather",
            f"{weather_icons[weather_name]} {weather_name.upper()}",  
        )
"""
## Compare different years
"""

YEARS = full_df["date"].dt.year.unique()
selected_years = st.pills(
    "Select years",
    options="years",
    selection_mode="multi"
)


if not selected_years:
    st.warning("You must select at least one year.", icon=":material/warning:")

df = full_df[full_df["date"].dt.year.isin(selected_years)]

cols = st.columns([3, 1])
with cols[0].container(border=True, height="stretch"):
    "### Temperature"

    st.altair_chart(
    alt.Chart(df)
    .mark_bar(width=3)
    .encode(
        x=alt.X("date:T", timeUnit="monthdate", title="Date"),
        y=alt.Y("temp_min:Q", title="Temperature (°C)"),
        y2="temp_max:Q",
        color=alt.Color("date:T", timeUnit="year", title="Year"),
        xOffset=alt.XOffset("date:T", timeUnit="year"),
    )
    .configure_legend(orient="bottom"),
    use_container_width=True
)


with cols[1].container(border=True, height="stretch"):
    "### Weather type distribution"

    st.altair_chart(
        alt.Chart(df)
        .mark_bar()
        .encode(
            alt.Theta("count()"),
            alt.Color("weather:N"),
        )
        .configure_legend(orient="bottom")
    )

    cols = st.columns(2)

    with cols[0].container(border=True, height="stretch"):
        st.altair_chart(
            alt.Chart(df)
            .transform_window(
                avg_wind="mean(wind)",
                std_wind="stdev(wind)",
                frame=[-14, 0],   # last 14 days rolling window (better logic)
            )
            .mark_line(size=1)
            .encode(
                x=alt.X("date:T", timeUnit="monthdate", title="Date"),
                y=alt.Y("avg_wind:Q", title="Average wind (past 2 weeks, m/s)"),
                color=alt.Color("date:T", timeUnit="year", title="Year"),
            )
            .configure_legend(orient="bottom"),
            use_container_width=True
        )


    with cols[1].container(border=True, height="stretch"):
        "### Precipitation over time"
        st.altair_chart(
            alt.Chart(df)
            .mark_line(size=1)
            .encode(
                alt.X("date", timeUnit="monthdate").title("date"),
                alt.Y("precipitation:Q").title("precipitation (mm)"),
                alt.Color("date:N", timeUnit="year").title("year"),
            )
            .configure_legend(orient="bottom")
        )
    cols = st.columns(2)

    with cols[0].container(border=True, height="stretch"):
        "### Montly weather breakdown"
        ""

        st.altair_chart(
    alt.Chart(df)
    .mark_bar()
    .encode(
        x=alt.X("month(date):O", title="Month"),
        y=alt.Y("count():Q", title="Days").stack("normalize"),
        color=alt.Color("weather:N", title="Weather"),
    )
    .configure_legend(orient="bottom"),
    use_container_width=True
)

with cols[1].container(border=True, height="stretch"):
    st.markdown("### Raw Data")
    st.dataframe(df)
