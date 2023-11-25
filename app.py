
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from olist.seller_updated import Seller
import plotly.graph_objects as go
import numpy as np
import json
import requests
import plotly.express as px

STYLES = {'title': {'weight':'heavy', 'name':'Liberation Serif', 'size':16,},
          'labels': {'weight': 'heavy', 'name': 'Liberation Serif', 'size': 14}}

def load_data():
    seller = Seller()
    data = seller.get_training_data()
    return data

def plot_pl (sellers):
    revenues_sales = sellers.sales.sum() * 0.1
    revenues_subscription = sellers.months_on_olist.sum() * 80
    costs_reviews = sellers.cost_of_reviews.sum()
    costs_it = 500_000
    profits_gross = sellers.profits.sum()
    profits_net = profits_gross - costs_it

    fig = go.Figure(go.Waterfall(
        orientation = "v",
        measure = ["relative", "relative", "total", "relative", "total", "relative", "total"],
        x = ["Abonnements mensuels", "Commissions de vente", "Revenus Totals", "Coûts des avis", "Bénéfice Brut", "Coûts IT", "Bénéfice Net"],
        textposition = "outside",
        y = [revenues_subscription, revenues_sales, 0, -costs_reviews, 0, -costs_it, 0],
        connector = {"line":{"color":"rgb(63, 63, 63)"}},
    ))

    fig.update_layout(
            title = {'text': "Bénéfices et Pertes d'Olist (BRL)",
                    'yanchor': 'top',
                    'xanchor': 'left',
                    'xref': 'paper',
                    'font': {'size': 36}},
            showlegend = False
    )


    return fig

def plot_profits_sellers (sellers):

    sns.set_palette('muted')

    fig, ax = plt.subplots(figsize=(12, 6))

    plt.suptitle(t="Répartition des profits d'Olist sur les vendeurs", **STYLES['title'])

    sns.histplot(sellers.profits,
                stat='count',
                element='step',
                ax=ax)

    quantiles = sellers.profits.quantile(q=[.01, .25, .5, .75, .99])

    ax.set_xlim(quantiles.iloc[0], quantiles.iloc[-1])
    ax.set_xlabel(xlabel='Profits (M. BRL)', fontdict=STYLES['labels'])
    ax.set_ylabel(ylabel='Vendeurs', fontdict=STYLES['labels'])

    for p, q in quantiles.iloc[1:-1].items():
        c_ = 'black'
        if p == .25:
            c_ = 'red'
        ax.axvline(x=q,
                color=c_,
                ls=':')
        ax.text(x=q,
                y=ax.get_yticks()[-1] - 30,
                s=f'{p:.0%}',
                color=c_,
                ha='center',
                va='center',
                weight='bold')

    fig.tight_layout();

    return fig

def plot_rm_sellers (sellers):
    n_sellers = sellers.shape[0]
    profits_gross = sellers.profits.sum()
    costs_reviews = sellers.cost_of_reviews.sum()
    revenues_total = sellers.revenues.sum()
    it_costs_per_seller_removed = 500_000

    sorted_sellers = sellers.sort_values(by='profits') \
                    [['months_on_olist',
                      'sales',
                      'profits',
                      'revenues',
                      'quantity',
                      'cost_of_reviews']] \
                    .reset_index()

    gross_profits_per_seller_removed = profits_gross - np.cumsum(sorted_sellers.profits[:-1])
    review_costs_per_seller_removed = costs_reviews - np.cumsum(sorted_sellers.cost_of_reviews[:-1])
    revenues_per_seller_removed = revenues_total - np.cumsum(sorted_sellers.revenues[:-1])
    profits_per_seller_removed = gross_profits_per_seller_removed - it_costs_per_seller_removed
    margin_per_seller_removed = profits_per_seller_removed / revenues_per_seller_removed
    costs_per_seller_removed = it_costs_per_seller_removed + review_costs_per_seller_removed


    fig, ax = plt.subplots(figsize=(12, 6))

    axs = [ax, ax.twinx()]

    x = np.arange(1, n_sellers, 1)

    plt.suptitle(t="Impact estimé sur les Profits",
                **STYLES['title'])

    profit_line = sns.lineplot(x=x,
                            y=profits_per_seller_removed,
                            label='Bénéfices Nets',
                            ax=axs[0])

    revenue_line = sns.lineplot(x=x,
                                y=revenues_per_seller_removed,
                                label='Revenus',
                                ax=axs[0])

    costs_line = sns.lineplot(x=x,
                            y=costs_per_seller_removed,
                            label='Coûts',
                            ax=axs[0])

    axs[0].set_xlabel('Nombre de vendeurs retirés',
                    fontdict=STYLES['labels'])
    axs[0].set_ylabel('BRL',
                    fontdict=STYLES['labels'])

    axs[0].tick_params(axis='y')

    margin_line = sns.lineplot(x=x,
                            y=margin_per_seller_removed,
                            label='Marge de profit',
                            color='purple',
                            ax=axs[1])

    axs[1].set_ylabel('%',
                    fontdict=STYLES['labels'])
    axs[1].tick_params(axis='y',
                    labelcolor='purple')
    axs[1].set(ylim=[0, 1])

    lines = [axs[1].lines[0], *axs[0].lines]
    labels = [line.get_label() for line in lines]
    axs[0].legend(lines, labels)

    fig.tight_layout()

    return fig

def creer_choroplethe(df, indicateur):

    url = "https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson"
    geojson = json.loads(requests.get(url).text)

    df = df.groupby('seller_state')[indicateur].sum().reset_index()

    fig = px.choropleth_mapbox(
        df,
        geojson=geojson,
        locations='seller_state',
        color=indicateur,
        featureidkey="properties.sigla",
        mapbox_style="carto-positron",
        center={"lat":-14, "lon": -55},
        zoom = 2,
        labels={indicateur: indicateur},
        opacity = 0.7,
    )
    fig.update_geos(fitbounds="locations", visible=False)
    return fig



# Streamlit app layout
def main():
    st.title('Data Analysis Presentation')
    data = load_data()

    # Tab layout
    tab1, tab2, tab3, tab4 = st.tabs(['Plot 1', 'Plot 2', 'Plot 3', "Map"])

    with tab1:
        st.header('Distribution des profits et revenus')
        fig = plot_pl(data)
        st.plotly_chart(fig, theme='streamlit', use_container_width=True)
        st.write('Explanation of Plot 1...')

    with tab2:
        st.header('Distribution des profits par vendeur')
        fig = plot_profits_sellers(data)
        st.pyplot(fig, theme='streamlit', use_container_width=True)

    with tab3:
        st.header('')
        fig = plot_rm_sellers(data)
        st.pyplot(fig, theme='streamlit', use_container_width=True)

    with tab4:
        st.header('Répartition des indicateurs par état')
        indicator = st.selectbox('Choisir un indicateur',
                                ['profits', 'revenues', 'cost_of_reviews'])
        fig = creer_choroplethe(data, indicator)
        st.plotly_chart(fig, theme='streamlit', use_container_width=True)

if __name__ == '__main__':
    main()
