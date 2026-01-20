import streamlit as st
import pandas as pd
import numpy as np

from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier

@st.cache_data
def load_data():
    iris = load_iris()
    df = pd.DataFrame(iris.data, columns=iris.feature_names)
    df['species'] = iris.target
    return df, iris.target_names

df, target_name=load_data()

model=RandomForestClassifier()
model.fit(df.iloc[:,:-1],df['species'])

st.sidebar.title("Input Features")
sepal_length = st.sidebar.slider(
    "Sepal length (cm)",
    float(df['sepal length (cm)'].min()),
    float(df['sepal length (cm)'].max()),
    key="sepal_length"
)

sepal_width = st.sidebar.slider(
    "Sepal width (cm)",
    float(df['sepal width (cm)'].min()),
    float(df['sepal width (cm)'].max()),
    key="sepal_width"
)

petal_length = st.sidebar.slider(
    "Petal length (cm)",
    float(df['petal length (cm)'].min()),
    float(df['petal length (cm)'].max()),
    key="petal_length"
)

petal_width = st.sidebar.slider(
    "Petal width (cm)",
    float(df['petal width (cm)'].min()),
    float(df['petal width (cm)'].max()),
    key="petal_width"
)

input_data = [[sepal_length, sepal_width, petal_length, petal_width]]

## Prediction
prediction = model.predict(input_data)
prediction_species = target_name[prediction[0]]