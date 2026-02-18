"""Visualization generation using Plotly."""
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import List, Dict, Any
import numpy as np

def generate_charts(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """Generate Plotly charts based on data types."""
    charts = []
    
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
    
    # 1. Numeric distributions (histograms)
    for col in numeric_cols[:3]:  # Limit to 3
        fig = px.histogram(df, x=col, title=f'Distribution of {col}',
                          labels={col: col}, nbins=30)
        fig.update_layout(showlegend=False, height=400)
        charts.append({
            'type': 'histogram',
            'title': f'Distribution of {col}',
            'data': fig.to_json()
        })
    
    # 2. Categorical bar charts
    for col in categorical_cols[:2]:  # Limit to 2
        value_counts = df[col].value_counts().head(10)
        fig = px.bar(x=value_counts.index, y=value_counts.values,
                    title=f'Top Values in {col}',
                    labels={'x': col, 'y': 'Count'})
        fig.update_layout(showlegend=False, height=400)
        charts.append({
            'type': 'bar',
            'title': f'Top Values in {col}',
            'data': fig.to_json()
        })
    
    # 3. Correlation heatmap (if multiple numeric columns)
    if len(numeric_cols) > 1:
        corr = df[numeric_cols].corr()
        fig = px.imshow(corr, text_auto=True, aspect='auto',
                       title='Correlation Heatmap',
                       color_continuous_scale='RdBu_r')
        fig.update_layout(height=500)
        charts.append({
            'type': 'heatmap',
            'title': 'Correlation Heatmap',
            'data': fig.to_json()
        })
    
    # 4. Box plots for outlier detection
    if len(numeric_cols) > 0:
        col = numeric_cols[0]
        fig = px.box(df, y=col, title=f'Box Plot - {col}')
        fig.update_layout(showlegend=False, height=400)
        charts.append({
            'type': 'box',
            'title': f'Box Plot - {col}',
            'data': fig.to_json()
        })
    
    # 5. Scatter plot if 2+ numeric columns
    if len(numeric_cols) >= 2:
        fig = px.scatter(df, x=numeric_cols[0], y=numeric_cols[1],
                        title=f'{numeric_cols[0]} vs {numeric_cols[1]}',
                        opacity=0.6)
        fig.update_layout(height=400)
        charts.append({
            'type': 'scatter',
            'title': f'{numeric_cols[0]} vs {numeric_cols[1]}',
            'data': fig.to_json()
        })
    
    return charts[:6]  # Max 6 charts

def create_summary_chart(stats: Dict) -> Dict[str, Any]:
    """Create a summary visualization of key metrics."""
    # Create a simple bar chart of column types
    dtypes_count = {}
    for dtype in stats.get('numeric_stats', {}).keys():
        dtypes_count['Numeric'] = dtypes_count.get('Numeric', 0) + 1
    for dtype in stats.get('categorical_stats', {}).keys():
        dtypes_count['Categorical'] = dtypes_count.get('Categorical', 0) + 1
    
    if dtypes_count:
        fig = px.bar(x=list(dtypes_count.keys()), y=list(dtypes_count.values()),
                    title='Column Types Distribution',
                    labels={'x': 'Type', 'y': 'Count'})
        fig.update_layout(showlegend=False, height=300)
        return {
            'type': 'summary',
            'title': 'Column Types',
            'data': fig.to_json()
        }
    
    return None
