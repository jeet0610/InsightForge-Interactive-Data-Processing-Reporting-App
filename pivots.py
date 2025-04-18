import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd

def create_pivot_table_window(root, df):
    """Open a new window for creating pivot tables."""
    if df is None or df.empty:
        messagebox.showerror("Error", "No data available to create a pivot table!")
        return

    pivot_window = tk.Toplevel(root)
    pivot_window.title("Create Pivot Table")
    pivot_window.geometry("800x600")

    tk.Label(pivot_window, text="Select Rows, Columns, and Values for Pivot Table").pack(pady=10)

    # Dropdowns for selecting rows, columns, and values
    row_var = tk.StringVar(value="")
    column_var = tk.StringVar(value="")
    value_var = tk.StringVar(value="")
    aggfunc_var = tk.StringVar(value="sum")

    tk.Label(pivot_window, text="Rows:").pack(pady=5)
    ttk.Combobox(pivot_window, textvariable=row_var, values=list(df.columns)).pack(pady=5)

    tk.Label(pivot_window, text="Columns:").pack(pady=5)
    ttk.Combobox(pivot_window, textvariable=column_var, values=list(df.columns)).pack(pady=5)

    tk.Label(pivot_window, text="Values:").pack(pady=5)
    ttk.Combobox(pivot_window, textvariable=value_var, values=list(df.columns)).pack(pady=5)

    tk.Label(pivot_window, text="Aggregation Function:").pack(pady=5)
    ttk.Combobox(pivot_window, textvariable=aggfunc_var, values=["sum", "mean", "count", "min", "max"]).pack(pady=5)

    # Treeview to display the pivot table preview
    # pivot_tree = ttk.Treeview(pivot_window, height=10)
    # pivot_tree.pack(fill="both", expand=True, padx=10, pady=10)

    # Variable to store the generated pivot table
    pivot_df = None

    # def generate_pivot_table():
    #     """Generate and display the pivot table preview."""
    #     nonlocal pivot_df
    #     try:
    #         pivot_df = pd.pivot_table(
    #             df,
    #             index=row_var.get() if row_var.get() else None,
    #             columns=column_var.get() if column_var.get() else None,
    #             values=value_var.get() if value_var.get() else None,
    #             aggfunc=aggfunc_var.get()
    #         )
            
    #         # Reset the index to include it in the Treeview
    #         pivot_df_reset = pivot_df.reset_index()

            

    #         # Clear the Treeview
    #         for item in pivot_tree.get_children():
    #             pivot_tree.delete(item)

    #         # Update Treeview with the first 10 rows of the pivot table
    #         pivot_tree["columns"] = list(pivot_df.columns)
    #         pivot_tree["show"] = "headings"

    #         for col in pivot_df_reset.columns:
    #             pivot_tree.heading(col, text=col)
    #             pivot_tree.column(col, width=100, anchor="center")

    #         # Add rows (including the first row of data)
    #         for _, row in pivot_df_reset.head(10).iterrows():
    #             pivot_tree.insert("", "end", values=list(row))

    #     except Exception as e:
    #         messagebox.showerror("Error", f"Failed to create pivot table: {e}")

    def download_pivot_table():
        """Download the generated pivot table as a CSV or Excel file."""
        if pivot_df is None or pivot_df.empty:
            messagebox.showerror("Error", "No pivot table available to download!")
            return

        file_types = [("CSV Files", "*.csv"), ("Excel Files", "*.xlsx")]
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=file_types, title="Save Pivot Table As")
        if not file_path:
            return  # User canceled the save dialog

        try:
            if file_path.endswith(".csv"):
                pivot_df.to_csv(file_path)
            elif file_path.endswith(".xlsx"):
                pivot_df.to_excel(file_path, engine="openpyxl")
            messagebox.showinfo("Success", f"Pivot table saved successfully to {file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save pivot table: {e}")

    # Buttons for generating preview and downloading the pivot table
    # tk.Button(pivot_window, text="Preview Pivot Table", command=generate_pivot_table).pack(pady=10)
    tk.Button(pivot_window, text="Download Pivot Table", command=download_pivot_table).pack(pady=10)