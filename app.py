from PIL import Image
import numpy as np
import png
import io
import base64

import plotly.express as px


import dash
from dash.dependencies import ClientsideFunction, Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc

app = dash.Dash(__name__, suppress_callback_exceptions=True, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

sidebar = html.Div(
  className='col-6 col-md-4 d-print-none',
  children=[
    html.H4("Upload Image"),
    html.P("Images must be JPEG (.jpg or .jpeg)"),
    html.Div(
      className='card',
      children=[
        dcc.Upload(
          id='upload-data',
          children=html.Div(
            children=[
              html.Div(['Drag and Drop or',
                html.Br(),
                html.A(className='btn btn-primary', children='Select Files', style={'color': 'white', 'margin-top': '1em' })
              ])
          ]),
          accept='image/jpeg',
          style={
              'width': 'auto',
              'min-height': '150px',
              'textAlign': 'center',
              'borderWidth': '0px',
              'display': 'flex',
              'flex-direction': 'column',
              'justify-content': 'center',
              'align-content': 'center'
          },
          # Allow multiple files to be uploaded
          multiple=True
        ),
      ]
    )
  ])

main_content = html.Div(
  className='col',
  children=[
    html.Div(children="blah", id='hidden-div', style={'display': 'none'}),
    html.Div(id='output-data')
  ]
)

grid = html.Div(
  className='row',
  children=[sidebar, main_content]
)

navbar = dbc.NavbarSimple(
  brand="SkyFinder",
  color="secondary",
  dark=True
)

preamble = html.Div([
  html.Img(src=app.get_asset_url('canopy.jpg'), id='canopy'),
  html.P([
    "Author: Dave Rosborough, Pacific Academy",
    html.Br(),
    "License: MIT",
    html.Br(),
    "Source Code: ",
    html.A("https://github.com/drosboro/skyfinder", href="https://github.com/drosboro/skyfinder")
  ]),
  html.P(
    """
      This tool attempts to detect sky in images of forest canopies.  It works by detecting any pixels in the image for which blue is the predominate colour.  
      As a result, it will likely work best with photos taken on relatively bright, sunny days.
    """
  )
])

app.layout = html.Div([
  navbar,
  html.Div(
    className='container mt-4',
    children=[preamble, grid]
  )
])

def isBlue(x):
  return np.uint8(255) if x[2] == max(x) else np.uint8(0)

def process_image(contents, filename, date):
  content_type, content_string = contents.split(',')
  decoded = base64.b64decode(content_string)

  buff = io.BytesIO()
  buff.write(decoded)
  buff.seek(0)
  image = Image.open(buff)
  data = np.asarray(image)

  blue = np.zeros([data.shape[0], data.shape[1]], dtype=np.uint8)
  blue = np.apply_along_axis(isBlue, 2, data)

  blue_flat = np.reshape(blue, -1)
  prop = sum(blue_flat) / (255 * blue_flat.size) * 100

  fig = px.imshow(blue, color_continuous_scale='gray')
  fig.update_layout(coloraxis_showscale=False)
  fig.update_traces(hoverinfo='skip', hovertemplate=None)
  # fig.update_xaxes(showticklabels=False)
  # fig.update_yaxes(showticklabels=False)




  return html.Div(children=[
    html.H3("Results"),
    html.P(["Sky: %0.2f%%" % (prop),
      html.Br(),
      "Canopy: %0.2f%%" % (100 - prop)]),
    dcc.Graph(figure=fig)
  ])

@app.callback(Output('output-data', 'children'),
              [Input('upload-data', 'contents')],
              [State('upload-data', 'filename'),
               State('upload-data', 'last_modified')])
def update_output(list_of_contents, list_of_names, list_of_dates):
      if list_of_contents is not None:
        
        children = [
            process_image(c, n, d) for c, n, d in
            zip(list_of_contents, list_of_names, list_of_dates)]
        return children




if __name__ == '__main__':
    app.run_server(debug=True)