import streamlit as st
import pandas as pd

st.title("Streamlit Text Input")

name=st.text_input("Enter your name:")

age=st.slider("Select your age:", 0, 100,25)

st.write("Your age is:", age)

options = ["Python", "Java", "C++", "Javascript"]
choice = st.selectbox("Choose your favorite Language:", options)
st.write("You selected {choice} as your favorite language.".format(choice=choice))

if name:
    st.write(f"Hello, {name}!")


data = {
    "Name" : ["John", "Anna", "Peter", "Linda"],
    "Age" : [28, 24, 35,40],
    "City" : ["New York", "Paris", "Berlin", "London"]
}

df = pd.DataFrame(data)
df.to_csv("sample_data.csv")
st.write(df)

uploaded_file=st.file_uploader("Choose a CSV file",type="csv")
if uploaded_file is not None:
    df=pd.read_csv(uploaded_file)
    st.write(df)