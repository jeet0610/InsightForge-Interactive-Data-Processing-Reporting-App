import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk  # For background image
from pivots import create_pivot_table_window
from Virtual_DB import create_virtual_dashboard
import pandas as pd

def launch_gui():
    def select_files():
        file_type = file_selection_var.get()
        if file_type == "Single File":
            file = filedialog.askopenfilename(title="Select a Sales File", filetypes=[("CSV/XLSX Files", "*.csv *.xlsx")])
            if file:
                selected_files.clear()
                selected_files.append(file)
                file_list_var.set(file)
        elif file_type == "Multiple Files":
            files = filedialog.askopenfilenames(title="Select Sales Files", filetypes=[("CSV/XLSX Files", "*.csv *.xlsx")])
            if files:
                selected_files.clear()
                selected_files.extend(files)
                file_list_var.set("\n".join(files))
        elif file_type == "Folder":
            folder = filedialog.askdirectory(title="Select a Folder")
            if folder:
                selected_files.clear()
                selected_files.append(folder)
                file_list_var.set(folder)

    def process_files():
        global merged_df
        if not selected_files:
            messagebox.showerror("Error", "No files or folder selected!")
            return

        delimiter = delimiter_var.get()
        remove_spaces = remove_spaces_var.get()
        ignore_special_chars = ignore_special_chars_var.get()

        try:
            dataframes = []
            for file in selected_files:
                if file.endswith(".csv"):
                    df = pd.read_csv(file, delimiter=delimiter)
                elif file.endswith(".xlsx"):
                    df = pd.read_excel(file)
                else:
                    continue

                # Apply cleaning options
                if remove_spaces:
                    df.columns = df.columns.str.strip()
                if ignore_special_chars:
                    df.columns = df.columns.str.replace(r'[^\w\s]', '', regex=True)

                dataframes.append(df)

            if not dataframes:
                messagebox.showerror("Error", "No valid files found!")
                return

            # Merge all DataFrames
            merged_df = pd.concat(dataframes, ignore_index=True)

            # Enable the Pivot Table Button
            pivot_button.config(state="normal")

            # Open header assignment screen
            assign_headers_screen(merged_df)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to process files: {e}")
        
    def save_cleaned_data():
        """Save the cleaned DataFrame to a file."""
        if 'merged_df' not in globals():
            messagebox.showerror("Error", "No cleaned data available to save!")
            return

        file_types = [("CSV Files", "*.csv"), ("Excel Files", "*.xlsx")]
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=file_types, title="Save Cleaned Data As")
        if not file_path:
            return  # User canceled the save dialog

        try:
            if file_path.endswith(".csv"):
                merged_df.to_csv(file_path, index=False)
            elif file_path.endswith(".xlsx"):
                merged_df.to_excel(file_path, index=False, engine="openpyxl")
            messagebox.showinfo("Success", f"Cleaned data saved successfully to {file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save cleaned data: {e}")

            
    def assign_headers_screen(df):
        def save_headers():
            # Get the new headers from user input
            new_headers = [header_var[i].get() for i in range(len(df.columns))]
            df.columns = new_headers  # Assign new headers to the DataFrame

            # Display the updated DataFrame (first 10 rows) in the Treeview
            update_preview(df.head(10))

            # Close the header assignment window
            header_window.destroy()

            # Open the missing values, duplicates, column standardization, and data type conversion GUI
            handle_missing_values_and_duplicates(df)

        header_window = tk.Toplevel(root)
        header_window.title("Assign Headers")
        header_window.geometry("800x600")

        tk.Label(header_window, text="Assign Headers to Columns").pack(pady=10)

        # Create a scrollable frame for better usability
        frame = tk.Frame(header_window)
        canvas = tk.Canvas(frame)
        scrollbar = tk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        frame.pack(fill="both", expand=True, padx=10, pady=10)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Create header assignment fields
        header_var = {}
        for i, col in enumerate(df.columns):
            # Default header is the column name (not the 0th row)
            default_header = col
            tk.Label(scrollable_frame, text=f"Column {i+1} (Default: {default_header}):").grid(row=i, column=0, padx=5, pady=5, sticky="w")
            var = tk.StringVar(value=default_header)
            header_var[i] = var
            tk.Entry(scrollable_frame, textvariable=var, width=30).grid(row=i, column=1, padx=5, pady=5)

        # Add a confirm button at the end
        tk.Button(header_window, text="Confirm Header Assignment", command=save_headers).pack(pady=20)

    def handle_missing_values_and_duplicates(df):
        def apply_cleaning():
            """Apply the cleaning steps to the DataFrame."""
            # Handle missing values
            missing_strategy = missing_value_strategy_var.get()
            default_value = default_value_var.get()

            if missing_strategy == "Replace with Default":
                df.fillna(default_value, inplace=True)
            elif missing_strategy == "Drop Rows":
                df.dropna(axis=0, inplace=True)
            elif missing_strategy == "Drop Columns":
                df.dropna(axis=1, inplace=True)

            # Handle duplicates if enabled
            if enable_duplicates_var.get():
                if duplicate_strategy_var.get() == "All Columns":
                    df.drop_duplicates(inplace=True)
                elif duplicate_strategy_var.get() == "Specific Columns":
                    selected_columns = selected_columns_var.get().split(", ")
                    if selected_columns:
                        df.drop_duplicates(subset=selected_columns, inplace=True)
            # Step 3: Standardize Column Names
            if standardize_lowercase_var.get():
                df.columns = df.columns.str.lower()
            if standardize_underscores_var.get():
                df.columns = df.columns.str.replace(" ", "_")
            if standardize_special_chars_var.get():
                df.columns = df.columns.str.replace(r"[^\w\s]", "", regex=True)
           
            # Step 4: Apply data type conversions
            for col, dtype_var in data_type_vars.items():
                dtype = dtype_var.get()
                try:
                    if dtype == "String":
                        df[col] = df[col].astype(str)
                    elif dtype == "Integer":
                        df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64")
                    elif dtype == "Float":
                        df[col] = pd.to_numeric(df[col], errors="coerce")
                    elif dtype == "Boolean":
                        df[col] = df[col].astype(bool)
                    elif dtype == "Datetime":
                        df[col] = pd.to_datetime(df[col], errors="coerce")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to convert column '{col}' to {dtype}: {e}")
            # Handle Outliers
            # if enable_outliers_var.get():  # Check if outlier handling is enabled
            #     if outlier_strategy_var.get() != "None":
            #         try:
            #             numeric_columns = df.select_dtypes(include=["float", "int"]).columns
            #             if numeric_columns.empty:
            #                 messagebox.showwarning("Warning", "No numeric columns available for outlier handling.")
            #                 return

            #             for col in numeric_columns:
            #                 Q1 = df[col].quantile(0.25)  # First quartile (25th percentile)
            #                 Q3 = df[col].quantile(0.75)  # Third quartile (75th percentile)
            #                 IQR = Q3 - Q1  # Interquartile range
            #                 lower_bound = Q1 - 1.5 * IQR
            #                 upper_bound = Q3 + 1.5 * IQR

            #                 if outlier_strategy_var.get() == "Remove Outliers":
            #                     # Remove rows with outliers
            #                     df = df[(df[col] >= lower_bound) & (df[col] <= upper_bound)]
            #                 elif outlier_strategy_var.get() == "Replace with Mean":
            #                     # Replace outliers with the mean
            #                     mean_value = df[col].mean()
            #                     df[col] = df[col].apply(lambda x: mean_value if x < lower_bound or x > upper_bound else x)
            #                 elif outlier_strategy_var.get() == "Replace with Median":
            #                 # Replace outliers with the median
            #                    median_value = df[col].median()
            #                    df[col] = df[col].apply(lambda x: median_value if x < lower_bound or x > upper_bound else x)
            #         except Exception as e:
            #             messagebox.showerror("Error", f"Failed to handle outliers: {e}")            

            # # Remove Irrelevant Columns
            # selected_indices = columns_to_remove_listbox.curselection()  # Get selected indices
            # columns_to_remove = [columns_to_remove_listbox.get(i) for i in selected_indices]  # Get column names
            # if columns_to_remove:
            #     df.drop(columns=columns_to_remove, inplace=True, errors="ignore")

            # Update the preview after cleaning
            update_preview(df)
           
            # Close the cleaning window after applying cleaning
            cleaning_window.destroy()

        def proceed():
            # Apply cleaning and close the window
            apply_cleaning()
            cleaning_window.destroy()


        # Create a new window for handling missing values, duplicates, column standardization, and data type conversion
        cleaning_window = tk.Toplevel(root)
        cleaning_window.title("Handle Missing Values, Duplicates, Column Standardization, and Data Type Conversion")
        cleaning_window.geometry("800x1000")

        # Create a scrollable frame
        canvas = tk.Canvas(cleaning_window)
        scrollbar = tk.Scrollbar(cleaning_window, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Create a grid layout inside the scrollable frame
        cleaning_frame = tk.Frame(scrollable_frame)
        cleaning_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Step 1: Handle Missing Values
        tk.Label(cleaning_frame, text="Step 1: Handle Missing Values", font=("Arial", 12, "bold")).grid(row=0, column=0, columnspan=2, pady=10, sticky="w")
        tk.Label(cleaning_frame, text="Strategy:").grid(row=1, column=0, pady=5, sticky="w")
        missing_value_strategy_var = tk.StringVar(value="Replace with Default")
        ttk.Combobox(
            cleaning_frame,
            textvariable=missing_value_strategy_var,
            values=["Replace with Default", "Drop Rows", "Drop Columns"]
        ).grid(row=1, column=1, pady=5, sticky="w")

        tk.Label(cleaning_frame, text="Default Value:").grid(row=2, column=0, pady=5, sticky="w")
        default_value_var = tk.StringVar(value="Unknown")
        tk.Entry(cleaning_frame, textvariable=default_value_var).grid(row=2, column=1, pady=5, sticky="w")

        # Step 2: Handle Duplicates
        tk.Label(cleaning_frame, text="Step 2: Handle Duplicates", font=("Arial", 12, "bold")).grid(row=3, column=0, columnspan=2, pady=10, sticky="w")

        # Variable to store user preferences
        duplicate_strategy_var = tk.StringVar(value="None")
        selected_columns_var = tk.StringVar(value="")

        def open_duplicate_removal_window():
            """Open a new window to configure duplicate removal options."""
            duplicate_window = tk.Toplevel(root)
            duplicate_window.title("Duplicate Removal Options")
            duplicate_window.geometry("400x400")

            tk.Label(duplicate_window, text="Duplicate Removal Options", font=("Arial", 12, "bold")).pack(pady=10)

            # Duplicate strategy dropdown
            tk.Label(duplicate_window, text="Duplicate Strategy:").pack(pady=5)
            strategy_var = tk.StringVar(value="All Columns")
            strategy_dropdown = ttk.Combobox(
                duplicate_window,
                textvariable=strategy_var,
                values=["All Columns", "Specific Columns"]
            )
            strategy_dropdown.pack(pady=5)

            # Specific columns checkboxes
            column_vars = {}
            column_checkboxes_frame = tk.Frame(duplicate_window)
            column_checkboxes_frame.pack(pady=10)

            def update_column_checkboxes(*args):
                """Show or hide column checkboxes based on the selected strategy."""
                for widget in column_checkboxes_frame.winfo_children():
                    widget.destroy()  # Clear existing checkboxes

                if strategy_var.get() == "Specific Columns":
                    for col in df.columns:
                        var = tk.BooleanVar(value=False)
                        column_vars[col] = var
                        tk.Checkbutton(column_checkboxes_frame, text=col, variable=var).pack(anchor="w")

            strategy_var.trace("w", update_column_checkboxes)

            # Save button
            def save_duplicate_options():
                """Save the duplicate removal options and close the window."""
                duplicate_strategy_var.set(strategy_var.get())
                if strategy_var.get() == "Specific Columns":
                    selected_columns = [col for col, var in column_vars.items() if var.get()]
                    selected_columns_var.set(", ".join(selected_columns))
                else:
                    selected_columns_var.set("All Columns")
                duplicate_window.destroy()

            tk.Button(duplicate_window, text="Save", command=save_duplicate_options).pack(pady=20)

        # Enable Duplicate Removal Checkbox
        enable_duplicates_var = tk.BooleanVar(value=False)
        tk.Checkbutton(
            cleaning_frame,
            text="Enable Duplicate Removal",
            variable=enable_duplicates_var,
            command=open_duplicate_removal_window
        ).grid(row=4, column=0, columnspan=2, pady=5, sticky="w")

        # Display user preferences
        tk.Label(cleaning_frame, text="Selected Strategy:").grid(row=5, column=0, pady=5, sticky="w")
        tk.Label(cleaning_frame, textvariable=duplicate_strategy_var).grid(row=5, column=1, pady=5, sticky="w")

        tk.Label(cleaning_frame, text="Selected Columns:").grid(row=6, column=0, pady=5, sticky="w")
        tk.Label(cleaning_frame, textvariable=selected_columns_var).grid(row=6, column=1, pady=5, sticky="w")
        
        
        # Step 3: Standardize Column Names
        tk.Label(cleaning_frame, text="Step 3: Standardize Column Names", font=("Arial", 12, "bold")).grid(row=7, column=0, columnspan=2, pady=10, sticky="w")
        standardize_lowercase_var = tk.BooleanVar(value=False)
        standardize_underscores_var = tk.BooleanVar(value=False)
        standardize_special_chars_var = tk.BooleanVar(value=False)
        tk.Checkbutton(cleaning_frame, text="Convert to Lowercase", variable=standardize_lowercase_var).grid(row=8, column=0, columnspan=2, sticky="w", padx=10, pady=5)
        tk.Checkbutton(cleaning_frame, text="Replace Spaces with Underscores", variable=standardize_underscores_var).grid(row=9, column=0, columnspan=2, sticky="w", padx=10, pady=5)
        tk.Checkbutton(cleaning_frame, text="Remove Special Characters", variable=standardize_special_chars_var).grid(row=10, column=0, columnspan=2, sticky="w", padx=10, pady=5)
        
        # Add a separator line after Step 3
        ttk.Separator(cleaning_frame, orient="horizontal").grid(row=11, column=0, columnspan=4, pady=20, sticky="ew")


        # Step 4: Data Type Conversion
        tk.Label(cleaning_frame, text="Step 4: Data Type Conversion", font=("Arial", 12, "bold")).grid(row=52, column=0, columnspan=4, pady=10, sticky="w")
        data_type_vars = {}
        for i, col in enumerate(df.columns):
            row = 60 + (i // 4)  # Calculate the row based on the index
            col_position = i % 4  # Calculate the column position (0-3)
            tk.Label(cleaning_frame, text=f"{col}:").grid(row=row, column=col_position * 2, pady=5, sticky="w", padx=10)
            dtype_var = tk.StringVar(value="String")
            data_type_vars[col] = dtype_var
            ttk.Combobox(
                cleaning_frame,
                textvariable=dtype_var,
                values=["String", "Integer", "Float", "Boolean", "Datetime"]
            ).grid(row=row, column=(col_position * 2) + 1, pady=5, sticky="w", padx=10)
        # Step 5: Handle Outliers
        tk.Label(cleaning_frame, text="Step 5: Handle Outliers", font=("Arial", 12, "bold")).grid(row=202, column=0, columnspan=4, pady=20, sticky="w")

        # Enable Outlier Handling Checkbox
        enable_outliers_var = tk.BooleanVar(value=False)
        tk.Checkbutton(
            cleaning_frame,
            text="Enable Outlier Handling",
            variable=enable_outliers_var
        ).grid(row=203, column=0, columnspan=2, pady=5, sticky="w")

        # Outlier Handling Options
        tk.Label(cleaning_frame, text="Outlier Handling Strategy:").grid(row=204, column=0, pady=5, sticky="w")
        outlier_strategy_var = tk.StringVar(value="None")
        ttk.Combobox(
            cleaning_frame,
            textvariable=outlier_strategy_var,
            values=["None", "Remove Outliers", "Replace with Mean", "Replace with Median"],
            state="readonly"
        ).grid(row=204, column=1, pady=5, sticky="w")

        # Step 8: Remove Irrelevant Columns
        tk.Label(cleaning_frame, text="Step 8: Remove Irrelevant Columns", font=("Arial", 12, "bold")).grid(row=300, column=0, columnspan=4, pady=20, sticky="w")

        # Multi-select Listbox for column selection
        tk.Label(cleaning_frame, text="Select Columns to Remove:").grid(row=301, column=0, pady=5, sticky="w")
        columns_to_remove_listbox = tk.Listbox(cleaning_frame, selectmode="multiple", height=10, exportselection=False)
        columns_to_remove_listbox.grid(row=301, column=1, pady=5, sticky="w")

        # Populate the Listbox with column names
        for col in df.columns:
            columns_to_remove_listbox.insert(tk.END, col)


        # Apply and Proceed buttons
        tk.Button(cleaning_frame, text="Apply Cleaning", command=apply_cleaning).grid(row=400, column=0, pady=20, sticky="w")
        tk.Button(cleaning_frame, text="Proceed", command=proceed).grid(row=400, column=1, pady=20, sticky="w")
        
    def update_preview(df):
        """Update the Treeview with the DataFrame."""
        # Clear the Treeview
        for item in tree.get_children():
            tree.delete(item)

        # Update columns
        tree["columns"] = list(df.columns)
        tree["show"] = "headings"

        # Add column headers
        for col in df.columns:
            tree.heading(col, text=col)
            tree.column(col, width=100, anchor="center")

        # Add rows
        for _, row in df.iterrows():
            tree.insert("", "end", values=list(row))

    root = tk.Tk()
    root.title("Automated Sales Reporting")
    root.geometry("800x600")

    selected_files = []

    file_list_var = tk.StringVar()
    delimiter_var = tk.StringVar(value=",")
    remove_spaces_var = tk.BooleanVar(value=False)
    ignore_special_chars_var = tk.BooleanVar(value=False)
    file_selection_var = tk.StringVar(value="Single File")

    # File/Folder selection
    tk.Label(root, text="Select File/Folder:").pack(pady=5)
    ttk.Combobox(root, textvariable=file_selection_var, values=["Single File", "Multiple Files", "Folder"]).pack(pady=5)
    tk.Button(root, text="Select", command=select_files).pack(pady=2)
    tk.Label(root, textvariable=file_list_var, justify="left", wraplength=600).pack(pady=5)

    # Data cleaning options
    tk.Label(root, text="Delimiter:").pack(pady=2)
    tk.Entry(root, textvariable=delimiter_var).pack(pady=2)
    tk.Checkbutton(root, text="Remove Empty Spaces", variable=remove_spaces_var).pack(pady=5)
    tk.Checkbutton(root, text="Ignore Special Characters", variable=ignore_special_chars_var).pack(pady=5)
    
    # Add Pivot Table Button (Initially Disabled)
    pivot_button = tk.Button(root, text="Create Pivot Table", command=lambda: create_pivot_table_window(root, merged_df), state="disabled")
    pivot_button.pack(pady=5)

    # Add Virtual Dashboard Button
    dashboard_button = tk.Button(root, text="Create Virtual Dashboard", command=create_virtual_dashboard)
    dashboard_button.pack(pady=5)
   
    # Data preview (Treeview for Excel-like table)
    tk.Label(root, text="Data Preview (First 10 Rows):").pack(pady=5)
    tree = ttk.Treeview(root, height=8)
    tree.pack(fill="both", expand=True, padx=10, pady=10)

    # Process files
    tk.Button(root, text="Process Files", command=process_files).pack(pady=10)
    
   # Save cleaned data
    tk.Button(root, text="Save Cleaned Data", command=save_cleaned_data).pack(pady=10)
   
   
    root.mainloop()