import dash_mantine_components as dmc
from dash import html


class QueryResultsViewer:
    def __init__(self):
        self.create_layout()

    def create_layout(self):
        self.layout = dmc.Group([html.Div("Here are the query results")])
