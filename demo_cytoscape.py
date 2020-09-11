from dash import Dash
from dash_cytoscape import Cytoscape
from dash_html_components import Div

import pandas as pd
import networkx as nx

if __name__ == '__main__':

    df = pd.read_csv(filepath_or_buffer='./vidhya.csv', )
    # ['source', 'target', 'edge']

    graph = nx.MultiDiGraph()
    for index, row in df.iterrows():
        graph.add_node(row['source'])
        graph.add_node(row['target'])
        graph.add_edge(u_for_edge=row['source'], v_for_edge=row['target'], kind=row['edge'])

    positions = nx.drawing.layout.spring_layout(G=graph, )
    # now build a map of nodes to x-y coordinates so we can put the positions back in the data frame above

    app = Dash(__name__)
    app.layout = Div([
        Cytoscape(
            id='cytoscape',
            elements=[
                {'data': {'id': 'one', 'label': 'Node 1'}, 'position': {'x': 50, 'y': 50}},
                {'data': {'id': 'two', 'label': 'Node 2'}, 'position': {'x': 200, 'y': 200}},
                {'data': {'source': 'one', 'target': 'two', 'label': 'Node 1 to 2'}}
            ],
            layout={'name': 'preset'}
        )
    ])
    app.run_server(debug=True)
