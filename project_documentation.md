# InsightForge - Interactive Data Processing & Reporting App

## Project Overview
InsightForge is a comprehensive data processing and visualization application designed to help users analyze, clean, and visualize their data efficiently. The application provides a user-friendly interface for handling various data formats and generating insightful visualizations.

## Project Structure
```
Tool_automated-sales-reporting/
├── gui.py                 # Main GUI implementation
├── visualization.py       # Visualization functionality
├── pivots.py             # Pivot table functionality
├── Logic.py              # Core business logic
├── main.py               # Application entry point
├── requirements.txt      # Project dependencies
└── visualizations/       # Generated visualization files
```

## Core Features

### 1. Data Processing
- **File Handling**
  - Support for multiple file formats (CSV, XLSX)
  - Single file and multiple file processing
  - Folder-based processing

- **Data Cleaning**
  - Missing value handling
  - Duplicate removal
  - Text cleaning
  - Date/time standardization
  - Numeric data cleaning
  - Categorical data cleaning
  - Column standardization
  - Data type conversion

### 2. Data Analysis
- **Pivot Tables**
  - Customizable pivot table creation
  - Multiple aggregation functions
  - Row and column grouping

- **Visualizations**
  - Time Series Analysis
  - Category Analysis
  - Correlation Analysis
  - Distribution Analysis
  - Comparative Analysis
  - Trend Analysis

### 3. User Interface
- **Main Window**
  - File selection interface
  - Data preview
  - Action buttons
  - Status bar

- **Configuration Windows**
  - Data cleaning options
  - Visualization settings
  - Pivot table configuration

## Detailed Functionality

### GUI Module (gui.py)
1. **Main Window Setup**
   - Creates the main application window
   - Sets up the title and geometry
   - Initializes custom styles

2. **File Processing**
   - `select_files()`: Handles file selection
   - `process_files()`: Processes selected files
   - `update_preview()`: Updates data preview

3. **Data Cleaning**
   - `apply_cleaning()`: Applies cleaning operations
   - `handle_missing_values_and_duplicates()`: Manages data cleaning options

### Visualization Module (visualization.py)
1. **Visualization Configuration**
   - `VisualizationConfig` class
   - Analysis type selection
   - Column selection
   - Visualization generation

2. **Analysis Types**
   - Time Series Analysis
   - Category Analysis
   - Correlation Analysis
   - Distribution Analysis
   - Comparative Analysis
   - Trend Analysis

### Pivot Module (pivots.py)
1. **Pivot Table Creation**
   - `create_pivot_table_window()`
   - Row and column selection
   - Value aggregation
   - Custom calculations

## Common Questions & Answers

### Q: What file formats does the application support?
A: The application supports CSV and Excel (XLSX) file formats.

### Q: How do I clean my data?
A: The application provides multiple cleaning options:
- Missing value handling (replace, drop rows, drop columns)
- Duplicate removal
- Text cleaning
- Date/time standardization
- Numeric data cleaning
- Categorical data cleaning
- Column standardization
- Data type conversion

### Q: What types of visualizations can I create?
A: You can create six types of visualizations:
1. Time Series Analysis
2. Category Analysis
3. Correlation Analysis
4. Distribution Analysis
5. Comparative Analysis
6. Trend Analysis

### Q: How do I create a pivot table?
A: 
1. Load your data
2. Click "Create Pivot Table"
3. Select rows, columns, and values
4. Choose aggregation function
5. Generate the pivot table

### Q: Can I save my cleaned data?
A: Yes, you can save your cleaned data in either CSV or Excel format using the "Save Cleaned Data" button.

### Q: What are the system requirements?
A: The application requires:
- Python 3.11 or higher
- Required packages (listed in requirements.txt)
- Sufficient memory for data processing
- Web browser for visualization display

## Technical Details

### Dependencies
```
pandas>=2.0.0
numpy>=1.24.0
plotly>=5.18.0
pillow>=8.3.0
openpyxl>=3.0.0
```

### Data Processing Flow
1. File Selection
2. Data Loading
3. Data Cleaning
4. Data Analysis
5. Visualization Generation
6. Results Export

### Error Handling
- File format validation
- Data type checking
- Missing value handling
- Memory management
- User input validation

## Best Practices

### Data Preparation
1. Ensure data is in a supported format
2. Check for consistent column names
3. Verify data types
4. Handle missing values appropriately

### Visualization
1. Choose appropriate chart types
2. Use meaningful labels
3. Consider data scale
4. Maintain consistent formatting

### Performance
1. Process large files in chunks
2. Use appropriate data types
3. Clean data before analysis
4. Save intermediate results

## Troubleshooting

### Common Issues
1. **File Loading Errors**
   - Check file format
   - Verify file integrity
   - Ensure proper encoding

2. **Memory Issues**
   - Process data in chunks
   - Clear unnecessary variables
   - Close unused visualizations

3. **Visualization Errors**
   - Check data types
   - Verify column selection
   - Ensure sufficient data points

### Support
For additional support:
1. Check the documentation
2. Review error messages
3. Contact support team
4. Check for updates 

def launch_gui():
    # Creates the main application window
    root = tk.Tk()
    root.title("InsightForge-Interactive-Data-Processing-Reporting-App")
    root.geometry("900x700") 

def select_files():
    file_type = file_selection_var.get()
    if file_type == "Single File":
        file = filedialog.askopenfilename(title="Select a Sales File", filetypes=[("CSV/XLSX Files", "*.csv *.xlsx")]) 

def process_files():
    try:
        dataframes = []
        for file in selected_files:
            if file.endswith(".csv"):
                df = pd.read_csv(file, delimiter=delimiter)
            elif file.endswith(".xlsx"):
                df = pd.read_excel(file) 

def apply_cleaning():
    try:
        missing_strategy = missing_value_strategy_var.get()
        if missing_strategy == "Replace with Default":
            df.fillna("Unknown", inplace=True)  # Replace missing values
            df.drop_duplicates(inplace=True)    # Remove duplicates
    except Exception as e:
        print(f"Error applying cleaning: {e}")

def __init__(self, root, df):
    self.root = root
    self.df = df
    self.selected_columns = []
    self.analysis_type = None 

def generate_analysis(self):
    if self.analysis_type == "Time Series Analysis":
        self.generate_time_series_analysis()
    elif self.analysis_type == "Category Analysis":
        self.generate_category_analysis() 

def show_config_window(self):
    self.config_window = tk.Toplevel(self.root)
    self.config_window.title("Data Analysis & Visualization") 

def generate_time_series_analysis(self):
    fig = sp.make_subplots(rows=2, cols=2)
    fig.add_trace(go.Scatter(x=df[date_col], y=df[value_col])) 

def generate_category_analysis(self):
    fig = go.Figure(data=[go.Bar(x=categories, y=values)]) 

def create_pivot_table_window(root, df):
    pivot_window = tk.Toplevel(root)
    pivot_window.title("Create Pivot Table") 

def generate_pivot_table(df, rows, columns, values, aggfunc):
    pivot = pd.pivot_table(df, values=values, index=rows, columns=columns, aggfunc=aggfunc) 

# User selects a CSV file
file = "sales_data.csv"
df = pd.read_csv(file)
# DataFrame contains:
# Date | Product | Region | Sales | Quantity 

# Create time series analysis
viz = VisualizationConfig(root, df)
viz.analysis_type = "Time Series Analysis"
viz.date_column = "Date"
viz.value_column = "Sales"
viz.generate_analysis()
# Generates a plot showing sales trends over time 

# Create pivot table
pivot = pd.pivot_table(df, 
                      values='Sales',
                      index='Region',
                      columns='Product',
                      aggfunc='sum')
# Shows total sales by region and product 