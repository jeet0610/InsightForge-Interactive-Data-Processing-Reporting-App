import pandas as pd
from tkinter import filedialog, messagebox

# Global variables
selected_files = []
merged_df = None

def select_files(file_selection_var, file_list_var):
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

def process_files(delimiter_var, remove_spaces_var, ignore_special_chars_var, pivot_button, assign_headers_screen):
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
    global merged_df
    if merged_df is None:
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