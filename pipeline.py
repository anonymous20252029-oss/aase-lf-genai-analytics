# ==============================================================================
# PIPELINE: ADVANCED ANALYTICS, TABLES & FIGURES FOR PAPER
# ==============================================================================

import pandas as pd
import numpy as np
import scipy.stats as stats
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import statsmodels.api as sm
import os

def run_pipeline():
    # 1. Plotting Configuration (IEEE / Springer Format)
    plt.style.use('seaborn-v0_8-paper')
    plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
    plt.rcParams['axes.edgecolor'] = '#333333'
    plt.rcParams['axes.linewidth'] = 0.8

    # Create directories for outputs if they don't exist
    os.makedirs('datasource', exist_ok=True)
    os.makedirs('figures', exist_ok=True)

    # 2. Load Data
    file_entry = 'SE301_ Khảo sát Đầu vào & Thiết lập Môi trường Thực hành (Tuần 1) (Responses) (1).xlsx'
    file_week7 = 'data-all.xlsx'

    df_entry_raw = pd.read_excel(file_entry)
    df_w7_raw = pd.read_excel(file_week7)

    # Filter consented students (Week 1 N=101)
    df_entry = df_entry_raw[df_entry_raw.iloc[:, 2].str.contains('đồng ý', case=False, na=False)].copy()

    # 3. Reliability & Quiz Scoring
    likert_cols_w7 = df_w7_raw.iloc[:, 8:12]
    quiz_cols_w7 = df_w7_raw.iloc[:, 12:132]

    for c in likert_cols_w7.columns:
        likert_cols_w7[c] = pd.to_numeric(likert_cols_w7[c], errors='coerce')

    def calculate_cronbach_alpha(df_items):
        item_vars = df_items.var(axis=0, ddof=1)
        total_var = df_items.sum(axis=1).var(ddof=1)
        k = df_items.shape[1]
        return (k / (k - 1)) * (1 - item_vars.sum() / total_var)

    alpha_likert = calculate_cronbach_alpha(likert_cols_w7)

    # Grade 120-item Quiz
    quiz_keys = quiz_cols_w7.mode().iloc[0]
    binary_quiz = (quiz_cols_w7 == quiz_keys).astype(int)
    quiz_scores = binary_quiz.sum(axis=1)
    kr20_quiz = calculate_cronbach_alpha(binary_quiz)

    df_w7_raw['Quiz_Score'] = quiz_scores
    df_w7_raw['Likert_Mean'] = likert_cols_w7.mean(axis=1)

    item_difficulty = binary_quiz.mean(axis=0)

    # 4. Statistical Models (OLS & Kruskal-Wallis)
    r_p, p_p = stats.pearsonr(df_w7_raw['Likert_Mean'], df_w7_raw['Quiz_Score'])
    exp_col = df_w7_raw.columns[6]
    X = sm.add_constant(df_w7_raw['Likert_Mean'])
    model = sm.OLS(df_w7_raw['Quiz_Score'], X).fit()

    exp_groups = [group['Quiz_Score'].values for name, group in df_w7_raw.groupby(exp_col)]
    kw_stat, kw_p = stats.kruskal(*exp_groups)

    # 5. K-Means Clustering (Week 1, N=101)
    freq_map = {
        'Hàng ngày (Là một phần cốt lõi trong quy trình làm việc)': 3,
        'Hàng tuần (Dùng khi gặp vướng mắc cụ thể)': 2,
        'Hiếm khi (Chỉ dùng khi bị tắc nghẽn nhiều giờ)': 1
    }

    w1_cluster_df = pd.DataFrame()
    w1_cluster_df['AI_Freq'] = df_entry.iloc[:, 9].map(freq_map).fillna(2)
    w1_cluster_df['Self_Efficacy'] = pd.to_numeric(df_entry.iloc[:, 11], errors='coerce').fillna(3)
    w1_cluster_df['Anxiety'] = pd.to_numeric(df_entry.iloc[:, 13], errors='coerce').fillna(3)

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(w1_cluster_df[['AI_Freq', 'Self_Efficacy', 'Anxiety']])

    kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
    w1_cluster_df['Cluster'] = kmeans.fit_predict(X_scaled)

    cluster_names = {
        0: 'Cluster 1: Anxious & Dependent', 
        1: 'Cluster 2: Autonomous AI-Daily', 
        2: 'Cluster 3: Moderate / Cautious'
    }
    w1_cluster_df['Cluster_Name'] = w1_cluster_df['Cluster'].map(cluster_names)

    # Jitter for visualization
    np.random.seed(42)
    w1_cluster_df['Self_Efficacy_Jitter'] = w1_cluster_df['Self_Efficacy'] + np.random.uniform(-0.12, 0.12, size=len(w1_cluster_df))
    w1_cluster_df['Anxiety_Jitter'] = w1_cluster_df['Anxiety'] + np.random.uniform(-0.12, 0.12, size=len(w1_cluster_df))

    # 6. Export CSV Tables
    table1 = pd.DataFrame({
        'Metric': ['Week 1 Sample Size', 'Week 7 Sample Size', "Cronbach's Alpha (Likert)", 'KR-20 (120-item Assessment)', 'Quiz Mean Score (out of 120)', 'Quiz Standard Deviation'],
        'Value': [len(df_entry), len(df_w7_raw), f"{alpha_likert:.4f}", f"{kr20_quiz:.4f}", f"{quiz_scores.mean():.2f}", f"{quiz_scores.std():.2f}"]
    })
    table1.to_csv('datasource/Table1_Reliability_Summary.csv', index=False)

    table2 = w1_cluster_df.groupby('Cluster_Name')[['AI_Freq', 'Self_Efficacy', 'Anxiety']].mean().reset_index()
    table2['Count'] = w1_cluster_df['Cluster_Name'].value_counts().values
    table2['Percentage (%)'] = (table2['Count'] / len(w1_cluster_df) * 100).round(1)
    table2.to_csv('datasource/Table2_KMeans_Archetypes.csv', index=False)

    table3 = pd.datasourceFrame({
        'Parameter': ['Intercept (const)', 'Slope (Likert_Mean)', 'R-squared', 'Pearson r', 'p-value'],
        'Value': [f"{model.params['const']:.4f}", f"{model.params['Likert_Mean']:.4f}", f"{model.rsquared:.4f}", f"{r_p:.4f}", f"{p_p:.4f}"]
    })
    table3.to_csv('datasource/Table3_Regression_Model.csv', index=False)

    # 7. Generate Figure 1
    fig, axes = plt.subplots(2, 2, figsize=(13, 11))

    sns.histplot(df_w7_raw['Quiz_Score'], bins=15, kde=True, color='#1f77b4', ax=axes[0,0])
    axes[0,0].set_title('(a) Distribution of Week 7 Assessment Scores', fontsize=11, fontweight='bold')
    axes[0,0].set_xlabel('Score (out of 120)')
    axes[0,0].set_ylabel('Student Frequency')

    sns.regplot(x='Likert_Mean', y='Quiz_Score', data=df_w7_raw, ax=axes[0,1],
                color='#d62728', scatter_kws={'alpha':0.6, 'color':'#1f77b4'}, line_kws={'linewidth':2})
    axes[0,1].set_title(f'(b) Perception vs Performance (R² = {model.rsquared:.3f}, p = {p_p:.3f})', fontsize=11, fontweight='bold')
    axes[0,1].set_xlabel('Likert Mean (Perception & Mindset)')
    axes[0,1].set_ylabel('Quiz Score (out of 120)')

    sns.scatterplot(x='Self_Efficacy_Jitter', y='Anxiety_Jitter', hue='Cluster_Name', data=w1_cluster_df, 
                    palette=['#e41a1c', '#377eb8', '#4daf4a'], s=80, ax=axes[1,0], alpha=0.85, edgecolor='k', linewidth=0.3)
    axes[1,0].set_title('(c) K-Means Clustering of Student Behaviors (Week 1, N=101)', fontsize=11, fontweight='bold')
    axes[1,0].set_xlabel('Self-Efficacy in Debugging (1-5 Scale)')
    axes[1,0].set_ylabel('Runtime Error Anxiety (1-5 Scale)')
    axes[1,0].legend(title='Student Archetypes', fontsize=8, loc='upper right')
    axes[1,0].set_xlim(0.5, 5.5)
    axes[1,0].set_ylim(0.5, 5.5)

    sns.boxplot(x=exp_col, y='Quiz_Score', hue=exp_col, data=df_w7_raw, ax=axes[1,1], palette='Blues', legend=False)
    axes[1,1].set_title('(d) Quiz Score by Prior Project Experience', fontsize=11, fontweight='bold')
    axes[1,1].set_xlabel('Project Experience Level')
    axes[1,1].set_ylabel('Quiz Score')
    axes[1,1].set_xticks(range(3))
    axes[1,1].set_xticklabels(['No Project', '1-2 Projects', '>2 Projects'], rotation=0)

    plt.tight_layout()
    plt.savefig('figures/Figure1_Empirical_Analysis_300DPI.png', dpi=300)
    plt.close()

    # 8. Generate Figure 2
    plt.figure(figsize=(12, 4))
    plt.plot(range(1, 121), item_difficulty, color='#2b5c8f', linewidth=1.2)
    plt.axhline(y=item_difficulty.mean(), color='r', linestyle='--', label=f'Mean Difficulty ({item_difficulty.mean():.2f})')
    plt.title('Figure 2: Item Difficulty Profile Across 120 Assessment Questions', fontsize=11, fontweight='bold')
    plt.xlabel('Question Item (1 to 120)')
    plt.ylabel('Pass Rate / Difficulty Index (p)')
    plt.ylim(0, 1.05)
    plt.legend()
    plt.tight_layout()
    plt.savefig('figures/Figure2_Item_Difficulty_300DPI.png', dpi=300)
    plt.close()

    print("[+] Pipeline execution finished successfully!")

if __name__ == '__main__':
    run_pipeline()
