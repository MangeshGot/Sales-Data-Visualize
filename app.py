import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Page configuration
st.set_page_config(
    page_title="Data Dashboard",
    page_icon="📊",
    layout="wide"
)

# Generate sample data
@st.cache_data
def generate_sample_data():
    """Generate sample sales data for visualization"""
    np.random.seed(42)
    
    # Date range for the last 90 days
    end_date = datetime.now()
    start_date = end_date - timedelta(days=90)
    dates = pd.date_range(start=start_date, end=end_date, freq='D')
    
    # Create sample data
    categories = ['Electronics', 'Clothing', 'Food & Beverage', 'Home & Garden', 'Sports']
    regions = ['North', 'South', 'East', 'West']
    
    data = []
    for date in dates:
        for category in categories:
            for region in regions:
                # Generate random sales data with some trends
                base_sales = np.random.randint(1000, 5000)
                trend = np.sin(date.dayofyear / 365 * 2 * np.pi) * 500
                sales = base_sales + trend + np.random.normal(0, 200)
                
                data.append({
                    'Date': date,
                    'Category': category,
                    'Region': region,
                    'Sales': max(0, sales),
                    'Units': np.random.randint(50, 200),
                    'Customers': np.random.randint(20, 100)
                })
    
    return pd.DataFrame(data)

# Load data
df = generate_sample_data()

# Header
st.title("📊 Sales Dashboard")
st.markdown("### Interactive data visualization and analytics")

# Sidebar filters
st.sidebar.header("Filters")

# Date range filter
min_date = df['Date'].min().date()
max_date = df['Date'].max().date()

date_range = st.sidebar.date_input(
    "Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

# Category filter
categories = st.sidebar.multiselect(
    "Categories",
    options=df['Category'].unique(),
    default=df['Category'].unique()
)

# Region filter
regions = st.sidebar.multiselect(
    "Regions",
    options=df['Region'].unique(),
    default=df['Region'].unique()
)

# Filter data based on selections
filtered_df = df.copy()

if len(date_range) == 2:
    start_date, end_date = date_range
    filtered_df = filtered_df[
        (filtered_df['Date'].dt.date >= start_date) & 
        (filtered_df['Date'].dt.date <= end_date)
    ]

if categories:
    filtered_df = filtered_df[filtered_df['Category'].isin(categories)]

if regions:
    filtered_df = filtered_df[filtered_df['Region'].isin(regions)]

# Key Metrics
st.markdown("---")
col1, col2, col3, col4 = st.columns(4)

with col1:
    total_sales = filtered_df['Sales'].sum()
    st.metric(
        label="Total Sales",
        value=f"${total_sales:,.0f}",
        delta=f"{(total_sales / df['Sales'].sum() * 100):.1f}% of total"
    )

with col2:
    total_units = filtered_df['Units'].sum()
    st.metric(
        label="Units Sold",
        value=f"{total_units:,}",
        delta=f"{len(filtered_df)} transactions"
    )

with col3:
    avg_sale = filtered_df['Sales'].mean()
    st.metric(
        label="Average Sale",
        value=f"${avg_sale:,.2f}",
        delta=f"±${filtered_df['Sales'].std():.2f} std"
    )

with col4:
    total_customers = filtered_df['Customers'].sum()
    st.metric(
        label="Total Customers",
        value=f"{total_customers:,}",
        delta=f"{(total_customers / df['Customers'].sum() * 100):.1f}% of total"
    )

st.markdown("---")

# Charts
tab1, tab2, tab3, tab4 = st.tabs(["📈 Trends", "📊 Categories", "🌍 Regions", "📉 Detailed Analysis"])

with tab1:
    st.subheader("Sales Trends Over Time")
    
    # Aggregate daily sales
    daily_sales = filtered_df.groupby('Date')['Sales'].sum().reset_index()
    
    fig_line = px.line(
        daily_sales,
        x='Date',
        y='Sales',
        title='Daily Sales Trend',
        labels={'Sales': 'Total Sales ($)'},
        template='plotly_white'
    )
    fig_line.update_traces(line_color='#1f77b4', line_width=2)
    fig_line.update_layout(height=400)
    st.plotly_chart(fig_line, use_container_width=True)
    
    # Moving average
    daily_sales['MA7'] = daily_sales['Sales'].rolling(window=7).mean()
    
    fig_ma = go.Figure()
    fig_ma.add_trace(go.Scatter(
        x=daily_sales['Date'],
        y=daily_sales['Sales'],
        mode='lines',
        name='Daily Sales',
        line=dict(color='lightgray', width=1)
    ))
    fig_ma.add_trace(go.Scatter(
        x=daily_sales['Date'],
        y=daily_sales['MA7'],
        mode='lines',
        name='7-Day Moving Average',
        line=dict(color='#ff7f0e', width=3)
    ))
    fig_ma.update_layout(
        title='Sales with 7-Day Moving Average',
        xaxis_title='Date',
        yaxis_title='Sales ($)',
        template='plotly_white',
        height=400
    )
    st.plotly_chart(fig_ma, use_container_width=True)

with tab2:
    st.subheader("Sales by Category")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Bar chart
        category_sales = filtered_df.groupby('Category')['Sales'].sum().reset_index()
        category_sales = category_sales.sort_values('Sales', ascending=False)
        
        fig_bar = px.bar(
            category_sales,
            x='Category',
            y='Sales',
            title='Total Sales by Category',
            labels={'Sales': 'Total Sales ($)'},
            template='plotly_white',
            color='Sales',
            color_continuous_scale='Blues'
        )
        fig_bar.update_layout(height=400)
        st.plotly_chart(fig_bar, use_container_width=True)
    
    with col2:
        # Pie chart
        fig_pie = px.pie(
            category_sales,
            values='Sales',
            names='Category',
            title='Sales Distribution by Category',
            template='plotly_white'
        )
        fig_pie.update_layout(height=400)
        st.plotly_chart(fig_pie, use_container_width=True)

with tab3:
    st.subheader("Sales by Region")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Region bar chart
        region_sales = filtered_df.groupby('Region')['Sales'].sum().reset_index()
        region_sales = region_sales.sort_values('Sales', ascending=False)
        
        fig_region = px.bar(
            region_sales,
            x='Region',
            y='Sales',
            title='Total Sales by Region',
            labels={'Sales': 'Total Sales ($)'},
            template='plotly_white',
            color='Sales',
            color_continuous_scale='Greens'
        )
        fig_region.update_layout(height=400)
        st.plotly_chart(fig_region, use_container_width=True)
    
    with col2:
        # Category performance by region
        region_category = filtered_df.groupby(['Region', 'Category'])['Sales'].sum().reset_index()
        
        fig_stacked = px.bar(
            region_category,
            x='Region',
            y='Sales',
            color='Category',
            title='Category Performance by Region',
            labels={'Sales': 'Total Sales ($)'},
            template='plotly_white',
            barmode='stack'
        )
        fig_stacked.update_layout(height=400)
        st.plotly_chart(fig_stacked, use_container_width=True)

with tab4:
    st.subheader("Detailed Analysis")
    
    # Scatter plot
    category_region = filtered_df.groupby(['Category', 'Region']).agg({
        'Sales': 'sum',
        'Units': 'sum',
        'Customers': 'sum'
    }).reset_index()
    
    fig_scatter = px.scatter(
        category_region,
        x='Units',
        y='Sales',
        size='Customers',
        color='Category',
        hover_data=['Region'],
        title='Sales vs Units (bubble size = customers)',
        labels={'Units': 'Units Sold', 'Sales': 'Total Sales ($)'},
        template='plotly_white'
    )
    fig_scatter.update_layout(height=500)
    st.plotly_chart(fig_scatter, use_container_width=True)
    
    # Data table
    st.subheader("Raw Data Preview")
    st.dataframe(
        filtered_df.sort_values('Date', ascending=False).head(100),
        use_container_width=True,
        hide_index=True
    )
    
    # Download button
    csv = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download Filtered Data as CSV",
        data=csv,
        file_name="dashboard_data.csv",
        mime="text/csv"
    )

# Footer
st.markdown("---")
st.markdown("Built with Streamlit 📊 | Data refreshes automatically")
