################################################################################
#   Imports
################################################################################

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import json

################################################################################
#   Variables
################################################################################

DATA_URL = (
    'wine_reviews.parq'
)
COUNTRY_FILE = 'contries.csv'
DICT_FILTER_LABEL = {
    'Variety': 'variety',
    'Country': 'country',
    # 'Designation':'designation'
}
INVALID_CHOICE = 'Select One'
INVALID_TEXT = ''
MAXIMUM_ELEMENTS_IN_CHART = 10
RECOMMENDED_TITLES_FILE = 'titles_recommended.parq'

################################################################################
#   Text functions
################################################################################

def text_normalization(text):
    return str(text).lower()

def search_possible_values(df, variable, text_searched, text_separator=' '):
    key_words_searched = text_searched.split(text_separator)
    possible_values = []
    for i in df[variable]:
        add_item = True
        for key_word in key_words_searched:
            if text_normalization(key_word) not in text_normalization(i):
                add_item = False
        if add_item:
            possible_values.append(i)
    return possible_values


################################################################################
#   Loading functions
################################################################################

# Loading and persisting data
@st.cache(persist=True)
def load_data():

    def valid_description(x):
        # Some descriptions are only 'Imported by Someone', thouse descriptions are invalid
        if 'imported by' in x.lower():
            return False
        # Short descriptions are also cutted of the recommended section
        elif len(x)<50:
            return False
        else:
            return True
    df_data = pd.read_parquet(DATA_URL).drop_duplicates()

    # Format reviews
    df_data['description']=df_data['description'].apply(
        lambda x: x if valid_description(x) else ''
    )
    # load file with the title and 3 recommended titles
    df_recommendation = pd.read_parquet(RECOMMENDED_TITLES_FILE)

    return df_data, df_recommendation

# Filtering data
def filtering_data(df_data, column, filter, title_searched):
    df_filtered = df_data.copy()
    if filter != INVALID_CHOICE:
        mask = (df_filtered[column]==filter)
        df_filtered = df_filtered[mask]
    if title_searched != INVALID_TEXT:
        possible_values = search_possible_values(
            df_filtered,
            'title',
            title_searched,
        )
        mask = (df_filtered['title'].isin(possible_values))
        df_filtered = df_filtered[mask]

    return df_filtered
################################################################################
#   Useful functions
################################################################################
def filtered_info(df):
    '''
    It plots some General info about a filtered data.

    Parameters:
        df :Filtered DataFrame.
    '''
    st.header('General info')
    # Number of wines
    number_of_wines = len(df)
    text = 'We found **{}** wine{}.'.format(
        number_of_wines,
        's' if number_of_wines>0 else ''
    )
    # Price
    prices = df.price.dropna()
    if len(prices) > 0:
        mean_price = np.average(prices)
        text += ' The average price is **{:.2f}** USD.'.format(mean_price)
    # Rate
    rates = df.points.dropna()
    if len(rates) > 0:
        mean_rate = np.average(rates)
        text += ' The average rate of especialists is **{:.1f}** in a 0-100 scale.'.format(mean_rate)
    # Writing
    st.markdown(text)

def write_statistics(subheader, dict_wine, list_of_plots):
    '''
    Given an especific wine. We plot a subheader and the Parameters of the Wine

    Parameters:
        subheader(str) :text of the subheader.
        dict_wine(dict) :dict with the wine informations.
        list_of_plots(list): list of dict, where each dictionary has the text
            and the variable key

    '''
    st.write('**{}:**'.format(subheader))
    for dict_plots in list_of_plots:
        text = dict_plots['text']
        variable = dict_plots['variable']
        variable_value = dict_wine.get(variable)
        if (variable_value is not None) and (variable_value==variable_value):
            print_text = "* {}: {}".format(text, dict_wine[variable])
            if 'adicional_text' in dict_plots.keys():
                print_text += dict_plots['adicional_text']
            st.markdown(print_text)

def show_statistics(df, variable, text, header_text):
    # Find the best and the worst wines in one especific variable
    higher = df.loc[df[variable].idxmax()].to_dict()
    lower = df.loc[df[variable].idxmin()].to_dict()
    list_of_plots = [
        {'text': 'Title', 'variable': 'title'},
        {'text': 'Rate', 'variable': 'points'},
        {'text': 'Designation', 'variable': 'designation'},
        {'text': 'Price', 'variable': 'price', 'adicional_text': ' USD'},
        {'text': 'Review', 'variable': 'description'},
    ]
    st.subheader(header_text)
    write_statistics("Higher ", higher, list_of_plots)
    write_statistics("Lower ", lower, list_of_plots)

def plot_pie_chart(df, column, title):
    # No null values alowed to plot
    df_temp = df.copy(deep=True)
    df_temp = df_temp[~df_temp[column].isnull()]
    # Filtering the values with lower percentage and ploting them as other
    if len(df_temp[column].unique()) > MAXIMUM_ELEMENTS_IN_CHART:
        list_of_others = list(
            df_temp[column].value_counts().index[MAXIMUM_ELEMENTS_IN_CHART-1:]
        )
        df_temp.loc[(df_temp[column].isin(list_of_others), column)] = 'Others'

    fig = px.pie(
        df_temp,
        names=column,
        title=title
        )
    st.write(fig)

def sidebarfilters(df):
    '''
    Create the sidebar filter

    Parameters:
        df: All data
    Returns:
        label(str): the filter that user wants to use
        filter(str): the value that user wants to filter
        filtered_column(str): the column value that user wants to filter
    '''
    # Sidebar filters

    # Find out which filter the user wants to use
    label_options = [INVALID_CHOICE] + sorted(list(DICT_FILTER_LABEL.keys()))
    label = st.sidebar.selectbox('Filter by:', label_options)

    # find out the value wanted by the user
    if label != INVALID_CHOICE:
        filtered_column = DICT_FILTER_LABEL[label]
        filter_list = [INVALID_CHOICE] + sorted(
            df[filtered_column]
                .dropna()
                .unique()
            )
        filter = st.sidebar.selectbox(label, filter_list)
    else:
        filter = INVALID_CHOICE
        filtered_column = 'title'
    return label, filter, filtered_column

def see_all_wines_filtered(df_filtered):
    """
    Plots the dataframe with the df_filtered

    Parameters:
        df_filtered: Data filtered (Dataframe)
    """
    df_temp = df_filtered[['title', 'price','points']].fillna('').copy(deep=True).rename(
        {
            'price': 'Price',
            'title': 'Title',
            'points': 'Rate'
        },
        axis=1
    ).sort_values('Title').reset_index(drop=True)
    st.dataframe(df_temp)

################################################################################
#   Countries
################################################################################
def load_countries_files():
    df_countries = pd.read_csv(
        COUNTRY_FILE,
        sep=';'
    )
    df_countries = df_countries[['name','latitude','longitude']]
    return df_countries

def plot_contry_map(df_filtered):
    number_of_variables = len(df_filtered.country.unique())
    # Only plots with there is more than one value to plot
    if number_of_variables>1:
        if  st.button('Open map'):
            st.map(df_filtered[["latitude", "longitude"]].dropna(how="any"))

def all_country_plots(df_filtered):
    plot_pie_chart(df_filtered, 'country',
    "Countries who produces the selected wines")

    # Merge country locations
    df_countries = load_countries_files()
    df_filtered = df_filtered.merge(
        df_countries,
        left_on='country',
        right_on='name',
        how='inner'
    )

    plot_contry_map(df_filtered)


def recommended_options(df_data, df_recommendation):
    MAX_POSSIBILITES = 50

    posible_titles = df_filtered.title.tolist()
    if len(posible_titles)>MAX_POSSIBILITES:
        posible_titles = posible_titles[:MAX_POSSIBILITES]
    # show only titles with recommendations
    posible_titles = [ i for i in posible_titles
        if i in df_recommendation.title.tolist()
    ]

    # If there is options
    if len(posible_titles)>0:
        posible_titles = [INVALID_CHOICE] + sorted(posible_titles)

        st.header('Recommendations:')
        chosen_title = st.selectbox("View recommendations of:", posible_titles)

        # If the user choose one title
        if chosen_title !=  INVALID_CHOICE:

            # Plot title chose infos
            list_of_plots = [
                {'text': 'Rate', 'variable': 'points'},
                {'text': 'Designation', 'variable': 'designation'},
                {'text': 'Price', 'variable': 'price', 'adicional_text': ' USD'},
                {'text': 'Review', 'variable': 'description'},
            ]
            item = df_filtered[df_filtered['title']==chosen_title].to_dict('records')[0]
            write_statistics("You chose: {}".format(chosen_title), item, list_of_plots)

            # Recommendations info
            st.subheader('We recommend:')
            recommended_titles = df_recommendation.loc[df_recommendation.title==chosen_title,'recommended'].tolist()
            df_titles_recommended = df_data[df_data.title.isin(recommended_titles)]
            for item in df_titles_recommended.to_dict('records'):
                write_statistics("{}".format(item['title']), item, list_of_plots)

################################################################################
#   Pipeline
################################################################################

# Title
st.sidebar.title('Filters:')

# Loading the data
df_data, df_recommendation = load_data()

title_searched = st.sidebar.text_input('Wine:')
title_searched = title_searched.strip()

# Mount the sidebar filter
label, filter, filtered_column = sidebarfilters(df_data)

valid_filter = (filter != INVALID_CHOICE)
valid_title = (title_searched != INVALID_TEXT)

if valid_filter or valid_title:

    st.title('WINE REVIEW')
    df_filtered = filtering_data(
        df_data,
        filtered_column,
        filter,
        title_searched
    )
    filtered_info(df_filtered)

    # Only show infos if we have wines filtered
    if len(df_filtered) > 0:

        if  st.button("See all wines' titles (filtered)"):
            see_all_wines_filtered(df_filtered)

        recommended_options(df_data, df_recommendation)

        st.header('Other informations')
        show_statistics(df_filtered, 'points', 'rate', "Wine Enthusiasts' rating")
        show_statistics(df_filtered, 'price', 'price', 'Prices')

        if label != 'Variety':
            st.header('Variety informations')
            plot_pie_chart(df_filtered, 'variety',
            "Variety distribution for the seleted wines")
        if label != 'Country':
            st.header('Country informations')
            all_country_plots(df_filtered)


################################################################################
#   Noot used (yet) functions
################################################################################
