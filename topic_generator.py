import streamlit as st
import random
import json
from datetime import date

# ----------------------
# Topics data (from your notebook)
# ----------------------
TOPICS = {
    "Python": {
        "List Comprehensions": "Concise syntax for creating lists.",
        "Decorators": "Functions that modify other functions without changing their source code.",
        "Generators": "Lazy iterators built with yield.",
        "Context Managers": "Use with statements to manage resources.",
    },
    "Data Science": {
        "EDA (Exploratory Data Analysis)": "Techniques to summarize main characteristics of data.",
        "Feature Engineering": "Create features to improve model performance.",
        "Model Evaluation": "Metrics and validation strategies.",
    },
    "Machine Learning": {
        "Linear Regression": "Predict continuous targets using linear models.",
        "Regularization (L1/L2)": "Penalize large weights to avoid overfitting.",
        "Decision Trees": "Non-linear models using tree structures.",
        "Cross Validation": "Robust evaluation through data splits.",
    },
    "NLP": {
        "Tokenization": "Splitting text into tokens.",
        "Word Embeddings": "Map words to vectors.",
        "Transformer Architecture": "Self-attention based models for language tasks.",
    },
    "SQL": {
        "JOINs": "Combine rows from two or more tables.",
        "Window Functions": "Perform calculations across sets of rows related to the current row.",
    },
    "Power BI": {
        "DAX Basics": "Data Analysis Expressions for calculations.",
        "Data Modeling": "Relationships and star schemas.",
    },
}

# ----------------------
# Helpers
# ----------------------

def _flatten_topics(selected_categories):
    items = []
    for c in selected_categories:
        for title, desc in TOPICS.get(c, {}).items():
            items.append({"category": c, "title": title, "desc": desc})
    return items


def pick_random_topics(items, per_category, seed=None):
    rng = random.Random(seed)
    results = []
    by_cat = {}
    for it in items:
        by_cat.setdefault(it["category"], []).append(it)
    for cat, its in by_cat.items():
        pool = its.copy()
        rng.shuffle(pool)
        take = min(per_category, len(pool))
        results.extend(pool[:take])
    return results

# ----------------------
# Session State Initialization
# ----------------------
if "seen_topics" not in st.session_state:
    st.session_state.seen_topics = []
if "learned" not in st.session_state:
    st.session_state.learned = {}
if "notes" not in st.session_state:
    st.session_state.notes = {}

# ----------------------
# UI Setup
# ----------------------
st.set_page_config(page_title="Topic-of-the-Day Generator", layout="wide")
st.markdown("""
    <style>
        .topic-card {
            background-color: #f8f9fa;
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        .topic-title {
            font-size: 1.3em;
            font-weight: bold;
            color: #1f77b4;
        }
        .topic-category {
            font-size: 0.9em;
            color: #888;
        }
        .topic-desc {
            margin-top: 10px;
        }
    </style>
""", unsafe_allow_html=True)

st.title("📚 Topic-of-the-Day")
st.write("Generate curated daily learning topics with notes, progress tracking, and a sleek UI.")

# Sidebar controls
with st.sidebar:
    st.header("Controls")
    categories = st.multiselect("Select categories", options=list(TOPICS.keys()), default=list(TOPICS.keys()))
    per_cat = st.slider("Topics per selected category", 1, 5, 1)
    unique_daily = st.checkbox("Daily stable topics", True)
    use_seed = date.today().isoformat() if unique_daily else None

    if st.button("Reset progress"):
        st.session_state.seen_topics.clear()
        st.session_state.learned.clear()
        st.session_state.notes.clear()
        st.success("Progress cleared")

# Generate topics
items = _flatten_topics(categories)
if items:
    topics = pick_random_topics(items, per_cat, seed=use_seed)
    for t in topics:
        st.markdown(f"<div class='topic-card'><div class='topic-title'>{t['title']}</div>"
                    f"<div class='topic-category'>Category: {t['category']}</div>"
                    f"<div class='topic-desc'>{t['desc']}</div></div>", unsafe_allow_html=True)

        key = t['title']
        if key in st.session_state.learned:
            st.success(f"✅ Learned on {st.session_state.learned[key]['learned_on']}")
            if st.button(f"Unmark as learned", key=f"unmark_{key}"):
                del st.session_state.learned[key]
        else:
            if st.button(f"Mark as learned", key=f"learn_{key}"):
                st.session_state.learned[key] = {"category": t['category'], "learned_on": date.today().isoformat()}

        note = st.text_area("Notes", st.session_state.notes.get(key, ""), key=f"note_{key}")
        if st.button("Save note", key=f"save_note_{key}"):
            st.session_state.notes[key] = note
            st.success("Note saved")

        st.session_state.seen_topics.append({"date": date.today().isoformat(), "title": key})
else:
    st.warning("Please select at least one category.")

# Footer: summary
st.markdown("---")
st.write(f"Total topics seen: {len(set([s['title'] for s in st.session_state.seen_topics]))}")
st.write(f"Total learned: {len(st.session_state.learned)}")
