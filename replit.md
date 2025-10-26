# Overview

This is a data visualization and analytics dashboard built with Streamlit. The application provides interactive charts, advanced analytics, and data exploration capabilities for sales data analysis. It uses Plotly for rich, interactive visualizations and supports both sample data generation and custom data uploads. The dashboard is designed as a multi-page application that allows users to explore sales patterns across different categories, regions, and time periods.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Frontend Architecture

**Framework**: Streamlit-based web application
- Multi-page application structure using Streamlit's native page routing
- Pages organized in a `/pages` directory with numbered prefixes for ordering
- Main entry point: `app.py` handles primary dashboard and data loading
- Wide layout configuration for better data visualization real estate

**State Management**: Streamlit session state
- Central data storage in `st.session_state.df` for the main dataset
- Filtered data cached in `st.session_state.filtered_df` for cross-page consistency
- Session state enables data sharing across multiple pages without re-loading

**Visualization Strategy**: Plotly for interactive charts
- Uses both Plotly Express (px) for quick charts and Plotly Graph Objects (go) for custom visualizations
- Supports multiple chart types: bar, line, scatter, box, violin, and histogram plots
- Interactive features built-in (zoom, pan, hover tooltips)

## Data Layer

**Data Generation**: Synthetic sample data
- `@st.cache_data` decorator used for performance optimization
- Sample data simulates 90 days of sales across multiple dimensions:
  - Categories: Electronics, Clothing, Food & Beverage, Home & Garden, Sports
  - Regions: North, South, East, West
  - Metrics: Sales (with sinusoidal trends), Units, Customers
- Deterministic random seed (42) for reproducible sample data

**Data Structure**: Pandas DataFrame
- Time-series data with daily granularity
- Multi-dimensional analysis support (Category × Region × Date)
- Calculated fields for advanced analytics (efficiency metrics, performance matrices)

## Application Pages

**Main Dashboard** (`app.py`):
- Primary data loading interface (upload or sample data)
- Core filtering controls for cross-page use
- Overview visualizations and key metrics

**Advanced Analytics** (`pages/1_Advanced_Analytics.py`):
- Performance matrix calculations
- Statistical aggregations (sum, mean, standard deviation)
- Category and regional performance comparisons
- Efficiency metrics derived from sales and units data

**Data Explorer** (`pages/2_Data_Explorer.py`):
- Custom chart builder interface
- User-configurable visualizations
- Dynamic axis selection for exploratory analysis
- Multiple chart type options for different analysis needs

## Key Design Patterns

**Separation of Concerns**:
- Data generation isolated in cached functions
- Each page handles its own specific analytics focus
- Shared data accessed through session state

**Lazy Loading & Caching**:
- Sample data generation cached to avoid recomputation
- Guards against missing data with conditional rendering (`st.stop()`)

**Modular Page Structure**:
- Each page can operate independently but shares common data
- Consistent page configuration and layout patterns
- User warnings when prerequisite data is missing

# External Dependencies

## Python Libraries

**Core Framework**:
- `streamlit`: Web application framework and UI components

**Data Processing**:
- `pandas`: Data manipulation and analysis
- `numpy`: Numerical computations and random data generation

**Visualization**:
- `plotly.express`: High-level plotting interface
- `plotly.graph_objects`: Low-level plotting for custom visualizations
- `plotly.subplots`: Multi-chart layouts (imported but implementation not shown in provided files)

**Utilities**:
- `datetime`: Date/time handling for time-series data
- `io`: In-memory file operations (likely for data upload/download features)

## Infrastructure

**Runtime**: Python-based Streamlit server
- No external database dependencies (in-memory data only)
- No external API integrations shown
- Self-contained application suitable for Replit deployment