from dash import Dash
from dash_cytoscape import Cytoscape
from dash_html_components import Div

import pandas as pd
import networkx as nx

if __name__ == '__main__':

    df = pd.read_csv(filepath_or_buffer='./vidhya.csv', )
    # ['source', 'target', 'edge']

    graph = nx.MultiGraph()
    for index, row in df.iterrows():
        graph.add_node(row['source'])
        graph.add_node(row['target'])
        graph.add_edge(u_for_edge=row['source'], v_for_edge=row['target'], kind=row['edge'])

    positions = nx.drawing.layout.spring_layout(G=graph, )
    # now build a map of nodes to x-y coordinates so we can put the positions back in the data frame above
    cytoscape_graph = nx.readwrite.cytoscape_data(graph)
    cytoscape_nodes = [{'data': {'id': item['data']['id'], 'label': item['data']['name']}} for item in
                       cytoscape_graph['elements']['nodes']]

    app = Dash(__name__)
    app.layout = Div([
        Cytoscape(
            id='cytoscape',
            elements=cytoscape_nodes + cytoscape_graph['elements']['edges'],
            style={'width': '100%', 'height': '600px'},
            layout={'name':  ['breadthfirst', 'circle', 'concentric', 'cose', 'grid', 'preset', 'random'][1]
}
        )
    ])
    app.run_server(debug=True,  host='localhost', port=8051, )
