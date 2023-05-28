'''
The libraries used for this project can be installed using the requirements.txt file
that contains the specific version.

if installing directly from the requirements.txt file does not work. Kindly install directly
from the terminal using pip. for example.

pip install dash==1.19.0

Libraries to be installed include the following.

dash==1.19.0
dash-bootstrap-components==0.11.3
dash-core-components==1.15.0
dash-html-components==1.1.2
Flask==1.1.2
MarkupSafe==1.1.1
Werkzeug==1.0.1
Jinja2==2.11.3
pandas==1.2.3
numpy==1.20.1


'''



import dash
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Output, Input
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import plotly.express as px
from dash.exceptions import PreventUpdate
#import matplotlib.pyplot as plt


app = dash.Dash(__name__ ,external_stylesheets=[dbc.themes.BOOTSTRAP]) 

df = pd.read_csv('./data/owid-covid-data.csv')
#df.head() 

#df.info() #this helps to give information about the various columns including the missing data amount and the data types in each column
df.isna().sum() # the isna() method checks for null data and the .sum() method aggregates the total amount of null data in each column
nan_columns=[i for i in df.columns if df[i].isna().sum() > 0 ]# using a list comprehension as an alternative to a conventional for loop helps shorten our code
len(nan_columns)# from the length of the columns returned we see that just 3 out of the columns contain complete data
complete_columns = df.columns[~df.columns.isin(nan_columns)] #this negates the result of the mask we passed to filter the three complete columns

'''
# for the purpose of this assessment since no machine learning 
# modelling is done with the dataset, 
# I will be dropping all the rows that have nan in some columns 
# while other columns nan value will be replaced by 0

'''

columns = df.columns.tolist() # this provides the list of columns in a list fomart allowing the possiblities of list methods to be applied
df['continent'].replace(np.nan,'not recorded', inplace = True) # the .replace() method takes in two compulsory parameters the item to be replaced and the item replacing,
#the inplace parameter overrided the default behaviour of most pandas method that do not act in place but instead return a new dataframe or series
df.continent.isna().sum() #verifying that the continent column no longer contains a row with missing data
#verifying that all the columns do not contain any null value.
df.isnull().sum()
mask =df['continent']=='not recorded' # creating a filter of only rows that have non-recorded as their continent value
df = df[~mask] # the ~ negates the result and provides us with only rows that do not have the non-recorded as their continent value
df.replace(np.nan, 0, inplace = True) #the other columns can be conviniently replaced with 0 and still be meaninggul.

#converting the date column type from object to datetime
df.date = pd.to_datetime(df.date,errors='coerce') 

df_cleaned = df


#creating a new dataset based on the df_cleaned data
#creating addtional columns to help with visualizations
df_cleaned['Year']=df_cleaned['date'].apply(lambda year: year.year)
df_cleaned['Month']=df_cleaned['date'].apply(lambda month: month.month)
df_cleaned['Day']=df_cleaned['date'].apply(lambda day: day.day)
#using the apply method which accepts a funtion that works on a series values 
# we attach an inline function using lambda to split the values into their respective datetime values

month_map = {1:'Jan',2:'Feb',3:'Mar',4:'Apr',5:'May',6:'Jun',7:'Jul',8:'Aug',9:'Sep',10:'Oct',11:'Nov',12:'Dec'} # dictionary for mapping months name to actual months in numbers

df_cleaned.Month = df.Month.map(month_map)

holder = df_cleaned.groupby(['Year','Month']).sum().reset_index() #grouping by year and month to create an aggregate dataframe.
                                                                    #the .reset_index creates a new index for the df.

merged_df = holder.merge(df_cleaned,how='outer') #merging the grouped data with the main data set based on months and date

merged_df = merged_df.dropna()

merged_df2 = merged_df 

merged_df_date = merged_df2

merged_df_date.loc[:,'date'] = merged_df2.date.astype(str) #setting the date column to a string type for easy mainpulation in some graphs.



df_continent = df.groupby('continent').sum().reset_index()
df_continent = df_continent
#idx = df_continent.index.to_list()
#df_continent = df_continent.reset_index(drop=True)
#df_continent['continent'] = idx

#df2= df_cleaned 
#col= ['iso_code', 'continent', 'date']
#for i in col:
    #del df2[i] # to remove all columns that are not of type int or float.


#Total death rates.
app.layout = html.Div([ #The app.layout method creates the layout pattern for the dash app.
    html.H1('World Covid_dataset'),
    html.H2('Source: Our World in Covid Data.'),
    #The dropdown method from the dash_core_component aids interactivity.
    #The line of code below iterates over the location column to enable selection of the individual countries.

    dcc.Dropdown(id='country_picker',
                    value = 'Portugal',
                    options=[{'label':country, 'value':country} 
                                for country in df_cleaned['location'].unique()]),
    dcc.Graph(id='country_chat'),

################################################# Trend of new cases discovered.
#BAR Chat layout
    html.Br(),
    html.H2('Trend of new cases occurence, side by side representation for selected Date and selected Country- Covid Dataset', style={'textAlign': 'center','color':'blue'}), #to see side by side layout you might have to minimize and mazzimise the screen.
    html.Br(),
    dbc.Row([
        dbc.Col([
            
            html.H2('Source: Our World in Covid Data.'),
            dcc.Dropdown(id='country_date_dropdown',                                       
                        value='2020-12-10',
                         options=[{'label': date, 'value': date}
                                  for date in merged_df['date'].drop_duplicates().sort_values()]), #the .drop_duplicates ensures only unique dates in the loop to be selected.
            html.Br(),
            dcc.Graph(id='countries_vax_barchart')
        ]),
        dbc.Col([
            dcc.Dropdown(id='country_vax_dropdown',
                         value='Nigeria',
                         options=[{'label': country, 'value': country}
                                  for country in merged_df_date['location'].unique()]),
            html.Br(),
            dcc.Graph(id='country_vax_barchart')
        ]),
    ]),


###################################
#continent
    html.Br(),
    dcc.Dropdown(id='continent_style',
                       value = 'female_smokers',
                        options = [{'label':continent, 'value':continent}
                        for continent in df_continent.columns]),
    dcc.Graph(id ='continent'),
######################333333

    html.P('The section below gives you the summary of the various columns for the specified country. Select your country, column and sumary info you seek.'),
     dcc.Dropdown(id='country_summary',
                    value='Nigeria',
                   options=[{'label':country, 'value':country} 
                                for country in df_cleaned['location'].unique()] ),
     dcc.Dropdown(id='column_picker',
                    value='new_cases',
                   options=[{'label':column, 'value':column} 
                                for column in df_cleaned.columns]),
      dcc.Dropdown(id='summary_picker',
                    value='sum',
                   options=[{'label':val, 'value':val} 
                                for val in ['sum','mean','min','max','median']]),
    html.Div(id='summary_report'),
    
#######################################################
   


 #####################################################

    dbc.Tabs([
       dbc.Tab([
           html.Ul([
               html.Br(),
               html.Li('Number of Countries: 170'),
               html.Li('Time Span: 2020-2022'),
               html.Li('Update Frequency: Daily'),
               html.Li('Last Data Point collected for this project: October 10, 2022'),
               html.Li([
                   'Source: ',
                   html.A('https://ourworldindata.org/coronavirus#coronavirus-country-profiles',
                          href='https://ourworldindata.org/coronavirus#coronavirus-country-profiles')
               ])
           ])

       ], label='Key Facts'),
        dbc.Tab([
            html.Ul([
                html.Br(),
                html.Li('Developer: Oluwaseun Boluro-Ajayi')
                
            ])
        ], label='Project Info')
    ]),

])

@app.callback(Output('continent','figure'), #the app.callback decorator links the function to the layout of the app.
                                             #it collects the paramemters from the layout and passes it on to the functions.   
                                             # the input represents the value that will be passed to the function while the ouput is the value that contains the return value from the function.    
                Input('continent_style','value'))
def display_continent(column):
    
    if column is None:
        raise PreventUpdate  #the preventupdate module acts as exception when there is no value initially passed onloading the page.
    fig = go.Figure()
    fig = px.scatter(data_frame = df_continent, x="continent", y=column)
    fig.layout.template = 'plotly_dark'
    return fig
    #fig.add_bar(x=df_continent['continent'], y=df_continent[continents])

#death timeline.
@app.callback(Output('country_chat','figure'),
                Input('country_picker','value'))
def display_death_timline(country):
    fig = go.Figure()
    country_data = df_cleaned[df_cleaned['location'] == country]
    #print(country_data.head(2))
   
    #fig.add_bar(x=country_data['date'],y=country_data['total_deaths'])
    fig = px.line(country_data, x="date", y="total_deaths", title=f'Death numbers across various timeframe for {country}')
    fig.layout.template = 'plotly_dark'
    return fig
 
 
 ############summary function
@app.callback(Output('summary_report','children'), #the app.callback decorator here contains multiple input an output values as required by the function 
               Input('country_summary','value'),
                Input('column_picker','value'),
                Input('summary_picker','value'))
def summary(country, column, val):
    selected_country = df[df['location'] == country]
    
    selected_column = selected_country[column]
    if val == 'sum':
        return f' This is the sum of {column} for {country}: {np.sum(selected_column)}'
    elif val == 'mean':
        return f' This is the mean value of {column} for {country}:{np.mean(selected_column)}'
    elif val == 'median':
        return f' This is the sum of {column} for {country}: {np.median(selected_column)}'
    elif val == 'min':
        return f' This is the sum of {column} for {country}:{np.min(selected_column)}'
    else:
        return f' This is the sum of {column} for {country}:{np.max(selected_column)}'

######################### side by side barchart function

@app.callback(Output('countries_vax_barchart','figure'),
               Input('country_date_dropdown','value') )
def year_vaccination_bar(year):
    if not year:
        raise PreventUpdate
    df_date = merged_df_date[merged_df_date['date']==year]
    num_countries = len(df['location'])
    fig = px.bar(df_date,
                x = 'new_cases',
                y='location',
                orientation='h',
        
                title= 'Trend of new cases in varioius countries as at' + ' '  + str(year))
    fig.layout.template = 'plotly_dark'
    return fig
############
@app.callback(Output('country_vax_barchart','figure'),
                Input('country_vax_dropdown','value'))
def country_vaccination_bar(country):
    if not country:
        raise PreventUpdate
    country_data = merged_df_date[merged_df_date['location'] == country]
    fig = px.bar(country_data,
                    x= 'date',
                    y='new_cases',
                    title=f'Trend of new cases in {country} on various dates')
    fig.layout.template = 'plotly_dark'
    return fig
    
if __name__ == '__main__':
    app.run_server(debug=True,port=8150)