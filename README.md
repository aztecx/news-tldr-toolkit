# News TL;DR Toolkit

Summarise news articles and create small news digests using a local transformer model (installed on the machine).

This project provides:

- **File summariser**: TL;DR + bullet points for a local `.txt`/`.md` file

- **URL summariser**: TL;DR + bullet points for a news article URL

- **News digest**: Search predefined RSS feeds for a keyword (e.g., `France`, `NHS`, `AI in Ipswich`) and summarise a few matching articles

- **Streamlit UI**: Simple web interface with all three tools in one place

Everything runs locally on your machine using a Hugging Face summarisation model (`sshleifer/distilbart-cnn-12-6` on PyTorch).

## 1. Installation

You will need:

- Python 3.10 or newer

- `pip` (or conda)

- Enough disk space for the model (about 1–2 GB download the first time)

Clone the repository:

```bash
git clone https://github.com/aztecx/news-tldr-toolkit.git
cd news-tldr-toolkit
```

Create and activate a virtual environment (example with conda):

```bash
conda create -n news-tldr python=3.10
conda activate news-tldr
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## 2. Features

### 2.1 Summarise a local file

- Input: `.txt` or `.md` file

- Output:
  
  - One-paragraph TL;DR
  
  - 2–5 bullet points

### 2.2 Summarise a URL

- Input: news article URL (e.g., BBC)

- The toolkit:
  
  1. Downloads the page HTML (`requests`)
  
  2. Extracts visible text (`BeautifulSoup`)
  
  3. Runs a transformer summariser (DistilBART)

- Output:
  
  - TL;DR
  
  - Bullet points

### 2.3 News digest (keyword search)

- Uses predefined RSS feeds (BBC top stories, world, UK, and regions such as Europe, Asia, US & Canada, Middle East).

- You provide:
  
  - A keyword or phrase (e.g., `Colchester`, `France`, `Japan`, `NHS`, `AI in Ipswich`)
  
  - How many articles to summarise (capped at 3 to keep it CPU-friendly)

- For each matching article:
  
  - Shows title and link
  
  - TL;DR
  
  - Bullet points  
  
  

---

## 3. Command-line Usage

All commands assume you are in the project root with the `news-tldr` environment activated.

### 3.1 Summarise a local file

```python
python summarise_file.py path/to/file.txt --max_chars 200
```

`--max_chars` is an approximate maximum size of the TL;DR paragraph (in characters).

Example:

```python
python summarise_file.py samples/news1.txt --max_chars 150
```



### 3.2 Summarise a URL

```python
python summarise_url.py "https://www.bbc.co.uk/news/..." --max_chars 200
```

The script:

1. Downloads the page HTML

2. Extracts the text with `BeautifulSoup`

3. Runs the summariser

4. Prints TL;DR and bullet points

### 3.3 News digest (keyword to summarised articles)

```python
python news_digest.py "France" --max_articles 2 --max_chars 150
```



python news_digest.py "France" --max_articles 2 --max_chars 150

- `query` (positional) – keyword or phrase to search for in article titles and descriptions

- `--max_articles` – maximum number of matching articles to summarise (limited to 3 in practice)

- `--max_chars` – approximate TL;DR length per article

The script:

1. Fetches items from the RSS feeds in `news_digest.py` (the `RSS_FEEDS` list).

2. Filters items where `query` appears in title or description (case-insensitive).

3. For up to `max_articles` matches:
   
   - Fetches the article page
   
   - Extracts article text
   
   - Summarises to TL;DR and bullet points

---

## 4. Streamlit UI

You can use everything via a simple local web UI.

From the project root:

```bash
streamlit run app.py
```

This opens a local page (usually `http://localhost:8501`) with three modes:

### 4.1 Summarise URL

- Text box for a URL

- Slider for TL;DR length

- Button: “Summarise URL”

- Output: TL;DR and bullet points

### 4.2 Summarise file

- File uploader (`.txt` or `.md`)

- Slider for TL;DR length

- Button: “Summarise file”

- Output: TL;DR and bullet points

### 4.3 News digest

- Text input: keyword or phrase (e.g., `Colchester`, `France`, `NHS`)

- Slider: maximum number of articles (1–3)

- Slider: TL;DR length

- Button: “Run news digest”

- Output: up to N matching articles, each in an expandable section:
  
  - “Read full article” link
  
  - TL;DR
  
  - Bullet points
    
    

---

## 5. Model Details and Performance Notes

- Model: `sshleifer/distilbart-cnn-12-6` (Hugging Face Transformers, PyTorch backend)

- Runs on CPU by default (`device=-1` in `NewsSummariser`)

- The first call will download the model (about 1 GB or more) into your Hugging Face cache

- Summarisation, especially in digest mode, can be heavy:
  
  - Each article currently uses two model calls (one for TL;DR, one for bullet points)
  
  - On CPU, summarising three full news articles is noticeably slower than summarising a single URL

Because of this, the UI intentionally caps digest mode to a maximum of three articles to avoid freezing a typical laptop CPU.

If you have a suitable GPU and a CUDA-enabled PyTorch installation, you can switch to GPU by changing the `device` argument in `NewsSummariser` to `0` (first GPU).



---

## 6. Repository Structure

```bash
news-tldr-toolkit/
├── app.py                 # Streamlit UI (URL, file, digest modes)
├── summarise_file.py      # CLI: summarise a local text file
├── summarise_url.py       # CLI: summarise a URL
├── news_digest.py         # CLI: RSS-based news digest
├── src/
│   └── summariser.py       # NewsSummariser class and SummaryResult dataclass
├── samples/
│   └── ...                 # Sample text files for testing
├── requirements.txt       # Python dependencies
└── README.md             
```
