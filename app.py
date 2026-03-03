import streamlit as st
import requests
from typing import List, Dict, Any

API_SEARCH = "https://api.semanticscholar.org/graph/v1/paper/search"

@st.cache_data(show_spinner=False)
def search_papers(query: str, limit: int = 8) -> List[Dict[str, Any]]:
    params = {
        "query": query,
        "limit": limit,
        "fields": "title,authors,year,abstract,url,openAccessPdf,citationCount"
    }
    try:
        resp = requests.get(API_SEARCH, params=params, timeout=12)
        resp.raise_for_status()
    except requests.RequestException as e:
        st.error(f"Search request failed: {e}")
        return []

    data = resp.json()
    return data.get("data", [])


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
        return "—"
    names = [a.get("name") for a in authors if a.get("name")]
    return ", ".join(names[:4]) + (" et al." if len(names) > 4 else "")


def show_results(papers: List[Dict[str, Any]]):
    if not papers:
        st.info("No results — try a different query.")
        return

    # compute score and sort
    for p in papers:
        p["_score"] = compute_score(p)
    papers.sort(key=lambda x: x["_score"], reverse=True)

    featured = papers[0]
    st.subheader("Featured Study")
    st.markdown(f"**{featured.get('title','Untitled')}**")
    st.write(f"Authors: {format_authors(featured.get('authors',[]))}")
    st.write(f"Year: {featured.get('year', '—')}")
    st.write(f"Citations: {featured.get('citationCount', 0)}")
    if featured.get("abstract"):
        st.write(featured.get("abstract"))
    if featured.get("url"):
        st.markdown(f"[View paper]({featured.get('url')})")
    st.info(f"Score: {featured.get('_score')}")

    st.markdown("---")
    st.subheader("Other Top Results")
    for p in papers[1:]:
        with st.expander(p.get("title", "Untitled")):
            st.write(f"Authors: {format_authors(p.get('authors', []))}")
            st.write(f"Year: {p.get('year', '—')} — Citations: {p.get('citationCount', 0)}")
            if p.get("abstract"):
                st.write(p.get("abstract"))
            if p.get("url"):
                st.markdown(f"[View paper]({p.get('url')})")
            st.write(f"Score: {p.get('_score')}")


def main():
    st.title("SciPulse — Research Summaries")
    st.write("Evidence-first summaries of peer-reviewed research. No hype. No paywall.")

    quick_topics = [
        "gut microbiome",
        "CRISPR gene editing",
        "climate change",
        "COVID-19 vaccine"
    ]

    st.sidebar.header("Quick topics")
    for t in quick_topics:
        if st.sidebar.button(t):
            st.session_state.query = t

    query = st.text_input("Search papers", value=st.session_state.get("query", ""))

    submit = st.button("Search")
    if submit and query:
        with st.spinner("Searching Semantic Scholar..."):
            papers = search_papers(query, limit=12)
            show_results(papers)
    elif query and not submit:
        st.write("Type your query and click Search, or use a quick topic.")


if __name__ == "__main__":
    main()
