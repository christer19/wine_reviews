################################################################################
#   Imports
################################################################################

import streamlit as st
import pandas as pd
import numpy as np
# import plotly.express as px

################################################################################
#   Variables
################################################################################

DATA_URL = (
    'wine_reviews.parq'
)
DICT_FILTER_LABEL = {
    'Variety': 'variety'
}

################################################################################
#   Loading functions
################################################################################

# Loading and persisting data
@st.cache(persist=True)
def load_data():
    df_data = pd.read_parquet(DATA_URL)
    return df_data
# Filtering data
def filtering_data(df_data, column, filter):

    if not isinstance(filter, list):
        filter = [filter]

    mask = (df_data[column].isin(filter))
    df_filtered = df_data[mask]

    return df_filtered
################################################################################
#   Useful functions
################################################################################
def write_statistics(subheader, dict_wine, list_of_plots):
    st.subheader(subheader)
    for dict_plots in list_of_plots:
        text = dict_plots['text']
        variable = dict_plots['variable']
        variable_value = dict_wine.get(variable)
        if variable_value is not None:
            print_text = "**{}**: {}".format(text, dict_wine[variable])
            if 'adicional_text' in dict_plots.keys():
                print_text += dict_plots['adicional_text']
            st.write(print_text)

def show_statistics(df, variable, text, header_text):
    # st.write('The number of points WineEnthusiast rated the wine on a scale of
    # 1-100 (though they say they only post reviews for')
    # Find the best and the worst wines
    higher = df.loc[df[variable].idxmax()].to_dict()
    lower = df.loc[df[variable].idxmin()].to_dict()
    list_of_plots = [
        {'text': 'Title', 'variable': 'title'},
        {'text': 'Rate', 'variable': 'points'},
        {'text': 'Designation', 'variable': 'designation'},
        {'text': 'Price', 'variable': 'price', 'adicional_text': ' USD'}
    ]
    st.header(header_text)
    write_statistics("Higher ".format(text), higher, list_of_plots)
    write_statistics("Lower ".format(text), lower, list_of_plots)


################################################################################
#   Pipeline
################################################################################

st.sidebar.title('Wine reviews:')
df_data = load_data()
label = 'Variety'
filter_column = DICT_FILTER_LABEL[label]
filter_list = ['Select One'] + sorted(
    df_data[filter_column]
        .dropna()
        .unique()
    )
filter = st.sidebar.selectbox(label, filter_list, )

if filter != 'Select One':
    st.write('You selected:', filter)
    df_filtered = filtering_data(df_data, filter_column, filter)
    st.write(df_filtered.head())
    show_statistics(df_filtered, 'points', 'rate', "WineEnthusiasts' rating")
    show_statistics(df_filtered, 'price', 'price', 'Prices')

################################################################################
#   Noot used (yet) functions
################################################################################
def text_normalization(text):
    return str(text).lower()

def search_possible_values(df_data, variable, text_searched,text_separator=' '):
    key_words_searched = text_searched.split(text_separator)
    possible_values = []
    for i in df_data[variable]:
        add_item = True
        for key_word in key_words_searched:
            if text_normalization(key_word) not in text_normalization(i):
                add_item = False
        if add_item:
            possible_values.append(i)
    return possible_values
