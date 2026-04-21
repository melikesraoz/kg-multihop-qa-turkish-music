<div align="center">

# 🎵 MusicKG-QA: Turkish Music Domain
### KG-Infused RAG for Multi-Hop Question Answering

**Wikidata5M · Neo4j · Spreading Activation · R-GAT Architecture**

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Neo4j](https://img.shields.io/badge/Neo4j-Graph_DB-008CC1?style=for-the-badge&logo=neo4j&logoColor=white)](https://neo4j.com)
[![Wikidata](https://img.shields.io/badge/Wikidata-5M_KG-006699?style=for-the-badge&logo=wikidata&logoColor=white)](https://www.wikidata.org)

</div>

---

## 🔍 Overview

**MusicKG-QA** is an end-to-end framework for answering complex, multi-hop natural language questions in the **Turkish Music** domain. By navigating a domain-specific Knowledge Graph (KG) extracted from **Wikidata5M**, the system overcomes the limitations of standard RAG models that struggle with reasoning gaps and hallucination in low-resource or niche domains.

### Core Innovations
- **KG-Guided Spreading Activation**: A deterministic graph traversal algorithm that retrieves relevant triplets beyond the initial retrieval window.
- **R-GAT Inspired Context Expansion**: Structuring retrieved graph evidence into natural language "Passage Notes" to ground the LLM.
- **Turkish Music Benchmark**: A verified dataset of 50 multi-hop questions (2-hop, 3-hop, and Comparison).

---

## 🏗 Modular Architecture

The project is structured into modular components to ensure scientific reproducibility:

- **Module 1: Spreading Activation**: Implements `scripts/module1_spreading_activation.py` for graph traversal.
- **Module 2: Query Expansion**: Implements `scripts/module2_query_expansion.py` to enrich queries with graph metadata.
- **Module 3: Answer Generation**: Implements `scripts/module3_answer_generation.py` for final RAG synthesis.

---

## 🖥 Interactive Presentation Dashboard

The project includes a **Premium Web Dashboard** for visual analysis of experimental results and KG connectivity.

- **Knowledge Graph Tab**: Explore T\u00fcrkiye entity distribution and relation frequency.
- **GNN Model Tab**: Visualize R-GAT training curves and method performance comparisons.
- **XAI Evidence Tab**: Trace the "Reasoning Path" for specific case studies (e.g., Z\u00fclf\u00fc Livaneli's birth coordinates).

**How to view:**
Simply open `dashboard/index.html` in any modern browser.

---

## 📂 Project Structure

```text
.
├── dashboard/              # Premium Presentation UI
│   ├── index.html          # Main Dashboard
│   ├── data.js             # Live Data (Synced from Neo4j)
│   ├── script.js           # Chart Logic (Chart.js v4)
│   └── style.css           # Dark Mode Aesthetics
├── data/
│   └── music_seed_ids.txt  # Selection of 10 Seed Artists
├── outputs/                # Scientific Deliverables
│   ├── final_project_report.tex    # Main Academic Report
│   ├── case_study_report.tex       # Error Analysis
│   ├── music_final_50_dataset.json  # 50-Question Benchmark
│   └── performance_chart.png       # EM/F1 Visualization
├── scripts/                # Modular Codebase
│   ├── pipeline_demo.py    # Main Entry Point
│   ├── neo4j_to_dashboard.py # Live Data Sync Utility
│   ├── run_experiments.py  # Automation for Metrics
│   └── *_activation.py     # Traversal Logic
├── README.md               # Documentation
└── requirements.txt        # Dependencies
```

---

## 🚀 Getting Started

### 1. Prerequisites
- **Neo4j 5.x**: Ensure a local instance is running.
- **Groq/OpenAI API Key**: For LLM-aided scoring and generation.

### 2. Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your NEO4J_URI and GROQ_API_KEY
```

### 3. Execution
```bash
# Sync data from Neo4j to the Dashboard
python scripts/neo4j_to_dashboard.py

# Run a full pipeline demo for a multi-hop question
python scripts/pipeline_demo.py

# Execute the 50-question experimental benchmark
python scripts/run_experiments.py
```

---

## 📊 Evaluation Results

| Method | Accuracy | F1 Score | EM | Recall |
| :--- | :--- | :--- | :--- | :--- |
| No-Retrieval | 34% | 0.411 | 0.340 | - |
| Vanilla RAG | 34% | 0.399 | 0.340 | 0.602 |
| **KG-Infused RAG** | **60%** | **0.681** | **0.600** | **0.824** |

*Results demonstrate a significant improvement in multi-hop reasoning accuracy when combining graph context with RAG.*

---

## 📜 Academic Deliverables

This repository fulfills the requirements for **CSE 474/5074 - Social Network Analysis**:
- **Phase 1-2**: Dataset Analysis & Türkiye Domain Selection.
- **Phase 3**: 50 verified Multi-Hop Questions.
- **Phase 4**: KG-Infused RAG modular implementation.
- **Phase 5-6**: Experimental evaluation and Case Study.

---
<div align="center">
<b>Built for Graduating Project | T\u00fcrkiye Music KG Analysis</b>
</div>
