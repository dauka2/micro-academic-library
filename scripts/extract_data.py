import sqlite3
import os
import json
import time
from openai import OpenAI
import pypdf
from dotenv import load_dotenv

load_dotenv()

DB_PATH = "database\\dbdb"
PDF_DIR = "database\\pdf"
API_KEY = os.getenv("API_KEY")
if not API_KEY:
    print("Error: No API_KEY")
    exit(1)
BASE_URL = "https://api.groq.com/openai/v1"  

client = OpenAI(
    api_key=API_KEY,
    base_url=BASE_URL 
)

model = "llama-3.1-8b-instant"

def get_ai_response(prompt, model=model, retries=3):
    for attempt in range(retries):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=1024,  
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"API request error (attempt {attempt + 1}/{retries}): {e}")
            if attempt < retries - 1:
                wait_time = 2 ** attempt  
                print(f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                return None

def extract_metadata(pdf_path):
    try:
        with open(pdf_path, 'rb') as f:
            reader = pypdf.PdfReader(f)
            text = ""
            for page in reader.pages:
                page_text = (page.extract_text() or "").strip()
                if page_text:
                    text += page_text + "\n"
                if len(text) > 8000:
                    break
            text = text.strip()[:8000]
    except Exception as e:
        print(f"Error reading PDF {pdf_path}: {e}")
        return {}

    prompt = f"""
    Extract the following metadata from the provided academic paper text as a valid JSON object. 
    Only output the JSON, nothing else. Use defaults if info is missing (e.g., year=2023, country="Unknown", language="en").
    
    Required fields:
    - "title": The full title of the paper (string)
    - "summary": A concise summary or abstract (string, max 200 words)
    - "tags": Array of 3-5 relevant keywords/tags (array of strings)
    - "year": Publication year as integer
    - "organization": Author affiliation/university/org (string)
    - "country": Country of the organization (string)
    - "language": Primary language (string, e.g., "en")
    
    Text: {text}
    """

    content = get_ai_response(prompt)
    if not content:
        return {}
    
    try:
        json_start = content.find('{')
        json_end = content.rfind('}') + 1
        if json_start == -1 or json_end <= json_start:
            raise ValueError("No valid JSON")
        json_str = content[json_start:json_end]
        metadata = json.loads(json_str)
    except Exception as e:
        print(f"Error in JSON for {pdf_path}: {e}")
        metadata = {}
    
    metadata['tags'] = ",".join(metadata.get('tags', []))
    metadata['pdf_path'] = os.path.basename(pdf_path)
    arxiv_id = os.path.basename(pdf_path)[:-4]  
    if 'v' in arxiv_id:
        arxiv_id = arxiv_id.split('v')[0]  
    metadata['original_link'] = f"https://arxiv.org/abs/{arxiv_id}"    
    return metadata

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

processed = 0
inserted = 0
for pdf_file in os.listdir(PDF_DIR):
    if pdf_file.endswith('.pdf'):
        pdf_path = os.path.join(PDF_DIR, pdf_file)
        metadata = extract_metadata(pdf_path)
        
        if not metadata or 'title' not in metadata:
            print(f"Skipping {pdf_file} due to failed metadata extraction.")
            continue

        cursor.execute("SELECT id FROM publications WHERE pdf_path = ?", (metadata['pdf_path'],))
        if cursor.fetchone():
            print(f"Skipping duplicate {pdf_file} (already in DB).")
            continue
        
        cursor.execute('''
            INSERT OR IGNORE INTO publications (title, summary, tags, year, organization, country, language, pdf_path, original_link)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            metadata.get('title', ''),
            metadata.get('summary', ''),
            metadata.get('tags', ''),
            metadata.get('year', 0),
            metadata.get('organization', ''),
            metadata.get('country', ''),
            metadata.get('language', 'en'),
            metadata['pdf_path'],
            metadata['original_link']
        ))
        if cursor.rowcount > 0:
            inserted += 1
        processed += 1
        print(f"Processed {pdf_file}: {metadata.get('title', 'No title')[:50]}...")
        
        time.sleep(1)  

conn.commit()
conn.close()
print(f"Extraction complete. Processed {processed} PDFs, inserted {inserted} new entries.")