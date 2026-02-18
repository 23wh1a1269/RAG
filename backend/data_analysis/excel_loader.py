"""Excel and CSV data loader with pandas."""
import pandas as pd
from pathlib import Path
from typing import Dict, List, Any

def load_excel_or_csv(file_path: str) -> Dict[str, Any]:
    """Load Excel or CSV file and return DataFrame with metadata."""
    path = Path(file_path)
    
    try:
        # Load based on extension
        if path.suffix.lower() == '.csv':
            df = pd.read_csv(file_path)
        elif path.suffix.lower() in ['.xlsx', '.xls']:
            # Read first sheet by default
            df = pd.read_excel(file_path, sheet_name=0)
        else:
            raise ValueError(f"Unsupported file type: {path.suffix}")
        
        # Handle large datasets - sample if needed
        original_rows = len(df)
        if original_rows > 10000:
            df = df.sample(n=10000, random_state=42)
            sampled = True
        else:
            sampled = False
        
        # Clean data
        df = df.dropna(how='all')  # Remove completely empty rows
        df = df.dropna(axis=1, how='all')  # Remove completely empty columns
        
        # Get metadata
        metadata = {
            'filename': path.name,
            'rows': len(df),
            'original_rows': original_rows,
            'sampled': sampled,
            'columns': df.columns.tolist(),
            'dtypes': {col: str(dtype) for col, dtype in df.dtypes.items()},
            'shape': df.shape,
            'preview': df.head(10).to_dict('records'),
            'memory_usage': df.memory_usage(deep=True).sum() / 1024 / 1024  # MB
        }
        
        return {
            'dataframe': df,
            'metadata': metadata,
            'success': True
        }
        
    except Exception as e:
        return {
            'dataframe': None,
            'metadata': None,
            'success': False,
            'error': str(e)
        }

def get_column_info(df: pd.DataFrame) -> List[Dict]:
    """Get detailed information about each column."""
    column_info = []
    
    for col in df.columns:
        info = {
            'name': col,
            'type': str(df[col].dtype),
            'non_null': int(df[col].count()),
            'null': int(df[col].isna().sum()),
            'unique': int(df[col].nunique()),
            'sample_values': df[col].dropna().head(5).tolist()
        }
        
        # Add type-specific info
        if pd.api.types.is_numeric_dtype(df[col]):
            info['numeric'] = True
            info['min'] = float(df[col].min()) if not df[col].isna().all() else None
            info['max'] = float(df[col].max()) if not df[col].isna().all() else None
            info['mean'] = float(df[col].mean()) if not df[col].isna().all() else None
        else:
            info['numeric'] = False
            info['categorical'] = True
        
        column_info.append(info)
    
    return column_info
