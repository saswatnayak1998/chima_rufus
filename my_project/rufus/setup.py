# setup.py
from setuptools import setup, find_packages

setup(
    name="Rufus",
    version="0.1",
    description="Rufus - AI-powered web scraping for RAG applications",
    author="Saswat",
    packages=find_packages(),
    install_requires=[
        "selenium",
        "beautifulsoup4",
        "faiss-cpu",
        "sentence-transformers",
        "openai",
        "python-dotenv",
        "webdriver-manager",
        "numpy",
    ],
    python_requires=">=3.9",

)
