import tkinter as tk
from tkinter import filedialog, messagebox, ttk, font
from PIL import Image, ImageTk  # For background image
from pivots import create_pivot_table_window
from visualization import VisualizationConfig
import pandas as pd
import numpy as np

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
            visualization_button.config(state="normal")
            save_button.config(state="normal")

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
        header_window.configure(bg="#f0f0f0")

        title_frame = tk.Frame(header_window, bg="#f0f0f0")
        title_frame.pack(fill="x", pady=10)
        tk.Label(title_frame, text="Assign Headers to Columns", font=("Arial", 14, "bold"), bg="#f0f0f0").pack()

        # Create a scrollable frame for better usability
        frame = tk.Frame(header_window, bg="#f0f0f0")
        canvas = tk.Canvas(frame, bg="#f0f0f0")
        scrollbar = tk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#f0f0f0")

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
            tk.Label(scrollable_frame, text=f"Column {i+1} (Default: {default_header}):", 
                     bg="#f0f0f0", font=("Arial", 10)).grid(row=i, column=0, padx=5, pady=5, sticky="w")
            var = tk.StringVar(value=default_header)
            header_var[i] = var
            entry = tk.Entry(scrollable_frame, textvariable=var, width=30, font=("Arial", 10))
            entry.grid(row=i, column=1, padx=5, pady=5)
            entry.config(relief="solid", borderwidth=1)

        # Add a confirm button at the end
        button_frame = tk.Frame(header_window, bg="#f0f0f0")
        button_frame.pack(pady=20)
        confirm_button = tk.Button(button_frame, text="Confirm Header Assignment", command=save_headers,
                                 bg="#4CAF50", fg="white", font=("Arial", 11), padx=10, pady=5)
        confirm_button.pack()

    def handle_missing_values_and_duplicates(df):
        # Add variable definitions
        selected_columns_var = tk.StringVar()
        missing_value_strategy_var = tk.StringVar(value="Replace with Default")
        default_value_var = tk.StringVar(value="Unknown")
        enable_duplicates_var = tk.BooleanVar(value=False)
        duplicate_strategy_var = tk.StringVar(value="All Columns")
        text_cleaning_enabled = tk.BooleanVar(value=False)
        remove_whitespace_var = tk.BooleanVar(value=False)
        remove_extra_spaces_var = tk.BooleanVar(value=False)
        text_case_var = tk.StringVar(value="No Change")
        remove_special_chars_var = tk.BooleanVar(value=False)
        standardize_lowercase_var = tk.BooleanVar(value=False)
        standardize_underscores_var = tk.BooleanVar(value=False)
        standardize_special_chars_var = tk.BooleanVar(value=False)

        def apply_cleaning():
            nonlocal df
            try:
                missing_strategy = missing_value_strategy_var.get()
                default_value = default_value_var.get()
                if missing_strategy == "Replace with Default":
                    df.fillna(default_value, inplace=True)
                elif missing_strategy == "Drop Rows":
                    df.dropna(axis=0, inplace=True)
                elif missing_strategy == "Drop Columns":
                    df.dropna(axis=1, inplace=True)
                update_preview(df)
                messagebox.showinfo("Success", "Data cleaning completed successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred during cleaning: {str(e)}")

        def proceed():
            # Apply cleaning and close the window
            apply_cleaning()
            cleaning_window.destroy()

        # Create a new window for handling missing values, duplicates, column standardization, and data type conversion
        cleaning_window = tk.Toplevel(root)
        cleaning_window.title("Data Cleaning Options")
        cleaning_window.geometry("1200x800")
        cleaning_window.configure(bg="#f0f0f0")

        # Title frame
        title_frame = tk.Frame(cleaning_window, bg="#007BFF", height=50)
        title_frame.pack(fill="x")
        title_label = tk.Label(title_frame, text="Data Cleaning Options", 
                             font=("Arial", 16, "bold"), fg="white", bg="#007BFF")
        title_label.pack(pady=10)

        # Create a scrollable frame
        canvas = tk.Canvas(cleaning_window, bg="#f0f0f0", highlightthickness=0)
        scrollbar = tk.Scrollbar(cleaning_window, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#f0f0f0")

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True, padx=20, pady=20)
        scrollbar.pack(side="right", fill="y")

        # Create a grid layout inside the scrollable frame
        cleaning_frame = tk.Frame(scrollable_frame, bg="#f0f0f0")
        cleaning_frame.pack(fill="both", expand=True)

        # Create a 2-column grid for the cleaning options
        left_frame = tk.Frame(cleaning_frame, bg="#f0f0f0")
        left_frame.pack(side="left", fill="both", expand=True, padx=10)
        
        right_frame = tk.Frame(cleaning_frame, bg="#f0f0f0")
        right_frame.pack(side="right", fill="both", expand=True, padx=10)

        # Step 1: Handle Missing Values
        step1_frame = tk.LabelFrame(left_frame, text="Step 1: Handle Missing Values", 
                                   font=("Arial", 12, "bold"), bg="#f0f0f0", padx=15, pady=15)
        step1_frame.pack(fill="x", pady=10)
        
        # Missing values options in grid
        missing_frame = tk.Frame(step1_frame, bg="#f0f0f0")
        missing_frame.pack(fill="x", pady=5)
        
        tk.Label(missing_frame, text="Strategy:", bg="#f0f0f0", font=("Arial", 10)).grid(row=0, column=0, pady=5, sticky="w")
        strategy_combo = ttk.Combobox(
            missing_frame,
            textvariable=missing_value_strategy_var,
            values=["Replace with Default", "Drop Rows", "Drop Columns"],
            width=20,
            state="readonly"
        )
        strategy_combo.grid(row=0, column=1, pady=5, padx=10, sticky="w")

        tk.Label(missing_frame, text="Default Value:", bg="#f0f0f0", font=("Arial", 10)).grid(row=1, column=0, pady=5, sticky="w")
        default_entry = tk.Entry(missing_frame, textvariable=default_value_var, width=20, font=("Arial", 10))
        default_entry.grid(row=1, column=1, pady=5, padx=10, sticky="w")

        # Step 2: Handle Duplicates
        step2_frame = tk.LabelFrame(left_frame, text="Step 2: Handle Duplicates", 
                                   font=("Arial", 12, "bold"), bg="#f0f0f0", padx=15, pady=15)
        step2_frame.pack(fill="x", pady=10)

        # Duplicate options in grid
        duplicate_frame = tk.Frame(step2_frame, bg="#f0f0f0")
        duplicate_frame.pack(fill="x", pady=5)

        tk.Checkbutton(duplicate_frame, text="Enable Duplicate Removal", 
                      variable=enable_duplicates_var, bg="#f0f0f0", font=("Arial", 10)).grid(row=0, column=0, pady=5, sticky="w")

        tk.Label(duplicate_frame, text="Strategy:", bg="#f0f0f0", font=("Arial", 10)).grid(row=1, column=0, pady=5, sticky="w")
        strategy_combo = ttk.Combobox(
            duplicate_frame,
            textvariable=duplicate_strategy_var,
            values=["All Columns", "Specific Columns"],
            width=20,
            state="readonly"
        )
        strategy_combo.grid(row=1, column=1, pady=5, padx=10, sticky="w")

        # Step 3: Text Cleaning
        step3_frame = tk.LabelFrame(left_frame, text="Step 3: Text Cleaning", 
                                   font=("Arial", 12, "bold"), bg="#f0f0f0", padx=15, pady=15)
        step3_frame.pack(fill="x", pady=10)

        text_frame = tk.Frame(step3_frame, bg="#f0f0f0")
        text_frame.pack(fill="x", pady=5)

        tk.Checkbutton(text_frame, text="Enable Text Cleaning", 
                      variable=text_cleaning_enabled, bg="#f0f0f0", font=("Arial", 10)).grid(row=0, column=0, pady=5, sticky="w")

        tk.Checkbutton(text_frame, text="Remove Leading/Trailing Whitespace", 
                      variable=remove_whitespace_var, bg="#f0f0f0", font=("Arial", 10)).grid(row=1, column=0, pady=2, sticky="w")

        tk.Checkbutton(text_frame, text="Remove Extra Spaces", 
                      variable=remove_extra_spaces_var, bg="#f0f0f0", font=("Arial", 10)).grid(row=2, column=0, pady=2, sticky="w")

        ttk.Combobox(
            text_frame,
            textvariable=text_case_var,
            values=["No Change", "Lowercase", "Uppercase", "Title Case"],
            width=15,
            state="readonly"
        ).grid(row=3, column=1, pady=2, padx=5, sticky="w")

        tk.Checkbutton(text_frame, text="Remove Special Characters", 
                      variable=remove_special_chars_var, bg="#f0f0f0", font=("Arial", 10)).grid(row=4, column=0, pady=2, sticky="w")

        # Step 4: Date/Time Standardization
        step4_frame = tk.LabelFrame(right_frame, text="Step 4: Date/Time Standardization", 
                                   font=("Arial", 12, "bold"), bg="#f0f0f0", padx=15, pady=15)
        step4_frame.pack(fill="x", pady=10)

        date_frame = tk.Frame(step4_frame, bg="#f0f0f0")
        date_frame.pack(fill="x", pady=5)

        date_cleaning_enabled = tk.BooleanVar(value=False)
        tk.Checkbutton(date_frame, text="Enable Date/Time Cleaning", 
                      variable=date_cleaning_enabled, bg="#f0f0f0", font=("Arial", 10)).grid(row=0, column=0, pady=5, sticky="w")

        date_columns_var = tk.StringVar(value="")
        tk.Label(date_frame, text="Date Columns:", bg="#f0f0f0", font=("Arial", 10)).grid(row=1, column=0, pady=2, sticky="w")
        tk.Entry(date_frame, textvariable=date_columns_var, width=30, font=("Arial", 10)).grid(row=1, column=1, pady=2, padx=5, sticky="w")

        date_format_var = tk.StringVar(value="No Change")
        tk.Label(date_frame, text="Date Format:", bg="#f0f0f0", font=("Arial", 10)).grid(row=2, column=0, pady=2, sticky="w")
        ttk.Combobox(
            date_frame,
            textvariable=date_format_var,
            values=["No Change", "%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%Y%m%d"],
            width=15,
            state="readonly"
        ).grid(row=2, column=1, pady=2, padx=5, sticky="w")

        extract_date_components_var = tk.BooleanVar(value=False)
        tk.Checkbutton(date_frame, text="Extract Date Components", 
                      variable=extract_date_components_var, bg="#f0f0f0", font=("Arial", 10)).grid(row=3, column=0, pady=2, sticky="w")

        # Step 5: Numeric Data Cleaning
        step5_frame = tk.LabelFrame(right_frame, text="Step 5: Numeric Data Cleaning", 
                                   font=("Arial", 12, "bold"), bg="#f0f0f0", padx=15, pady=15)
        step5_frame.pack(fill="x", pady=10)

        numeric_frame = tk.Frame(step5_frame, bg="#f0f0f0")
        numeric_frame.pack(fill="x", pady=5)

        numeric_cleaning_enabled = tk.BooleanVar(value=False)
        tk.Checkbutton(numeric_frame, text="Enable Numeric Cleaning", 
                      variable=numeric_cleaning_enabled, bg="#f0f0f0", font=("Arial", 10)).grid(row=0, column=0, pady=5, sticky="w")

        numeric_columns_var = tk.StringVar(value="")
        tk.Label(numeric_frame, text="Numeric Columns:", bg="#f0f0f0", font=("Arial", 10)).grid(row=1, column=0, pady=2, sticky="w")
        tk.Entry(numeric_frame, textvariable=numeric_columns_var, width=30, font=("Arial", 10)).grid(row=1, column=1, pady=2, padx=5, sticky="w")

        remove_currency_var = tk.BooleanVar(value=False)
        tk.Checkbutton(numeric_frame, text="Remove Currency Symbols", 
                      variable=remove_currency_var, bg="#f0f0f0", font=("Arial", 10)).grid(row=2, column=0, pady=2, sticky="w")

        convert_percentage_var = tk.BooleanVar(value=False)
        tk.Checkbutton(numeric_frame, text="Convert Percentage Strings", 
                      variable=convert_percentage_var, bg="#f0f0f0", font=("Arial", 10)).grid(row=3, column=0, pady=2, sticky="w")

        handle_scientific_var = tk.BooleanVar(value=False)
        tk.Checkbutton(numeric_frame, text="Handle Scientific Notation", 
                      variable=handle_scientific_var, bg="#f0f0f0", font=("Arial", 10)).grid(row=4, column=0, pady=2, sticky="w")

        round_frame = tk.Frame(numeric_frame, bg="#f0f0f0")
        round_frame.grid(row=5, column=0, columnspan=2, pady=2, sticky="w")
        
        round_numbers_var = tk.BooleanVar(value=False)
        tk.Checkbutton(round_frame, text="Round Numbers to", 
                      variable=round_numbers_var, bg="#f0f0f0", font=("Arial", 10)).pack(side="left")
        
        round_decimal_var = tk.StringVar(value="2")
        tk.Entry(round_frame, textvariable=round_decimal_var, width=3, 
                font=("Arial", 10)).pack(side="left", padx=5)
        
        tk.Label(round_frame, text="decimal places", bg="#f0f0f0", 
                font=("Arial", 10)).pack(side="left")

        # Step 6: Categorical Data Cleaning
        step6_frame = tk.LabelFrame(right_frame, text="Step 6: Categorical Data Cleaning", 
                                   font=("Arial", 12, "bold"), bg="#f0f0f0", padx=15, pady=15)
        step6_frame.pack(fill="x", pady=10)

        categorical_frame = tk.Frame(step6_frame, bg="#f0f0f0")
        categorical_frame.pack(fill="x", pady=5)

        categorical_cleaning_enabled = tk.BooleanVar(value=False)
        tk.Checkbutton(categorical_frame, text="Enable Categorical Cleaning", 
                      variable=categorical_cleaning_enabled, bg="#f0f0f0", font=("Arial", 10)).grid(row=0, column=0, pady=5, sticky="w")

        categorical_columns_var = tk.StringVar(value="")
        tk.Label(categorical_frame, text="Categorical Columns:", bg="#f0f0f0", font=("Arial", 10)).grid(row=1, column=0, pady=2, sticky="w")
        tk.Entry(categorical_frame, textvariable=categorical_columns_var, width=30, font=("Arial", 10)).grid(row=1, column=1, pady=2, padx=5, sticky="w")

        standardize_categories_var = tk.BooleanVar(value=False)
        tk.Checkbutton(categorical_frame, text="Standardize Categories", 
                      variable=standardize_categories_var, bg="#f0f0f0", font=("Arial", 10)).grid(row=2, column=0, pady=2, sticky="w")

        replace_missing_categories_var = tk.BooleanVar(value=False)
        tk.Checkbutton(categorical_frame, text="Replace Missing with Mode", 
                      variable=replace_missing_categories_var, bg="#f0f0f0", font=("Arial", 10)).grid(row=3, column=0, pady=2, sticky="w")

        one_hot_encode_var = tk.BooleanVar(value=False)
        tk.Checkbutton(categorical_frame, text="One-Hot Encode", 
                      variable=one_hot_encode_var, bg="#f0f0f0", font=("Arial", 10)).grid(row=4, column=0, pady=2, sticky="w")

        # Step 7: Column Standardization
        step7_frame = tk.LabelFrame(left_frame, text="Step 7: Column Standardization", 
                                   font=("Arial", 12, "bold"), bg="#f0f0f0", padx=15, pady=15)
        step7_frame.pack(fill="x", pady=10)

        standardize_frame = tk.Frame(step7_frame, bg="#f0f0f0")
        standardize_frame.pack(fill="x", pady=5)

        standardize_lowercase_var = tk.BooleanVar(value=False)
        tk.Checkbutton(standardize_frame, text="Convert to Lowercase", 
                      variable=standardize_lowercase_var, bg="#f0f0f0", font=("Arial", 10)).grid(row=0, column=0, pady=2, sticky="w")

        standardize_underscores_var = tk.BooleanVar(value=False)
        tk.Checkbutton(standardize_frame, text="Replace Spaces with Underscores", 
                      variable=standardize_underscores_var, bg="#f0f0f0", font=("Arial", 10)).grid(row=1, column=0, pady=2, sticky="w")

        standardize_special_chars_var = tk.BooleanVar(value=False)
        tk.Checkbutton(standardize_frame, text="Remove Special Characters", 
                      variable=standardize_special_chars_var, bg="#f0f0f0", font=("Arial", 10)).grid(row=2, column=0, pady=2, sticky="w")

        # Step 8: Data Type Conversion
        step8_frame = tk.LabelFrame(left_frame, text="Step 8: Data Type Conversion", 
                                   font=("Arial", 12, "bold"), bg="#f0f0f0", padx=15, pady=15)
        step8_frame.pack(fill="x", pady=10)

        data_type_frame = tk.Frame(step8_frame, bg="#f0f0f0")
        data_type_frame.pack(fill="x", pady=5)

        data_type_vars = {}
        for i, col in enumerate(df.columns):
            row = i // 2
            col_position = i % 2
            
            col_frame = tk.Frame(data_type_frame, bg="#f0f0f0")
            col_frame.grid(row=row, column=col_position, padx=10, pady=5, sticky="w")
            
            tk.Label(col_frame, text=f"{col}:", bg="#f0f0f0", font=("Arial", 10)).pack(side="left")
            dtype_var = tk.StringVar(value="String")
            data_type_vars[col] = dtype_var
            dtype_combo = ttk.Combobox(
                col_frame,
                textvariable=dtype_var,
                values=["String", "Integer", "Float", "Boolean", "Datetime"],
                width=12,
            state="readonly"
            )
            dtype_combo.pack(side="left", padx=5)

        # Step 9: Remove Columns
        step9_frame = tk.LabelFrame(right_frame, text="Step 9: Remove Columns", 
                                   font=("Arial", 12, "bold"), bg="#f0f0f0", padx=15, pady=15)
        step9_frame.pack(fill="x", pady=10)

        listbox_frame = tk.Frame(step9_frame, bg="#f0f0f0")
        listbox_frame.pack(fill="both", expand=True, pady=5)

        vsb = ttk.Scrollbar(listbox_frame, orient="vertical")
        vsb.pack(side="right", fill="y")

        hsb = ttk.Scrollbar(listbox_frame, orient="horizontal")
        hsb.pack(side="bottom", fill="x")

        columns_to_remove_listbox = tk.Listbox(
            listbox_frame,
            selectmode="multiple",
            height=6,
            exportselection=False,
            yscrollcommand=vsb.set,
            xscrollcommand=hsb.set,
            font=("Arial", 10),
            bg="white"
        )
        columns_to_remove_listbox.pack(fill="both", expand=True)

        vsb.config(command=columns_to_remove_listbox.yview)
        hsb.config(command=columns_to_remove_listbox.xview)

        for col in df.columns:
            columns_to_remove_listbox.insert(tk.END, col)

        # Action Buttons
        button_frame = tk.Frame(cleaning_window, bg="#f0f0f0")
        button_frame.pack(fill="x", pady=20)
        
        apply_button = tk.Button(button_frame, text="Apply Cleaning", command=apply_cleaning,
                               bg="#4CAF50", fg="white", font=("Arial", 11), padx=15, pady=5)
        apply_button.pack(side="left", padx=10)
        
        proceed_button = tk.Button(button_frame, text="Proceed", command=proceed,
                                 bg="#007BFF", fg="white", font=("Arial", 11), padx=15, pady=5)
        proceed_button.pack(side="left", padx=10)
        
        # Status bar
        status_frame = tk.Frame(cleaning_window, bg="#007BFF", height=25)
        status_frame.pack(fill="x", side="bottom")
        status_label = tk.Label(status_frame, text="Ready", fg="white", bg="#007BFF", anchor="w")
        status_label.pack(fill="x", padx=10)
        
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

    # Set up the main window
    root = tk.Tk()
    root.title("InsightForge-Interactive-Data-Processing-Reporting-App")
    root.geometry("900x700")
    root.configure(bg="#f0f0f0")
    
    # Define custom styles
    style = ttk.Style()
    style.configure("TButton", font=("Arial", 10))
    style.configure("TCombobox", font=("Arial", 10))
    style.configure("Treeview", font=("Arial", 10))
    style.configure("Treeview.Heading", font=("Arial", 10, "bold"))

    # Create a title frame
    title_frame = tk.Frame(root, bg="#007BFF", height=60)
    title_frame.pack(fill="x")
    title_label = tk.Label(title_frame, text="InsightForge-Interactive-Data-Processing-Reporting-App", 
                          font=("Arial", 18, "bold"), fg="white", bg="#007BFF")
    title_label.pack(pady=10)

    # Main content area
    main_frame = tk.Frame(root, bg="#f0f0f0")
    main_frame.pack(fill="both", expand=True, padx=20, pady=20)

    selected_files = []
    file_list_var = tk.StringVar()
    delimiter_var = tk.StringVar(value=",")
    remove_spaces_var = tk.BooleanVar(value=False)
    ignore_special_chars_var = tk.BooleanVar(value=False)
    file_selection_var = tk.StringVar(value="Single File")

    # File selection frame
    file_frame = tk.LabelFrame(main_frame, text="File Selection", font=("Arial", 12, "bold"), bg="#f0f0f0", padx=10, pady=10)
    file_frame.pack(fill="x", pady=10)

    file_selection_frame = tk.Frame(file_frame, bg="#f0f0f0")
    file_selection_frame.pack(fill="x")
    
    tk.Label(file_selection_frame, text="Selection Type:", bg="#f0f0f0").grid(row=0, column=0, padx=5, pady=5, sticky="w")
    file_type_combo = ttk.Combobox(file_selection_frame, textvariable=file_selection_var, 
                                  values=["Single File", "Multiple Files", "Folder"], width=15)
    file_type_combo.grid(row=0, column=1, padx=5, pady=5, sticky="w")
    
    select_button = tk.Button(file_selection_frame, text="Browse", command=select_files,
                             bg="#007BFF", fg="white", font=("Arial", 10), padx=10)
    select_button.grid(row=0, column=2, padx=10, pady=5, sticky="w")
    
    # File list display
    file_list_frame = tk.Frame(file_frame, bg="#f0f0f0")
    file_list_frame.pack(fill="x", pady=5)
    
    tk.Label(file_list_frame, text="Selected Files:", bg="#f0f0f0").pack(anchor="w")
    file_list_display = tk.Label(file_list_frame, textvariable=file_list_var, justify="left", 
                               wraplength=800, bg="white", relief="solid", bd=1)
    file_list_display.pack(fill="x", pady=5)

    # Options frame
    options_frame = tk.LabelFrame(main_frame, text="Data Cleaning Options", font=("Arial", 12, "bold"), bg="#f0f0f0", padx=10, pady=10)
    options_frame.pack(fill="x", pady=10)
    
    # Organize options in a grid
    tk.Label(options_frame, text="Delimiter:", bg="#f0f0f0").grid(row=0, column=0, padx=5, pady=5, sticky="w")
    delimiter_entry = tk.Entry(options_frame, textvariable=delimiter_var, width=5)
    delimiter_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")
    
    tk.Checkbutton(options_frame, text="Remove Empty Spaces", variable=remove_spaces_var, 
                  bg="#f0f0f0").grid(row=0, column=2, padx=20, pady=5, sticky="w")
    tk.Checkbutton(options_frame, text="Ignore Special Characters", variable=ignore_special_chars_var, 
                  bg="#f0f0f0").grid(row=0, column=3, padx=20, pady=5, sticky="w")

    # Action buttons frame
    button_frame = tk.Frame(main_frame, bg="#f0f0f0")
    button_frame.pack(fill="x", pady=10)
    
    process_button = tk.Button(button_frame, text="Process Files", command=process_files,
                             bg="#4CAF50", fg="white", font=("Arial", 11, "bold"), padx=15, pady=5)
    process_button.pack(side="left", padx=5)
    
    # Add Pivot Table Button (Initially Disabled)
    pivot_button = tk.Button(button_frame, text="Create Pivot Table", 
                           command=lambda: create_pivot_table_window(root, merged_df),
                           state="disabled", bg="#FF9800", fg="white", font=("Arial", 11), padx=15, pady=5)
    pivot_button.pack(side="left", padx=5)
    
    # Add Visualization Button
    visualization_button = tk.Button(button_frame, text="Create Visualization", 
                                   command=lambda: VisualizationConfig(root, merged_df).show_config_window(),
                                   state="disabled", bg="#9C27B0", fg="white", font=("Arial", 11), padx=15, pady=5)
    visualization_button.pack(side="left", padx=5)
    
    # Save cleaned data button
    save_button = tk.Button(button_frame, text="Save Cleaned Data", command=save_cleaned_data,
                          state="disabled", bg="#007BFF", fg="white", font=("Arial", 11), padx=15, pady=5)
    save_button.pack(side="left", padx=5)
    
    # Data preview frame
    preview_frame = tk.LabelFrame(main_frame, text="Data Preview", font=("Arial", 12, "bold"), bg="#f0f0f0", padx=10, pady=10)
    preview_frame.pack(fill="both", expand=True, pady=10)
    
    # Create a frame for the Treeview and its scrollbars
    tree_frame = tk.Frame(preview_frame)
    tree_frame.pack(fill="both", expand=True)
    
    # Create vertical scrollbar
    vsb = ttk.Scrollbar(tree_frame, orient="vertical")
    vsb.pack(side="right", fill="y")
    
    # Create horizontal scrollbar
    hsb = ttk.Scrollbar(tree_frame, orient="horizontal")
    hsb.pack(side="bottom", fill="x")
    
    # Create Treeview with scrollbars
    tree = ttk.Treeview(tree_frame, height=10, yscrollcommand=vsb.set, xscrollcommand=hsb.set)
    tree.pack(fill="both", expand=True)
    
    # Configure scrollbars
    vsb.config(command=tree.yview)
    hsb.config(command=tree.xview)
    
    # Status bar
    status_frame = tk.Frame(root, bg="#007BFF", height=25)
    status_frame.pack(fill="x", side="bottom")
    status_label = tk.Label(status_frame, text="Ready", fg="white", bg="#007BFF", anchor="w")
    status_label.pack(fill="x", padx=10)
   
    root.mainloop()