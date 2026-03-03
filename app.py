import streamlit as st
import requests
import re
import time
from typing import List, Dict, Any

st.set_page_config(page_title="SciPulse", page_icon="🧬", layout="wide")

API_SEARCH = "https://api.semanticscholar.org/graph/v1/paper/search"

st.markdown("""
<style>
[data-testid="stAppViewContainer"] {
    background-color: #0c140c;
}
[data-testid="stSidebar"] {
    background-color: #0a120a;
    border-right: 1px solid #1e2e1e;
}
[data-testid="stSidebar"] .stButton button {
    background: #111a11;
    color: #7eda7e;
    border: 1px solid #2a4a2a;
    border-radius: 8px;
    width: 100%;
    text-align: left;
    padding: 6px 12px;
    font-size: 0.85rem;
    margin-bottom: 4px;
}
[data-testid="stSidebar"] .stButton button:hover {
    border-color: #7eda7e;
    background: #1a2a1a;
}
.stTextInput input {
    background: #111a11;
    color: #cfe8cf;
    border: 1px solid #2a4a2a;
    border-radius: 10px;
    padding: 10px 14px;
}
.stTextInput input:focus {
    border-color: #7eda7e;
    box-shadow: 0 0 0 2px #7eda7e33;
}
.stButton > button {
    background: #1a4a1a;
    color: #7eda7e;
    border: 1px solid #3a7a3a;
    border-radius: 10px;
    padding: 8px 24px;
    font-weight: 600;
}
.stButton > button:hover {
    background: #2a6a2a;
    border-color: #7eda7e;
}
.main-title {
    font-size: 2.4rem;
    font-weight: 700;
    color: #e8f5e8;
    margin-bottom: 0.2rem;
}
.subtitle {
    font-size: 0.95rem;
    color: #6a8a6a;
    margin-bottom: 1.8rem;
}
.featured-card {
    background: linear-gradient(135deg, #0f2a1a 0%, #0a1f2e 100%);
    border: 1px solid #2a5a3a;
    border-radius: 18px;
    padding: 32px 36px;
    margin-bottom: 24px;
}
.paper-card {
    background: #111a11;
    border: 1px solid #1e2e1e;
    border-radius: 14px;
    padding: 24px 28px;
    margin-bottom: 16px;
}
.paper-card:hover {
    border-color: #3a6a3a;
}
.paper-title {
    font-size: 1.15rem;
    font-weight: 700;
    color: #e8f5e8;
    margin-bottom: 6px;
    line-height: 1.4;
}
.featured-title {
    font-size: 1.5rem;
    font-weight: 700;
    color: #e8f5e8;
    margin-bottom: 8px;
    line-height: 1.4;
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
.badge-year  { background: #2a2a2a; color: #cccccc; }
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
.meta-line {
    font-size: 0.78rem;
    color: #4a6a4a;
    margin-bottom: 4px;
}
.stats-bar {
    background: #0f1a0f;
    border: 1px solid #1e2e1e;
    border-radius: 10px;
    padding: 12px 20px;
    margin-bottom: 24px;
    font-size: 0.82rem;
    color: #6a8a6a;
}
.section-header {
    font-size: 1.1rem;
    font-weight: 600;
    color: #7eda7e;
    margin: 24px 0 14px 0;
    padding-bottom: 6px;
    border-bottom: 1px solid #1e2e1e;
}
.no-results {
    text-align: center;
    padding: 60px 20px;
    color: #4a6a4a;
    font-size: 1.05rem;
}
.abstract-text {
    font-size: 0.88rem;
    color: #8aaa8a;
    line-height: 1.6;
    margin-top: 10px;
}
.read-link a {
    color: #7eda7e;
    font-size: 0.85rem;
    text-decoration: none;
}
</style>
""", unsafe_allow_html=True)


def detect_study_type(text):
    if not text:
        return "Research Study"
    t = text.lower()
    if "meta-analysis" in t:
        return "Meta-Analysis"
    if "systematic review" in t:
        return "Systematic Review"
    if "randomized" in t:
        return "Randomized Controlled Trial"
    if "double-blind" in t:
        return "Double-Blind Trial"
    if "cohort" in t:
        return "Cohort Study"
    if "case-control" in t:
        return "Case-Control Study"
    if "cross-sectional" in t:
        return "Cross-Sectional Study"
    if "mouse" in t or "mice" in t or "rat" in t:
        return "Animal Study"
    if "in vitro" in t:
        return "Laboratory Study"
    return "Research Study"


def extract_sample_size(text):
    if not text:
        return None
    match = re.search(r"(\d{2,5})\s+(participants|patients|subjects)", text.lower())
    return match.group(1) if match else None


def extract_findings(abstract):
    if not abstract:
        return None
    sentences = re.split(r"(?<=[.!?])\s+", abstract)
    keywords = ["found", "result", "associated", "significant", "increase",
                "decrease", "suggest", "indicate", "demonstrate", "conclude"]
    scored = [(sum(k in s.lower() for k in keywords), s) for s in sentences]
    scored.sort(reverse=True)
    top = [s for score, s in scored[:2] if score > 0]
    return " ".join(top) if top else None


def strength_note(study_type):
    notes = {
        "Animal Study": "Preliminary - may not generalize to humans.",
        "Meta-Analysis": "Aggregates multiple studies, high evidence strength.",
        "Systematic Review": "Comprehensive review of existing literature.",
        "Randomized Controlled Trial": "Controlled design supports causal interpretation.",
        "Double-Blind Trial": "Double-blind design minimizes bias.",
        "Laboratory Study": "In vitro results may not replicate in vivo.",
    }
    return notes.get(study_type, "Observational design - interpret causality with care.")


def make_summary_html(paper):
    abstract = paper.get("abstract", "")
    title = paper.get("title", "")
    study_type = detect_study_type(abstract)
    findings = extract_findings(abstract) or "Key findings reported - see full abstract below."
    sample_size = extract_sample_size(abstract)
    sample_line = ("Approx. " + sample_size + " participants included.") if sample_size else "Sample size not stated in abstract."

    return (
        "<div class=\"plain-summary\">"
        "<h4>What They Studied</h4>"
        "<p>This " + study_type.lower() + " investigated: <strong>" + title + "</strong></p>"
        "<h4>Key Findings</h4>"
        "<p>" + findings + "</p>"
        "<h4>Study Strength</h4>"
        "<p>" + sample_line + " Design: <strong>" + study_type + "</strong>. " + strength_note(study_type) + "</p>"
        "<h4>Takeaway</h4>"
        "<p>Findings contribute to the evidence base. Consult a professional before acting on research.</p>"
        "</div>"
    )


def make_badges_html(paper):
    study_type = detect_study_type(paper.get("abstract", ""))
    year = paper.get("year")
    citations = paper.get("citationCount")
    is_open = paper.get("openAccessPdf")
    is_new = year and int(year) >= 2024

    html = "<div class=\"badge-row\">"
    html += "<span class=\"badge badge-study\">" + study_type + "</span>"
    if year:
        html += "<span class=\"badge badge-year\">" + str(year) + "</span>"
    if citations is not None:
        html += "<span class=\"badge badge-cite\">" + str(citations) + " citations</span>"
    if is_open:
        html += "<span class=\"badge badge-open\">Open Access</span>"
    if is_new:
        html += "<span class=\"badge badge-new\">New 2024+</span>"
    html += "</div>"
    return html


def format_authors(authors):
    if not authors:
        return "Unknown"
    names = [a.get("name") for a in authors if a.get("name")]
    return ", ".join(names[:4]) + (" et al." if len(names) > 4 else "")


def compute_score(paper):
    citations = paper.get("citationCount") or 0
    score = int(citations) * 2
    if paper.get("openAccessPdf"):
        score += 5
    try:
        if paper.get("year") and int(paper.get("year")) >= 2024:
            score += 3
    except Exception:
        pass
    return score


@st.cache_data(ttl=3600, show_spinner=False)
def search_papers(query, limit=12):
    params = {
        "query": query,
        "limit": limit,
        "fields": "title,authors,year,abstract,url,openAccessPdf,citationCount,journal,fieldsOfStudy"
    }
    for attempt in range(3):
        try:
            resp = requests.get(API_SEARCH, params=params, timeout=12)
            if resp.status_code == 429:
                wait = 5 * (attempt + 1)
                st.warning("Rate limited. Retrying in " + str(wait) + "s...")
                time.sleep(wait)
                continue
            resp.raise_for_status()
            return resp.json().get("data", [])
        except requests.RequestException:
            if attempt == 2:
                st.error("Search failed after 3 attempts. Please wait and try again.")
                time.sleep(3)
                return []


def render_featured(paper):
    title = paper.get("title", "Untitled")
    authors = format_authors(paper.get("authors", []))
    journal = (paper.get("journal") or {}).get("name", "")
    url = paper.get("url", "")

    st.markdown("<div class=\"featured-card\">", unsafe_allow_html=True)
    if journal:
        st.markdown("<div class=\"meta-line\">Published in <em>" + journal + "</em></div>", unsafe_allow_html=True)
    st.markdown("<div class=\"featured-title\">" + title + "</div>", unsafe_allow_html=True)
    st.markdown(make_badges_html(paper), unsafe_allow_html=True)
    st.markdown("<div class=\"meta-line\">Authors: " + authors + "</div>", unsafe_allow_html=True)
    st.markdown(make_summary_html(paper), unsafe_allow_html=True)
    col1, col2 = st.columns([1, 4])
    with col1:
        if paper.get("abstract"):
            with st.expander("Full Abstract"):
                st.markdown("<div class=\"abstract-text\">" + paper.get("abstract") + "</div>", unsafe_allow_html=True)
    with col2:
        if url:
            st.markdown("<div class=\"read-link\"><a href=\"" + url + "\" target=\"_blank\">Read Full Paper</a></div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


def render_paper(paper):
    title = paper.get("title", "Untitled")
    authors = format_authors(paper.get("authors", []))
    journal = (paper.get("journal") or {}).get("name", "")
    url = paper.get("url", "")

    st.markdown("<div class=\"paper-card\">", unsafe_allow_html=True)
    if journal:
        st.markdown("<div class=\"meta-line\">Published in <em>" + journal + "</em></div>", unsafe_allow_html=True)
    st.markdown("<div class=\"paper-title\">" + title + "</div>", unsafe_allow_html=True)
    st.markdown(make_badges_html(paper), unsafe_allow_html=True)
    st.markdown("<div class=\"meta-line\">Authors: " + authors + "</div>", unsafe_allow_html=True)
    st.markdown(make_summary_html(paper), unsafe_allow_html=True)
    col1, col2 = st.columns([1, 4])
    with col1:
        if paper.get("abstract"):
            with st.expander("Full Abstract"):
                st.markdown("<div class=\"abstract-text\">" + paper.get("abstract") + "</div>", unsafe_allow_html=True)
    with col2:
        if url:
            st.markdown("<div class=\"read-link\"><a href=\"" + url + "\" target=\"_blank\">Read Full Paper</a></div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


def render_stats(papers):
    total = len(papers)
    open_count = sum(1 for p in papers if p.get("openAccessPdf"))
    recent = sum(1 for p in papers if p.get("year") and int(p.get("year") or 0) >= 2024)
    avg_cite = int(sum(p.get("citationCount", 0) for p in papers) / total) if total else 0
    st.markdown(
        "<div class=\"stats-bar\">"
        + str(total) + " papers found  |  "
        + str(open_count) + " open access  |  "
        + str(recent) + " from 2024+  |  "
        + "avg " + str(avg_cite) + " citations"
        + "</div>",
        unsafe_allow_html=True
    )


def main():
    with st.sidebar:
        st.markdown("<div style=\"color:#7eda7e;font-size:1.1rem;font-weight:600;margin-bottom:12px;\">Search Options</div>", unsafe_allow_html=True)
        # manual search field
        user_query = st.text_input("Search topics", value=st.session_state.get("manual_query", ""), placeholder="e.g. migraine, probiotics...")
        if st.button("Go", key="manual_search") and user_query:
            st.session_state["manual_query"] = user_query
            st.session_state["query"] = user_query
        result_limit = st.slider("Number of results", min_value=5, max_value=20, value=12, step=5)
        st.markdown("—")
        st.markdown("<div style=\"color:#7eda7e;font-size:1.1rem;font-weight:600;margin-bottom:10px;\">Quick Topics</div>", unsafe_allow_html=True)
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
            if st.button(t, use_container_width=True, key=f"topic_{i}"):
                st.session_state["query"] = t
        st.markdown("—")
        st.markdown("<div style=\"font-size:0.75rem;color:#4a6a4a;\">Data from Semantic Scholar.<br>Results cached 1 hour.</div>", unsafe_allow_html=True)

    st.markdown("<div class=\"main-title\">SciPulse</div>", unsafe_allow_html=True)
    st.markdown("<div class=\"subtitle\">Evidence-first summaries of peer-reviewed research. No hype. No paywall.</div>", unsafe_allow_html=True)

    # automatically run search when a quick topic has been selected
    current_query = st.session_state.get("query", "")
    if current_query:
        st.markdown(f"<div class=\"meta-line\">Searching for: <strong>{current_query}</strong></div>", unsafe_allow_html=True)
        with st.spinner("Fetching research..."):
            papers = search_papers(current_query, limit=result_limit)
        if papers:
            for p in papers:
                p["_score"] = compute_score(p)
            papers.sort(key=lambda x: x["_score"], reverse=True)
            render_stats(papers)
            st.markdown("<div class=\"section-header\">Featured Study</div>", unsafe_allow_html=True)
            render_featured(papers[0])
            if len(papers) > 1:
                st.markdown("<div class=\"section-header\">More Research</div>", unsafe_allow_html=True)
                for p in papers[1:]:
                    render_paper(p)
        else:
            st.markdown("<div class=\"no-results\">No results found. Try broader terms.</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div class=\"no-results\">Pick a topic from the sidebar to begin.</div>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()

