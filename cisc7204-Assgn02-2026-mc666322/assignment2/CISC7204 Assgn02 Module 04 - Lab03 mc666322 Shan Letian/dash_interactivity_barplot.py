# 1/ 导入所需库并读取数据集
import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html
from dash.dependencies import Input, Output

# 读取数据（与任务3相同）
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

# 2/ 应用布局
app.layout = html.Div(children=[
    # 标题，字体大小 40
    html.H1(
        'Total number of flights to the destination state split by reporting airline',
        style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}
    ),
    
    # 输入框组件
    html.Div(
        [
            "Input Year: ",
            dcc.Input(
                id='input-year',
                value='2010',
                type='number',
                style={'height': '50px', 'font-size': 35} # 输入框高度和字体
            )
        ],
        style={'font-size': 40} # 整个 div 的字体大小
    ),
    
    html.Br(),
    html.Br(),
    
    # 柱状图输出组件
    html.Div(
        dcc.Graph(id='bar-plot')
    )
])

# 3/ 添加回调装饰器
@app.callback(
    Output(component_id='bar-plot', component_property='figure'),
    Input(component_id='input-year', component_property='value')
)
# 4/ 定义回调函数
def get_bar_graph(entered_year):
    # 根据输入年份筛选数据
    df = airline_data[airline_data['Year'] == int(entered_year)]
    
    # 按目的地州 (DestState) 和报告航空公司 (Reporting_Airline) 分组，计算航班总数 (Flights)
    bar_data = df.groupby(['DestState', 'Reporting_Airline'])['Flights'].sum().reset_index()
    
    # 使用 plotly express 绘制柱状图
    fig = px.bar(
        bar_data, 
        x='DestState', 
        y='Flights', 
        color='Reporting_Airline', # 用颜色区分航空公司
        title='Flights to Destination State'
    )
    
    return fig

# 5/ 运行应用
if __name__ == '__main__':
    # 为了避免和之前的折线图抢占 8050 端口，这里我们改成 8051
    app.run(debug=True, port=8051)
