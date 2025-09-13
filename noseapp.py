# app.py
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ============================================
# Custom CSS styling
# ============================================
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap');

    html, body, [class*="css"]  {
        font-family: 'Poppins', sans-serif;
    }

    .title {
        text-align: center;
        color: #FF7F11;
        font-size: 36px;
        font-weight: 600;
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# ============================================
# Helpers
# ============================================
def collapse(result, levels):
    """Collapse Moderate into Severe if 2-level mode chosen."""
    if levels == 2 and result == "MODERATE":
        return "SEVERE"
    return result

def check_sparse(a, b, c, d):
    """Check if table has at least one zero cell."""
    if all(x > 0 for x in [a, b, c, d]):
        return "ERROR: This tool applies only to sparse tables (at least one zero cell)."
    return None

# ============================================
# Classifiers (rules from published paper)
# ============================================
def classify_or(a, b, c, d, epsilon=0.5, levels=3):
    err = check_sparse(a, b, c, d)
    if err: return err

    cc = epsilon
    m = 1.0 / cc

    if a == 0 and (b * c * d > 0):
        if d <= (b + c): return collapse("MILD", levels)
        elif d <= (b + c) + (m * b * c): return collapse("MODERATE", levels)
        else: return collapse("SEVERE", levels)

    if b == 0 and (a * c * d > 0):
        if c <= (a + d): return collapse("MILD", levels)
        elif c <= (a + d) + (m * a * d): return collapse("MODERATE", levels)
        else: return collapse("SEVERE", levels)

    if c == 0 and (a * b * d > 0):
        if b <= (a + d): return collapse("MILD", levels)
        elif b <= (a + d) + (m * a * d): return collapse("MODERATE", levels)
        else: return collapse("SEVERE", levels)

    if d == 0 and (a * b * c > 0):
        if a <= (b + c): return collapse("MILD", levels)
        elif a <= (b + c) + (m * b * c): return collapse("MODERATE", levels)
        else: return collapse("SEVERE", levels)

    if a == 0 and b == 0 and (c * d > 0):
        return collapse("MILD" if d <= 2 * c * (c + 1) else "SEVERE", levels)

    if a == 0 and c == 0 and (b * d > 0):
        return collapse("MILD" if d <= 2 * b * (b + 1) else "SEVERE", levels)

    if a == 0 and d == 0 and (b * c > 0): return collapse("MODERATE", levels)
    if b == 0 and c == 0 and (a * d > 0): return collapse("MILD", levels)

    if b == 0 and d == 0 and (a * c > 0):
        return collapse("MILD" if a <= 2 * c * (c + 1) else "SEVERE", levels)

    if c == 0 and d == 0 and (a * b > 0):
        return collapse("MILD" if a <= 2 * b * (b + 1) else "SEVERE", levels)

    if a == 0 and b == 0 and c == 0 and d > 0: return collapse("SEVERE", levels)
    if a == 0 and b == 0 and d == 0 and c > 0: return collapse("MODERATE", levels)
    if a == 0 and c == 0 and d == 0 and b > 0: return collapse("SEVERE", levels)
    if b == 0 and c == 0 and d == 0 and a > 0: return collapse("MODERATE", levels)
    if a == b == c == d == 0: return collapse("SEVERE", levels)

    return collapse("MILD", levels)

def classify_rr(a, b, c, d, nt, nc, levels=3):
    err = check_sparse(a, b, c, d)
    if err: return err

    if a == 0 and (b * c * d > 0):
        return collapse("MODERATE" if d > (b + c) else "MILD", levels)

    if c == 0 and (a * b * d > 0):
        return collapse("MODERATE" if b <= (d + a) else "MILD", levels)

    if b == 0 and d == 0:
        return collapse("MILD" if a == c else "SEVERE", levels)

    if b == 0 and (a * c * d > 0): return collapse("MILD", levels)
    if d == 0 and (a * b * c > 0): return collapse("MILD", levels)

    if a == 0 and b == 0: return collapse("MILD", levels)
    if a == 0 and c == 0: return collapse("MILD", levels)
    if a == 0 and d == 0: return collapse("MILD", levels)
    if b == 0 and c == 0: return collapse("MILD", levels)
    if c == 0 and d == 0: return collapse("MILD", levels)

    if a == 0 and b == 0 and c == 0 and d > 0: return collapse("MILD", levels)
    if a == 0 and b == 0 and d == 0 and c > 0: return collapse("MILD", levels)
    if a == 0 and c == 0 and d == 0 and b > 0: return collapse("MILD", levels)
    if b == 0 and c == 0 and d == 0 and a > 0: return collapse("MILD", levels)
    if a == b == c == d == 0: return collapse("MILD", levels)

    return collapse("MILD", levels)

def classify_rd(a, b, c, d, nt, nc, levels=3):
    err = check_sparse(a, b, c, d)
    if err: return err

    if a == 0 and c == 0 and (b * d > 0):
        return collapse("MILD" if nt == nc else "SEVERE", levels)

    if b == 0 and d == 0 and (a * c > 0):
        return collapse("MILD" if nt == nc else "SEVERE", levels)

    if a == 0 and (b * c * d > 0): return collapse("MILD", levels)
    if b == 0 and (a * c * d > 0): return collapse("MILD", levels)
    if c == 0 and (a * b * d > 0): return collapse("MILD", levels)
    if d == 0 and (a * b * c > 0): return collapse("MILD", levels)

    if a == 0 and d == 0 and (b * c > 0): return collapse("MILD", levels)
    if a == 0 and b == 0 and (c * d > 0): return collapse("MILD", levels)
    if b == 0 and c == 0 and (a * d > 0): return collapse("MILD", levels)
    if c == 0 and d == 0 and (a * b > 0): return collapse("MILD", levels)

    if a == 0 and b == 0 and c == 0 and d > 0: return collapse("SEVERE", levels)
    if a == 0 and b == 0 and d == 0 and c > 0: return collapse("SEVERE", levels)
    if a == 0 and c == 0 and d == 0 and b > 0: return collapse("SEVERE", levels)
    if b == 0 and c == 0 and d == 0 and a > 0: return collapse("SEVERE", levels)
    if a == b == c == d == 0: return collapse("MILD", levels)

    return collapse("MILD", levels)

# ============================================
# Navigation
# ============================================
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Home", "Single Table", "Batch Upload", "Sensitivity Plot"])

# ============================================
# Page 1: Home
# ============================================
if page == "Home":
    st.markdown('<div class="title">Sparse Contingency Table Classifier</div>', unsafe_allow_html=True)

    st.markdown("""
    ### About this Package

    This Streamlit package implements the methodology of:

    **Subbiah, M. & Srinivasan, M.R. (2008). 
    "Classification of 2×2 sparse data sets with zero cells," 
    *Statistics & Probability Letters*, 78(18), 3212–3215. Elsevier.**

    The classifier is designed for **2×2 contingency tables with one or more zero cells**. 
    Standard methods can be unreliable in such sparse cases; this tool provides a systematic 
    classification into **Mild**, **Moderate**, or **Severe** sparseness.

    **Key Features:**
    - Classify single or multiple 2×2 tables
    - Choice of 2-level (Mild/Severe) or 3-level (Mild/Moderate/Severe) classification
    - Support for Odds Ratio, Relative Risk, and Risk Difference
    - Adjustable continuity correction (ε) down to 1e-8
    - Sensitivity plots of measure values versus ε
    """)

# ============================================
# Page 2: Single Table
# ============================================
elif page == "Single Table":
    st.markdown('<div class="title">Classify a Single 2×2 Table</div>', unsafe_allow_html=True)

    # show static layout image
    st.image("table_layout.png", caption="2×2 Table Layout (a, b, c, d)", width=250)

    measure = st.sidebar.selectbox("Summary Measure", ["OR", "RR", "RD"])
    levels = st.sidebar.radio("Classification Levels", [2, 3], index=1)
    epsilon = st.sidebar.number_input("Continuity correction ε", value=0.5, min_value=1e-8, format="%.8f")

    col1, col2 = st.columns(2)
    with col1:
        a = st.number_input("a (Top-Left)", value=5)
        b = st.number_input("b (Top-Right)", value=1)
    with col2:
        c = st.number_input("c (Bottom-Left)", value=0)
        d = st.number_input("d (Bottom-Right)", value=10)

    nt, nc = a + b, c + d

    if st.button("Classify"):
        if measure == "OR":
            cls = classify_or(a, b, c, d, epsilon, levels)
        elif measure == "RR":
            cls = classify_rr(a, b, c, d, nt, nc, levels)
        else:
            cls = classify_rd(a, b, c, d, nt, nc, levels)
        st.success(f"Classification: {cls}")

# ============================================
# Page 3: Batch Upload
# ============================================
elif page == "Batch Upload":
    st.markdown('<div class="title">Batch Upload Classification</div>', unsafe_allow_html=True)

    measure = st.sidebar.selectbox("Summary Measure", ["OR", "RR", "RD"])
    levels = st.sidebar.radio("Classification Levels", [2, 3], index=1)
    epsilon = st.sidebar.number_input("Continuity correction ε", value=0.5, min_value=1e-8, format="%.8f")

    uploaded = st.file_uploader("Upload CSV with columns a,b,c,d", type=["csv"])
    if uploaded:
        df = pd.read_csv(uploaded)
        results = []
        for _, row in df.iterrows():
            a,b,c,d = int(row["a"]), int(row["b"]), int(row["c"]), int(row["d"])
            nt, nc = a+b, c+d
            if measure == "OR":
                cls = classify_or(a,b,c,d,epsilon,levels)
            elif measure == "RR":
                cls = classify_rr(a,b,c,d,nt,nc,levels)
            else:
                cls = classify_rd(a,b,c,d,nt,nc,levels)
            results.append([a,b,c,d,cls])
        res_df = pd.DataFrame(results, columns=["a","b","c","d","Class"])
        st.dataframe(res_df)
        csv = res_df.to_csv(index=False).encode("utf-8")
        st.download_button("Download Results", data=csv, file_name="classification_results.csv")

# ============================================
# Page 4: Sensitivity Plot
# ============================================
elif page == "Sensitivity Plot":
    st.markdown('<div class="title">Sensitivity to Continuity Correction ε</div>', unsafe_allow_html=True)

    measure = st.sidebar.selectbox("Summary Measure", ["OR", "RR", "RD"])
    scale = st.sidebar.radio("X-axis scale", ["Log", "Linear"], index=0)

    a = st.number_input("a", value=1)
    b = st.number_input("b", value=0)
    c = st.number_input("c", value=2)
    d = st.number_input("d", value=5)

    epsilons = np.logspace(-8, 0, 200)  # ε from 1e-8 to 1
    values = []

    for eps in epsilons:
        a_eps, b_eps, c_eps, d_eps = a+eps, b+eps, c+eps, d+eps
        if measure == "OR":
            val = (a_eps * d_eps) / (b_eps * c_eps)
        elif measure == "RR":
            val = (a_eps / (a_eps + b_eps)) / (c_eps / (c_eps + d_eps))
        else:  # RD
            val = (a_eps / (a_eps + b_eps)) - (c_eps / (c_eps + d_eps))
        values.append(val)

    # Plot
    plt.style.use("dark_background")
    plt.figure(figsize=(8,4))
    if scale == "Log":
        plt.semilogx(epsilons, values, color="#FF7F11", linewidth=2)
    else:
        plt.plot(epsilons, values, color="#FF7F11", linewidth=2)

    plt.xlabel("Continuity correction ε")
    plt.ylabel(measure)
    plt.title(f"Sensitivity of {measure} to ε ({scale} scale)")
    st.pyplot(plt)
