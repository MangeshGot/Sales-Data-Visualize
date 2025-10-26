import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import io

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

def validate_and_prepare_data(df):
    """Validate and prepare uploaded data"""
    required_columns = {'Date', 'Category', 'Region', 'Sales', 'Units', 'Customers'}
    
    # Check if all required columns exist
    missing_columns = required_columns - set(df.columns)
    if missing_columns:
        st.error(f"Missing required columns: {', '.join(missing_columns)}")
        st.info("Required columns: Date, Category, Region, Sales, Units, Customers")
        return None
    
    # Try to convert Date column to datetime
    try:
        df['Date'] = pd.to_datetime(df['Date'])
    except Exception as e:
        st.error(f"Error converting 'Date' column to datetime: {e}")
        return None
    
    # Ensure numeric columns are numeric
    numeric_columns = ['Sales', 'Units', 'Customers']
    for col in numeric_columns:
        try:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        except Exception as e:
            st.error(f"Error converting '{col}' to numeric: {e}")
            return None
    
    # Drop rows with missing values
    df = df.dropna()
    
    if len(df) == 0:
        st.error("No valid data remaining after cleaning")
        return None
    
    return df

def load_uploaded_file(uploaded_file):
    """Load data from uploaded CSV or Excel file"""
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(uploaded_file)
        else:
            st.error("Unsupported file format. Please upload CSV or Excel file.")
            return None
        
        return validate_and_prepare_data(df)
    
    except Exception as e:
        st.error(f"Error loading file: {e}")
        return None

# Header
st.title("📊 Sales Dashboard")
st.markdown("### Interactive data visualization and analytics")

# Sidebar - Data Source Selection
st.sidebar.header("Data Source")

data_source = st.sidebar.radio(
    "Choose data source:",
    ["Sample Data", "Upload File"],
    help="Use sample data or upload your own CSV/Excel file"
)

df = None

if data_source == "Sample Data":
    df = generate_sample_data()
    st.sidebar.success("Using sample sales data")
else:
    st.sidebar.markdown("Upload a CSV or Excel file with columns:")
    st.sidebar.code("Date, Category, Region, Sales, Units, Customers")
    
    uploaded_file = st.sidebar.file_uploader(
        "Choose a file",
        type=['csv', 'xlsx', 'xls'],
        help="Upload CSV or Excel file"
    )
    
    if uploaded_file is not None:
        df = load_uploaded_file(uploaded_file)
        if df is not None:
            st.sidebar.success(f"Loaded {len(df)} rows from {uploaded_file.name}")
    else:
        st.info("Please upload a file to continue")
        st.stop()

# If no valid data, stop (but clear dataset signature to force reset on next load)
if df is None or len(df) == 0:
    # Clear dataset signature so filters reset on next successful load
    if 'dataset_signature' in st.session_state:
        del st.session_state.dataset_signature
    st.warning("No data available. Please check your file or use sample data.")
    st.stop()

# Store in session state for other pages
st.session_state.df = df

# Sidebar filters
st.sidebar.header("Filters")

# Get current dataset characteristics
min_date = df['Date'].min().date()
max_date = df['Date'].max().date()
available_categories = sorted(df['Category'].unique())
available_regions = sorted(df['Region'].unique())

# Create a signature for the current dataset
current_dataset_signature = {
    'source': data_source,
    'categories': tuple(available_categories),
    'regions': tuple(available_regions),
    'date_range': (min_date, max_date)
}

# Check if dataset has changed (compare with stored signature)
dataset_changed = False
if 'dataset_signature' not in st.session_state:
    dataset_changed = True
elif st.session_state.dataset_signature != current_dataset_signature:
    dataset_changed = True

# Update signature only after confirming we have valid data
st.session_state.dataset_signature = current_dataset_signature

# Initialize or reset filters when dataset changes
if dataset_changed or 'filter_date_range' not in st.session_state:
    st.session_state.filter_date_range = (min_date, max_date)
    st.session_state.filter_categories = available_categories
    st.session_state.filter_regions = available_regions
    
    # Clear widget keys to prevent validation errors with stale values
    if 'date_range_input' in st.session_state:
        del st.session_state['date_range_input']
    if 'categories_input' in st.session_state:
        del st.session_state['categories_input']
    if 'regions_input' in st.session_state:
        del st.session_state['regions_input']

# Validate and clean filter values to ensure they're valid for current dataset
valid_categories = [cat for cat in st.session_state.filter_categories if cat in available_categories]
valid_regions = [reg for reg in st.session_state.filter_regions if reg in available_regions]

# If all filters were invalidated, reset to all available options
if not valid_categories:
    valid_categories = available_categories
if not valid_regions:
    valid_regions = available_regions

# Update session state with validated values BEFORE rendering widgets
st.session_state.filter_categories = valid_categories
st.session_state.filter_regions = valid_regions

# Validate date range
try:
    filter_start, filter_end = st.session_state.filter_date_range
    if filter_start < min_date or filter_end > max_date:
        st.session_state.filter_date_range = (min_date, max_date)
except (ValueError, TypeError):
    st.session_state.filter_date_range = (min_date, max_date)

# Date range filter
date_range = st.sidebar.date_input(
    "Date Range",
    value=st.session_state.filter_date_range,
    min_value=min_date,
    max_value=max_date,
    key='date_range_input'
)

# Category filter
categories = st.sidebar.multiselect(
    "Categories",
    options=available_categories,
    default=st.session_state.filter_categories,
    key='categories_input'
)

# Region filter
regions = st.sidebar.multiselect(
    "Regions",
    options=available_regions,
    default=st.session_state.filter_regions,
    key='regions_input'
)

# Update session state with user selections
st.session_state.filter_date_range = date_range
st.session_state.filter_categories = categories
st.session_state.filter_regions = regions

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

# Check if filtered data is empty
if len(filtered_df) == 0:
    st.warning("No data matches the selected filters. Please adjust your filters.")
    st.stop()

# Store filtered data in session state for other pages
st.session_state.filtered_df = filtered_df

# Export Options in Sidebar
st.sidebar.markdown("---")
st.sidebar.header("Export Options")

# Create summary report for export
def create_summary_report(df, filtered_df):
    """Create a comprehensive Excel report with multiple sheets"""
    output = io.BytesIO()
    
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # Sheet 1: Summary Statistics
        summary_data = {
            'Metric': [
                'Total Sales',
                'Total Units',
                'Total Customers',
                'Average Sale',
                'Number of Transactions',
                'Date Range Start',
                'Date Range End',
                'Number of Categories',
                'Number of Regions'
            ],
            'Value': [
                f"${filtered_df['Sales'].sum():,.2f}",
                f"{filtered_df['Units'].sum():,}",
                f"{filtered_df['Customers'].sum():,}",
                f"${filtered_df['Sales'].mean():,.2f}",
                f"{len(filtered_df):,}",
                str(filtered_df['Date'].min().date()),
                str(filtered_df['Date'].max().date()),
                filtered_df['Category'].nunique(),
                filtered_df['Region'].nunique()
            ]
        }
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_excel(writer, sheet_name='Summary', index=False)
        
        # Sheet 2: Sales by Category
        category_sales = filtered_df.groupby('Category').agg({
            'Sales': 'sum',
            'Units': 'sum',
            'Customers': 'sum'
        }).reset_index()
        category_sales.columns = ['Category', 'Total Sales', 'Total Units', 'Total Customers']
        category_sales = category_sales.sort_values('Total Sales', ascending=False)
        category_sales.to_excel(writer, sheet_name='By Category', index=False)
        
        # Sheet 3: Sales by Region
        region_sales = filtered_df.groupby('Region').agg({
            'Sales': 'sum',
            'Units': 'sum',
            'Customers': 'sum'
        }).reset_index()
        region_sales.columns = ['Region', 'Total Sales', 'Total Units', 'Total Customers']
        region_sales = region_sales.sort_values('Total Sales', ascending=False)
        region_sales.to_excel(writer, sheet_name='By Region', index=False)
        
        # Sheet 4: Daily Sales Trends
        daily_sales = filtered_df.groupby('Date').agg({
            'Sales': 'sum',
            'Units': 'sum',
            'Customers': 'sum'
        }).reset_index()
        daily_sales.columns = ['Date', 'Total Sales', 'Total Units', 'Total Customers']
        daily_sales.to_excel(writer, sheet_name='Daily Trends', index=False)
        
        # Sheet 5: Raw Data
        filtered_df.to_excel(writer, sheet_name='Raw Data', index=False)
    
    return output.getvalue()

# Export buttons
st.sidebar.download_button(
    label="📥 Download Summary Report (Excel)",
    data=create_summary_report(df, filtered_df),
    file_name=f"sales_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    help="Download comprehensive Excel report with summary statistics and breakdowns"
)

st.sidebar.download_button(
    label="📥 Download Filtered Data (CSV)",
    data=filtered_df.to_csv(index=False).encode('utf-8'),
    file_name=f"filtered_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
    mime="text/csv",
    help="Download filtered data as CSV"
)

st.sidebar.info("💡 **Chart Export:** Hover over any chart and click the camera icon to download it as PNG")

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
    st.plotly_chart(fig_line, width='stretch')
    
    # Moving average
    if len(daily_sales) >= 7:
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
        st.plotly_chart(fig_ma, width='stretch')
    
    # Area chart
    st.subheader("Sales Area Chart")
    fig_area = px.area(
        daily_sales,
        x='Date',
        y='Sales',
        title='Sales Over Time (Area View)',
        labels={'Sales': 'Total Sales ($)'},
        template='plotly_white'
    )
    fig_area.update_traces(fillcolor='rgba(31, 119, 180, 0.3)', line_color='#1f77b4')
    fig_area.update_layout(height=400)
    st.plotly_chart(fig_area, width='stretch')

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
        st.plotly_chart(fig_bar, width='stretch')
    
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
        st.plotly_chart(fig_pie, width='stretch')

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
        st.plotly_chart(fig_region, width='stretch')
    
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
        st.plotly_chart(fig_stacked, width='stretch')
    
    # Heatmap
    st.subheader("Sales Heatmap: Category vs Region")
    heatmap_data = filtered_df.pivot_table(
        values='Sales',
        index='Category',
        columns='Region',
        aggfunc='sum',
        fill_value=0
    )
    
    fig_heatmap = px.imshow(
        heatmap_data,
        labels=dict(x="Region", y="Category", color="Sales ($)"),
        title="Sales Intensity by Category and Region",
        template='plotly_white',
        color_continuous_scale='YlOrRd',
        aspect='auto'
    )
    fig_heatmap.update_layout(height=400)
    st.plotly_chart(fig_heatmap, width='stretch')

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
    st.plotly_chart(fig_scatter, width='stretch')
    
    # Data table
    st.subheader("Raw Data Preview")
    st.dataframe(
        filtered_df.sort_values('Date', ascending=False).head(100),
        width='stretch',
        hide_index=True
    )

# Footer
st.markdown("---")
st.markdown("Built with Streamlit 📊 | Data refreshes automatically")
