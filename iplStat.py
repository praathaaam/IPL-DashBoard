import dash
#import dash_core_components as dcc
from dash import dcc
#import dash_html_components as html
from dash import html
import pandas as pd
from dash.dependencies import Input, Output
import plotly.express as px

app = dash.Dash(__name__) #initalize dash app
server = app.server #this line will only be used by Heroku server and not used on local
app.title = "IPL Dashboard" #Assigning title to be displayed on tab

#Reading the dataset
df = pd.read_excel("IPL Ball-by-Ball 2008-2020.xlsx")

#cleaning the data
team_names = {
                "Sunrisers Hyderabad":"Deccan Chargers",
                "Rising Pune Supergiant": "Rising Pune Supergiants",
                "Delhi Capitals": "Delhi Daredevils"
             }
df["batting_team"] = df["batting_team"].replace(team_names)
df["bowling_team"] = df["bowling_team"].replace(team_names)


#function which will render bar graph for run scored by player
def get_total_runs(player):
    global df
    bat_df = df.groupby(["bowling_team", "batsman"])["batsman_runs"].sum().reset_index().copy()
    bat_df = bat_df[bat_df["batsman"]==player]
    bat_df = bat_df[bat_df["batsman_runs"]>0]

    fig = px.bar(bat_df, x="bowling_team", y="batsman_runs", color="batsman_runs",
             labels={'bowling_team':'Teams', 'batsman_runs':'Runs Scored'}, height=400, width = 500,
                title="Runs Scored by " + player + " against all teams", template='plotly_dark')
    fig.update_layout({'paper_bgcolor': '#282828', 'plot_bgcolor':'#282828'})
    return fig

#function which will render bar graph for wickets by player
def get_total_wickets(player):
    global df
    bol_df = df[~df["dismissal_kind"].isin(["retired hurt", "run out", "obstructing the field"])].copy()
    bol_df = bol_df.groupby(["batting_team", "bowler"])['is_wicket'].sum().reset_index().copy()
    bol_df = bol_df[bol_df["bowler"]==player]
    bol_df = bol_df[bol_df['is_wicket']>0]
                    
    fig = px.pie(bol_df, values='is_wicket', names='batting_team', labels={'batting_team':'Teams', 'is_wicket':'Wickets_taken'}, height=400, width = 500,
                title="Wickets taken by " + player + " against all teams", template='plotly_dark')
    fig.update_layout({'paper_bgcolor': '#282828', 'plot_bgcolor':'#282828'})
    fig.update_traces(textinfo='value')
    return fig

#creating css for main div 
main_div_style = {"background-color": "#181818", 
                    "padding":"0", 
                    "width":"100%", 
                    "height":"100", 
                    "position": "fixed",
                    "top": "0%",
                    "left": "0",
                    "bottom": "0",
                }

#creating options for dropdown display
options = [{"label":i, "value":i} for i in df["batsman"].unique()] 

#creating dropdown section
dropdown_box = html.Div(children = [
            dcc.Dropdown(
                    id='player_name',              #unique identifier for this element
                    options=options,               #list of players
                    clearable=False,               #this feature helps in not sending an empty value
                    value = "V Kohli",             #setting a default vali
                    placeholder="Select a player", #not really required but just for fun
             )
            ],
            style = {'width': '90%', "position": "fixed", "left": "5%",
                     'display': 'inline-block', "top": "1%", "z-index":"1"}
)

#creating graphs section
Graphs = html.Div(children = [html.Div(children = [
                            dcc.Graph(id = "runsScored")       #graph only requireds unique id in our case
                                    ],
                            style = {'width': '45%', "position": "fixed", "left": "2%",
                                     'display': 'inline-block', "background-color": "#282828",
                                     "top": "10%",
                                    }
                                    ),

                        html.Div(children = [
                                dcc.Graph(id = "wicketsTaken") #graph only requireds unique id in our case
                                ],
                        style = {'width': '45%', "position": "fixed", "left": "53%",
                                 'display': 'inline-block', "background-color": "#282828",
                                 "top": "10%"
                                })
                        ]
)

#adding the layout to the dash app
app.layout = html.Div(id = "main_div", children =[dropdown_box, Graphs],
                      style = main_div_style)

@app.callback([Output(component_id = "runsScored", component_property = "figure"),
               Output(component_id = "wicketsTaken", component_property = "figure")],
               [Input(component_id = "player_name", component_property = "value")]
             )
def the_callback_function(player_name):
    fig1 = get_total_runs(player_name)
    fig2 = get_total_wickets(player_name)
    return fig1, fig2

if __name__ == "__main__":
    app.run_server(debug=False, port = 8080)