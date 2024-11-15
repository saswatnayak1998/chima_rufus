# Rufus: Intelligent Web Scraping for Retrieval-Augmented Generation (RAG) Systems

Rufus is a web scraping tool designed for Retrieval-Augmented Generation (RAG) systems. This tool intelligently scrapes relevant content from websites based on user-defined instructions and synthesizes it into structured JSON documents ready for use in downstream LLM applications(maybe RAG).

## Features

- Intelligent, recursive web scraping using Selenium
- Semantic relevance filtering with a locally run LLM(Llama2)
- Efficient data storage with FAISS indexing
- Easy-to-use API for integration with RAG pipelines

## How does it work?

- Rufus scrapes the web for user defined **url**. There is a depth parameter that controls how deep the scraper will go(It is set to 3 by default).
- The scraped content is then filtered for relevance using a locally run LLM by comparing them with the user defined **instructions**. This is not very good yet because I am using Llama2 instead of a state of the art LLM like GPT-4o which will perform much better because of the larger context length and the larger number of parameters.

---

## Setup

### Prerequisites

Ensure you have the following installed:

- **Python 3.9 or later**
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
cd my_project/rufus
pip install -e .
```

### Step 5: test it out!

```bash
cd ..
python test.py
```
