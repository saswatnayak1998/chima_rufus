# Rufus: Intelligent Web Scraping for Retrieval-Augmented Generation (RAG) Systems

Rufus is a web scraping tool designed for Retrieval-Augmented Generation (RAG) systems. This tool intelligently scrapes relevant content from websites based on user-defined instructions and synthesizes it into structured JSON documents ready for use in downstream LLM applications(maybe RAG).

## Features

- Intelligent, recursive web scraping using Selenium
- Semantic relevance filtering with a locally run LLM(Llama2)
- Efficient data storage with FAISS indexing
- Easy-to-use API for integration with RAG pipelines

## How does it work?

- Rufus scrapes the web for user defined **url**. There is a depth parameter that controls how deep the scraper will go(It is set to 3 by default).
- The scraped content along with the FAISS vector database is then filtered for relevance using a locally run LLM by comparing them with the user defined **instructions**. This is not very good yet because I am using Llama2 instead of a state of the art LLM like GPT-4o which will perform much better because of the larger context length and the larger number of parameters.
- I have scraped a YC W24 website and the results are stored in the **my_project/website_metadata.json** and the vector database is stored in the **my_project/website_docs_faiss.index** file.

## How to use it in a RAG pipeline?

- First get the relevant data from the web with Rufus(Intelligent scraping)
- When given a query, use the same embedding model used to embed the web data to FAISS vector db(all-MiniLM-L6-v2) to embed the query. Then use this query vector to search for the most semantically similar chunks in the FAISS vector db. The metadata(links, title etc) are stored in the same metadata file. Some example data scraped are stored in the **my_project/website_metadata.json** and **my_project/website_docs_faiss.index** file.
- Then this metadata can be used as context to answer the query!

## IMPROVEMENTS

- Use GPT-4 instead of Llama2(7B)
- Use Claude API which knows what link to click in the webpage based on the instructions(Need more time to implement). Need to pull up a VM and train it.

---

## Setup

### Prerequisites

Ensure you have the following installed:

- **Python 3.9 or later**
- Have a local instance of Llama2 running(use Ollama for this)
- **pip** (Python package manager)
- **Ollama** (optional) for local LLM processing

### Step 1: Clone the Repository

Clone the repository to your local machine:

```bash
git clone https://github.com/yourusername/rufus.git
```

### Step 2: Set Up a Virtual Environment

```bash
python3 -m venv chima_venv
source chima_venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: pip install rufus

This will allow us to make changes to the code and have them reflected without needing to reinstall the package.

```bash
cd my_project
pip install Rufus
```

### Step 5: test it out!

```bash
cd ..
python test.py

```

or

```bash
from rufus import RufusClient

client = RufusClient(api_key="your_api_key")
instructions = "tell me about the FAQs and the product differentiator for Delve"
results = client.scrape("https://www.getdelve.com/", instructions)
```
