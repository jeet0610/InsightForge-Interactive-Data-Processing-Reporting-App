import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import plotly.subplots as sp
import webbrowser
import os
import numpy as np
from datetime import datetime

class VisualizationConfig:
    def __init__(self, root, df):
        self.root = root
        self.df = df
        self.config_window = None
        self.selected_columns = []
        self.analysis_type = None
        self.date_column = None
        self.value_column = None
        self.category_column = None

    def show_config_window(self):
        """Show the configuration window for visualization settings."""
        self.config_window = tk.Toplevel(self.root)
        self.config_window.title("Data Analysis & Visualization")
        self.config_window.geometry("1000x800")
        self.config_window.configure(bg="#f0f0f0")

        # Title frame
        title_frame = tk.Frame(self.config_window, bg="#007BFF", height=50)
        title_frame.pack(fill="x")
        title_label = tk.Label(title_frame, text="Data Analysis & Visualization", 
                             font=("Arial", 16, "bold"), fg="white", bg="#007BFF")
        title_label.pack(pady=10)

        # Main content frame
        content_frame = tk.Frame(self.config_window, bg="#f0f0f0", padx=20, pady=20)
        content_frame.pack(fill="both", expand=True)

        # Welcome message
        welcome_label = tk.Label(content_frame, 
                               text="Welcome to the Data Analysis Dashboard!\n\n" +
                                    "We'll automatically analyze your data and show you the most important insights.\n" +
                                    "Click 'Generate Smart Dashboard' to get started.",
                               font=("Arial", 12),
                               bg="#f0f0f0",
                               wraplength=800)
        welcome_label.pack(pady=20)

        # Action Buttons
        button_frame = tk.Frame(self.config_window, bg="#f0f0f0")
        button_frame.pack(fill="x", pady=20)
        
        # Smart Dashboard Button
        smart_dashboard_button = tk.Button(button_frame, 
                                         text="Generate Smart Dashboard", 
                                         command=self.generate_smart_dashboard,
                                         bg="#4CAF50", 
                                         fg="white", 
                                         font=("Arial", 11), 
                                         padx=15, 
                                         pady=5)
        smart_dashboard_button.pack(side="left", padx=10)
        
        # Customize Button
        customize_button = tk.Button(button_frame, 
                                   text="Customize Analysis", 
                                   command=self.show_customization_options,
                                   bg="#2196F3", 
                                   fg="white", 
                                   font=("Arial", 11), 
                                   padx=15, 
                                   pady=5)
        customize_button.pack(side="left", padx=10)
        
        # Cancel Button
        cancel_button = tk.Button(button_frame, 
                                text="Cancel", 
                                command=self.config_window.destroy,
                                bg="#f44336", 
                                fg="white", 
                                font=("Arial", 11), 
                                padx=15, 
                                pady=5)
        cancel_button.pack(side="left", padx=10)

    def show_customization_options(self):
        """Show the customization options for advanced users."""
        # Clear the current window
        for widget in self.config_window.winfo_children():
            widget.destroy()
            
        # Show the original analysis type selection interface
        self.show_config_window()
        
        # Analysis Type Selection
        tk.Label(self.config_window, text="Select Analysis Type:", bg="#f0f0f0", 
                font=("Arial", 12, "bold")).pack(anchor="w", pady=10)
        
        self.analysis_combo = ttk.Combobox(self.config_window, 
                                         values=["Time Series Analysis", "Category Analysis", 
                                                "Correlation Analysis", "Distribution Analysis",
                                                "Comparative Analysis", "Trend Analysis"],
                                         state="readonly", width=40)
        self.analysis_combo.pack(fill="x", pady=5)
        self.analysis_combo.bind("<<ComboboxSelected>>", self.update_column_selection)

        # Column Selection Frame
        self.column_frame = tk.Frame(self.config_window, bg="#f0f0f0")
        self.column_frame.pack(fill="x", pady=10)

    def update_column_selection(self, event=None):
        """Update the column selection interface based on the analysis type."""
        # Clear previous widgets
        for widget in self.column_frame.winfo_children():
            widget.destroy()

        analysis_type = self.analysis_combo.get()
        
        if analysis_type == "Time Series Analysis":
            self.setup_time_series_selection()
        elif analysis_type == "Category Analysis":
            self.setup_category_selection()
        elif analysis_type == "Correlation Analysis":
            self.setup_correlation_selection()
        elif analysis_type == "Distribution Analysis":
            self.setup_distribution_selection()
        elif analysis_type == "Comparative Analysis":
            self.setup_comparative_selection()
        elif analysis_type == "Trend Analysis":
            self.setup_trend_selection()

    def setup_time_series_selection(self):
        """Setup interface for time series analysis."""
        tk.Label(self.column_frame, text="Date Column:", bg="#f0f0f0").pack(anchor="w")
        self.date_combo = ttk.Combobox(self.column_frame, values=list(self.df.columns), 
                                     state="readonly", width=40)
        self.date_combo.pack(fill="x", pady=5)

        tk.Label(self.column_frame, text="Value Column:", bg="#f0f0f0").pack(anchor="w")
        self.value_combo = ttk.Combobox(self.column_frame, values=list(self.df.columns), 
                                      state="readonly", width=40)
        self.value_combo.pack(fill="x", pady=5)

    def setup_category_selection(self):
        """Setup interface for category analysis."""
        tk.Label(self.column_frame, text="Category Column:", bg="#f0f0f0").pack(anchor="w")
        self.category_combo = ttk.Combobox(self.column_frame, values=list(self.df.columns), 
                                         state="readonly", width=40)
        self.category_combo.pack(fill="x", pady=5)

        tk.Label(self.column_frame, text="Value Column:", bg="#f0f0f0").pack(anchor="w")
        self.value_combo = ttk.Combobox(self.column_frame, values=list(self.df.columns), 
                                      state="readonly", width=40)
        self.value_combo.pack(fill="x", pady=5)

    def setup_correlation_selection(self):
        """Setup interface for correlation analysis."""
        tk.Label(self.column_frame, text="Select Numeric Columns:", bg="#f0f0f0").pack(anchor="w")
        self.correlation_listbox = tk.Listbox(self.column_frame, selectmode="multiple", 
                                            height=5, width=40)
        for col in self.df.select_dtypes(include=['number']).columns:
            self.correlation_listbox.insert(tk.END, col)
        self.correlation_listbox.pack(fill="x", pady=5)

    def setup_distribution_selection(self):
        """Setup interface for distribution analysis."""
        tk.Label(self.column_frame, text="Select Column:", bg="#f0f0f0").pack(anchor="w")
        self.distribution_combo = ttk.Combobox(self.column_frame, 
                                            values=list(self.df.select_dtypes(include=['number']).columns),
                                            state="readonly", width=40)
        self.distribution_combo.pack(fill="x", pady=5)

    def setup_comparative_selection(self):
        """Setup interface for comparative analysis."""
        tk.Label(self.column_frame, text="Category Column:", bg="#f0f0f0").pack(anchor="w")
        self.category_combo = ttk.Combobox(self.column_frame, values=list(self.df.columns), 
                                         state="readonly", width=40)
        self.category_combo.pack(fill="x", pady=5)

        tk.Label(self.column_frame, text="Value Column:", bg="#f0f0f0").pack(anchor="w")
        self.value_combo = ttk.Combobox(self.column_frame, values=list(self.df.columns), 
                                      state="readonly", width=40)
        self.value_combo.pack(fill="x", pady=5)

    def setup_trend_selection(self):
        """Setup interface for trend analysis."""
        tk.Label(self.column_frame, text="Date Column:", bg="#f0f0f0").pack(anchor="w")
        self.date_combo = ttk.Combobox(self.column_frame, values=list(self.df.columns), 
                                     state="readonly", width=40)
        self.date_combo.pack(fill="x", pady=5)

        tk.Label(self.column_frame, text="Value Column:", bg="#f0f0f0").pack(anchor="w")
        self.value_combo = ttk.Combobox(self.column_frame, values=list(self.df.columns), 
                                      state="readonly", width=40)
        self.value_combo.pack(fill="x", pady=5)

    def generate_analysis(self):
        """Generate the analysis and visualizations based on selected configurations."""
        try:
            analysis_type = self.analysis_combo.get()
            
            if not analysis_type:
                messagebox.showerror("Error", "Please select an analysis type")
                return

            # Create visualization directory if it doesn't exist
            if not os.path.exists('visualizations'):
                os.makedirs('visualizations')

            # Generate the appropriate analysis
            if analysis_type == "Time Series Analysis":
                self.generate_time_series_analysis()
            elif analysis_type == "Category Analysis":
                self.generate_category_analysis()
            elif analysis_type == "Correlation Analysis":
                self.generate_correlation_analysis()
            elif analysis_type == "Distribution Analysis":
                self.generate_distribution_analysis()
            elif analysis_type == "Comparative Analysis":
                self.generate_comparative_analysis()
            elif analysis_type == "Trend Analysis":
                self.generate_trend_analysis()

            messagebox.showinfo("Success", "Analysis generated and opened in your browser")
            self.config_window.destroy()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate analysis: {str(e)}")

    def generate_time_series_analysis(self):
        """Generate time series analysis with multiple visualizations."""
        date_col = self.date_combo.get()
        value_col = self.value_combo.get()
        
        if not date_col or not value_col:
            messagebox.showerror("Error", "Please select both date and value columns")
            return

        # Convert date column to datetime
        df = self.df.copy()
        df[date_col] = pd.to_datetime(df[date_col])
        
        # Create subplots
        fig = sp.make_subplots(rows=2, cols=2, 
                              subplot_titles=("Time Series", "Monthly Trend", 
                                            "Yearly Trend", "Moving Average"))

        # Time Series Plot
        fig.add_trace(
            go.Scatter(x=df[date_col], y=df[value_col], mode='lines+markers', name='Time Series'),
            row=1, col=1
        )

        # Monthly Trend
        monthly = df.groupby(df[date_col].dt.to_period('M'))[value_col].mean()
        fig.add_trace(
            go.Bar(x=monthly.index.astype(str), y=monthly.values, name='Monthly Average'),
            row=1, col=2
        )

        # Yearly Trend
        yearly = df.groupby(df[date_col].dt.year)[value_col].mean()
        fig.add_trace(
            go.Bar(x=yearly.index, y=yearly.values, name='Yearly Average'),
            row=2, col=1
        )

        # Moving Average
        window = 7
        df['MA'] = df[value_col].rolling(window=window).mean()
        fig.add_trace(
            go.Scatter(x=df[date_col], y=df['MA'], mode='lines', name=f'{window}-day MA'),
            row=2, col=2
        )

        # Update layout
        fig.update_layout(height=800, width=1200, title_text="Time Series Analysis")
        
        # Save and open
        output_file = f'visualizations/time_series_analysis.html'
        fig.write_html(output_file)
        webbrowser.open('file://' + os.path.abspath(output_file))

    def generate_category_analysis(self):
        """Generate category analysis with multiple visualizations."""
        category_col = self.category_combo.get()
        value_col = self.value_combo.get()
        
        if not category_col or not value_col:
            messagebox.showerror("Error", "Please select both category and value columns")
            return

        # Create subplots
        fig = sp.make_subplots(rows=2, cols=2, 
                              subplot_titles=("Category Distribution", "Category Comparison",
                                            "Top Categories", "Category Statistics"))

        # Category Distribution
        fig.add_trace(
            go.Bar(x=self.df[category_col].value_counts().index,
                  y=self.df[category_col].value_counts().values,
                  name='Distribution'),
            row=1, col=1
        )

        # Category Comparison
        category_means = self.df.groupby(category_col)[value_col].mean()
        fig.add_trace(
            go.Bar(x=category_means.index, y=category_means.values, name='Mean Values'),
            row=1, col=2
        )

        # Top Categories
        top_categories = self.df.groupby(category_col)[value_col].sum().nlargest(10)
        fig.add_trace(
            go.Bar(x=top_categories.index, y=top_categories.values, name='Top Categories'),
            row=2, col=1
        )

        # Category Statistics
        stats = self.df.groupby(category_col)[value_col].agg(['mean', 'std', 'min', 'max'])
        fig.add_trace(
            go.Box(x=self.df[category_col], y=self.df[value_col], name='Statistics'),
            row=2, col=2
        )

        # Update layout
        fig.update_layout(height=800, width=1200, title_text="Category Analysis")
        
        # Save and open
        output_file = f'visualizations/category_analysis.html'
        fig.write_html(output_file)
        webbrowser.open('file://' + os.path.abspath(output_file))

    def generate_correlation_analysis(self):
        """Generate correlation analysis."""
        selected_indices = self.correlation_listbox.curselection()
        if not selected_indices:
            messagebox.showerror("Error", "Please select at least two numeric columns")
            return

        selected_columns = [self.correlation_listbox.get(i) for i in selected_indices]
        if len(selected_columns) < 2:
            messagebox.showerror("Error", "Please select at least two numeric columns")
            return

        # Calculate correlation matrix
        corr_matrix = self.df[selected_columns].corr()

        # Create correlation heatmap
        fig = go.Figure(data=go.Heatmap(
            z=corr_matrix,
            x=selected_columns,
            y=selected_columns,
            colorscale='RdBu',
            zmin=-1,
            zmax=1
        ))

        # Update layout
        fig.update_layout(
            title='Correlation Analysis',
            height=800,
            width=1200
        )

        # Save and open
        output_file = f'visualizations/correlation_analysis.html'
        fig.write_html(output_file)
        webbrowser.open('file://' + os.path.abspath(output_file))

    def generate_distribution_analysis(self):
        """Generate distribution analysis."""
        column = self.distribution_combo.get()
        if not column:
            messagebox.showerror("Error", "Please select a numeric column")
            return

        # Create subplots
        fig = sp.make_subplots(rows=2, cols=2, 
                              subplot_titles=("Histogram", "Box Plot",
                                            "Density Plot", "Q-Q Plot"))

        # Histogram
        fig.add_trace(
            go.Histogram(x=self.df[column], name='Histogram'),
            row=1, col=1
        )

        # Box Plot
        fig.add_trace(
            go.Box(y=self.df[column], name='Box Plot'),
            row=1, col=2
        )

        # Density Plot
        fig.add_trace(
            go.Histogram(x=self.df[column], histnorm='probability density', name='Density'),
            row=2, col=1
        )

        # Q-Q Plot
        sorted_data = np.sort(self.df[column].dropna())
        theoretical_quantiles = np.percentile(sorted_data, np.linspace(0, 100, len(sorted_data)))
        fig.add_trace(
            go.Scatter(x=theoretical_quantiles, y=sorted_data, mode='markers', name='Q-Q Plot'),
            row=2, col=2
        )

        # Update layout
        fig.update_layout(height=800, width=1200, title_text="Distribution Analysis")
        
        # Save and open
        output_file = f'visualizations/distribution_analysis.html'
        fig.write_html(output_file)
        webbrowser.open('file://' + os.path.abspath(output_file))

    def generate_comparative_analysis(self):
        """Generate comparative analysis."""
        category_col = self.category_combo.get()
        value_col = self.value_combo.get()
        
        if not category_col or not value_col:
            messagebox.showerror("Error", "Please select both category and value columns")
            return

        # Create subplots
        fig = sp.make_subplots(rows=2, cols=2, 
                              subplot_titles=("Category Comparison", "Category Distribution",
                                            "Category Statistics", "Category Trends"))

        # Category Comparison
        category_means = self.df.groupby(category_col)[value_col].mean()
        fig.add_trace(
            go.Bar(x=category_means.index, y=category_means.values, name='Mean Values'),
            row=1, col=1
        )

        # Category Distribution
        fig.add_trace(
            go.Box(x=self.df[category_col], y=self.df[value_col], name='Distribution'),
            row=1, col=2
        )

        # Category Statistics
        stats = self.df.groupby(category_col)[value_col].agg(['mean', 'std', 'min', 'max'])
        fig.add_trace(
            go.Table(
                header=dict(values=['Category'] + list(stats.columns)),
                cells=dict(values=[stats.index] + [stats[col] for col in stats.columns])
            ),
            row=2, col=1
        )

        # Category Trends
        if pd.api.types.is_datetime64_any_dtype(self.df[category_col]):
            trend = self.df.groupby(category_col)[value_col].mean()
            fig.add_trace(
                go.Scatter(x=trend.index, y=trend.values, mode='lines+markers', name='Trend'),
                row=2, col=2
            )

        # Update layout
        fig.update_layout(height=800, width=1200, title_text="Comparative Analysis")
        
        # Save and open
        output_file = f'visualizations/comparative_analysis.html'
        fig.write_html(output_file)
        webbrowser.open('file://' + os.path.abspath(output_file))

    def generate_trend_analysis(self):
        """Generate trend analysis."""
        date_col = self.date_combo.get()
        value_col = self.value_combo.get()
        
        if not date_col or not value_col:
            messagebox.showerror("Error", "Please select both date and value columns")
            return

        # Convert date column to datetime
        df = self.df.copy()
        df[date_col] = pd.to_datetime(df[date_col])
        
        # Create subplots
        fig = sp.make_subplots(rows=2, cols=2, 
                              subplot_titles=("Trend Line", "Seasonal Decomposition",
                                            "Moving Average", "Trend Statistics"))

        # Trend Line
        fig.add_trace(
            go.Scatter(x=df[date_col], y=df[value_col], mode='lines+markers', name='Trend'),
            row=1, col=1
        )

        # Seasonal Decomposition
        # Calculate moving average
        window = 12
        df['MA'] = df[value_col].rolling(window=window).mean()
        fig.add_trace(
            go.Scatter(x=df[date_col], y=df['MA'], mode='lines', name='Seasonal'),
            row=1, col=2
        )

        # Moving Average
        window = 7
        df['MA'] = df[value_col].rolling(window=window).mean()
        fig.add_trace(
            go.Scatter(x=df[date_col], y=df['MA'], mode='lines', name=f'{window}-day MA'),
            row=2, col=1
        )

        # Trend Statistics
        stats = df[value_col].describe()
        fig.add_trace(
            go.Table(
                header=dict(values=['Statistic', 'Value']),
                cells=dict(values=[stats.index, stats.values])
            ),
            row=2, col=2
        )

        # Update layout
        fig.update_layout(height=800, width=1200, title_text="Trend Analysis")
        
        # Save and open
        output_file = f'visualizations/trend_analysis.html'
        fig.write_html(output_file)
        webbrowser.open('file://' + os.path.abspath(output_file))

    def detect_data_types(self):
        """Automatically detect column types and patterns in the data."""
        self.column_types = {
            'date_columns': [],
            'numeric_columns': [],
            'categorical_columns': [],
            'text_columns': []
        }
        
        # Detect column types
        for col in self.df.columns:
            # Try to detect date columns
            try:
                pd.to_datetime(self.df[col])
                self.column_types['date_columns'].append(col)
            except:
                # Check if numeric
                if pd.api.types.is_numeric_dtype(self.df[col]):
                    self.column_types['numeric_columns'].append(col)
                # Check if categorical (few unique values)
                elif self.df[col].nunique() < len(self.df) * 0.1:  # Less than 10% unique values
                    self.column_types['categorical_columns'].append(col)
                else:
                    self.column_types['text_columns'].append(col)
        
        # Find potential relationships
        self.relationships = {
            'time_series': [],
            'category_analysis': [],
            'correlation_pairs': []
        }
        
        # Find time series relationships
        for date_col in self.column_types['date_columns']:
            for num_col in self.column_types['numeric_columns']:
                self.relationships['time_series'].append((date_col, num_col))
        
        # Find category analysis relationships
        for cat_col in self.column_types['categorical_columns']:
            for num_col in self.column_types['numeric_columns']:
                self.relationships['category_analysis'].append((cat_col, num_col))
        
        # Find correlation pairs
        for i, num_col1 in enumerate(self.column_types['numeric_columns']):
            for num_col2 in self.column_types['numeric_columns'][i+1:]:
                correlation = self.df[num_col1].corr(self.df[num_col2])
                if abs(correlation) > 0.3:  # Significant correlation
                    self.relationships['correlation_pairs'].append((num_col1, num_col2, correlation))
        
        return self.column_types, self.relationships 

    def generate_smart_dashboard(self):
        """Generate an automatic analysis dashboard based on detected data patterns."""
        try:
            # Create visualization directory if it doesn't exist
            if not os.path.exists('visualizations'):
                os.makedirs('visualizations')
                
            # Detect data types and relationships
            self.detect_data_types()
            
            # Create a dashboard with multiple subplots
            fig = sp.make_subplots(
                rows=3, cols=2,
                specs=[
                    [{"type": "table"}, {"type": "xy"}],
                    [{"type": "xy"}, {"type": "xy"}],
                    [{"type": "xy"}, {"type": "table"}]
                ],
                subplot_titles=(
                    "Data Overview", "Key Trends",
                    "Category Analysis", "Distribution Analysis",
                    "Correlation Analysis", "Insights"
                )
            )
            
            # 1. Data Overview (Table)
            overview_data = {
                'Column': list(self.df.columns),
                'Type': [],
                'Unique Values': [],
                'Missing Values': []
            }
            
            for col in self.df.columns:
                col_type = 'Numeric' if col in self.column_types['numeric_columns'] else \
                          'Date' if col in self.column_types['date_columns'] else \
                          'Category' if col in self.column_types['categorical_columns'] else 'Text'
                overview_data['Type'].append(col_type)
                overview_data['Unique Values'].append(self.df[col].nunique())
                overview_data['Missing Values'].append(self.df[col].isnull().sum())
                
            fig.add_trace(
                go.Table(
                    header=dict(values=list(overview_data.keys())),
                    cells=dict(values=list(overview_data.values()))
                ),
                row=1, col=1
            )
            
            # 2. Key Trends (Time Series if available)
            if self.relationships['time_series']:
                date_col, value_col = self.relationships['time_series'][0]
                df = self.df.copy()
                df[date_col] = pd.to_datetime(df[date_col])
                monthly = df.groupby(df[date_col].dt.to_period('M'))[value_col].mean()
                
                fig.add_trace(
                    go.Scatter(x=monthly.index.astype(str), y=monthly.values, mode='lines+markers'),
                    row=1, col=2
                )
            
            # 3. Category Analysis
            if self.relationships['category_analysis']:
                cat_col, value_col = self.relationships['category_analysis'][0]
                top_categories = self.df.groupby(cat_col)[value_col].mean().nlargest(10)
                
                fig.add_trace(
                    go.Bar(x=top_categories.index, y=top_categories.values),
                    row=2, col=1
                )
            
            # 4. Distribution Analysis
            if self.column_types['numeric_columns']:
                num_col = self.column_types['numeric_columns'][0]
                fig.add_trace(
                    go.Histogram(x=self.df[num_col], name='Distribution'),
                    row=2, col=2
                )
            
            # 5. Correlation Analysis
            if self.relationships['correlation_pairs']:
                num_col1, num_col2, _ = self.relationships['correlation_pairs'][0]
                fig.add_trace(
                    go.Scatter(x=self.df[num_col1], y=self.df[num_col2], mode='markers'),
                    row=3, col=1
                )
            
            # 6. Insights (Text)
            insights = []
            if self.relationships['time_series']:
                insights.append("Time series data detected. Consider analyzing trends over time.")
            if self.relationships['category_analysis']:
                insights.append("Categorical data found. Look for patterns across different categories.")
            if self.relationships['correlation_pairs']:
                insights.append("Strong correlations detected between numeric columns.")
            
            fig.add_trace(
                go.Table(
                    header=dict(values=['Key Insights']),
                    cells=dict(values=[insights])
                ),
                row=3, col=2
            )
            
            # Update layout
            fig.update_layout(
                height=1200,
                width=1600,
                title_text="Automatic Data Analysis Dashboard",
                showlegend=False
            )
            
            # Save and open
            output_file = 'visualizations/smart_dashboard.html'
            fig.write_html(output_file)
            webbrowser.open('file://' + os.path.abspath(output_file))
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate dashboard: {str(e)}") 