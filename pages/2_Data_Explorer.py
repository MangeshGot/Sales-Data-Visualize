import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="Data Explorer",
    page_icon="🔍",
    layout="wide"
)

st.title("🔍 Data Explorer")
st.markdown("### Interactive data exploration and custom visualizations")

# Check if data is loaded in session state
if 'df' not in st.session_state or st.session_state.df is None:
    st.warning("No data loaded. Please upload data or select sample data on the main page.")
    st.stop()

df = st.session_state.df
filtered_df = st.session_state.get('filtered_df', df)

st.markdown("---")

# Custom Chart Builder
st.subheader("Custom Chart Builder")

col1, col2, col3 = st.columns(3)

with col1:
    chart_type = st.selectbox(
        "Chart Type",
        ["Bar Chart", "Line Chart", "Scatter Plot", "Box Plot", "Violin Plot", "Histogram"]
    )

with col2:
    x_axis = st.selectbox(
        "X-Axis",
        ["Category", "Region", "Date"],
        key="x_axis"
    )

with col3:
    y_axis = st.selectbox(
        "Y-Axis",
        ["Sales", "Units", "Customers"],
        key="y_axis"
    )

# Color option
color_by = st.selectbox(
    "Color By (optional)",
    ["None", "Category", "Region"]
)

# Generate custom chart
if chart_type == "Bar Chart":
    agg_data = filtered_df.groupby(x_axis)[y_axis].sum().reset_index()
    if color_by != "None" and x_axis != color_by:
        fig = px.bar(filtered_df, x=x_axis, y=y_axis, color=color_by, 
                     title=f"{y_axis} by {x_axis}", template='plotly_white')
    else:
        fig = px.bar(agg_data, x=x_axis, y=y_axis, 
                     title=f"{y_axis} by {x_axis}", template='plotly_white')

elif chart_type == "Line Chart":
    agg_data = filtered_df.groupby(x_axis)[y_axis].sum().reset_index()
    fig = px.line(agg_data, x=x_axis, y=y_axis, 
                  title=f"{y_axis} Trend", template='plotly_white')

elif chart_type == "Scatter Plot":
    if color_by != "None":
        fig = px.scatter(filtered_df, x=x_axis, y=y_axis, color=color_by,
                        title=f"{y_axis} vs {x_axis}", template='plotly_white')
    else:
        fig = px.scatter(filtered_df, x=x_axis, y=y_axis,
                        title=f"{y_axis} vs {x_axis}", template='plotly_white')

elif chart_type == "Box Plot":
    fig = px.box(filtered_df, x=x_axis, y=y_axis, color=color_by if color_by != "None" else None,
                 title=f"{y_axis} Distribution by {x_axis}", template='plotly_white')

elif chart_type == "Violin Plot":
    fig = px.violin(filtered_df, x=x_axis, y=y_axis, color=color_by if color_by != "None" else None,
                    title=f"{y_axis} Distribution by {x_axis}", template='plotly_white', box=True)

else:  # Histogram
    fig = px.histogram(filtered_df, x=y_axis, nbins=30, 
                       title=f"{y_axis} Distribution", template='plotly_white')

fig.update_layout(height=500)
st.plotly_chart(fig, width='stretch')

st.markdown("---")

# Data Filtering and Search
st.subheader("Advanced Data Filtering")

col1, col2 = st.columns(2)

with col1:
    sales_range = st.slider(
        "Sales Range ($)",
        float(filtered_df['Sales'].min()),
        float(filtered_df['Sales'].max()),
        (float(filtered_df['Sales'].min()), float(filtered_df['Sales'].max()))
    )

with col2:
    units_range = st.slider(
        "Units Range",
        int(filtered_df['Units'].min()),
        int(filtered_df['Units'].max()),
        (int(filtered_df['Units'].min()), int(filtered_df['Units'].max()))
    )

# Apply filters
custom_filtered = filtered_df[
    (filtered_df['Sales'] >= sales_range[0]) &
    (filtered_df['Sales'] <= sales_range[1]) &
    (filtered_df['Units'] >= units_range[0]) &
    (filtered_df['Units'] <= units_range[1])
]

st.info(f"Showing {len(custom_filtered):,} of {len(filtered_df):,} records")

# Display filtered data
st.dataframe(
    custom_filtered.sort_values('Date', ascending=False),
    width='stretch',
    hide_index=True
)

st.markdown("---")

# Quick Statistics
st.subheader("Quick Statistics")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Records",
        f"{len(custom_filtered):,}",
        f"{((len(custom_filtered) / len(filtered_df) * 100) - 100):.1f}%"
    )

with col2:
    st.metric(
        "Avg Sales",
        f"${custom_filtered['Sales'].mean():,.2f}",
        f"{((custom_filtered['Sales'].mean() / filtered_df['Sales'].mean() * 100) - 100):.1f}%"
    )

with col3:
    st.metric(
        "Avg Units",
        f"{custom_filtered['Units'].mean():,.1f}",
        f"{((custom_filtered['Units'].mean() / filtered_df['Units'].mean() * 100) - 100):.1f}%"
    )

with col4:
    st.metric(
        "Avg Customers",
        f"{custom_filtered['Customers'].mean():,.1f}",
        f"{((custom_filtered['Customers'].mean() / filtered_df['Customers'].mean() * 100) - 100):.1f}%"
    )

st.markdown("---")

# Statistical Summary
st.subheader("Statistical Summary")

summary_stats = custom_filtered[['Sales', 'Units', 'Customers']].describe()
summary_stats = summary_stats.transpose()

st.dataframe(
    summary_stats.style.format('{:,.2f}'),
    width='stretch'
)

st.markdown("---")

# Comparison Tool
st.subheader("Category/Region Comparison")

comparison_type = st.radio("Compare by:", ["Category", "Region"], horizontal=True)

if comparison_type == "Category":
    selected_items = st.multiselect(
        "Select categories to compare",
        options=sorted(filtered_df['Category'].unique()),
        default=sorted(filtered_df['Category'].unique())[:3]
    )
    comparison_data = filtered_df[filtered_df['Category'].isin(selected_items)]
    group_col = 'Category'
else:
    selected_items = st.multiselect(
        "Select regions to compare",
        options=sorted(filtered_df['Region'].unique()),
        default=sorted(filtered_df['Region'].unique())[:2]
    )
    comparison_data = filtered_df[filtered_df['Region'].isin(selected_items)]
    group_col = 'Region'

if len(selected_items) > 0:
    # Comparison metrics
    comparison_summary = comparison_data.groupby(group_col).agg({
        'Sales': ['sum', 'mean', 'count'],
        'Units': 'sum',
        'Customers': 'sum'
    }).reset_index()
    
    comparison_summary.columns = [group_col, 'Total Sales', 'Avg Sale', 'Transactions', 'Total Units', 'Total Customers']
    
    st.dataframe(
        comparison_summary.style.format({
            'Total Sales': '${:,.2f}',
            'Avg Sale': '${:,.2f}',
            'Transactions': '{:,.0f}',
            'Total Units': '{:,.0f}',
            'Total Customers': '{:,.0f}'
        }),
        width='stretch',
        hide_index=True
    )
    
    # Comparison visualization
    col1, col2 = st.columns(2)
    
    with col1:
        fig_compare = px.bar(
            comparison_summary,
            x=group_col,
            y='Total Sales',
            title=f'Total Sales Comparison by {group_col}',
            template='plotly_white',
            color='Total Sales',
            color_continuous_scale='Blues'
        )
        fig_compare.update_layout(height=400)
        st.plotly_chart(fig_compare, width='stretch')
    
    with col2:
        fig_avg = px.bar(
            comparison_summary,
            x=group_col,
            y='Avg Sale',
            title=f'Average Sale Comparison by {group_col}',
            template='plotly_white',
            color='Avg Sale',
            color_continuous_scale='Greens'
        )
        fig_avg.update_layout(height=400)
        st.plotly_chart(fig_avg, width='stretch')

else:
    st.info(f"Please select at least one {comparison_type.lower()} to compare")

st.markdown("---")
st.markdown("*Use the Data Explorer to create custom views and deep dive into your data*")
