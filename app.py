import streamlit as st
import requests
import re
from typing import List, Dict

st.set_page_config(page_title="SciPulse", page_icon="🧬", layout="wide")

# ============================================================

# STYLES

# ============================================================

st.markdown(”””

<style>
body { background-color: #0c140c; }

.main-title {
    font-size: 2.4rem;
    font-weight: 700;
    color: #e8f5e8;
    margin-bottom: 0.2rem;
}

.subtitle {
    font-size: 0.95rem;
    color: #6a8a6a;
    margin-bottom: 1.5rem;
}

.paper-card {
    background: #111a11;
    border: 1px solid #1e2e1e;
    border-radius: 14px;
    padding: 24px 28px;
    margin-bottom: 18px;
    transition: transform 0.2s ease, border-color 0.2s ease;
}
.paper-card:hover {
    border-color: #3a6a3a;
    transform: translateY(-3px);
}

.featured-card {
    background: linear-gradient(135deg, #0f2a1a 0%, #0a1f2e 100%);
    border: 1px solid #2a5a3a;
    border-radius: 18px;
    padding: 32px 36px;
    margin-bottom: 24px;
}

.badge-row { margin-bottom: 10px; }

.badge {
    display: inline-block;
    padding: 4px 10px;
    border-radius: 10px;
    font-size: 0.7rem;
    margin-right: 6px;
    margin-bottom: 4px;
    font-weight: 500;
}

.badge-study { background: #2a203a; color: #c9a8ff; }
.badge-field { background: #1f2e3a; color: #a8d0ff; }
.badge-year  { background: #2a2a2a; color: #ccc; }
.badge-cite  { background: #3a2a2a; color: #ffb3b3; }
.badge-open  { background: #1d3a1d; color: #7eda7e; }
.badge-new   { background: #3a3a1a; color: #e0e07e; }

.plain-summary {
    background: #0f1d14;
    border: 1px solid #244a2c;
    border-radius: 12px;
    padding: 18px 20px;
    margin: 14px 0 16px 0;
    line-height: 1.65;
    font-size: 0.94rem;
    color: #cfe8cf;
}

.plain-summary h4 {
    margin: 12px 0 6px 0;
    font-size: 0.78rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #7eda7e;
}

.journal-line {
    font-size: 0.75rem;
    color: #4a6a4a;
    margin-bottom: 6px;
}

.no-results {
    text-align: center;
    padding: 60px 20px;
    color: #4a6a4a;
    font-size: 1.1rem;
}

.stats-bar {
    background: #0f1a0f;
    border: 1px solid #1e2e1e;
    border-radius: 10px;
    padding: 12px 20px;
    margin-bottom: 20px;
    font-size: 0.82rem;
    color: #6a8a6a;
}
</style>

“””, unsafe_allow_html=True)

# ============================================================

# HELPERS

# ============================================================

def detect_study_type(text: str) -> str:
if not text:
return “Research Study”
t = text.lower()
if “meta-analysis” in t:
return “Meta-Analysis”
if “systematic review” in t:
return “Systematic Review”
if “randomized” in t:
return “Randomized Controlled Trial”
if “double-blind” in t:
return “Double-Blind Trial”
if “cohort” in t:
return “Cohort Study”
if “case-control” in t:
return “Case-Control Study”
if “cross-sectional” in t:
return “Cross-Sectional Study”
if “mouse” in t or “mice” in t or “rat” in t:
return “Animal Study”
if “in vitro” in t:
return “Laboratory Study”
return “Research Study”

def extract_sample_size(text: str):
if not text:
return None
match = re.search(r’(\d{2,5})\s+(participants|patients|subjects)’, text.lower())
return match.group(1) if match else None

def extract_finding_sentences(abstract: str):
if not abstract:
return None
sentences = re.split(r’(?<=[.!?])\s+’, abstract)
keywords = [“found”, “result”, “associated”, “significant”, “increase”, “decrease”,
“suggest”, “indicate”, “demonstrate”, “conclude”, “show”, “reveal”]
scored = []
for s in sentences:
score = sum(k in s.lower() for k in keywords)
scored.append((score, s))
scored.sort(reverse=True)
top = [s for score, s in scored[:2] if score > 0]
return “ “.join(top) if top else None

def generate_plain_summary(paper: dict) -> str:
abstract = paper.get(“abstract”, “”)
title = paper.get(“title”, “”)
study_type = detect_study_type(abstract)
findings = extract_finding_sentences(abstract)
sample_size = extract_sample_size(abstract)

```
if not findings:
    findings = "Key findings were reported in the study, though detailed outcome extraction was limited from the abstract."

strength_note = ""
if study_type == "Animal Study":
    strength_note = "⚠️ Findings are preliminary and may not directly generalize to humans."
elif study_type == "Meta-Analysis":
    strength_note = "✅ Aggregates multiple studies, increasing overall evidence strength."
elif study_type == "Systematic Review":
    strength_note = "✅ Comprehensive review of existing literature on the topic."
elif "Randomized" in study_type:
    strength_note = "✅ Controlled trial design supports stronger causal interpretation."
elif "Double-Blind" in study_type:
    strength_note = "✅ Double-blind design minimizes observer and participant bias."
elif study_type == "Laboratory Study":
    strength_note = "⚠️ In vitro results may not replicate in living organisms."
else:
    strength_note = "ℹ️ Observational design — interpret causality with care."

sample_line = (
    f"Approximately {sample_size} participants were included."
    if sample_size
    else "Sample size not clearly stated in the abstract."
)

return f"""
<div class="plain-summary">
    <h4>What They Studied</h4>
    <p>This {study_type.lower()} investigated the research question addressed in:
    <strong>{title}</strong>.</p>

    <h4>What They Found</h4>
    <p>{findings}</p>

    <h4>Study Strength</h4>
    <p>{sample_line} Design classified as <strong>{study_type}</strong>. {strength_note}</p>

    <h4>Practical Takeaway</h4>
    <p>These findings contribute to the evolving evidence base in this field.
    Always consult a qualified professional before acting on research findings.</p>
</div>
"""
```

def rank_papers(papers: List[Dict]) -> List[Dict]:
def score(p):
return (
p.get(“citationCount”, 0) * 2
+ (5 if p.get(“isOpenAccess”) else 0)
+ (3 if (p.get(“publicationDate”) or “”) >= “2024-01-01” else 0)
)
return sorted(papers, key=score, reverse=True)

# ============================================================

# API

# ============================================================

@st.cache_data(ttl=60 * 60)
def fetch_papers(query: str, limit: int = 15) -> List[Dict]:
fields = (
“title,abstract,authors,year,url,fieldsOfStudy,”
“citationCount,isOpenAccess,publicationDate,journal”
)
url = “https://api.semanticscholar.org/graph/v1/paper/search”
params = {
“query”: query,
“limit”: limit,
“fields”: fields,
“sort”: “publicationDate:desc”,
}
try:
response = requests.get(url, params=params, timeout=10)
if response.status_code == 200:
return response.json().get(“data”, [])
except Exception:
pass
return []

# ============================================================

# UI COMPONENTS

# ============================================================

def make_badges(paper: dict) -> str:
study_type = detect_study_type(paper.get(“abstract”, “”))
year       = paper.get(“year”)
citations  = paper.get(“citationCount”)
is_open    = paper.get(“isOpenAccess”, False)
fields     = paper.get(“fieldsOfStudy”) or []

```
html = '<div class="badge-row">'
html += f'<span class="badge badge-study">{study_type}</span>'

for field in fields[:2]:
    html += f'<span class="badge badge-field">{field}</span>'

if year:
    html += f'<span class="badge badge-year">{year}</span>'
if citations is not None:
    html += f'<span class="badge badge-cite">★ {citations:,} citations</span>'
if is_open:
    html += '<span class="badge badge-open">Open Access</span>'

html += '</div>'
return html
```

def render_paper(paper: dict, featured: bool = False):
container_class = “featured-card” if featured else “paper-card”
st.markdown(f’<div class="{container_class}">’, unsafe_allow_html=True)

```
journal = (paper.get("journal") or {}).get("name")
if journal:
    st.markdown(
        f'<div class="journal-line">📄 Published in <em>{journal}</em></div>',
        unsafe_allow_html=True,
    )

title = paper.get("title", "Untitled")
if featured:
    st.markdown(f"## {title}")
else:
    st.markdown(f"### {title}")

st.markdown(make_badges(paper), unsafe_allow_html=True)

authors = paper.get("authors") or []
if authors:
    author_names = ", ".join(a.get("name", "") for a in authors[:4])
    if len(authors) > 4:
        author_names += f" +{len(authors) - 4} more"
    st.markdown(
        f'<div class="journal-line">👤 {author_names}</div>',
        unsafe_allow_html=True,
    )

st.markdown(generate_plain_summary(paper), unsafe_allow_html=True)

col1, col2 = st.columns([1, 5])
with col1:
    if paper.get("abstract"):
        with st.expander("Full Abstract"):
            st.write(paper.get("abstract"))
with col2:
    if paper.get("url"):
        st.markdown(f"[→ Read Full Paper]({paper.get('url')})")

st.markdown("</div>", unsafe_allow_html=True)
```

def render_stats_bar(papers: List[Dict]):
total       = len(papers)
open_access = sum(1 for p in papers if p.get(“isOpenAccess”))
recent      = sum(1 for p in papers if (p.get(“publicationDate”) or “”) >= “2024-01-01”)
avg_cite    = (
int(sum(p.get(“citationCount”, 0) for p in papers) / total)
if total else 0
)
st.markdown(
f’<div class="stats-bar">’
f’📊 <strong>{total}</strong> papers found  |  ’
f’🔓 <strong>{open_access}</strong> open access  |  ’
f’🆕 <strong>{recent}</strong> from 2024+  |  ’
f’★ avg <strong>{avg_cite:,}</strong> citations’
f’</div>’,
unsafe_allow_html=True,
)

# ============================================================

# SIDEBAR

# ============================================================

with st.sidebar:
st.markdown(”### ⚙️ Search Options”)
result_limit = st.slider(“Number of results”, min_value=5, max_value=30, value=15, step=5)
st.markdown(”—”)
st.markdown(”### 📌 Quick Topics”)
quick_topics = [
“mRNA vaccine efficacy”,
“gut microbiome mental health”,
“CRISPR gene editing cancer”,
“sleep deprivation cognition”,
“intermittent fasting longevity”,
“climate change mental health”,
“psychedelic therapy depression”,
“antibiotic resistance”,
]
for topic in quick_topics:
if st.button(topic, use_container_width=True):
st.session_state[“quick_query”] = topic

```
st.markdown("---")
st.markdown(
    '<div style="font-size:0.75rem;color:#4a6a4a;">'
    "Data sourced from Semantic Scholar.<br>"
    "Results cached for 1 hour."
    "</div>",
    unsafe_allow_html=True,
)
```

# ============================================================

# MAIN APP

# ============================================================

st.markdown(’<div class="main-title">🧬 SciPulse</div>’, unsafe_allow_html=True)
st.markdown(
‘<div class="subtitle">Evidence-first summaries of peer-reviewed research. No hype. No paywall.</div>’,
unsafe_allow_html=True,
)

# Handle quick-topic button clicks from sidebar

default_query = st.session_state.pop(“quick_query”, “”)
query = st.text_input(
“Search research topics”,
value=default_query,
placeholder=“e.g. gut microbiome, CRISPR, sleep deprivation…”,
)

if query:
with st.spinner(“Fetching latest research…”):
papers = fetch_papers(query, limit=result_limit)
papers = rank_papers(papers)

```
if papers:
    render_stats_bar(papers)

    st.markdown("## 🏆 Featured Study")
    render_paper(papers[0], featured=True)

    if len(papers) > 1:
        st.markdown("## 📚 More Research")
        for p in papers[1:]:
            render_paper(p)
else:
    st.markdown(
        '<div class="no-results">'
        "🔬 No results found for that query.<br>"
        "<small>Try broader terms or check your spelling.</small>"
        "</div>",
        unsafe_allow_html=True,
    )
```

else:
st.markdown(
‘<div class="no-results">’
“🧬 Enter a research topic above to get started.<br>”
“<small>Or pick a quick topic from the sidebar.</small>”
“</div>”,
unsafe_allow_html=True,
)