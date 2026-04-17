<div align="center">

# 🎵 MusicKG-QA

### Knowledge Graph Question Answering over Turkish Music Domain

**Multi-hop Reasoning · Spreading Activation · Wikidata5M · Neo4j**

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Neo4j](https://img.shields.io/badge/Neo4j-Graph_DB-008CC1?style=for-the-badge&logo=neo4j&logoColor=white)](https://neo4j.com)
[![Wikidata](https://img.shields.io/badge/Wikidata-5M_KG-006699?style=for-the-badge&logo=wikidata&logoColor=white)](https://www.wikidata.org)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

<br/>

*An end-to-end pipeline that extracts a domain-specific music knowledge sub-graph from the 5-million-entity Wikidata5M dataset, imports it into Neo4j, and answers multi-hop natural language questions using spreading activation and KG-enhanced query expansion.*

</div>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Architecture](#-architecture)
- [Key Features](#-key-features)
- [Pipeline Stages](#-pipeline-stages)
- [Dataset](#-dataset)
- [Case Study](#-case-study)
- [Tech Stack](#-tech-stack)
- [Getting Started](#-getting-started)
- [Project Structure](#-project-structure)
- [Results](#-results)
- [Future Work](#-future-work)
- [License](#-license)

---

## 🔍 Overview

**MusicKG-QA** explores how large-scale Knowledge Graphs can be leveraged to answer complex, multi-hop factual questions without relying on large language models. The project focuses on the **Turkish Music** domain and builds a complete pipeline from raw Wikidata5M triples to a working question-answering system.

The core research question:

> *Can graph traversal algorithms — specifically Spreading Activation — combined with structured query expansion, reliably answer multi-hop reasoning questions by navigating a knowledge graph?*

### Problem Space

Traditional QA systems struggle with questions that require chaining multiple facts together. For example:

| Question | Required Reasoning |
|---|---|
| *"In which country was Zülfü Livaneli born?"* | `Livaneli → birthplace → Ilgın → country → Türkiye` (2-hop) |
| *"In which country is the administrative entity containing Arif Sağ's birthplace?"* | `Sağ → birthplace → Erzurum → admin_entity → Erzurum Province → country → Türkiye` (3-hop) |
| *"Which artist was born in Konya Province, Zülfü Livaneli or Ümit Besen?"* | Comparison requiring parallel 2-hop paths |

This project tackles exactly these types of questions using **graph-native** approaches.

---

## 🏗 Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     Wikidata5M Raw Data                         │
│         (5M+ entities · 21M+ triplets · 2.4GB text)            │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                   ┌────────▼────────┐
                   │   Domain Filter  │  ← Seed entities (10 Turkish musicians)
                   │  & Subset Build  │  ← Multi-hop relation chains
                   └────────┬────────┘
                            │
               ┌────────────▼────────────┐
               │  Neo4j Graph Database   │
               │  (Nodes + Relationships)│
               └────────────┬────────────┘
                            │
          ┌─────────────────┼─────────────────┐
          │                 │                 │
   ┌──────▼──────┐  ┌──────▼──────┐  ┌──────▼──────┐
   │  Spreading   │  │  KG Query   │  │  Question   │
   │  Activation  │  │  Expansion  │  │  Generation │
   │  Algorithm   │  │  & Answer   │  │  Pipeline   │
   └──────┬──────┘  └──────┬──────┘  └──────┬──────┘
          │                │                 │
          └────────────────┼─────────────────┘
                           │
                  ┌────────▼────────┐
                  │  50-Question    │
                  │  Benchmark      │
                  │  Dataset        │
                  └─────────────────┘
```

---

## ✨ Key Features

### 🔗 Multi-Hop Reasoning
- **2-hop questions**: Entity → Relation → Mid-entity → Relation → Answer
- **3-hop questions**: Extended chains through 3 intermediate relations
- **Comparison questions**: Parallel multi-hop paths comparing two entities

### 🌊 Spreading Activation Algorithm
A biologically-inspired graph traversal technique that:
1. Starts from a **seed entity** identified from the question
2. Propagates activation energy to neighboring nodes
3. Uses **query-aware relation scoring** to prioritize relevant paths
4. Supports configurable rounds, with diminishing activation per hop

### 📊 KG-Enhanced Query Expansion (KG-QE)
- Builds structured **KG summaries** from retrieved triples
- Expands the original query with contextual facts
- Generates **passage notes** combining entity descriptions with graph evidence
- Produces a final answer through deterministic KG traversal

### 🗃 Automated Benchmark Generation
- Programmatic generation of **2-hop**, **3-hop**, and **comparison** questions
- Template-based natural language question construction
- Automated **gold answer** extraction from graph paths
- Quality filtering to remove noisy ontology artifacts

---

## 🔄 Pipeline Stages

### Stage 1: Data Extraction & Analysis
```
Wikidata5M (457MB triplets) → Seed Entity Selection → Reasoning Path Extraction
```
- Parse 21M+ Wikidata5M triples
- Select 10 Turkish music domain seed entities
- Extract all 2-hop reasoning paths with music-relevant relations

### Stage 2: Sub-graph Construction
```
Filtered Paths → CSV Node/Relationship Export → Neo4j Import
```
- Build domain-specific node and relationship CSVs
- Batch import into Neo4j with constraints and indexes
- Entity deduplication via `MERGE` operations

### Stage 3: Question Generation
```
Reasoning Paths → Template Matching → Quality Filtering → 50-Question Dataset
```
| Type | Count | Example |
|------|-------|---------|
| 2-hop | 30 | *"What broader instrument class does the instrument used by Arif Sağ belong to?"* |
| 3-hop | 15 | *"What broader family does the instrument used by Ümit Besen belong to?"* |
| Comparison | 5 | *"Which artist was born in Konya Province, Zülfü Livaneli or Arif Sağ?"* |

### Stage 4: Spreading Activation & QA
```
Question → Seed Identification → Graph Traversal → KG Summary → Answer
```

---

## 📁 Dataset

### Wikidata5M Source
| Item | Size |
|------|------|
| All Triplets | 457 MB (21M+ triples) |
| Entity Text Descriptions | 2.4 GB |
| Entity Aliases | ~5M entries |
| Relation Aliases | 828 relations |

### Generated Benchmark
The final benchmark dataset contains **50 curated questions** across 3 difficulty levels:

```json
{
  "question_id": "MUSIC_2HOP_001",
  "question_text": "In which country was Zulfu Livaneli born?",
  "gold_answer": "turkiye",
  "reasoning_path": ["Zulfu Livaneli", "place of birth", "ilgın", "country", "turkiye"],
  "seed_entity": "Zulfu Livaneli",
  "difficulty": "2-hop",
  "domain": "Turkish Music"
}
```

### Seed Entities
| Wikidata ID | Artist |
|-------------|--------|
| Q248059 | Zülfü Livaneli |
| Q660599 | Arif Sağ |
| Q334814 | Ümit Besen |
| Q962106 | Hümeyra |
| Q6823378 | Mete Özgencil |
| Q388757 | Şehrazat |
| Q240368 | Haluk Levent |
| Q6093986 | İlhan Usmanbaş |
| Q343693 | Demet Sağıroğlu |
| Q4156426 | Aynur Aydın |

---

## 📖 Case Study

### Question: *"In which country was Zülfü Livaneli born?"*

**Step 1 — Seed Identification**
```
Query: "In which country was Zulfu Livaneli born?"
  → Matched seed: Zulfu Livaneli (Q248059)
```

**Step 2 — Spreading Activation (2 rounds)**
```
Round 1:
  Zulfu Livaneli ──[place of birth]──→ Ilgın           ← HIGH priority
  Zulfu Livaneli ──[country of citizenship]──→ Türkiye
  Zulfu Livaneli ──[occupation]──→ vocalist
  Zulfu Livaneli ──[occupation]──→ Film Directors
  ...

Round 2:
  Ilgın ──[country]──→ Türkiye                          ← ANSWER PATH
  Ilgın ──[located in admin entity]──→ Konya Province
  Türkiye ──[instance of]──→ Sovereign State
  ...
```

**Step 3 — KG Summary & Answer**
```
KG Summary: "Zulfu Livaneli was born in Ilgın. Ilgın is located in Konya Province.
             Ilgın is in Türkiye. Zulfu Livaneli has citizenship in Türkiye."

Expanded Query: "What is the birthplace of Zulfu Livaneli?"

Final Answer: Türkiye ✅
```

---

## 🛠 Tech Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Language** | Python 3.10+ | Core pipeline implementation |
| **Graph Database** | Neo4j 5.x | Knowledge graph storage & traversal |
| **Graph Driver** | neo4j (Python) | Bolt protocol communication |
| **Data Source** | Wikidata5M | Large-scale knowledge graph |
| **Data Formats** | JSON, TSV, CSV | Dataset interchange & export |
| **Query Language** | Cypher | Neo4j graph queries |

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- Neo4j 5.x (Community or Enterprise)
- ~5 GB disk space for Wikidata5M data

### Installation

```bash
# Clone the repository
git clone https://github.com/<your-username>/MusicKG-QA.git
cd MusicKG-QA

# Install dependencies
pip install neo4j

# Download Wikidata5M data (see below)
```

### Wikidata5M Setup
Download the Wikidata5M dataset from the [official source](https://deepgraphlearning.github.io/project/wikidata5m) and place files under `data/wikidata5m_raw_data/`.

### Neo4j Setup
1. Start your Neo4j instance
2. Update credentials in the script files if needed
3. Run the import script:

```bash
python scripts/import_music_subset_small_to_neo4j.py
```

### Running the Pipeline

```bash
# Step 1: Extract reasoning paths from Wikidata5M
python scripts/extract_music_reasoning_paths.py

# Step 2: Filter question-worthy paths
python scripts/filter_music_question_paths.py

# Step 3: Generate benchmark questions
python scripts/generate_music_2hop_questions.py
python scripts/generate_music_3hop_questions.py
python scripts/generate_music_comparison_questions.py

# Step 4: Build final 50-question dataset
python scripts/build_final_music_dataset.py

# Step 5: Run Spreading Activation demo
python scripts/spreading_activation_demo.py

# Step 6: Run KG-QE & Answer demo
python scripts/kg_qe_and_answer_demo.py

# Step 7: Build case study bundle
python scripts/build_case_study_bundle.py
```

---

## 📂 Project Structure

```
MusicKG-QA/
├── data/
│   ├── music_seed_ids.txt              # 10 Turkish music artist Wikidata IDs
│   ├── wikidata5m_raw_data/            # Raw Wikidata5M files (~3 GB)
│   │   ├── wikidata5m_all_triplet.txt  #   21M+ subject-relation-object triples
│   │   ├── wikidata5m_text.txt         #   Entity descriptions (2.4 GB)
│   │   └── wikidata5m_alias/           #   Entity & relation name mappings
│   └── wikidata5m_kg/
│       └── wikidata5m_kg.jsonl         #   Full KG in JSONL format (4.1 GB)
│
├── scripts/
│   ├── analyze_music_seeds.py          # Analyze seed entity coverage
│   ├── extract_music_reasoning_paths.py# Extract 2-hop paths from raw triples
│   ├── filter_music_question_paths.py  # Filter paths into question templates
│   ├── generate_music_2hop_questions.py# Generate 2-hop benchmark questions
│   ├── generate_music_3hop_questions.py# Generate 3-hop benchmark questions
│   ├── generate_music_comparison_questions.py # Generate comparison questions
│   ├── build_final_music_dataset.py    # Assemble final 50-question dataset
│   ├── build_music_subset_csv.py       # Export music sub-graph to CSV
│   ├── build_music_subset_csv_small.py # Export smaller sub-graph variant
│   ├── import_music_subset_to_neo4j.py # Import full sub-graph to Neo4j
│   ├── import_music_subset_small_to_neo4j.py # Import small sub-graph to Neo4j
│   ├── spreading_activation_demo.py    # Spreading Activation algorithm demo
│   ├── kg_qe_and_answer_demo.py        # KG-QE and answer extraction demo
│   └── build_case_study_bundle.py      # Bundle case study outputs
│
├── outputs/
│   ├── music_final_50_dataset.json     # ⭐ Final 50-question benchmark (JSON)
│   ├── music_final_50_dataset.tsv      # ⭐ Final 50-question benchmark (TSV)
│   ├── spreading_activation_demo.json  # Activation trace output
│   ├── kg_qe_and_answer_demo.json      # KG-QE demo output
│   ├── case_study_bundle.json          # Complete case study bundle
│   ├── music_reasoning_paths.txt       # All extracted reasoning paths
│   └── music_questionworthy_paths.tsv  # Filtered question-worthy paths
│
├── test_neo4j.py                       # Neo4j connectivity test
└── README.md
```

---

## 📊 Results

### Dataset Composition
| Difficulty | Count | Avg. Hops | Example Relations |
|-----------|-------|-----------|-------------------|
| **2-hop** | 30 | 2 | birthplace→country, instrument→subclass, genre→instance |
| **3-hop** | 15 | 3 | birthplace→admin_entity→country, instrument→subclass→subclass |
| **Comparison** | 5 | 2 (×2) | Parallel birthplace paths for two artists |
| **Total** | **50** | — | — |

### Relation Coverage
| Relation Chain | Question Type | Count |
|---------------|---------------|-------|
| place_of_birth → country | Geographic | 8 |
| place_of_birth → admin_entity | Geographic | 7 |
| instrument → subclass | Musical | 5 |
| genre → instance/subclass | Musical | 6 |
| educated_at → country | Institutional | 2 |
| award → instance | Achievement | 2 |

### Spreading Activation Performance
- **Seed identification accuracy**: Exact match via string search on Neo4j
- **Relevant triple retrieval**: Query-aware scoring with relation priority sets
- **Multi-round traversal**: 2 rounds sufficient for 2-hop; extensible to N rounds

---

## 🔮 Future Work

- [ ] **LLM Integration**: Use retrieved KG context as grounding for GPT/LLaMA-based answer generation
- [ ] **Larger Domain Coverage**: Expand beyond Turkish music to broader cultural domains
- [ ] **Evaluation Framework**: Implement EM/F1 scoring against gold answers
- [ ] **Embedding-Based Seed Matching**: Replace string matching with TransE/DistMult entity embeddings
- [ ] **Interactive Web UI**: Build a Streamlit/Gradio interface for live KG-QA exploration
- [ ] **Scalability Testing**: Benchmark on the full 5M-entity graph

---

## 📜 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

<div align="center">

**Built with ❤️ for Knowledge Graph Research**

*If you found this project useful, please consider giving it a ⭐*

</div>
