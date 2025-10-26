import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(
    page_title="Advanced Analytics",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Advanced Analytics")
st.markdown("### Deep dive into sales patterns and correlations")

# Check if data is loaded in session state
if 'df' not in st.session_state or st.session_state.df is None:
    st.warning("No data loaded. Please upload data or select sample data on the main page.")
    st.stop()

df = st.session_state.df
filtered_df = st.session_state.get('filtered_df', df)

# Advanced analytics section
st.markdown("---")

# Performance Metrics
col1, col2 = st.columns(2)

with col1:
    st.subheader("Category Performance Matrix")
    
    # Create performance matrix
    category_metrics = filtered_df.groupby('Category').agg({
        'Sales': ['sum', 'mean', 'std'],
        'Units': 'sum',
        'Customers': 'sum'
    }).reset_index()
    
    category_metrics.columns = ['Category', 'Total Sales', 'Avg Sale', 'Std Dev', 'Units', 'Customers']
    category_metrics['Efficiency'] = category_metrics['Total Sales'] / category_metrics['Units']
    category_metrics = category_metrics.sort_values('Total Sales', ascending=False)
    
    st.dataframe(
        category_metrics.style.format({
            'Total Sales': '${:,.2f}',
            'Avg Sale': '${:,.2f}',
            'Std Dev': '${:,.2f}',
            'Units': '{:,.0f}',
            'Customers': '{:,.0f}',
            'Efficiency': '${:,.2f}'
        }),
        width='stretch',
        hide_index=True
    )

with col2:
    st.subheader("Regional Performance Matrix")
    
    region_metrics = filtered_df.groupby('Region').agg({
        'Sales': ['sum', 'mean', 'std'],
        'Units': 'sum',
        'Customers': 'sum'
    }).reset_index()
    
    region_metrics.columns = ['Region', 'Total Sales', 'Avg Sale', 'Std Dev', 'Units', 'Customers']
    region_metrics['Efficiency'] = region_metrics['Total Sales'] / region_metrics['Units']
    region_metrics = region_metrics.sort_values('Total Sales', ascending=False)
    
    st.dataframe(
        region_metrics.style.format({
            'Total Sales': '${:,.2f}',
            'Avg Sale': '${:,.2f}',
            'Std Dev': '${:,.2f}',
            'Units': '{:,.0f}',
            'Customers': '{:,.0f}',
            'Efficiency': '${:,.2f}'
        }),
        width='stretch',
        hide_index=True
    )

st.markdown("---")

# Correlation Analysis
st.subheader("Correlation Analysis")

col1, col2 = st.columns(2)

with col1:
    # Correlation matrix
    correlation_data = filtered_df[['Sales', 'Units', 'Customers']].corr()
    
    fig_corr = px.imshow(
        correlation_data,
        labels=dict(color="Correlation"),
        title="Correlation Matrix",
        template='plotly_white',
        color_continuous_scale='RdBu_r',
        aspect='auto',
        text_auto='.2f'
    )
    fig_corr.update_layout(height=400)
    st.plotly_chart(fig_corr, width='stretch')

with col2:
    # Box plots for sales distribution
    fig_box = go.Figure()
    
    for category in filtered_df['Category'].unique():
        category_data = filtered_df[filtered_df['Category'] == category]['Sales']
        fig_box.add_trace(go.Box(
            y=category_data,
            name=category,
            boxmean='sd'
        ))
    
    fig_box.update_layout(
        title="Sales Distribution by Category",
        yaxis_title="Sales ($)",
        template='plotly_white',
        height=400,
        showlegend=True
    )
    st.plotly_chart(fig_box, width='stretch')

st.markdown("---")

# Time Series Decomposition
st.subheader("Time Series Analysis")

# Aggregate by date
daily_data = filtered_df.groupby('Date').agg({
    'Sales': 'sum',
    'Units': 'sum',
    'Customers': 'sum'
}).reset_index()

# Create subplots
fig_time = make_subplots(
    rows=3, cols=1,
    subplot_titles=('Daily Sales', 'Daily Units', 'Daily Customers'),
    vertical_spacing=0.1
)

fig_time.add_trace(
    go.Scatter(x=daily_data['Date'], y=daily_data['Sales'], name='Sales', line=dict(color='#1f77b4')),
    row=1, col=1
)

fig_time.add_trace(
    go.Scatter(x=daily_data['Date'], y=daily_data['Units'], name='Units', line=dict(color='#ff7f0e')),
    row=2, col=1
)

fig_time.add_trace(
    go.Scatter(x=daily_data['Date'], y=daily_data['Customers'], name='Customers', line=dict(color='#2ca02c')),
    row=3, col=1
)

fig_time.update_layout(
    height=800,
    template='plotly_white',
    showlegend=False
)
fig_time.update_yaxes(title_text="Sales ($)", row=1, col=1)
fig_time.update_yaxes(title_text="Units", row=2, col=1)
fig_time.update_yaxes(title_text="Customers", row=3, col=1)

st.plotly_chart(fig_time, width='stretch')

st.markdown("---")

# Top/Bottom Performers
st.subheader("Top and Bottom Performers")

col1, col2 = st.columns(2)

with col1:
    st.markdown("**Top 10 Days by Sales**")
    top_days = daily_data.nlargest(10, 'Sales')[['Date', 'Sales', 'Units', 'Customers']]
    st.dataframe(
        top_days.style.format({
            'Sales': '${:,.2f}',
            'Units': '{:,.0f}',
            'Customers': '{:,.0f}'
        }),
        width='stretch',
        hide_index=True
    )

with col2:
    st.markdown("**Bottom 10 Days by Sales**")
    bottom_days = daily_data.nsmallest(10, 'Sales')[['Date', 'Sales', 'Units', 'Customers']]
    st.dataframe(
        bottom_days.style.format({
            'Sales': '${:,.2f}',
            'Units': '{:,.0f}',
            'Customers': '{:,.0f}'
        }),
        width='stretch',
        hide_index=True
    )

# Pareto Analysis
st.markdown("---")
st.subheader("Pareto Analysis (80/20 Rule)")

category_sales = filtered_df.groupby('Category')['Sales'].sum().reset_index()
category_sales = category_sales.sort_values('Sales', ascending=False)
category_sales['Cumulative %'] = (category_sales['Sales'].cumsum() / category_sales['Sales'].sum() * 100)
category_sales['% of Total'] = (category_sales['Sales'] / category_sales['Sales'].sum() * 100)

fig_pareto = go.Figure()

fig_pareto.add_trace(go.Bar(
    x=category_sales['Category'],
    y=category_sales['Sales'],
    name='Sales',
    marker_color='#1f77b4'
))

fig_pareto.add_trace(go.Scatter(
    x=category_sales['Category'],
    y=category_sales['Cumulative %'],
    name='Cumulative %',
    yaxis='y2',
    line=dict(color='#ff7f0e', width=3),
    mode='lines+markers'
))

fig_pareto.add_hline(y=80, line_dash="dash", line_color="red", yref='y2', 
                      annotation_text="80%", annotation_position="right")

fig_pareto.update_layout(
    title='Category Sales Pareto Chart',
    yaxis=dict(title='Sales ($)'),
    yaxis2=dict(title='Cumulative %', overlaying='y', side='right', range=[0, 100]),
    template='plotly_white',
    height=500
)

st.plotly_chart(fig_pareto, width='stretch')

st.markdown("---")
st.markdown("*Advanced analytics help identify patterns, outliers, and optimization opportunities*")
