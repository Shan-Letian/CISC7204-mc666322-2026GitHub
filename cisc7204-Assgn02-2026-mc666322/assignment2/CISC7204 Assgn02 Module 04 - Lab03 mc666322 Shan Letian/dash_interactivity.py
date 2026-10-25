# 导入所需库
# 导入所需库
import pandas as pd
import plotly.graph_objects as go
from dash import Dash, dcc, html
from dash.dependencies import Input, Output

# 将航空公司数据读入 pandas 数据帧
airline_data = pd.read_csv(
    'https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/'
    'IBMDeveloperSkillsNetwork-DV0101EN-SkillsNetwork/Data%20Files/airline_data.csv',
    encoding="ISO-8859-1",
    dtype={
        'Div1Airport': str,
        'Div1TailNum': str,
        'Div2Airport': str,
        'Div2TailNum': str
    }
)

# 创建 Dash 应用
app = Dash(__name__)

# 应用布局
app.layout = html.Div(children=[
    html.H1(
        'Airline Performance Dashboard',
        style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}
    ),
    html.Div(
        [
            "Input Year: ",
            dcc.Input(
                id='input-year',
                value='2010',
                type='number',
                style={'height': '50px', 'font-size': 35}
            )
        ],
        style={'font-size': 40}
    ),
    html.Br(),
    html.Br(),
    html.Div(
        dcc.Graph(id='line-plot')
    )
])

# 回调装饰器
@app.callback(
    Output(component_id='line-plot', component_property='figure'),
    Input(component_id='input-year', component_property='value')
)
def get_graph(entered_year):
    # 根据输入年份筛选数据
    df = airline_data[airline_data['Year'] == int(entered_year)]

    # 按月份分组，计算到达延迟平均值
    line_data = df.groupby('Month')['ArrDelay'].mean().reset_index()

    # 创建折线图
    fig = go.Figure(
        data=go.Scatter(
            x=line_data['Month'],
            y=line_data['ArrDelay'],
            mode='lines',
            marker=dict(color='green')
        )
    )

    fig.update_layout(
        title='Month vs Average Flight Delay Time',
        xaxis_title='Month',
        yaxis_title='ArrDelay'
    )

    return fig


# 运行应用
if __name__ == '__main__':
    app.run(debug=True)