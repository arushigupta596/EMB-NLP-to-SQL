"""Data loading and normalization module."""
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple
import logging

logger = logging.getLogger(__name__)


class DataLoader:
    """Handle loading and normalizing Excel/CSV files."""

    def __init__(self, data_dir: Path):
        """Initialize data loader.

        Args:
            data_dir: Path to directory containing data files
        """
        self.data_dir = Path(data_dir)
        self.dataframes: Dict[str, pd.DataFrame] = {}

    def load_all_files(self) -> Dict[str, pd.DataFrame]:
        """Load all CSV and Excel files from the data directory.

        Returns:
            Dictionary mapping table names to DataFrames
        """
        logger.info(f"Loading files from {self.data_dir}")

        if not self.data_dir.exists():
            raise FileNotFoundError(f"Data directory not found: {self.data_dir}")

        # Support both CSV and Excel files
        file_patterns = ["*.csv", "*.xlsx", "*.xls"]
        files = []
        for pattern in file_patterns:
            files.extend(self.data_dir.glob(pattern))

        if not files:
            raise ValueError(f"No data files found in {self.data_dir}")

        for file_path in files:
            try:
                table_name = file_path.stem
                logger.info(f"Loading {file_path.name}")

                if file_path.suffix == '.csv':
                    df = pd.read_csv(file_path)
                else:
                    df = pd.read_excel(file_path)

                # Normalize the dataframe
                df = self._normalize_dataframe(df, table_name)
                self.dataframes[table_name] = df

                logger.info(f"Loaded {table_name}: {df.shape[0]} rows, {df.shape[1]} columns")

            except Exception as e:
                logger.error(f"Error loading {file_path.name}: {str(e)}")
                continue

        return self.dataframes

    def _normalize_dataframe(self, df: pd.DataFrame, table_name: str) -> pd.DataFrame:
        """Normalize a DataFrame.

        Args:
            df: Input DataFrame
            table_name: Name of the table

        Returns:
            Normalized DataFrame
        """
        # Make a copy to avoid modifying original
        df = df.copy()

        # 1. Clean column names
        df.columns = df.columns.str.strip()
        df.columns = df.columns.str.lower()
        df.columns = df.columns.str.replace(' ', '_')
        df.columns = df.columns.str.replace('[^a-z0-9_]', '', regex=True)

        # 2. Remove duplicate columns
        df = df.loc[:, ~df.columns.duplicated()]

        # 3. Handle missing values
        for col in df.columns:
            # For numeric columns, fill with median
            if df[col].dtype in ['int64', 'float64']:
                if df[col].isna().any():
                    median_val = df[col].median()
                    df[col].fillna(median_val, inplace=True)
            # For categorical/string columns, fill with mode or 'Unknown'
            elif df[col].dtype == 'object':
                if df[col].isna().any():
                    mode_val = df[col].mode()
                    if len(mode_val) > 0:
                        df[col].fillna(mode_val[0], inplace=True)
                    else:
                        df[col].fillna('Unknown', inplace=True)

        # 4. Remove duplicate rows
        original_rows = len(df)
        df = df.drop_duplicates()
        if len(df) < original_rows:
            logger.info(f"Removed {original_rows - len(df)} duplicate rows from {table_name}")

        # 5. Strip whitespace from string columns
        for col in df.select_dtypes(include=['object']):
            df[col] = df[col].astype(str).str.strip()

        # 6. Detect and convert date columns
        for col in df.columns:
            if 'date' in col.lower() or 'time' in col.lower():
                try:
                    df[col] = pd.to_datetime(df[col], errors='coerce')
                except:
                    pass

        # 7. Reset index
        df.reset_index(drop=True, inplace=True)

        return df

    def get_table_info(self) -> Dict[str, Dict]:
        """Get information about all loaded tables.

        Returns:
            Dictionary with table information
        """
        info = {}
        for table_name, df in self.dataframes.items():
            info[table_name] = {
                'rows': len(df),
                'columns': list(df.columns),
                'dtypes': {col: str(dtype) for col, dtype in df.dtypes.items()},
                'sample': df.head(3).to_dict('records')
            }
        return info

    def get_dataframe(self, table_name: str) -> pd.DataFrame:
        """Get a specific DataFrame by table name.

        Args:
            table_name: Name of the table

        Returns:
            DataFrame
        """
        if table_name not in self.dataframes:
            raise ValueError(f"Table {table_name} not found. Available tables: {list(self.dataframes.keys())}")
        return self.dataframes[table_name]

    def get_table_names(self) -> List[str]:
        """Get list of all table names.

        Returns:
            List of table names
        """
        return list(self.dataframes.keys())
