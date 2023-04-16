from dash import Dash
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate
from dash import dcc, html
import plotly.express as px
import dash_ag_grid as dag
import pandas as pd

# Load data from CSV file
sales_df = pd.read_csv('assets/sales_data.csv')

# Aggregate this data at month and product level
sales_by_product_month_df = sales_df.groupby(by=['Product Name', 'Month Name']).aggregate({'Revenue':'sum'}).reset_index()
# Above statement is equivalent to below sql statement
# select "Product Name", "Month Name", sum(Revenue) as "Revenue"
# from sales
# group by "Product Name", "Month Name"

app = Dash(__name__)

# Let's create a simple visualisation with our dataframe
revenue_by_product_month_chart = px.bar(
        data_frame=sales_by_product_month_df,
        x='Month Name', # Column from data_frame which will indicate values to be plotted on x axis
        y='Revenue', # Column from data_frame which will indicate values to be plotted on y axis (measure or fact)
        color='Product Name', # This will be the legend. Colored stacks will be governed by this column in data_frame
        custom_data = ['Product Name'] # This information will be included in the clickData when the bars in chart are clicked
    )

# Let us define the layout of our app.
app.layout = html.Div(
    [
        # HTML Div component to hold our graph. The graph will in turn contain a figure object
       html.Div(
        id='chart-container-div',
        children=dcc.Graph(
            id='bar-chart',
            figure = revenue_by_product_month_chart
            )
       ),

       # This Div will hold the Dash AG Grid
       # AG Grid is an advanced table rendered in Dash app. 
       # The html.Table object could be used as well. We will use AG Grid. 
       html.Div(
            id='table-container-div',
            style = {'display': 'flex',  'justifyContent': 'center'},
            children=None
            )
    ]
)

# Define Callbacks Here
@app.callback(
    Output('table-container-div', 'children'),
    Input('bar-chart','clickData'),
    prevent_initial_call = True # To prevent the callback to run when the application loads
)
def update_table(click_data):
    # print(click_data)
    if click_data is None:
        raise PreventUpdate
    
    # Here is an example of click_data:
    # {
    #   'points': [
    #         {
    #         'curveNumber': 2, 
    #         'pointNumber': 7, 
    #         'pointIndex': 7, 
    #         'x': 'Mar 2022', 
    #         'y': 47463, 
    #         'label': 'Mar 2022', 
    #         'value': 47463, 
    #         'bbox': {
    #             'x0': 711.03, 
    #             'x1': 781.23, 
    #             'y0': 192.56, 
    #             'y1': 192.56
    #             }, 
    #         'customdata': ['Product 3']
    #         }
    #   ]
    # }
    
    #Extract the product and month which was clicked on the chart.
    product_clicked = click_data['points'][0]['customdata'][0]
    month_clicked = click_data['points'][0]['x']

    # Filter the sales_df with the selected product and month name
    filtered_df = sales_df[(sales_df['Product Name'] == product_clicked) & (sales_df['Month Name'] == month_clicked)]

    # Create and return a dash ag grid object with this data.
    return dag.AgGrid(
            enableEnterpriseModules=False,
            columnDefs=[{"headerName": column, "field": column} for column in filtered_df.columns],
            rowData= filtered_df.to_dict('records'),
            columnSize="sizeToFit",
            defaultColDef=dict(
                resizable=True,
            ),
            style = {'height': '250px', 'width': '60%'}
    )


if __name__ == "__main__":
    app.run_server(debug=True)
