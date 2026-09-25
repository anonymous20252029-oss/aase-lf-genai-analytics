import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

st.set_page_config(
    page_title="AASE-LF GenAI Analytics Platform",
    page_icon="🎓",
    layout="wide"
)

st.title("🎓 Empirical Profiling & AASE-LF Pedagogical Platform")
st.markdown("""
**Paper Reference:** *Empirical Profiling and Pedagogical Assessment of Generative AI Integration in Computing Education: A Two-Phase Mixed-Methods Study*
""")

# Sidebar Navigation
st.sidebar.header("Navigation")
option = st.sidebar.radio(
    "Select Module:",
    ["1. Real-Time Archetype Profiler", "2. AASE-LF Prompt Assistant", "3. Instructor Diagnostic Dashboard"]
)

# ==============================================================================
# MODULE 1: REAL-TIME ARCHETYPE PROFILER
# ==============================================================================
if option == "1. Real-Time Archetype Profiler":
    st.header("🔍 Real-Time Student Archetype Profiler")
    st.markdown("Input student baseline metrics to dynamically classify them into a research archetype.")

    col1, col2, col3 = st.columns(3)
    with col1:
        ai_freq = st.selectbox("GenAI Usage Frequency:", [1, 2, 3], 
                               format_func=lambda x: {1: "Rarely", 2: "Weekly", 3: "Daily"}[x])
    with col2:
        efficacy = st.slider("Debugging Self-Efficacy (1-5):", 1.0, 5.0, 2.5, 0.1)
    with col3:
        anxiety = st.slider("Runtime Error Anxiety (1-5):", 1.0, 5.0, 3.5, 0.1)

    if st.button("Classify Archetype"):
        # Centroids based on empirical K-Means model (Table 2)
        # C1: Anxious & Dependent (2.77, 1.65, 4.42)
        # C2: Autonomous AI-Daily (3.00, 2.83, 2.85)
        # C3: Moderate / Cautious (1.91, 2.91, 3.53)
        centroids = np.array([
            [2.77, 1.65, 4.42],
            [3.00, 2.83, 2.85],
            [1.91, 2.91, 3.53]
        ])
        
        user_vector = np.array([ai_freq, efficacy, anxiety])
        distances = np.linalg.norm(centroids - user_vector, axis=1)
        cluster_idx = np.argmin(distances)

        archetypes = [
            ("Cluster 1: Anxious & Dependent", "error", 
             "⚠️ High anxiety and low efficacy despite heavy AI reliance. **Recommended Intervention:** Provide scaffolded conceptual prompts to prevent passive copy-pasting."),
            ("Cluster 2: Autonomous AI-Daily", "success", 
             "✅ Strong self-efficacy and low anxiety with frequent AI usage. **Recommended Intervention:** Engage with architectural decomposition and edge-case verification tasks."),
            ("Cluster 3: Moderate / Cautious", "info", 
             "ℹ️ Deliberate AI usage with high self-efficacy. **Recommended Intervention:** Encourage deeper integration of AI for automated unit testing.")
        ]

        name, status_type, advice = archetypes[cluster_idx]
        
        if status_type == "error":
            st.error(f"**Classification Outcome:** {name}")
        elif status_type == "success":
            st.success(f"**Classification Outcome:** {name}")
        else:
            st.info(f"**Classification Outcome:** {name}")
            
        st.markdown(advice)

# ==============================================================================
# MODULE 2: AASE-LF INTERACTIVE PROMPT ASSISTANT
# ==============================================================================
elif option == "2. AASE-LF Prompt Assistant":
    st.header("🛠 Scaffolded Conceptual Prompt Builder (AASE-LF Protocol)")
    st.markdown("Enforces the 3-step interaction protocol to prevent uncritical AI code generation.")

    step = st.tabs(["Step 1: Conceptual Decomposition", "Step 2: Error Trace Diagnosis", "Step 3: Code Verification"])

    with step[0]:
        concept = st.text_input("Enter unfamiliar topic / design pattern:", "Observer Pattern in Java")
        st.code(f"""
Prompt: Explain the core mechanism of '{concept}' using an everyday analogy. 
Do NOT write full implementation code yet. Focus on the structural relationship 
between components and list 3 key benefits.
        """, language="markdown")

    with step[1]:
        error_log = st.text_area("Paste error log:", "NullPointerException at com.example.Main.render(Main.java:42)")
        user_hypothesis = st.text_input("Your initial hypothesis:", "The object context was not initialized before render()")
        st.code(f"""
Prompt: I encountered the following error trace:
{error_log}

My hypothesis is: '{user_hypothesis}'.
Based on this log, do NOT provide a direct code fix. Instead:
1. Evaluate whether my hypothesis is correct.
2. Provide 2 diagnostic clues to help me trace the root cause manually.
        """, language="markdown")

    with step[2]:
        requirements = st.text_area("Function description:", "A method that calculates the average quiz score given an array of integers.")
        st.code(f"""
Prompt: I need to write unit tests for a function described as follows:
'{requirements}'

Provide a list of 5 edge-case scenarios (e.g., empty input, boundary values) 
and JUnit test cases without implementing the target function logic.
        """, language="markdown")

# ==============================================================================
# MODULE 3: INSTRUCTOR DIAGNOSTIC DASHBOARD
# ==============================================================================
elif option == "3. Instructor Diagnostic Dashboard":
    st.header("📊 Cohort Analytics & Empirical Overview")

    if os.path.exists("data/Table1_Reliability_Summary.csv"):
        t1 = pd.read_csv("data/Table1_Reliability_Summary.csv")
        t2 = pd.read_csv("data/Table2_KMeans_Archetypes.csv")
        t3 = pd.read_csv("data/Table3_Regression_Model.csv")

        st.subheader("1. Measurement Reliability (Table 1)")
        st.dataframe(t1, use_container_width=True)

        st.subheader("2. Student Behavioral Archetypes (Table 2)")
        st.dataframe(t2, use_container_width=True)

        st.subheader("3. OLS Regression Model (Table 3)")
        st.dataframe(t3, use_container_width=True)
    else:
        st.warning("Processed CSV data files not found in `/data`. Run `python pipeline.py` first to generate tables.")

    st.subheader("4. Publication Figures")
    fig_col1, fig_col2 = st.columns(2)

    with fig_col1:
        if os.path.exists("figures/Figure1_Empirical_Analysis_300DPI.png"):
            st.image("figures/Figure1_Empirical_Analysis_300DPI.png", caption="Figure 1: Empirical Evaluation")
        else:
            st.info("Figure 1 not found in `/figures`.")

    with fig_col2:
        if os.path.exists("figures/Figure2_Item_Difficulty_300DPI.png"):
            st.image("figures/Figure2_Item_Difficulty_300DPI.png", caption="Figure 2: Item Difficulty Profile")
        else:
            st.info("Figure 2 not found in `/figures`.")
