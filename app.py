import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objs as go
import ast
import numpy as np

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# global color scheme for background and text
colors = {
    'background': '#000000',
    'text': '#FDFCFC'
}

# Read the data from file into pandas dataframe
filename = 'data2.csv'
df = pd.read_csv(filename)

# get list of unique datastores 
datastores = df['Datastore'].unique()

# slider dictionary for labeling in visualization
slider_time = {-6:'2017 Q2',-5:'2017 Q3',-4:'2017 Q4',-3:'2018 Q1',-2:'2018 Q2',-1:'2018 Q3',0:'2018 Q4'}

# Kmeans calculation function. This takes list of x and y coordinates, zips them together and then finds clusters. 
# Z is the list of data element associated with point (x,y).
def kmeans(x,y,z):
    from sklearn.cluster import KMeans
    import matplotlib.pyplot as plt
    
    point = list(zip(x,y))
    kmeans = KMeans(n_clusters=round(len(point)/5))
    kmeans.fit(point)
    centers = kmeans.cluster_centers_
    y_kmeans = kmeans.predict(point)
	
    new = {} 
    for i in range(len(y_kmeans)):
    	new.setdefault(y_kmeans[i],[]).append(z[i])
    	labels = [value for (key, value) in sorted(new.items())]
    
    return centers,labels
		

# tracer for the parallel coordinate charts		
def tracer(dff,color,each):
	return go.Scatter(
            x=['2017 Q2','2017 Q3','2017 Q4','2018 Q1','2018 Q2','2018 Q3','2018 Q4'],
            y=dff[0],
            mode='lines+markers',
			name = each,
			marker={
                'size': 10,
                'opacity': 1,
                'line': {'width': 0.08},
				'color':color[0],
				'colorscale':'RdBu',
            }
        )


app.layout = html.Div(style={'backgroundColor': colors['background']},children=[
	
	# Header 
    html.Div([
		html.Div([html.H2('TOPOLOGICAL DATA DISCOVERY')], style={'width': '35%', 'display': 'inline-block','marginLeft': '2%','color': colors['text']}),
        html.Div([
			# Drop down for datastores
            dcc.Dropdown(
                id='crossfilter-xaxis-column',
                options=[{'label': i, 'value': i} for i in datastores],
                value='datastore1' # default value for drop down
            )], style={'width': '30%', 'display': 'inline-block','marginLeft': '30%','marginTop': '1%'}
        ),
		
	# Header Style	
    ], style={
        'borderBottom': 'thin lightgrey solid',
		'padding': '5x 0px',
		'width': '97%',
		'marginLeft': '1.5%',
		'marginRight': '1.5%'

    }),
	# Scatter plot
    html.Div([
        dcc.Graph(
            id='crossfilter-indicator-scatter',
            hoverData={'points': [{'customdata': 'column1101'}]}
        ),
			# Slider for time series
		    html.Div(dcc.Slider(
			id='crossfilter-year--slider',
			min=-6,
			max=0,
			value=0,
			marks={str(t) : {'label' : slider_time[t], 'style':{'color':colors['text']}} for t in range(-6,1)}
		), style={'width': '80%', 'padding': '0px 0px 30px 30px','color': colors['text'],'backgroundColor': colors['background']})
		
    ], style={'width': '50%', 'display': 'inline-block'}),
	# Graph division for parallel coordinate graphs
    html.Div([
        dcc.Graph(id='x-time-series'),
		dcc.Graph(id='y-time-series'),
    ], style={'display': 'inline-block', 'width': '50%'}),
	# Caption
	html.Div([html.P("This dashboard represents the supply and demand volatility indexes (SVI and DVI) of data elements. The graph to the left is a scatter plot of centroids of data elements that are grouped using K-means clustering on DVI and SVI axes. The color of nodes represents the correlation to revenue (adj R2). The graphs to the right represents the parallel coordinate graphs of the data elements belonging to the cluster of the centroid selected on the left hand side graph through a period of multiple quarters. The top graph shows SVI for these data elements and the bottom graph shows the DVI for each quarter.")],style={'borderTop': 'thin lightgrey solid','padding': '5px 0px','color':colors['text'],'marginTop': '1%','marginBottom': '1%','marginLeft': '1.5%','marginRight': '1.5%'})

])


@app.callback(
    dash.dependencies.Output('crossfilter-indicator-scatter', 'figure'),
    [dash.dependencies.Input('crossfilter-xaxis-column', 'value'),
    dash.dependencies.Input('crossfilter-year--slider', 'value')])
def update_graph(xaxis_column_name,
                 year_value):
				 
    dff = df[df['Datastore'] == str(xaxis_column_name)]
    #print(dff)
    svi_dict = {0:'SVI_1',-1:'SVI_2',-2:'SVI_3',-3:'SVI_4',-4:'SVI_5',-5:'SVI_6',-6:'SVI_7'}
    dvi_dict = {0:'DVI_1',-1:'DVI_2',-2:'DVI_3',-3:'DVI_4',-4:'DVI_5',-5:'DVI_6',-6:'DVI_7'}
    AdjR2_dict = {0:'AdjR2_1',-1:'AdjR2_2',-2:'AdjR2_3',-3:'AdjR2_4',-4:'AdjR2_5',-5:'AdjR2_6',-6:'AdjR2_7'}
	
    x1=dff[svi_dict[year_value]].values
    y1=dff[dvi_dict[year_value]].values
    z1=dff['DataElement'].values
	
    centers,labels = kmeans(x1,y1,z1)
    min_x,min_y = centers.min(axis=0)
    max_x,max_y = centers.max(axis=0)

    return {
		# Tracer for scatter plot
        'data': [go.Scatter(
            x=centers[:,0], 
            y=centers[:,1], 
            text=labels, 
            customdata=dff['DataElement'],
            mode='markers',
            marker={
                'size': 15,
                'opacity': 1,
                'line': {'width': 0.5, 'color': 'white'},
				'color':dff[AdjR2_dict[year_value]].values,
				'colorscale':'RdBu',
				'showscale':True,
				'colorbar':{'title':'Adj R2'}
            },
			
		# Quadrant lines plot	
        ),
		go.Scatter(
            x=[(min_x+max_x)/2,(min_x+max_x)/2],
            y=[0,max_y],  
            mode='lines',
            line={'width': 1, 'color': colors['text']}
        ),
		go.Scatter(
		    x=[min_x,max_x],  
            y=[max_y/2,max_y/2],
            mode='lines',
            line={'width': 1, 'color': colors['text']}
        ),
		
		# Quadrant labels
		# Top Right
		go.Scatter(
			x=[max_x],
			y=[max_y],
			name='Text',
			mode='text',
			text=['High Demand & Supply'],
			textposition='top left',
			textfont={'size':10,'color':colors['text']}
		),
		# Bottom Left
		go.Scatter(
			x=[min_x],
			y=[min_y],
			name='Text',
			mode='text',
			text=['Low Demand & Supply'],
			textposition='bottom right',
			textfont={'size':10,'color':colors['text']}
		),
		# Top Left
		go.Scatter(
			x=[min_x],
			y=[max_y],
			name='Text',
			mode='text',
			text=['High Demand & Low Supply'],
			textposition='top right',
			textfont={'size':10,'color':colors['text']}
		),
		# Bottom Right
		go.Scatter(
			x=[max_x],
			y=[min_y],
			name='Text',
			mode='text',
			text=['Low Demand & High Supply'],
			textposition='bottom left',
			textfont={'size':10,'color':colors['text']}
		)

		],
        'layout': go.Layout(
            xaxis={
                'title': 'Supply Volatility Index (SVI)',
                'type': 'linear',
				'mirror':True,
				'ticks':'outside',
				'showline':True,
				'zeroline':False
		
            },
            yaxis={
                'title': 'Demand Volatility Index (DVI)',
				'type': 'linear',
				'mirror':True,
				'ticks':'outside',
				'showline':True,
				'zeroline':False
         
            },
            margin={'l': 50, 'b': 75, 't': 40, 'r': 2},
            height=600,
            hovermode='closest',
			title='<b>{}</b><br>'.format('Data Element Volatility in terms of Supply & Demand'),
			showlegend=False,
			plot_bgcolor=colors['background'],
            paper_bgcolor=colors['background'],
            font={'color': colors['text']},

        )
    }


def create_time_series(data, title, color):
    return {
        'data': data,
        'layout': {
            'height': 325,
            'margin': {'l': 30, 'b': 40, 'r': 5, 't': 5},
            'annotations': [{
                'x': 0, 'y': 1, 'xanchor': 'left', 'yanchor': 'top',
                'xref': 'paper', 'yref': 'paper', 'showarrow': False,
                'align': 'left', 'bgcolor': colors['background'],
                'text': title,
            }],
            'yaxis': {'type': 'linear','range':[0,35],'autorange':True},
            'xaxis': {'showgrid': False},
			'plot_bgcolor': colors['background'],
            'paper_bgcolor': colors['background'],
            'font': {
                    'color': colors['text']
                }
        }
    }


@app.callback(
    dash.dependencies.Output('x-time-series', 'figure'),
    [dash.dependencies.Input('crossfilter-indicator-scatter', 'hoverData'),
     dash.dependencies.Input('crossfilter-xaxis-column', 'value')])
def update_y_timeseries(hoverData, xaxis_column_name):
    country_name = hoverData['points'][0]['text']
    names = ast.literal_eval(country_name)
    data = []
    for each in names:
        dff = df[df['DataElement'] == each][['SVI_1','SVI_2','SVI_3','SVI_4','SVI_5','SVI_6','SVI_7']].values
        color = df[df['DataElement'] == each][['AdjR2_1','AdjR2_2','AdjR2_3','AdjR2_4','AdjR2_5','AdjR2_6','AdjR2_7']].values
        data.append(tracer(dff,color,each))
    return create_time_series(data, '<b>{}</b><br>'.format("Supply Volatility Index (SVI) over 7 Quarters (2017-2018)"), color)

@app.callback(
    dash.dependencies.Output('y-time-series', 'figure'),
    [dash.dependencies.Input('crossfilter-indicator-scatter', 'hoverData')])
def update_x_timeseries(hoverData):
    country_name = hoverData['points'][0]['text']
    names = ast.literal_eval(country_name)
    data = []
    for each in names:
        dff = df[df['DataElement'] == each][['DVI_1','DVI_2','DVI_3','DVI_4','DVI_5','DVI_6','DVI_7']].values
        color = df[df['DataElement'] == each][['AdjR2_1','AdjR2_2','AdjR2_3','AdjR2_4','AdjR2_5','AdjR2_6','AdjR2_7']].values
        data.append(tracer(dff,color,each))
    return create_time_series(data, '<b>{}</b><br>'.format("Demand Volatility Index (DVI) over 7 Quarters (2017-2018)"), color)


if __name__ == '__main__':
    app.run_server(debug=True)