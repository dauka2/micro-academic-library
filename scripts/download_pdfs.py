import requests
import xml.etree.ElementTree as ET
import os

PDF_DIR = "database/pdf"
os.makedirs(PDF_DIR, exist_ok=True)

query = 'cat:cs.* AND all:"fault tolerance"'
url = f"http://export.arxiv.org/api/query?search_query={query}&start=0&max_results=100&sortBy=submittedDate&sortOrder=descending"

try:
    response = requests.get(url)
    response.raise_for_status()
    root = ET.fromstring(response.text)
    if len(root.findall('{http://www.w3.org/2005/Atom}entry')) == 0:
        print("No entries found in arXiv response.")
        exit(1)
except Exception as e:
    print(f"Failed to fetch arXiv results: {e}")
    exit(1)

downloaded_count = 0
for entry in root.findall('{http://www.w3.org/2005/Atom}entry'):
    title = entry.find('{http://www.w3.org/2005/Atom}title').text.strip()
    arxiv_id = entry.find('{http://www.w3.org/2005/Atom}id').text.split('/')[-1]
    pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
    pdf_path = os.path.join(PDF_DIR, f"{arxiv_id}.pdf")
    
    try:
        pdf_resp = requests.get(pdf_url, timeout=30)
        pdf_resp.raise_for_status()
        with open(pdf_path, 'wb') as f:
            f.write(pdf_resp.content)
        print(f"Downloaded: {title} to {pdf_path}")
        downloaded_count += 1
    except Exception as e:
        print(f"Error downloading {pdf_url}: {e}")

print(f"Downloaded {downloaded_count} PDFs.")