import pandas as pd
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Create app
app = dash.Dash(__name__)

# 清除布局，回调未执行前不显示异常
app.config.suppress_callback_exceptions = True

# 读取野火数据
df = pd.read_csv(
    'https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/'
    'IBMDeveloperSkillsNetwork-DV0101EN-SkillsNetwork/Data%20Files/Historical_Wildfires.csv'
)

# 从 Date 列提取月份名称和年份
df['Month'] = pd.to_datetime(df['Date']).dt.month_name()   # 月份名称
df['Year']  = pd.to_datetime(df['Date']).dt.year           # 年份

# ---------------- Layout Section ----------------
app.layout = html.Div(children=[
    # TASK 2.1: 标题
    html.H1('Australia Wildfire Dashboard',
            style={'textAlign': 'center',
                   'color': '#503D36',
                   'fontSize': 26}),

    # 外层 division
    html.Div([
        # 第一个内部 division：RadioItems + Dropdown
        html.Div([
            html.H2('Select Region:', style={'margin-right': '2em'}),

            # TASK 2.2: RadioItems 选择 Region
            dcc.RadioItems([
                {"label": "New South Wales",    "value": "NSW"},
                {"label": "Northern Territory", "value": "NT"},
                {"label": "Queensland",         "value": "QL"},
                {"label": "South Australia",    "value": "SA"},
                {"label": "Tasmania",           "value": "TA"},
                {"label": "Victoria",           "value": "VI"},
                {"label": "Western Australia",  "value": "WA"},
            ], value='NSW', id='region', inline=True),
        ]),

        # Dropdown 选择 Year
        html.Div([
            html.H2('Select Year:', style={'margin-right': '2em'}),
            dcc.Dropdown(df.Year.unique(), value=2005, id='year'),
        ]),

        # TASK 2.3: 第二个内部 division：两个空 div 放输出图
        html.Div([
            html.Div([], id='plot1'),
            html.Div([], id='plot2'),
        ], style={'display': 'flex'}),
    ])
])

# ---------------- Callback Section ----------------
# TASK 2.4: 回调装饰器
@app.callback(
    [Output(component_id='plot1', component_property='children'),
     Output(component_id='plot2', component_property='children')],
    [Input(component_id='region', component_property='value'),
     Input(component_id='year',   component_property='value')]
)
# TASK 2.5: 回调函数
def reg_year_display(input_region, input_year):
    # 按区域和年份筛选数据
    region_data = df[df['Region'] == input_region]
    y_r_data    = region_data[region_data['Year'] == input_year]

    # Plot 1: 每月平均预计火灾面积（饼图）
    est_data = y_r_data.groupby('Month')['Estimated_fire_area'].mean().reset_index()
    fig1 = px.pie(
        est_data,
        values='Estimated_fire_area',
        names='Month',
        title="{} : Monthly Average Estimated Fire Area in year {}".format(
            input_region, input_year)
    )

    # Plot 2: 每月疑似植被火灾像元平均数量（柱状图）
    veg_data = y_r_data.groupby('Month')['Count'].mean().reset_index()
    fig2 = px.bar(
        veg_data,
        x='Month',
        y='Count',
        title='{} : Average Count of Pixels for Presumed Vegetation Fires in year {}'.format(
            input_region, input_year)
    )

    return [dcc.Graph(figure=fig1),
            dcc.Graph(figure=fig2)]


# ---------------- Run ----------------
if __name__ == '__main__':
    # 在 Spyder 中运行时，务必关闭 debug 和 use_reloader，否则会反复重启
    app.run(debug=False, use_reloader=False)