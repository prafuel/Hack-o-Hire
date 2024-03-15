
import pandas as pd
import numpy as np
import time


import plotly.express as px
def get_line(df: pd.DataFrame):
    col = df.columns
    figure = px.line(df, x = col[0], y=col[1])
    return figure

def get_histogram(df : pd.Series):
    figure = px.histogram(df)
    return figure

def get_bar(df: pd.DataFrame):
    col = df.columns
    figure = px.bar(df, x=col[0], y=col[1])
    return figure

def get_scatter(df):
    return px.scatter(df)

import streamlit as st
st.set_page_config(layout='wide')

st.title("Analysis of Anomaly in Various Datasets")
dataset = st.radio("Select any of the dataset given", options=['mama earth sales', 'imports trades', 'exports trades'])
select_dataset = {
    "mama earth sales" : "./datasets/main_clean.csv",
    "imports trades" : "./datasets/imports.csv",
    "exports trades" : "./datasets/exports.csv"
}


df = pd.read_csv(select_dataset[dataset])
st.dataframe(df.describe())

# Overall
feature = st.selectbox("Analysis is based on selected Columns", options=sorted(df.columns))
st.write("--"*100)

st.header("Overall")
series : pd.DataFrame = df[feature].value_counts().reset_index().sort_values(by=feature, ascending=True)

col1, col2 = st.columns(spec=2)
with st.spinner("Loading Please wait"):
    time.sleep(4)
    with col1:
        st.write("Histogram")
        # st.plotly_chart(get_histogram(series[feature]))
        st.plotly_chart(get_bar(series))

        st.write("Scatter plot")
        st.plotly_chart(px.scatter(x=series[feature], y=series['count']))

    with col2:
        st.write("Line plot")
        st.plotly_chart(get_line(series))

        st.dataframe(series.sort_values(by='count', ascending=False))

    st.write("--"*100)

# feature wise
st.header("Feature wise")
columns_options = list(df.columns)
columns_options.remove(feature)

col1, col2, col3 = st.columns(spec=3)
with col1:
    st.write(f"Feature name : {feature}")
with col2:
    st.write(f"DataType : {df[feature].dtype}")
with col3:
    st.write(f"Unique values : {df[feature].unique().__len__()}")

col1, col2 = st.columns(spec=2)
with col1:
    value_options = sorted(df[feature].unique())
    value_options.insert(0, "Overall")

    value = st.selectbox("Choose from following", options=value_options)
with col2:
    comparing_features = st.multiselect("Choose comparing features", options=columns_options)

st.write("--"*100)

# comparing feature
if comparing_features:  
    st.header("Comparing Features")

    if value != "Overall":
        df = df[df[feature] == value].copy()

    options_dict = {}

    for index,col in enumerate(st.columns(spec=comparing_features.__len__())):
        current_feature = comparing_features[index]
        current_feature_options = list(df[current_feature].unique())
        current_feature_options.insert(0, "Overall")

        with col:
            option = st.selectbox(f"{current_feature}", options=current_feature_options)
            options_dict[current_feature] = option

    g = df.copy()
    for compare in comparing_features:
        if options_dict[compare] == "Overall" : continue
        g = g[df[compare] == options_dict[compare]]

    # st.dataframe(g.reset_index(drop=True))

# Show Barplot
if comparing_features:
    st.write("--"*100)

    columns_options2 = comparing_features.copy()
    for item in list(options_dict.keys()):
        if options_dict[item] == "Overall" : continue
        columns_options2.remove(item)

    st.header("Show Barplot")
    col1, col2 = st.columns(spec=2)

    with col1:
        selected = st.selectbox("Select from following", options=columns_options2)
        st.plotly_chart(get_bar(g[selected].value_counts().reset_index()))
    with col2:
        st.dataframe(g[selected].value_counts().reset_index())
