# Rufus: Intelligent Web Scraping for Retrieval-Augmented Generation (RAG) Systems

Rufus is a web scraping tool designed for Retrieval-Augmented Generation (RAG) systems. This tool intelligently scrapes relevant content from websites based on user-defined instructions and synthesizes it into structured JSON documents ready for use in downstream LLM applications.

## Features

- Intelligent, recursive web scraping using Selenium
- Semantic relevance filtering with GPT-4 (using OpenAI API)
- Efficient data storage with FAISS indexing
- Easy-to-use API for integration with RAG pipelines
- Optional integration with Ollama for local LLM processing

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
cd rufus
```
