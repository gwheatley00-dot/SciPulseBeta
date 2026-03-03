import streamlit as st
import requests
import re
import time
import json
from typing import List, Dict, Any

st.set_page_config(page_title="SciPulse", page_icon="🧬", layout="wide")

API_SEARCH = "https://api.semanticscholar.org/graph/v1/paper/search"
CLAUDE_API = "https://api.anthropic.com/v1/messages"

st.markdown("""

<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=DM+Sans:wght@300;400;500;600&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

[data-testid="stAppViewContainer"] {
    background-color: #080f08;
    font-family: 'DM Sans', sans-serif;
}
[data-testid="stAppViewContainer"] > .main > .block-container {
    padding: 2rem 2.5rem 4rem 2.5rem;
    max-width: 1100px;
}
[data-testid="stSidebar"] {
    background-color: #060d06;
    border-right: 1px solid #162016;
}
[data-testid="stSidebar"] > div { padding: 1.5rem 1rem; }

[data-testid="stSidebar"] .stButton button {
    background: transparent;
    color: #5a8a5a;
    border: 1px solid #1a2a1a;
    border-radius: 6px;
    width: 100%;
    text-align: left;
    padding: 7px 11px;
    font-size: 0.78rem;
    font-family: 'DM Sans', sans-serif;
    margin-bottom: 3px;
    transition: all 0.15s ease;
}
[data-testid="stSidebar"] .stButton button:hover {
    border-color: #3a7a3a;
    color: #7eda7e;
    background: #0f1a0f;
}

.stTextInput input {
    background: #0d160d !important;
    color: #cfe8cf !important;
    border: 1px solid #1e3a1e !important;
    border-radius: 8px !important;
    padding: 10px 14px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.95rem !important;
}
.stTextInput input:focus {
    border-color: #4a8a4a !important;
    box-shadow: 0 0 0 3px #7eda7e18 !important;
}
.stTextInput label {
    color: #4a6a4a !important;
    font-size: 0.78rem !important;
    font-family: 'IBM Plex Mono', monospace !important;
    letter-spacing: 0.06em !important;
    text-transform: uppercase !important;
}

.stButton > button {
    background: #0f2a0f;
    color: #7eda7e;
    border: 1px solid #2a5a2a;
    border-radius: 8px;
    padding: 9px 28px;
    font-weight: 500;
    font-family: 'DM Sans', sans-serif;
    font-size: 0.88rem;
    letter-spacing: 0.04em;
    transition: all 0.15s ease;
}
.stButton > button:hover {
    background: #1a3a1a;
    border-color: #5a9a5a;
}

.wordmark {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 1.6rem;
    font-weight: 500;
    color: #7eda7e;
    letter-spacing: -0.02em;
    margin-bottom: 2px;
}
.wordmark span { color: #2a5a2a; }
.tagline {
    font-size: 0.8rem;
    color: #3a5a3a;
    font-family: 'IBM Plex Mono', monospace;
    letter-spacing: 0.04em;
    margin-bottom: 2rem;
}

.stats-row {
    display: flex;
    gap: 0;
    margin-bottom: 2rem;
    border: 1px solid #162016;
    border-radius: 8px;
    overflow: hidden;
}
.stat-cell {
    flex: 1;
    padding: 12px 16px;
    border-right: 1px solid #162016;
    background: #0a130a;
}
.stat-cell:last-child { border-right: none; }
.stat-num {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 1.3rem;
    font-weight: 500;
    color: #7eda7e;
    line-height: 1;
    margin-bottom: 3px;
}
.stat-label {
    font-size: 0.68rem;
    color: #3a5a3a;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    font-family: 'IBM Plex Mono', monospace;
}

.section-label {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.68rem;
    color: #3a6a3a;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    margin-bottom: 12px;
    padding-bottom: 8px;
    border-bottom: 1px solid #162016;
}

.featured {
    background: #0a1a0a;
    border: 1px solid #1e3e1e;
    border-radius: 12px;
    padding: 28px 32px;
    margin-bottom: 12px;
    position: relative;
    overflow: hidden;
}
.featured::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, #2a6a2a, #7eda7e, #2a6a2a);
}

.pcard {
    background: #0a130a;
    border: 1px solid #142014;
    border-radius: 10px;
    padding: 20px 24px;
    margin-bottom: 8px;
    transition: border-color 0.15s ease;
}
.pcard:hover { border-color: #2a4a2a; }

.card-journal {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.68rem;
    color: #3a5a3a;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin-bottom: 8px;
}
.card-title {
    font-size: 1.05rem;
    font-weight: 600;
    color: #d8ecd8;
    line-height: 1.45;
    margin-bottom: 8px;
}
.featured .card-title { font-size: 1.25rem; }
.card-authors {
    font-size: 0.75rem;
    color: #3a5a3a;
    margin-bottom: 10px;
    line-height: 1.4;
}

.badges { margin-bottom: 12px; display: flex; flex-wrap: wrap; gap: 5px; }
.b {
    display: inline-block;
    padding: 3px 9px;
    border-radius: 4px;
    font-size: 0.67rem;
    font-family: 'IBM Plex Mono', monospace;
    font-weight: 400;
    letter-spacing: 0.03em;
    border: 1px solid transparent;
}
.b-type  { background: #1a1428; color: #a88ccc; border-color: #2a1e3e; }
.b-year  { background: #141414; color: #888888; border-color: #242424; }
.b-cite  { background: #281a1a; color: #cc8888; border-color: #3a2020; }
.b-open  { background: #0e200e; color: #6ab86a; border-color: #1a3a1a; }
.b-new   { background: #201e0a; color: #b8b060; border-color: #302a10; }

.sumbox {
    background: #080f08;
    border: 1px solid #142014;
    border-radius: 8px;
    margin: 12px 0;
    overflow: hidden;
}
.sum-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
}
.sum-cell {
    padding: 12px 16px;
    border-right: 1px solid #142014;
    border-bottom: 1px solid #142014;
}
.sum-cell:nth-child(even) { border-right: none; }
.sum-cell:nth-last-child(-n+2) { border-bottom: none; }
.sum-key {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.6rem;
    color: #3a6a3a;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: 5px;
}
.sum-val {
    font-size: 0.83rem;
    color: #9abf9a;
    line-height: 1.55;
}
.sum-val strong { color: #b8d8b8; }

.finding-bar {
    background: #080f08;
    border: 1px solid #142014;
    border-top: none;
    padding: 14px 16px;
}
.finding-label {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.6rem;
    color: #3a6a3a;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: 6px;
}
.finding-text {
    font-size: 0.88rem;
    color: #b8d8b8;
    line-height: 1.6;
}
.ai-badge {
    display: inline-block;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.55rem;
    color: #4a7a4a;
    border: 1px solid #1a3a1a;
    border-radius: 3px;
    padding: 1px 5px;
    margin-left: 6px;
    vertical-align: middle;
    letter-spacing: 0.05em;
}

.card-footer {
    display: flex;
    align-items: center;
    gap: 16px;
    margin-top: 12px;
    padding-top: 12px;
    border-top: 1px solid #142014;
}
.read-btn {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.72rem;
    color: #5a9a5a;
    text-decoration: none;
    letter-spacing: 0.04em;
    transition: color 0.15s;
}
.read-btn:hover { color: #7eda7e; }

.abstract-inner {
    font-size: 0.82rem;
    color: #6a8a6a;
    line-height: 1.65;
    padding: 4px 2px;
    font-family: 'DM Sans', sans-serif;
}

.sidebar-label {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.65rem;
    color: #3a5a3a;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: 8px;
    margin-top: 16px;
}
.sidebar-note {
    font-size: 0.7rem;
    color: #2a3a2a;
    font-family: 'IBM Plex Mono', monospace;
    line-height: 1.6;
    margin-top: 16px;
}

.empty-state {
    text-align: center;
    padding: 80px 20px;
}
.empty-big {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 2.5rem;
    margin-bottom: 12px;
    color: #1a3a1a;
}
.empty-msg {
    font-size: 0.85rem;
    color: #2a4a2a;
    font-family: 'IBM Plex Mono', monospace;
}

#MainMenu, footer, header { visibility: hidden; }
</style>

""", unsafe_allow_html=True)


# ============================================================
# HELPERS
# ============================================================

def detect_study_type(text):
    if not text: return "Research Study"
    t = text.lower()
    if "meta-analysis" in t: return "Meta-Analysis"
    if "systematic review" in t: return "Systematic Review"
    if "randomized" in t: return "RCT"
    if "double-blind" in t: return "Double-Blind Trial"
    if "cohort" in t: return "Cohort Study"
    if "case-control" in t: return "Case-Control"
    if "cross-sectional" in t: return "Cross-Sectional"
    if "mouse" in t or "mice" in t or "rat" in t: return "Animal Study"
    if "in vitro" in t: return "Lab Study"
    return "Research Study"

def extract_sample_size(text):
    if not text: return None
    patterns = [
        r"n\s*=\s*(\d{2,6})",
        r"(\d{2,6})\s+(participants|patients|subjects|individuals|adults|children|women|men)",
        r"(\d{2,6})\s+(enrolled|included|recruited|analyzed)",
        r"total\s+of\s+(\d{2,6})",
        r"sample\s+of\s+(\d{2,6})",
    ]
    for pat in patterns:
        match = re.search(pat, text.lower())
        if match:
            return match.group(1)
    return None

def extract_outcomes(abstract):
    if not abstract: return []
    sentences = re.split(r"(?<=[.!?])\s+", abstract)
    keywords = ["found", "result", "associated", "significant", "increase", "decrease",
                "suggest", "indicate", "demonstrate", "conclude", "show", "reveal",
                "effect", "outcome", "improvement", "reduction", "increase", "risk",
                "benefit", "efficacy", "effective", "compared", "versus", "higher", "lower"]
    scored = []
    for s in sentences:
        score = sum(k in s.lower() for k in keywords)
        if score > 0:
            scored.append((score, s.strip()))
    scored.sort(reverse=True)
    return [s for _, s in scored[:3]]

def strength_info(study_type):
    levels = {
        "Meta-Analysis": ("HIGH", "Pools data across many studies. Strongest form of evidence."),
        "Systematic Review": ("HIGH", "Structured synthesis of existing literature."),
        "RCT": ("STRONG", "Randomized design controls for confounding variables."),
        "Double-Blind Trial": ("STRONG", "Eliminates observer and participant bias."),
        "Cohort Study": ("MODERATE", "Follows subjects over time but not randomized."),
        "Case-Control": ("MODERATE", "Compares outcomes retrospectively."),
        "Cross-Sectional": ("MODERATE", "Snapshot in time, cannot establish causation."),
        "Animal Study": ("PRELIMINARY", "Preclinical data, human applicability unconfirmed."),
        "Lab Study": ("PRELIMINARY", "In vitro findings may not translate in vivo."),
    }
    level, note = levels.get(study_type, ("MODERATE", "Observational design, causation not confirmed."))
    return level, note

def format_authors(authors):
    if not authors: return "Authors unknown"
    names = [a.get("name") for a in authors if a.get("name")]
    if not names: return "Authors unknown"
    return ", ".join(names[:3]) + (" et al." if len(names) > 3 else "")

def compute_score(paper):
    score = (paper.get("citationCount") or 0) * 2
    if paper.get("openAccessPdf"): score += 5
    try:
        if paper.get("year") and int(paper["year"]) >= 2024: score += 3
    except Exception: pass
    return score

def make_badges(paper):
    stype = detect_study_type(paper.get("abstract", ""))
    year = paper.get("year")
    cites = paper.get("citationCount")
    is_open = paper.get("openAccessPdf")
    is_new = year and int(year) >= 2024
    h = "<div class=\"badges\">"
    h += "<span class=\"b b-type\">" + stype + "</span>"
    if year: h += "<span class=\"b b-year\">" + str(year) + "</span>"
    if cites is not None: h += "<span class=\"b b-cite\">" + str(cites) + " cited</span>"
    if is_open: h += "<span class=\"b b-open\">open access</span>"
    if is_new: h += "<span class=\"b b-new\">2024+</span>"
    h += "</div>"
    return h

# ============================================================
# AI SUMMARY via Claude API
# ============================================================

@st.cache_data(ttl=86400, show_spinner=False)
def get_ai_summary(paper_id, title, abstract, study_type):
    if not abstract or len(abstract) < 80:
        return None
    prompt = (
        "You are a science communicator writing for an educated general audience. "
        "Analyze this research paper and return ONLY a JSON object with these exact keys:\n"
        "- what_studied: 1 sentence describing the research question (do not just repeat the title)\n"
        "- key_finding: 2-3 sentences with the most important specific result, including numbers/stats if present\n"
        "- practical_meaning: 1-2 sentences on what this means for real people or future research\n"
        "- limitation: 1 sentence on the main limitation or caveat\n\n"
        "Paper title: " + title + "\n"
        "Study type: " + study_type + "\n"
        "Abstract: " + abstract + "\n\n"
        "Return only valid JSON, no other text."
    )
    try:
        resp = requests.post(
            CLAUDE_API,
            headers={"Content-Type": "application/json"},
            json={
                "model": "claude-sonnet-4-20250514",
                "max_tokens": 1000,
                "messages": [{"role": "user", "content": prompt}]
            },
            timeout=20
        )
        if resp.status_code == 200:
            raw = resp.json()["content"][0]["text"].strip()
            raw = re.sub(r"^`json|^`|```$", "", raw, flags=re.MULTILINE).strip()
            return json.loads(raw)
    except Exception:
        pass
    return None

# ============================================================
# API
# ============================================================

@st.cache_data(ttl=3600, show_spinner=False)
def search_papers(query, limit=12):
    params = {
        "query": query,
        "limit": limit,
        "fields": "title,authors,year,abstract,url,openAccessPdf,citationCount,journal,fieldsOfStudy,publicationDate"
    }
    for attempt in range(3):
        try:
            resp = requests.get(API_SEARCH, params=params, timeout=12)
            if resp.status_code == 429:
                time.sleep(5 * (attempt + 1))
                continue
            resp.raise_for_status()
            return resp.json().get("data", [])
        except requests.RequestException:
            if attempt == 2: return []
            time.sleep(3)
    return []

# ============================================================
# RENDER
# ============================================================

def make_summary_block(paper, use_ai=True):
    abstract = paper.get("abstract", "")
    title = paper.get("title", "")
    pid = paper.get("paperId", title[:20])
    study_type = detect_study_type(abstract)
    sample = extract_sample_size(abstract)
    sample_txt = sample + " participants" if sample else "Not reported"
    level, strength_txt = strength_info(study_type)

    ai_data = None
    if use_ai and abstract and len(abstract) > 80:
        ai_data = get_ai_summary(pid, title, abstract, study_type)

    if ai_data:
        what = ai_data.get("what_studied", "")
        finding = ai_data.get("key_finding", "")
        practical = ai_data.get("practical_meaning", "")
        limitation = ai_data.get("limitation", "")
        ai_label = "<span class=\"ai-badge\">AI</span>"
    else:
        outcomes = extract_outcomes(abstract)
        what = "Investigated: " + title
        finding = " ".join(outcomes) if outcomes else "See full abstract for detailed findings."
        practical = "Results contribute to the evidence base in this field."
        limitation = strength_txt
        ai_label = ""

    html = (
        "<div class=\"sumbox\">"
        "<div class=\"sum-grid\">"

        "<div class=\"sum-cell\">"
        "<div class=\"sum-key\">What They Studied</div>"
        "<div class=\"sum-val\">" + what + "</div>"
        "</div>"

        "<div class=\"sum-cell\">"
        "<div class=\"sum-key\">Sample Size</div>"
        "<div class=\"sum-val\">" + sample_txt + "</div>"
        "</div>"

        "<div class=\"sum-cell\">"
        "<div class=\"sum-key\">Practical Meaning</div>"
        "<div class=\"sum-val\">" + practical + "</div>"
        "</div>"

        "<div class=\"sum-cell\">"
        "<div class=\"sum-key\">Evidence Level &nbsp;<strong style=\"color:#" +
        ("4a9a4a\">HIGH" if level == "HIGH" else
         "7a9a4a\">STRONG" if level == "STRONG" else
         "9a8a4a\">MODERATE" if level == "MODERATE" else
         "8a6a4a\">PRELIMINARY") +
        "</strong></div>"
        "<div class=\"sum-val\">" + strength_txt + "</div>"
        "</div>"

        "</div>"

        "<div class=\"finding-bar\">"
        "<div class=\"finding-label\">Key Finding " + ai_label + "</div>"
        "<div class=\"finding-text\">" + finding + "</div>"
        "</div>"

        "</div>"
    )

    if ai_data and limitation:
        html += (
            "<div style=\"padding:8px 16px 10px;background:#080f08;border:1px solid #142014;"
            "border-top:none;border-radius:0 0 8px 8px;\">"
            "<span style=\"font-family:'IBM Plex Mono',monospace;font-size:0.6rem;color:#5a3a3a;"
            "text-transform:uppercase;letter-spacing:0.1em;\">Limitation: </span>"
            "<span style=\"font-size:0.8rem;color:#7a5a5a;\">" + limitation + "</span>"
            "</div>"
        )

    return html

def render_card(paper, featured=False, use_ai=True):
    title = paper.get("title", "Untitled")
    authors = format_authors(paper.get("authors", []))
    journal = (paper.get("journal") or {}).get("name", "")
    url = paper.get("url", "")
    abstract = paper.get("abstract", "")
    card_class = "featured" if featured else "pcard"

    st.markdown("<div class=\"" + card_class + "\">", unsafe_allow_html=True)
    if journal:
        st.markdown("<div class=\"card-journal\">" + journal + "</div>", unsafe_allow_html=True)
    st.markdown("<div class=\"card-title\">" + title + "</div>", unsafe_allow_html=True)
    st.markdown("<div class=\"card-authors\">" + authors + "</div>", unsafe_allow_html=True)
    st.markdown(make_badges(paper), unsafe_allow_html=True)
    st.markdown(make_summary_block(paper, use_ai=use_ai), unsafe_allow_html=True)

    col1, col2 = st.columns([1, 5])
    with col1:
        if abstract:
            with st.expander("abstract"):
                st.markdown("<div class=\"abstract-inner\">" + abstract + "</div>", unsafe_allow_html=True)
    with col2:
        if url:
            st.markdown(
                "<div style=\"padding-top:6px;\"><a class=\"read-btn\" href=\"" + url + "\" target=\"_blank\">[read full paper]</a></div>",
                unsafe_allow_html=True
            )
    st.markdown("</div>", unsafe_allow_html=True)

def render_stats(papers):
    total = len(papers)
    open_c = sum(1 for p in papers if p.get("openAccessPdf"))
    recent = sum(1 for p in papers if p.get("year") and int(p.get("year") or 0) >= 2024)
    avg = int(sum(p.get("citationCount", 0) for p in papers) / total) if total else 0
    st.markdown(
        "<div class=\"stats-row\">"
        "<div class=\"stat-cell\"><div class=\"stat-num\">" + str(total) + "</div><div class=\"stat-label\">Results</div></div>"
        "<div class=\"stat-cell\"><div class=\"stat-num\">" + str(open_c) + "</div><div class=\"stat-label\">Open Access</div></div>"
        "<div class=\"stat-cell\"><div class=\"stat-num\">" + str(recent) + "</div><div class=\"stat-label\">From 2024+</div></div>"
        "<div class=\"stat-cell\"><div class=\"stat-num\">" + str(avg) + "</div><div class=\"stat-label\">Avg Citations</div></div>"
        "</div>",
        unsafe_allow_html=True
    )

# ============================================================
# MAIN
# ============================================================

def main():
    with st.sidebar:
        st.markdown("<div class=\"sidebar-label\" style=\"margin-top:0;\">SciPulse</div>", unsafe_allow_html=True)
        st.markdown("<div style=\"font-family:'IBM Plex Mono',monospace;font-size:0.75rem;color:#3a6a3a;margin-bottom:20px;\">research discovery</div>", unsafe_allow_html=True)

        user_query = st.text_input("Search topics", value=st.session_state.get("manual_query", ""), placeholder="e.g. migraine, probiotics...")
        if st.button("Search", key="manual_search") and user_query:
            st.session_state["manual_query"] = user_query
            st.session_state["query"] = user_query

        result_limit = st.slider("Results", min_value=5, max_value=20, value=10, step=5)

        use_ai = st.toggle("AI Summaries", value=True, help="Use Claude to generate intelligent summaries from abstracts")

        st.markdown("<div class=\"sidebar-label\">Quick Topics</div>", unsafe_allow_html=True)
        quick_topics = [
            "gut microbiome mental health",
            "CRISPR gene editing cancer",
            "mRNA vaccine efficacy",
            "sleep deprivation cognition",
            "intermittent fasting longevity",
            "climate change mental health",
            "psychedelic therapy depression",
            "antibiotic resistance",
        ]
        for i, t in enumerate(quick_topics):
            if st.button(t, use_container_width=True, key="topic_" + str(i)):
                st.session_state["query"] = t

        st.markdown("<div class=\"sidebar-note\">Semantic Scholar API<br>AI summaries by Claude<br>Cached 1hr per query</div>", unsafe_allow_html=True)

    st.markdown("<div class=\"wordmark\">Sci<span>Pulse</span></div>", unsafe_allow_html=True)
    st.markdown("<div class=\"tagline\">evidence-first research summaries / no hype / no paywall</div>", unsafe_allow_html=True)

    current_query = st.session_state.get("query", "")

    if current_query:
        with st.spinner(""):
            papers = search_papers(current_query, limit=result_limit)

        if papers:
            for p in papers:
                p["_score"] = compute_score(p)
            papers.sort(key=lambda x: x["_score"], reverse=True)

            render_stats(papers)

            st.markdown("<div class=\"section-label\">top result</div>", unsafe_allow_html=True)
            render_card(papers[0], featured=True, use_ai=use_ai)

            if len(papers) > 1:
                st.markdown("<div class=\"section-label\" style=\"margin-top:24px;\">more results</div>", unsafe_allow_html=True)
                for p in papers[1:]:
                    render_card(p, use_ai=use_ai)
        else:
            st.markdown(
                "<div class=\"empty-state\"><div class=\"empty-big\">[ ]</div>"
                "<div class=\"empty-msg\">no results found. try broader search terms.</div></div>",
                unsafe_allow_html=True
            )
    else:
        st.markdown(
            "<div class=\"empty-state\"><div class=\"empty-big\">_</div>"
            "<div class=\"empty-msg\">enter a topic or select from sidebar</div></div>",
            unsafe_allow_html=True
        )

if __name__ == "__main__":
    main()

