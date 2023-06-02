from dash import Dash, dcc, html, Input, Output, dash_table
import pandas as pd
import dash_bootstrap_components as dbc



long_req = pd.read_csv("./data/long_list_raw.csv")
subjects = long_req["Code"].str.split("_").str.get(0).unique()
ms_seasons = ['Fall_2020', 'Spring_2021', 'Fall_2021']
phd_seasons = ['Spring_2022', 'Fall_2022', 'Spring_2023', 'Fall_2023']

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# the style arguments for the sidebar. We use position:fixed and a fixed width
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "14rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
}

CONTENT_STYLE = {
    "margin-left": "16rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}

control_div = html.Div([
    html.H5("Program:"),
    dbc.Checklist(["MS", "PhD"], value = ["PhD"], inline=False, id="in-program-cb"),
    html.H5("Courses:"),
    dbc.Checklist(["required", "electives"], value = ["required", "electives"], inline=False, id="in-courses-cb"),
    html.H5("Subjects:"),
    dbc.Checklist(subjects, value = subjects, inline=False, id="in-subj-cb"),
    html.H5("Include In-Progress"),
    dcc.Checklist(["Yes"], value = ["Yes"], id="ip-cb")
],
style=SIDEBAR_STYLE
)

table =  html.Div([
        html.H1("Course Progress"),
        html.A("PhD Program Requirement", href = "https://www.bgsu.edu/graduate/catalogs-and-policies/graduate-catalog/data-science.html"),
        html.H3("", id="out-stat"),
    dash_table.DataTable(
        data = [{"1":1, "2":2}, {"1":2, "2":2}],
        style_data={
                'whiteSpace': 'normal',
                'height': 'auto',
        },
        fill_width=False,
        style_header={
            'backgroundColor': 'blue',
            'color': 'white',
            'fontWeight': 'bold'
        },
        style_data_conditional=[
            {
                'if': {'row_index': 'odd'},
                'backgroundColor': 'rgb(245, 245, 245)',
            }
        ],
        id = 'data-table',
)],
style=CONTENT_STYLE)


app.layout = html.Div([
    html.Div([
        control_div,
        table
    ])
])


def select_courses(progr_cb, type_cb, subj = subjects, ip_cb="Yes"):
    dff = long_req[~long_req["grade"].isna()]
    dff = dff[(long_req["type"].isin(type_cb))]
    if(not "MS" in progr_cb):
        dff = dff[~dff["season"].isin(ms_seasons)]
    if(not "PhD" in progr_cb):
        dff = dff[~dff["season"].isin(phd_seasons)]
    dff = dff[dff["Code"].str.split("_").str.get(0).isin(subj)]
    if(len(ip_cb)==0):
        dff = dff[dff["grade"]!="IP"]
    return dff



@app.callback(
    Output(component_id='out-stat', component_property='children'),
    Input(component_id='in-program-cb', component_property='value'),
    Input(component_id='in-courses-cb', component_property='value'),
    Input(component_id='in-subj-cb', component_property='value'),
    Input(component_id='ip-cb', component_property='value')
)
def update_hours_div(progr_cb, type_cb, subj_cb, ip_cb):
    dff = select_courses(progr_cb, type_cb, subj_cb, ip_cb)
    hours = int(dff["Credits"].sum())
    dff = dff[(dff["number_grade"]>0) & (~dff["Credits"].isna())]
    if len(dff)>0:
        gpa = sum(dff["Credits"]*dff["number_grade"])/sum(dff["Credits"])
    else:
        gpa = 0
    return "Hours: {}, GPA: {:.2f}".format(hours, gpa)


@app.callback(
    Output(component_id='data-table', component_property='data'),
    Input(component_id='in-program-cb', component_property='value'),
    Input(component_id='in-courses-cb', component_property='value'),
    Input(component_id='in-subj-cb', component_property='value'),
    Input(component_id='ip-cb', component_property='value')
)
def update_table(progr_cb, type_cb, subj_cb, ip_cb):
    ddf = select_courses(progr_cb, type_cb, subj_cb, ip_cb)
    ddf = ddf[["season", "Code", "Name", "Lector", "Credits", "grade"]]
    ddf["Name"] = ddf["Name"].apply(lambda r: " ".join(str(r).split()[:4])+("..." if len(str(r).split())>4 else ""))
    return ddf.to_dict("records")
    # print(f"update table: [ddf]={len(ddf)}")
    # return [{"1":1, "2":2}, {"1":2, "2":2}]



if __name__ == '__main__':
    app.run_server(debug=True)
