"""LLM-powered insights generation with grounding."""
from groq import Groq
from typing import Dict, Any
import json

def generate_llm_insights(stats: Dict[str, Any], groq_api_key: str, groq_model: str) -> str:
    """Generate natural language insights using LLM with grounded statistics."""
    
    # Prepare grounded context from computed statistics
    context = f"""Dataset Statistics:
- Total Rows: {stats['basic']['rows']}
- Total Columns: {stats['basic']['columns']}
- Missing Values: {stats['missing_values']['total']}

"""
    
    # Add numeric statistics
    if stats.get('numeric_stats'):
        context += "Numeric Columns Summary:\n"
        for col, col_stats in list(stats['numeric_stats'].items())[:5]:
            if 'mean' in col_stats:
                context += f"- {col}: mean={col_stats['mean']:.2f}, min={col_stats['min']:.2f}, max={col_stats['max']:.2f}\n"
    
    # Add categorical info
    if stats.get('categorical_stats'):
        context += "\nCategorical Columns:\n"
        for col, col_stats in list(stats['categorical_stats'].items())[:3]:
            context += f"- {col}: {col_stats['unique']} unique values\n"
    
    # Add outliers
    if stats.get('outliers'):
        context += f"\nOutliers Detected: {len(stats['outliers'])} columns have outliers\n"
    
    # Add correlations
    if stats.get('correlations'):
        context += "\nCorrelations: Available between numeric columns\n"
    
    prompt = f"""You are a data analyst. Analyze the following dataset statistics and provide insights.

{context}

Provide:
1. A brief summary of the dataset
2. Key findings (3-5 points)
3. Notable patterns or anomalies
4. Recommendations for further analysis

IMPORTANT: Only use the statistics provided above. Do not invent numbers or facts."""
    
    try:
        client = Groq(api_key=groq_api_key)
        completion = client.chat.completions.create(
            model=groq_model,
            messages=[
                {"role": "system", "content": "You are a data analyst who provides insights based strictly on provided statistics. Never fabricate data."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=600
        )
        
        return completion.choices[0].message.content.strip()
    
    except Exception as e:
        return f"Unable to generate insights: {str(e)}"

def answer_data_question(question: str, stats: Dict[str, Any], df_info: Dict, groq_api_key: str, groq_model: str) -> str:
    """Answer questions about the dataset using computed statistics."""
    
    # Build context from statistics
    context = f"""Dataset Information:
- Rows: {stats['basic']['rows']}
- Columns: {stats['basic']['columns']}
- Column Names: {', '.join(df_info.get('columns', []))}

Statistics Available:
"""
    
    # Add relevant stats
    if stats.get('numeric_stats'):
        context += "\nNumeric Statistics:\n"
        for col, col_stats in stats['numeric_stats'].items():
            if 'mean' in col_stats:
                context += f"- {col}: mean={col_stats['mean']:.2f}, median={col_stats.get('50%', 'N/A')}, std={col_stats.get('std', 'N/A'):.2f}\n"
    
    if stats.get('categorical_stats'):
        context += "\nCategorical Data:\n"
        for col, col_stats in stats['categorical_stats'].items():
            context += f"- {col}: {col_stats['unique']} unique values, mode={col_stats.get('mode', 'N/A')}\n"
    
    prompt = f"""You are analyzing a dataset. Answer the user's question using ONLY the provided statistics.

{context}

User Question: {question}

Rules:
1. Answer using only the statistics provided above
2. If the question cannot be answered with available data, say: "This cannot be determined from the uploaded dataset."
3. Be precise and factual
4. Do not invent or estimate values"""
    
    try:
        client = Groq(api_key=groq_api_key)
        completion = client.chat.completions.create(
            model=groq_model,
            messages=[
                {"role": "system", "content": "You are a data analyst assistant. Answer questions using only provided statistics. Never fabricate data."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=400
        )
        
        return completion.choices[0].message.content.strip()
    
    except Exception as e:
        return f"Unable to answer question: {str(e)}"
