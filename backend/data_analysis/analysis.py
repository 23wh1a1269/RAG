"""Data analysis and statistics generation."""
import pandas as pd
import numpy as np
from typing import Dict, Any, List

def generate_statistics(df: pd.DataFrame) -> Dict[str, Any]:
    """Generate comprehensive statistics for the dataset."""
    
    stats = {
        'basic': {
            'rows': len(df),
            'columns': len(df.columns),
            'total_cells': df.size,
            'memory_mb': df.memory_usage(deep=True).sum() / 1024 / 1024
        },
        'missing_values': {
            'total': int(df.isna().sum().sum()),
            'by_column': {col: int(df[col].isna().sum()) for col in df.columns}
        },
        'numeric_stats': {},
        'categorical_stats': {},
        'correlations': None,
        'outliers': {},
        'trends': {}
    }
    
    # Numeric columns analysis
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    if numeric_cols:
        desc = df[numeric_cols].describe().to_dict()
        stats['numeric_stats'] = desc
        
        # Correlations
        if len(numeric_cols) > 1:
            corr = df[numeric_cols].corr()
            stats['correlations'] = corr.to_dict()
        
        # Detect outliers using IQR
        for col in numeric_cols:
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            outliers = df[(df[col] < Q1 - 1.5 * IQR) | (df[col] > Q3 + 1.5 * IQR)][col]
            if len(outliers) > 0:
                stats['outliers'][col] = {
                    'count': len(outliers),
                    'values': outliers.head(10).tolist()
                }
    
    # Categorical columns analysis
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
    if categorical_cols:
        for col in categorical_cols[:5]:  # Limit to first 5
            value_counts = df[col].value_counts().head(10)
            stats['categorical_stats'][col] = {
                'unique': int(df[col].nunique()),
                'top_values': value_counts.to_dict(),
                'mode': df[col].mode()[0] if len(df[col].mode()) > 0 else None
            }
    
    return stats

def detect_trends(df: pd.DataFrame) -> Dict[str, Any]:
    """Detect trends in numeric columns."""
    trends = {}
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    
    for col in numeric_cols[:5]:  # Limit to first 5
        if len(df[col].dropna()) > 2:
            values = df[col].dropna().values
            # Simple trend detection
            if len(values) > 1:
                diff = values[-1] - values[0]
                pct_change = (diff / values[0] * 100) if values[0] != 0 else 0
                
                trends[col] = {
                    'direction': 'increasing' if diff > 0 else 'decreasing' if diff < 0 else 'stable',
                    'change': float(diff),
                    'percent_change': float(pct_change),
                    'min': float(values.min()),
                    'max': float(values.max()),
                    'mean': float(values.mean())
                }
    
    return trends

def find_insights(df: pd.DataFrame, stats: Dict) -> List[str]:
    """Generate automatic insights from data."""
    insights = []
    
    # Missing data insights
    total_missing = stats['missing_values']['total']
    if total_missing > 0:
        pct = (total_missing / (df.shape[0] * df.shape[1])) * 100
        insights.append(f"Dataset has {total_missing} missing values ({pct:.1f}% of total data)")
    
    # Outlier insights
    if stats['outliers']:
        for col, outlier_info in stats['outliers'].items():
            insights.append(f"Column '{col}' has {outlier_info['count']} outliers detected")
    
    # Correlation insights
    if stats['correlations']:
        corr_df = pd.DataFrame(stats['correlations'])
        # Find strong correlations (>0.7 or <-0.7)
        for i in range(len(corr_df.columns)):
            for j in range(i+1, len(corr_df.columns)):
                corr_val = corr_df.iloc[i, j]
                if abs(corr_val) > 0.7:
                    col1 = corr_df.columns[i]
                    col2 = corr_df.columns[j]
                    insights.append(f"Strong correlation ({corr_val:.2f}) between '{col1}' and '{col2}'")
    
    # Categorical insights
    if stats['categorical_stats']:
        for col, cat_stats in stats['categorical_stats'].items():
            if cat_stats['unique'] < 10:
                insights.append(f"Column '{col}' has {cat_stats['unique']} unique categories")
    
    return insights[:10]  # Limit to top 10 insights
