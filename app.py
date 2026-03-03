import streamlit as st
import requests
import time
from typing import List, Dict, Any

API_SEARCH = "https://api.semanticscholar.org/graph/v1/paper/search"


@st.cache_data(ttl=3600, show_spinner=False)
def search_papers(query: str, limit: int = 8) -> List[Dict[str, Any]]:
    params = {
        "query": query,
        "limit": limit,
        "fields": "title,authors,year,abstract,url,openAccessPdf,citationCount"
    }

    for attempt in range(3):
        try:
            resp = requests.get(API_SEARCH, params=params, timeout=12)
            if resp.status_code == 429:
                wait = 5 * (attempt + 1)
                st.warning(f"Rate limited by Semantic Scholar. Retrying in {wait}s...")
                time.sleep(wait)
                continue
            resp.raise_for_status()
            data = resp.json()
            return data.get("data", [])
        except requests.RequestException:
            if attempt == 2:
                st.error("Search failed after 3 attempts. Please wait a moment and try again.")
                time.sleep(3)
                return []
            time.sleep(1)


def compute_score(paper: Dict[str, Any]) -> int:
    citations = paper.get("citationCount") or 0
    score = int(citations) * 2
    if paper.get("openAccessPdf"):
        score += 5
    year = paper.get("year")
    try:
        if year and int(year) >= 2024:
            score += 3
    except Exception:
        pass
    return score


def format_authors(authors: List[Dict[str, Any]]) -> str:
    if not authors:
        return "Unknown"
    names = [a.get("name") for a in authors if a.get("name")]
    return ", ".join(names[:4]) + (" et al." if len(names) > 4 else "")


def show_results(papers: List[Dict[str, Any]]):
    if not papers:
        st.info("No results - try a different query.")
        return

    for p in papers:
        p["_score"] = compute_score(p)
    papers.sort(key=lambda x: x["_score"], reverse=True)

    featured = papers[0]
    st.subheader("Featured Study")
    st.markdown("**" + featured.get("title", "Untitled") + "**")
    st.write("Authors: " + format_authors(featured.get("authors", [])))
    st.write("Year: " + str(featured.get("year", "Unknown")))
    st.write("Citations: " + str(featured.get("citationCount", 0)))
    if featured.get("abstract"):
        st.write(featured.get("abstract"))
    if featured.get("url"):
        st.markdown("[View paper](" + featured.get("url") + ")")

    st.markdown("---")
    st.subheader("Other Top Results")
    for p in papers[1:]:
        with st.expander(p.get("title", "Untitled")):
            st.write("Authors: " + format_authors(p.get("authors", [])))
            st.write("Year: " + str(p.get("year", "Unknown")) + " | Citations: " + str(p.get("citationCount", 0)))
            if p.get("abstract"):
                st.write(p.get("abstract"))
            if p.get("url"):
                st.markdown("[View paper](" + p.get("url") + ")")


def main():
    st.title("SciPulse - Research Summaries")
    st.write("Evidence-first summaries of peer-reviewed research. No hype. No paywall.")

    quick_topics = [
        "gut microbiome",
        "CRISPR gene editing",
        "climate change",
        "COVID-19 vaccine",
        "sleep deprivation",
        "antibiotic resistance",
    ]

    st.sidebar.header("Quick Topics")
    for t in quick_topics:
        if st.sidebar.button(t):
            st.session_state.query = t

    query = st.text_input("Search papers", value=st.session_state.get("query", ""))

    if st.button("Search") and query:
        with st.spinner("Searching Semantic Scholar..."):
            papers = search_papers(query, limit=12)
            show_results(papers)
    elif query:
        st.write("Click Search or pick a quick topic from the sidebar.")


if __name__ == "__main__":
    main()
