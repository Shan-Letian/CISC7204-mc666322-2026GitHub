#!/usr/bin/env python
# coding: utf-8
"""
MovieLens Interactive Dashboard
"""

import os
import ssl
import zipfile
import urllib.request
import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px

# =============================================================
# 1. Download and extract MovieLens (SSL-safe)
# =============================================================
DATA_DIR = 'ml-latest-small'
ZIP_URL = 'https://files.grouplens.org/datasets/movielens/ml-latest-small.zip'
ZIP_PATH = 'ml-latest-small.zip'

if not os.path.exists(DATA_DIR):
    if not os.path.exists(ZIP_PATH):
        print("Downloading MovieLens dataset ...")
        # 关键：忽略 SSL 证书验证，避免 CERTIFICATE_VERIFY_FAILED
        ctx = ssl._create_unverified_context()
        with urllib.request.urlopen(ZIP_URL, context=ctx) as resp, \
             open(ZIP_PATH, 'wb') as f:
            f.write(resp.read())
        print("Download complete.")
    else:
        print("Zip already exists, skipping download.")

    print("Extracting ...")
    with zipfile.ZipFile(ZIP_PATH, 'r') as z:
        z.extractall('.')
    print("Extraction done.")

# =============================================================
# 2. Load and prepare data
# =============================================================
movies = pd.read_csv(os.path.join(DATA_DIR, 'movies.csv'))
ratings = pd.read_csv(os.path.join(DATA_DIR, 'ratings.csv'))

df = ratings.merge(movies, on='movieId', how='left')
df['year'] = df['title'].str.extract(r'\((\d{4})\)\s*$').astype(float)
df['datetime'] = pd.to_datetime(df['timestamp'], unit='s')
df['rating_year'] = df['datetime'].dt.year

user_stats = (
    df.groupby('userId')
      .agg(n_ratings=('rating', 'count'),
           avg_rating=('rating', 'mean'))
      .reset_index()
)

def activity_level(n):
    if n < 50:
        return 'Low (<50)'
    elif n < 200:
        return 'Medium (50-199)'
    else:
        return 'High (200+)'

user_stats['activity'] = user_stats['n_ratings'].apply(activity_level)
df = df.merge(user_stats[['userId', 'activity']], on='userId', how='left')

all_genres = sorted({g for s in movies['genres'].str.split('|') for g in s})
min_year = int(df['rating_year'].min())
max_year = int(df['rating_year'].max())

# =============================================================
# 3. Dash app & layout
# =============================================================
app = dash.Dash(__name__)

app.layout = html.Div([

    html.H1(
        "Decoding Cinematic Taste: MovieLens Rating Dynamics",
        style={'textAlign': 'center', 'color': '#503D36', 'fontSize': 28,
               'marginTop': '20px', 'marginBottom': '20px'}
    ),

    html.Div([
        html.Div([
            html.Label("Select Genre(s):", style={'fontWeight': 'bold'}),
            dcc.Dropdown(
                id='genre-dropdown',
                options=[{'label': g, 'value': g} for g in all_genres],
                value=[],
                multi=True,
                placeholder='All genres'
            )
        ], style={'width': '30%', 'padding': '10px'}),

        html.Div([
            html.Label("Rating Year Range:", style={'fontWeight': 'bold'}),
            dcc.RangeSlider(
                id='year-slider',
                min=min_year, max=max_year,
                value=[min_year, max_year],
                marks={str(y): str(y) for y in range(min_year, max_year + 1, 3)},
                step=1,
                tooltip={'placement': 'bottom', 'always_visible': False}
            )
        ], style={'width': '40%', 'padding': '10px'}),

        html.Div([
            html.Label("User Activity Level:", style={'fontWeight': 'bold'}),
            dcc.Dropdown(
                id='activity-dropdown',
                options=[
                    {'label': 'Low (<50)',       'value': 'Low (<50)'},
                    {'label': 'Medium (50-199)', 'value': 'Medium (50-199)'},
                    {'label': 'High (200+)',     'value': 'High (200+)'},
                ],
                value=['Low (<50)', 'Medium (50-199)', 'High (200+)'],
                multi=True
            )
        ], style={'width': '25%', 'padding': '10px'}),

    ], style={'display': 'flex', 'justifyContent': 'space-between',
              'alignItems': 'flex-end', 'padding': '0 20px'}),

    html.Div(
        id='output-container',
        style={'display': 'flex', 'flexDirection': 'column',
               'padding': '20px', 'gap': '10px'}
    ),
])

# =============================================================
# 4. Callback
# =============================================================
@app.callback(
    Output('output-container', 'children'),
    [Input('genre-dropdown',    'value'),
     Input('year-slider',       'value'),
     Input('activity-dropdown', 'value')]
)
def update_charts(selected_genres, year_range, selected_activity):

    dff = df[(df['rating_year'] >= year_range[0]) &
             (df['rating_year'] <= year_range[1])]

    if selected_activity:
        dff = dff[dff['activity'].isin(selected_activity)]

    if selected_genres:
        dff = dff[dff['genres'].apply(
            lambda s: any(g in str(s).split('|') for g in selected_genres)
        )]

    if dff.empty:
        return html.Div(
            "No data for the current filters. Try widening the year range "
            "or removing some genre selections.",
            style={'textAlign': 'center', 'padding': '80px',
                   'color': '#888', 'fontSize': 18}
        )

    # Chart 1
    exploded = dff.assign(genre=dff['genres'].str.split('|')).explode('genre')
    genre_avg = (
        exploded.groupby('genre')['rating']
                .agg(['mean', 'count'])
                .reset_index()
    )
    genre_avg = genre_avg[genre_avg['count'] >= 50].sort_values('mean', ascending=False)

    fig1 = px.bar(
        genre_avg, x='genre', y='mean',
        color='mean', color_continuous_scale='Viridis',
        title='Average Rating by Genre',
        labels={'genre': 'Genre', 'mean': 'Average Rating', 'count': '# Ratings'}
    )
    fig1.update_layout(coloraxis_showscale=False,
                       xaxis_tickangle=-40,
                       margin=dict(t=50, b=80))

    # Chart 2
    year_trend = (
        dff.groupby('rating_year')
           .agg(n_ratings=('rating', 'count'),
                avg_rating=('rating', 'mean'))
           .reset_index()
    )
    fig2 = px.line(
        year_trend, x='rating_year', y='n_ratings',
        markers=True,
        title='Number of Ratings per Year',
        labels={'rating_year': 'Year',
                'n_ratings': 'Number of Ratings',
                'avg_rating': 'Average Rating'}
    )
    fig2.update_traces(line_color='#2c7fb8', line_width=2)
    fig2.update_layout(margin=dict(t=50, b=60))

    # Chart 3
    fig3 = px.histogram(
        dff, x='rating', nbins=10,
        title='Distribution of Ratings',
        labels={'rating': 'Rating'},
        color_discrete_sequence=['#41b6c4']
    )
    fig3.update_layout(bargap=0.1, margin=dict(t=50, b=60))

    # Chart 4
    us = user_stats.copy()
    if selected_activity:
        us = us[us['activity'].isin(selected_activity)]

    fig4 = px.scatter(
        us, x='n_ratings', y='avg_rating',
        color='activity',
        opacity=0.55,
        hover_data={'userId': True, 'n_ratings': True, 'avg_rating': ':.2f'},
        title='User Activity vs. Average Rating (all-time)',
        labels={'n_ratings': 'Number of Ratings (log scale)',
                'avg_rating': 'Average Rating',
                'activity': 'Activity'}
    )
    fig4.update_xaxes(type='log')
    fig4.update_layout(margin=dict(t=50, b=60))

    return [
        html.Div([
            html.Div(dcc.Graph(figure=fig1), style={'width': '50%'}),
            html.Div(dcc.Graph(figure=fig2), style={'width': '50%'}),
        ], style={'display': 'flex', 'gap': '10px'}),
        html.Div([
            html.Div(dcc.Graph(figure=fig3), style={'width': '50%'}),
            html.Div(dcc.Graph(figure=fig4), style={'width': '50%'}),
        ], style={'display': 'flex', 'gap': '10px'}),
    ]

# =============================================================
# 5. Run
# =============================================================
if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)