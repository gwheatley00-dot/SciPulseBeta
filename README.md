# 🧬 SciPulse

> **Evidence-first summaries of peer-reviewed research. No hype. No paywall.**

SciPulse is a clean, fast research discovery tool that searches 200M+ academic papers and returns plain-language breakdowns — automatically detecting study type, surfacing key findings, and ranking results by quality.

Built with Python + Streamlit. Data from Semantic Scholar.

-----

## 🔍 What It Does

- **Search any research topic** — from gut microbiome to CRISPR to climate change
- **Plain-language summaries** — extracts what was studied, what was found, and how strong the evidence is
- **Auto-detects study type** — RCT, Meta-Analysis, Cohort Study, Animal Study, Lab Study, and more
- **Ranks by quality** — citation count, recency, and open access status
- **Quick-topic sidebar** — one-click searches for popular research areas
- **Stats bar** — snapshot of result quality at a glance
- **Direct links** — every paper links to the full source

-----

## 🚀 Running Locally

**1. Clone the repo**

```bash
git clone https://github.com/YOUR_USERNAME/scipulse.git
cd scipulse
```

**2. Install dependencies**

```bash
pip install -r requirements.txt
```

**3. Run the app**

```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`

-----

## ☁️ Deploying to Streamlit Cloud

1. Push this repo to GitHub (must be **public**)
1. Go to [share.streamlit.io](https://share.streamlit.io)
1. Sign in with GitHub
1. Click **New App** → select this repo → set main file to `app.py`
1. Click **Deploy**

Your live URL will look like:

```
https://YOUR_USERNAME-scipulse-app-xxxx.streamlit.app
```

-----

## 📁 Project Structure

```
scipulse/
├── app.py                  # Main Streamlit application
├── requirements.txt        # Python dependencies
├── README.md               # You are here
└── .streamlit/
    └── config.toml         # Theme + server configuration
```

-----

## 🛠 Tech Stack

|Tool                                                    |Purpose                       |
|--------------------------------------------------------|------------------------------|
|[Streamlit](https://streamlit.io)                       |Web app framework             |
|[Semantic Scholar API](https://api.semanticscholar.org/)|Paper search & metadata       |
|Python                                                  |Core logic & text extraction  |
|HTML + CSS                                              |Custom dark-green card styling|

-----

## 📊 How Papers Are Ranked

Papers are scored using a weighted formula:

- `citation count × 2` — rewards highly cited work
- `+5` for open access papers
- `+3` for papers published in 2024 or later

The top-scoring paper becomes the **Featured Study**.

-----

## ⚠️ Disclaimer

SciPulse summarizes publicly available research abstracts. Summaries are auto-generated and should not be used as medical, legal, or professional advice. Always read original papers and consult qualified professionals before drawing conclusions.

-----

## 📜 License

MIT — free to use, modify, and distribute.

-----

*Made with 🧬 and too much coffee.*# SciPulseBeta