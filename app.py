
import pandas as pd
import numpy as np
import time
import seaborn as snb

import os
from dotenv import load_dotenv
load_dotenv()

import google.generativeai as genai
genai.configure(api_key=os.environ['GEMINI_API_TOKEN'])

model = genai.GenerativeModel('gemini-pro')

def get_insight(df:pd.DataFrame, x_label:str, y_label:str):
    prompt = f'''{np.array(df)} based on the provided array, your task is to analys it in term of business point of view, by considering x_lable={x_label} which is feature1, and y_label={y_label} which is number of sold product at that price, give me insight on it in following format: 1] <insight point>, give at least 4 point of analysis and next 2-3 points for solution'''
    result = model.generate_content(prompt)
    return result.text.replace("*","")


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

radio = st.sidebar.radio(
    "Select Working page",
    options=['Overall', 'Feature Analysis', 'Outlier Analysis']
)


dataset = st.radio("Select any of the dataset given", options=['mama earth sales', 'imports trades', 'exports trades'])
select_dataset = {
    "mama earth sales" : "./datasets/main_clean.csv",
    "imports trades" : "./datasets/imports.csv",
    "exports trades" : "./datasets/exports.csv"
}


df = pd.read_csv(select_dataset[dataset])
col1, col2 = st.columns(spec=2)
with col2:
    st.write("Describe Dataframe")
    st.dataframe(df.describe())
with col1:
    df_corr = df[df.describe().columns].corr()
    st.plotly_chart(px.density_heatmap(df_corr, title="Heatmap"))

feature = st.selectbox("Analysis is based on selected Columns", options=sorted(df.columns))

# Overall
if radio == "Overall":
    st.write("--"*100)

    st.header("Overall")
    series : pd.DataFrame = df[feature].value_counts().reset_index().sort_values(by=feature, ascending=True)

    col1, col2 = st.columns(spec=2)
    with st.spinner("Loading Please wait"):
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
        
        if st.button("Get Insights"):
                st.code(f'''
                x_label = {feature} y_label = Count\n{get_insight(series, feature, 'count')}''')

# feature wise
if radio == "Feature Analysis":
    st.header("Feature wise")
    columns_options = list(df.columns)
    # columns_options.remove(feature)

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
            current_feature_options = sorted(list(df[current_feature].unique()))
            if current_feature_options[0] != value:
                current_feature_options.insert(0, "Overall")

            with col:
                option = st.selectbox(f"{current_feature}", options=current_feature_options)
                options_dict[current_feature] = option
            
        g = df.copy()
        for compare in comparing_features:
            if options_dict[compare] == "Overall" : continue
            g = g[df[compare] == options_dict[compare]]
        
        # st.dataframe(g.reset_index(drop=True)[comparing_features])

    # Create Plot here
    if comparing_features:
        st.write("--"*100)
        st.header("Create plot here")
        columns_options2 = comparing_features.copy()
        for item in list(options_dict.keys()):
            if options_dict[item] == "Overall" : continue
            columns_options2.remove(item)

        selected = st.selectbox("Select from following", options=columns_options2, key=index)

        col1, col2 = st.columns(spec=2)
        with col1:
            st.write("Bar plot")
            st.plotly_chart(get_bar(g[selected].value_counts().reset_index()))
            
        with col2:
            # g count
            g_count = g[selected].value_counts().reset_index()
            st.write("Scatter plot")
            st.plotly_chart(px.scatter(g_count, x=g_count.columns[0], y='count'))

        if st.button("Get Insights"):
                with st.spinner("Loading Please wait"):
                    st.code(f'''x_label = {selected} y_label = Count\n{get_insight(g_count,selected,'count')}''')


if radio == 'Outlier Analysis':
    st.header("Outlier Analysis")
    g = df[feature].value_counts().reset_index()
    st.plotly_chart(px.scatter(g, x=feature, y='count'))