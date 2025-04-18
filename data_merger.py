import pandas as pd
import os
from typing import Dict, List, Tuple, Optional
import re

class DataMerger:
    def __init__(self):
        self.dataframes: Dict[str, pd.DataFrame] = {}
        self.relationships: List[Tuple[str, str, str, str]] = []  # (table1, table2, key1, key2)
        self.primary_keys: Dict[str, str] = {}  # table_name -> primary_key

    def load_files(self, folder_path: str) -> None:
        """Load all CSV and Excel files from a folder."""
        for file in os.listdir(folder_path):
            if file.endswith(('.csv', '.xlsx')):
                file_path = os.path.join(folder_path, file)
                table_name = os.path.splitext(file)[0].lower()
                
                try:
                    if file.endswith('.csv'):
                        df = pd.read_csv(file_path)
                    else:
                        df = pd.read_excel(file_path)
                    
                    self.dataframes[table_name] = df
                    self._detect_primary_key(table_name, df)
                except Exception as e:
                    print(f"Error loading {file}: {str(e)}")

    def _detect_primary_key(self, table_name: str, df: pd.DataFrame) -> None:
        """Detect primary key based on column names and data uniqueness."""
        # Common primary key patterns (in order of likelihood)
        key_patterns = [
            # Exact matches
            f"{table_name}_id",
            f"{table_name[:-1]}_id" if table_name.endswith('s') else None,  # Plural form
            f"{table_name}id",
            f"{table_name[:-1]}id" if table_name.endswith('s') else None,   # Plural form
            
            # Simple key names
            "id",
            "key",
            f"{table_name}_key",
            
            # Common variations
            "pk",
            f"{table_name}_pk",
            "object_id",
            "record_id",
            "sequence",
            "seq",
            "code"
        ]
        
        # Remove None values from patterns
        key_patterns = [p for p in key_patterns if p]
        
        # First try exact pattern matches on columns that are unique
        for pattern in key_patterns:
            for col in df.columns:
                if col.lower() == pattern.lower():
                    # Check if column values are unique
                    if df[col].is_unique:
                        self.primary_keys[table_name] = col
                        print(f"Found primary key for {table_name}: {col} (exact match)")
                        return
        
        # Try columns that sound like they could be keys
        for col in df.columns:
            col_lower = col.lower()
            if ('id' in col_lower or 'key' in col_lower or 'code' in col_lower or 'num' in col_lower) and df[col].is_unique:
                self.primary_keys[table_name] = col
                print(f"Found primary key for {table_name}: {col} (contains key term)")
                return
                
        # Last resort: check if any column is unique and could be a primary key
        numeric_cols = df.select_dtypes(include=['number']).columns
        for col in numeric_cols:
            if df[col].is_unique:
                self.primary_keys[table_name] = col
                print(f"Found primary key for {table_name}: {col} (numeric and unique)")
                return
                
        # If we get here, no primary key was detected
        print(f"No primary key detected for {table_name}")

    def detect_relationships(self) -> None:
        """Detect relationships between tables based on column names and data values."""
        # Clear existing relationships
        self.relationships = []
        
        # These patterns cover most common database naming conventions
        relationship_patterns = [
            # Basic foreign key patterns
            lambda t1, t2: f"{t2}_id",
            lambda t1, t2: f"{t2}id", 
            lambda t1, t2: f"{t2[:-1]}_id",  # For plural table names (customers -> customer_id)
            
            # Table name in column name
            lambda t1, t2: f"{t2}_key",
            lambda t1, t2: f"{t2}_code",
            lambda t1, t2: f"{t2}_number",
            
            # Singular version of table name
            lambda t1, t2: f"{t2[:-1]}id",
            lambda t1, t2: f"{t2[:-1]}_code",
            
            # Special patterns for common tables
            lambda t1, t2: "customer_id" if t2 == "customers" else None,
            lambda t1, t2: "product_id" if t2 == "products" else None,
            lambda t1, t2: "order_id" if t2 == "orders" else None,
            lambda t1, t2: "employee_id" if t2 == "employees" else None,
            lambda t1, t2: "category_id" if t2 == "categories" else None,
            lambda t1, t2: "supplier_id" if t2 == "suppliers" else None
        ]
        
        # Check all table pairs
        for table1, df1 in self.dataframes.items():
            for table2, df2 in self.dataframes.items():
                if table1 == table2:
                    continue
                
                # Try to find foreign key columns in table1 that reference table2
                for pattern_func in relationship_patterns:
                    potential_fk = pattern_func(table1, table2)
                    if not potential_fk:
                        continue
                        
                    for col1 in df1.columns:
                        if col1.lower() == potential_fk.lower():
                            # Now find the matching primary key in table2
                            if table2 in self.primary_keys:
                                pk_col = self.primary_keys[table2]
                                self.relationships.append((table1, table2, col1, pk_col))
                            else:
                                # If no primary key is explicitly detected, look for likely candidates
                                for col2 in df2.columns:
                                    if col2.lower() in ['id', f'{table2}_id', f'{table2}id']:
                                        if df2[col2].is_unique:
                                            self.relationships.append((table1, table2, col1, col2))
                                            # Also register this as primary key for future reference
                                            self.primary_keys[table2] = col2
                                            break
        
        # Print detected relationships for debugging
        print(f"Detected {len(self.relationships)} relationships:")
        for rel in self.relationships:
            print(f"  {rel[0]}.{rel[2]} -> {rel[1]}.{rel[3]}")

    def merge_data(self) -> pd.DataFrame:
        """Merge tables based on detected relationships."""
        if not self.dataframes:
            raise ValueError("No data loaded")
            
        if not self.relationships:
            raise ValueError("No relationships detected between tables. Please add relationships manually.")
            
        # Create a graph of relationships to determine merge order
        relationship_graph = {}
        for table_name in self.dataframes.keys():
            relationship_graph[table_name] = []
            
        # Add relationships to the graph
        for rel in self.relationships:
            table1, table2, col1, col2 = rel
            if table1 in relationship_graph:
                relationship_graph[table1].append((table2, col1, col2))
            if table2 in relationship_graph:
                relationship_graph[table2].append((table1, col2, col1))
        
        # Find a table to start with (table with most relationships)
        start_table = max(relationship_graph.keys(), 
                         key=lambda table: len(relationship_graph[table]), 
                         default=next(iter(self.dataframes.keys())) if self.dataframes else None)
        
        if not start_table:
            raise ValueError("No tables to merge")
        
        # Start with the chosen table
        result_df = self.dataframes[start_table].copy()
        merged_tables = {start_table}
        remaining_tables = set(self.dataframes.keys()) - merged_tables
        
        # Keep track of merge attempts to avoid infinite loops
        merge_attempts = 0
        max_attempts = len(self.dataframes) * 2  # Allow more attempts than tables
        
        # Continue merging until all tables are merged or no more merges are possible
        while remaining_tables and merge_attempts < max_attempts:
            merge_attempts += 1
            
            # Try to find a table to merge
            merge_found = False
            
            # Look for direct connections to already merged tables
            for table in list(merged_tables):  # Use a copy since we're modifying the set
                for target_table, from_col, to_col in relationship_graph.get(table, []):
                    if target_table in remaining_tables:
                        # Merge this table
                        print(f"Merging {target_table} with {table} on {from_col}={to_col}")
                        
                        # Determine which table is already in result_df
                        if table in merged_tables:
                            left_on, right_on = from_col, to_col
                            right_df = self.dataframes[target_table]
                        else:
                            left_on, right_on = to_col, from_col
                            right_df = self.dataframes[table]
                        
                        # Perform the merge
                        result_df = pd.merge(
                            result_df,
                            right_df,
                            left_on=left_on,
                            right_on=right_on,
                            how='left'
                        )
                        
                        # Mark the table as merged
                        merged_tables.add(target_table)
                        remaining_tables.remove(target_table)
                        merge_found = True
            
            # If no merges were performed in this iteration, we can't continue
            if not merge_found:
                break
        
        # Warn about unmerged tables
        if remaining_tables:
            unmerged = ", ".join(remaining_tables)
            print(f"Warning: Could not find relationships to merge these tables: {unmerged}")
        
        return result_df

    def get_table_info(self) -> Dict:
        """Get information about loaded tables and their relationships."""
        return {
            'tables': list(self.dataframes.keys()),
            'primary_keys': self.primary_keys,
            'relationships': self.relationships
        }

    def set_primary_key(self, table_name: str, column_name: str) -> None:
        """Manually set a primary key for a table."""
        if table_name not in self.dataframes:
            raise ValueError(f"Table {table_name} not found in loaded dataframes")
        
        if column_name not in self.dataframes[table_name].columns:
            raise ValueError(f"Column {column_name} not found in table {table_name}")
            
        self.primary_keys[table_name] = column_name
        print(f"Manually set primary key for {table_name}: {column_name}")
        
    def add_relationship(self, table1: str, table2: str, column1: str, column2: str) -> None:
        """Manually add a relationship between two tables."""
        if table1 not in self.dataframes:
            raise ValueError(f"Table {table1} not found in loaded dataframes")
            
        if table2 not in self.dataframes:
            raise ValueError(f"Table {table2} not found in loaded dataframes")
            
        if column1 not in self.dataframes[table1].columns:
            raise ValueError(f"Column {column1} not found in table {table1}")
            
        if column2 not in self.dataframes[table2].columns:
            raise ValueError(f"Column {column2} not found in table {table2}")
            
        # Add the relationship
        self.relationships.append((table1, table2, column1, column2))
        print(f"Manually added relationship: {table1}.{column1} -> {table2}.{column2}")
    
    def print_tables(self) -> None:
        """Print information about loaded tables."""
        print("Loaded tables:")
        for table_name, df in self.dataframes.items():
            columns = ", ".join(df.columns)
            print(f"  {table_name}: {len(df)} rows, {len(df.columns)} columns")
            print(f"    Columns: {columns}")
            
    def print_table_preview(self, table_name: str, rows: int = 5) -> None:
        """Print a preview of a specific table."""
        if table_name not in self.dataframes:
            raise ValueError(f"Table {table_name} not found in loaded dataframes")
            
        print(f"Preview of table {table_name}:")
        print(self.dataframes[table_name].head(rows))
    
    def get_relationship_graph(self) -> dict:
        """Return a graph representation of table relationships."""
        graph = {}
        
        for table in self.dataframes.keys():
            graph[table] = []
            
        for rel in self.relationships:
            table1, table2, col1, col2 = rel
            if table1 not in graph:
                graph[table1] = []
            graph[table1].append({"table": table2, "from": col1, "to": col2})
            
        return graph 