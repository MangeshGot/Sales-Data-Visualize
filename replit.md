# Overview

This is a comprehensive data visualization and analytics dashboard built with Streamlit. The application provides interactive charts, advanced analytics, and data exploration capabilities for sales data analysis. It uses Plotly for rich, interactive visualizations and supports both sample data generation and custom data uploads (CSV/Excel). The dashboard is designed as a multi-page application that allows users to explore sales patterns across different categories, regions, and time periods.

## Recent Updates (October 2025)

- Added CSV/Excel file upload functionality with robust data validation
- Implemented comprehensive export features (multi-sheet Excel reports, CSV downloads)
- Created multi-page dashboard structure with navigation
- Added advanced chart types (heatmaps, area charts, correlation matrices, Pareto charts)
- Implemented smart filter persistence with dataset change detection
- Enhanced session state management for seamless cross-page navigation

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Frontend Architecture

**Framework**: Streamlit-based web application
- Multi-page application structure using Streamlit's native page routing
- Pages organized in a `/pages` directory with numbered prefixes for ordering
- Main entry point: `app.py` handles primary dashboard and data loading
- Wide layout configuration for better data visualization real estate

**State Management**: Advanced session state with dataset tracking
- Central data storage in `st.session_state.df` for the main dataset
- Filtered data cached in `st.session_state.filtered_df` for cross-page consistency
- Filter state persistence: `filter_date_range`, `filter_categories`, `filter_regions`
- Dataset change detection via signature tracking to prevent validation errors
- Session state enables data sharing across multiple pages without re-loading

**Visualization Strategy**: Plotly for interactive charts
- Uses both Plotly Express (px) for quick charts and Plotly Graph Objects (go) for custom visualizations
- Supports multiple chart types: bar, line, area, scatter, box, violin, histogram, heatmap, pie
- Interactive features built-in (zoom, pan, hover tooltips, camera icon for PNG export)

## Data Layer

**Data Sources**: Dual-mode data loading
- **Sample Data**: Synthetic sales data generation with 90 days of data
- **File Upload**: CSV/Excel file upload with comprehensive validation
  - Required columns: Date, Category, Region, Sales, Units, Customers
  - Automatic type conversion and data cleaning
  - Error handling with clear user feedback

**Data Validation Pipeline**:
1. File format detection (CSV, XLSX, XLS)
2. Required column verification
3. Date column conversion to datetime
4. Numeric column validation and type coercion
5. Missing value handling
6. Empty dataset detection

**Data Structure**: Pandas DataFrame
- Time-series data with daily granularity
- Multi-dimensional analysis support (Category × Region × Date)
- Calculated fields for advanced analytics (efficiency metrics, performance matrices)

## Application Pages

### Main Dashboard (`app.py`)
**Features**:
- Data source selection (Sample Data or Upload File)
- Smart filters with persistence and validation:
  - Date range picker
  - Multi-select categories
  - Multi-select regions
  - Filter state persists across page navigation
  - Automatic filter reset when dataset changes
- Key metrics dashboard (4 KPI cards)
- Export options:
  - Multi-sheet Excel summary report
  - Filtered CSV data download
  - Chart exports via Plotly's built-in camera icon
- Multiple visualization tabs:
  - **Trends**: Line charts, moving averages, area charts
  - **Categories**: Bar charts, pie charts
  - **Regions**: Bar charts, stacked bars, heatmaps
  - **Detailed Analysis**: Scatter plots, raw data preview

### Advanced Analytics (`pages/1_Advanced_Analytics.py`)
**Features**:
- Performance matrices (Category & Region)
- Correlation analysis with heatmap
- Box plots for distribution analysis
- Time series decomposition
- Top/Bottom performers analysis
- Pareto analysis (80/20 rule)
- Statistical aggregations and efficiency metrics

### Data Explorer (`pages/2_Data_Explorer.py`)
**Features**:
- Custom chart builder:
  - Configurable chart types (Bar, Line, Scatter, Box, Violin, Histogram)
  - Dynamic axis selection
  - Color-by options
- Advanced data filtering with sliders
- Quick statistics overview
- Statistical summary tables
- Comparison tools (Category vs Region)
- Interactive exploration with real-time updates

## Key Design Patterns

**Filter Persistence Architecture**:
- Dataset signature tracking (source, categories, regions, date range)
- Automatic filter reset on dataset changes
- Widget key cleanup to prevent validation errors
- Validated filter values applied before widget rendering
- Handles edge cases: failed uploads, dataset switches, invalid filter values

**Separation of Concerns**:
- Data generation/loading isolated in cached functions
- Each page handles its own specific analytics focus
- Shared data accessed through session state
- Clear separation between data, logic, and presentation

**Lazy Loading & Caching**:
- Sample data generation cached with `@st.cache_data`
- Guards against missing data with conditional rendering (`st.stop()`)
- Efficient data sharing via session state

**Modular Page Structure**:
- Each page operates independently but shares common data
- Consistent page configuration and layout patterns
- User warnings when prerequisite data is missing

## Export Functionality

**Excel Summary Reports** (Multi-sheet):
1. Summary Statistics
2. Sales by Category
3. Sales by Region
4. Daily Sales Trends
5. Raw Data

**CSV Exports**:
- Filtered data download
- Timestamp-based file naming

**Chart Exports**:
- Individual chart PNG downloads via Plotly camera icon
- All charts support interactive export

# External Dependencies

## Python Libraries

**Core Framework**:
- `streamlit`: Web application framework and UI components

**Data Processing**:
- `pandas`: Data manipulation and analysis
- `numpy`: Numerical computations and random data generation
- `openpyxl`: Excel file reading and writing

**Visualization**:
- `plotly`: Interactive visualization library
  - `plotly.express`: High-level plotting interface
  - `plotly.graph_objects`: Low-level plotting for custom visualizations
  - `plotly.subplots`: Multi-chart layouts
- `kaleido`: Static image export for Plotly charts

**Utilities**:
- `datetime`: Date/time handling for time-series data
- `io`: In-memory file operations for data upload/download

## Infrastructure

**Runtime**: Python 3.11-based Streamlit server
- Port 5000 (configured for Replit)
- No external database dependencies (in-memory data only)
- No external API integrations
- Self-contained application suitable for Replit deployment

## Technical Notes

**Session State Management**:
- All filter state persists across page navigation
- Dataset changes trigger automatic filter reset
- Widget keys cleared on dataset changes to prevent validation errors
- Comprehensive validation ensures filters are always valid for current dataset

**Error Handling**:
- Graceful handling of invalid file formats
- Clear user feedback for missing columns or invalid data
- Empty dataset detection and user warnings
- Failed upload recovery with dataset signature cleanup

**Performance Optimizations**:
- Sample data cached with deterministic seed
- Efficient session state usage
- Minimal recomputation through smart state management
