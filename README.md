# NOSE_Stlit
Nature of Sparsenss - NOSE project – Streamlit web application

# NOSE_Stlit

This Streamlit app implements the methodology of:

**Subbiah, M. & Srinivasan, M.R. (2008).**  
*"Classification of 2×2 sparse data sets with zero cells,"*  
*Statistics & Probability Letters, 78(18), 3212–3215. Elsevier.*

---

## Overview
The classifier is designed for **2×2 contingency tables with one or more zero cells**.  
Standard methods can be unreliable in such sparse cases; this tool provides a **systematic classification** into *Mild, Moderate, or Severe* sparseness.

---

## Key Features
- Classify single or multiple 2×2 tables  
- Choice of **2-level** (Mild/Severe) or **3-level** (Mild/Moderate/Severe) classification  
- Support for **Odds Ratio**, **Relative Risk**, and **Risk Difference**  
- Adjustable continuity correction (ε) down to `1e-8`  
- Sensitivity plots of measure values versus ε  

---

## How to Run
1. Install dependencies:
   ```bash
   pip install -r requirements.txt


---

## 📌 How to Cite

If you use this app or its methodology in research or applied work, please cite:

> Subbiah, M. & Srinivasan, M.R. (2008).  
> *Classification of 2×2 sparse data sets with zero cells.*  
> **Statistics & Probability Letters, 78(18), 3212–3215. Elsevier.**  
> https://doi.org/10.1016/j.spl.2008.06.010
