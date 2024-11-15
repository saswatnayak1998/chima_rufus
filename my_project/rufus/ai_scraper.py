import time
import random
import faiss
import numpy as np
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
import os
import requests

class RufusClient:
    def __init__(self, api_key, embedding_size=384):
        if not api_key:
            raise ValueError("API key is required")
        self.api_key = api_key
        self.index = self.initialize_faiss_index(embedding_size)
        self.filtered_index = self.initialize_faiss_index(embedding_size)
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Use absolute paths
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.metadata_file = os.path.join(self.base_dir, '..', 'website_metadata.json')
        self.filtered_metadata_file = os.path.join(self.base_dir, '..', 'website_metadata_filtered.json')
        self.index_file = os.path.join(self.base_dir, '..', 'website_docs_faiss.index')
        self.filtered_index_file = os.path.join(self.base_dir, '..', 'website_docs_faiss_filtered.index')
        
        # Create/empty the metadata files
        os.makedirs(os.path.dirname(self.metadata_file), exist_ok=True)
        with open(self.metadata_file, 'w', encoding='utf-8') as f:
            json.dump([], f, indent=4)
        with open(self.filtered_metadata_file, 'w', encoding='utf-8') as f:
            json.dump([], f, indent=4)
        
        self.visited_links = set()
        self.driver = self.get_driver(headless=True)
        self.relevant_keywords = []

    def get_driver(self, headless=True):
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless=new")  
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--enable-javascript")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    def get_relevant_keywords(self, instructions):
        """Get semantically similar keywords using LLM"""
        try:
            prompt = f"""Given these instructions: {instructions}

            Please generate a list of semantically similar keywords and phrases that could indicate relevant content.
            Include variations of words (singular/plural, different tenses).

            For example, if looking for "product information", relevant keywords might include:
            - product
            - products 
            - what we do
            - our product
            - our products
            - features
            - capabilities
            - solutions

            Respond with ONLY the keywords/phrases, one per line, no bullets or other formatting."""

            response = requests.post('http://localhost:11434/api/generate',
                json={
                    "model": "llama2",
                    "prompt": prompt,
                    "stream": False
                })
            keywords = response.json()['response'].strip().split('\n')
            self.relevant_keywords = [k.strip().lower() for k in keywords if k.strip()]
            print(f"Generated keywords: {self.relevant_keywords}")
            return self.relevant_keywords
        except Exception as e:
            print(f"Error generating keywords: {e}")
            return []
        
    def check_content_relevance(self, content, instructions, title):
        """Check if content contains any relevant keywords from LLM response"""
        if not self.relevant_keywords:
            self.get_relevant_keywords(instructions)
            
        prompt = f"""Given these instructions: {instructions}
                And this page title: {title}

                Based on this title, would this page likely contain information that answers or is relevant to the instructions?
                Consider the semantic meaning and topic of the title.
                Respond with ONLY 'yes' or 'no'."""

        try:
            response = requests.post('http://localhost:11434/api/generate',
                json={
                    "model": "llama2", 
                    "prompt": prompt,
                    "stream": False
                })
            is_relevant = response.json()['response'].strip().lower() == 'yes'
            
            if is_relevant:
                print(f"LLM determined title '{title}' is relevant")
                return True
                
        except Exception as e:
            print(f"Error checking relevance with LLM: {e}")
            # Fall back to keyword matching if LLM fails
            content_lower = content.lower()
            for keyword in self.relevant_keywords:
                if keyword.lower() in content_lower:
                    print(f"Found relevant keyword: {keyword}")
                    return True
                    
        return False

    def initialize_faiss_index(self, embedding_size=384):
        return faiss.IndexFlatL2(embedding_size)  # FAISS index for L2 distance

    def get_headers(self, soup):
        """Extract first 3 headers from the page"""
        headers = []
        for tag in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
            headers.append(tag.get_text(strip=True))
            if len(headers) == 3:
                break
        return headers

    def save_metadata(self, metadata_entry, instructions):
        """Save a single metadata entry by appending to both filtered and unfiltered JSON files"""
        try:
            if not os.path.exists(self.metadata_file):
                with open(self.metadata_file, 'w', encoding='utf-8') as f:
                    json.dump([], f)

            try:
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            except json.JSONDecodeError:
                print("Error reading metadata file, creating new one")
                data = []
            
            url = metadata_entry.get('url')
            data = [item for item in data if item.get('url') != url]
            data.append(metadata_entry)
            
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
                f.flush()
                os.fsync(f.fileno())

            if self.check_content_relevance(metadata_entry['content'], instructions, metadata_entry['content']):
                if not os.path.exists(self.filtered_metadata_file):
                    with open(self.filtered_metadata_file, 'w', encoding='utf-8') as f:
                        json.dump([], f)

                try:
                    with open(self.filtered_metadata_file, 'r', encoding='utf-8') as f:
                        filtered_data = json.load(f)
                except json.JSONDecodeError:
                    print("Error reading filtered metadata file, creating new one")
                    filtered_data = []
                
                filtered_data = [item for item in filtered_data if item.get('url') != url]
                filtered_data.append(metadata_entry)
                
                with open(self.filtered_metadata_file, 'w', encoding='utf-8') as f:
                    json.dump(filtered_data, f, indent=4, ensure_ascii=False)
                    f.flush()
                    os.fsync(f.fileno())
                
                print(f"Successfully saved metadata for: {metadata_entry['url']} (filtered)")
            
            print(f"Successfully saved metadata for: {metadata_entry['url']} (unfiltered)")
                    
        except Exception as e:
            print(f"Failed to save metadata: {e}")
            import traceback
            traceback.print_exc()

    def scrape_website_page(self, url, instructions, max_depth=3, current_depth=0):
        """
        Scrapes a webpage and its internal links recursively.
        
        Args:
            url (str): The URL to scrape
            instructions (str): Scraping instructions for relevance checking
            max_depth (int): Maximum depth for recursive scraping
            current_depth (int): Current depth in the recursion
        """
        try:
            if url in self.visited_links or current_depth > max_depth:
                return

            print(f"Scraping: {url}")
            self.driver.get(url)
            
            time.sleep(3)
            
            try:
                from selenium.webdriver.common.by import By
                from selenium.webdriver.support.ui import WebDriverWait
                from selenium.webdriver.support import expected_conditions as EC
                
                WebDriverWait(self.driver, 20).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                
                
                self.driver.execute_script(
                    "window.scrollTo(0, document.body.scrollHeight);"
                )
                time.sleep(2)  
                
            except Exception as e:
                print(f"Timeout waiting for page to load: {e}")
                return

            page_content = self.driver.execute_script(
                "return document.documentElement.outerHTML"
            )
            soup = BeautifulSoup(page_content, 'html.parser')
            
            title = soup.title.string if soup.title else "No Title"
            
            main_content = (
                soup.find('main') or 
                soup.find('div', {'id': 'main-content'}) or 
                soup.find('div', {'class': 'main-content'}) or 
                soup.find('article') or 
                soup.body
            )
            
            if main_content:
                # Remove unwanted elements
                for element in main_content.find_all(['script', 'style', 'nav', 'footer']):
                    element.decompose()
                
                content_text = main_content.get_text(separator=' ', strip=True)
            else:
                content_text = "No main content found."

            headers = self.get_headers(soup)
            
            if content_text != "No main content found.":
                try:
                    embedding = self.model.encode([content_text])[0].astype('float32')
                    
                    metadata_entry = {
                        "title": title,
                        "url": url,
                        "content": content_text,
                        "headers": headers
                    }
                    
                    self.index.add(np.array([embedding]))
                    
                    if self.check_content_relevance(content_text, instructions, title):
                        self.filtered_index.add(np.array([embedding]))
                        print(f"✓ Added to filtered index: {title} | {url}")
                    
                    self.save_metadata(metadata_entry, instructions)
                    print(f"✓ Successfully stored content: {title} | {url}")
                        
                except Exception as e:
                    print(f"Failed to process embeddings for {url}: {e}")
            else:
                print(f"⨯ Skipping empty page: {url}")

            self.visited_links.add(url)

            if current_depth < max_depth:
                internal_links = soup.find_all('a', href=True)
                base_domain = url.split('/')[2]  
                
                for link in internal_links:
                    href = link['href']
                    full_url = urljoin(url, href)
                    
                   
                    if base_domain in full_url and full_url not in self.visited_links:
                        print(f"→ Following link: {full_url}")
                        self.scrape_website_page(
                            full_url, 
                            instructions, 
                            max_depth, 
                            current_depth + 1
                        )

        except Exception as e:
            print(f"Failed to scrape {url}: {e}")

    def save_index(self):
        """Save both FAISS indexes to files."""
        
        os.makedirs(os.path.dirname(self.index_file) if os.path.dirname(self.index_file) else '.', exist_ok=True)
        
     
        faiss.write_index(self.index, self.index_file)
        print(f"Main vector store saved to {os.path.abspath(self.index_file)}")
        
     
        faiss.write_index(self.filtered_index, self.filtered_index_file)
        print(f"Filtered vector store saved to {os.path.abspath(self.filtered_index_file)}")

    def scrape(self, url, instructions):
        """Main method to initiate scraping and save the results."""
        
        self.get_relevant_keywords(instructions)
        
        self.scrape_website_page(url, instructions)
        self.save_index()
        self.driver.quit()
        
        
        print(f"\nChecking final metadata files:")
        try:
            with open(self.metadata_file, 'r', encoding='utf-8') as f:
                final_data = json.load(f)
                print(f"Number of total entries in metadata: {len(final_data)}")
                
            with open(self.filtered_metadata_file, 'r', encoding='utf-8') as f:
                final_filtered_data = json.load(f)
                print(f"Number of filtered entries in metadata: {len(final_filtered_data)}")
                
            return {
                'all_data': final_data,
                'filtered_data': final_filtered_data
            }
        except Exception as e:
            print(f"Error reading final metadata: {e}")
            return {'all_data': [], 'filtered_data': []}