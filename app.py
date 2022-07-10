import dash, os
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd

fitbit = 'fitbit_export_20220704.csv'
folder = r'data'

def fitbit_parser(csv_name):
    
    #read in csv
    df = pd.read_csv(csv_name, skiprows=1)
    #subset using masks
    mask = df['Date'].str.contains(':')
    sleep = df[mask]
    activity = df[~mask]
    #format df
    header = activity.iloc[-1].tolist()
    sleep.columns = header
    sleep = sleep.drop(sleep.columns[-1], axis=1)

    return sleep, activity

def loseit_parser(folder_name):
    
    filelist = [file for file in os.listdir(folder_name) if file.startswith('W')]
    
    database = {}
    for file in filelist:
        database[file] = pd.read_csv(r'data/'+file)
        
    food = pd.concat(database, axis=0).reset_index(level=0)
    
    return food

def sleep_date_time(df):
    df['Start Time'] = pd.to_datetime( df['Start Time'])
    df['End Time'] = pd.to_datetime( df['End Time'])
    df.sort_values(by='End Time', inplace=True)
    df['DayOfWeek'] = df['End Time'].dt.day_name()
    
    return df

def food_date_time(df):
    food['Date'] = pd.to_datetime(food['Date'])
    food.sort_values(by='Date', inplace=True)
    df['DayOfWeek'] = df['Date'].dt.day_name()
    df = df.drop(df.columns[0], axis=1)
    
    return df

activity = fitbit_parser(fitbit)[1]
sleep = fitbit_parser(fitbit)[0]
food = loseit_parser(folder)

sleep = sleep_date_time(sleep)
food = food_date_time(food)

food = food.set_index('Date')
food_weekly = food.resample('W').sum()
food_weekly.reset_index(inplace=True)

app = dash.Dash(__name__)

app.layout = html.Div(
    children=[
        html.H1(children="Avocado Analytics",),
        html.P(
            children="Analyze the behavior of avocado prices"
            " and the number of avocados sold in the US"
            " between 2015 and 2018",
        ),
        dcc.Graph(
            figure={
                "data": [
                    {
                        "x": food_weekly["Date"],
                        "y": food_weekly["Fat (g)"],
                        "type": "lines",
                    },
                ],
                "layout": {"title": "Average Price of Avocados"},
            },
        ),
        dcc.Graph(
            figure={
                "data": [
                    {
                        "x": food_weekly["Date"],
                        "y": food_weekly["Protein (g)"],
                        "type": "lines",
                    },
                ],
                "layout": {"title": "Avocados Sold"},
            },
        ),
    ]
)

if __name__ == "__main__":
    app.run_server(debug=True)