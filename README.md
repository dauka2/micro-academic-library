# Micro Academic Library

This repository implements a simple micro academic library as per the test task. It downloads scientific publications from arXiv, extracts metadata using OpenAI's API, stores the data in an SQLite database, and serves it via a basic Flask web app with pagination (20 publications per page).

## Project Structure

- `app.py`: The main Flask application to serve the web page.
- `index.html`: HTML template for rendering publications (located in a `templates/` folder; create it if missing).
- `requirements.txt`: List of Python dependencies.
- `database/dbdb`: The SQLite database file (included in the repo after running scripts).
- `database/pdf/`: Folder for downloaded PDF files (not committed to GitHub due to size; generated locally).
- `scripts/`: Folder containing helper scripts (move the following files here if not already):
  - `create_db.py`: Creates the SQLite database schema.
  - `download_pdfs.py`: Downloads 100 PDFs from arXiv based on a search query (e.g., "fault tolerance" in CS category).
  - `extract_data.py`: Extracts metadata from PDFs using OpenAI and inserts into the database.
- `.env`: Environment file for API keys (not committed; see setup below).
- `README.md`: This file.

**Note:** The `database/pdf/` folder may contain up to 100 PDFs after running the download script. Do not commit large binary files to GitHub; add `database/pdf/` to `.gitignore`.

## Prerequisites

- Python 3.8+ installed.
- An OpenAI API key (sign up at [https://console.groq.com] if needed).

## Setup Instructions

1. **Clone the Repository:**
   ```
   git clone https://github.com/dauka2/micro-academic-library.git
   cd micro-academic-library
   ```

2. **Install Dependencies:**
   Create a virtual environment (optional but recommended) and install packages:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Set Up Environment Variables:**
   Create a `.env` file in the root directory with your OpenAI API key:
   ```
   API_KEY=your-openai-api-key-here
   ```
   **Important:** Do not commit `.env` to GitHub. Add it to `.gitignore`.

4. **Prepare the Database and Data:**
   Run the scripts in order (assuming they are in `scripts/`; adjust paths if needed):
   - Create the database:
     ```
     python scripts/create_db.py
     ```
   - Download PDFs (fetches ~100 from arXiv; may take time):
     ```
     python scripts/download_pdfs.py
     ```
   - Extract metadata and populate the database (uses OpenAI; ensure API key is set):
     ```
     python scripts/extract_data.py
     ```

## Running the App

1. Start the Flask server:
   ```
   python app.py
   ```

2. Open your browser and visit `http://127.0.0.1:5000/` to view the publications.
   - Publications are paginated (20 per page).
   - Click on page numbers to navigate.
   - Each entry shows metadata, a link to the local PDF, and the original arXiv link.

## Troubleshooting

- **Database Not Found:** Ensure `database/dbdb` exists after running `create_db.py`.
- **No Publications:** Run `download_pdfs.py` and `extract_data.py` first. Check console output for errors.
- **API Errors in extract_data.py:** Verify your OpenAI API key in `.env` and internet connection. Use a model like `gpt-4o-mini` for lower costs.
- **PDF Serving Issues:** Ensure `database/pdf/` contains the files and paths are relative.
- **Duplicates:** The DB has a unique constraint on title to prevent duplicates.

## Customization

- Change the arXiv query in `download_pdfs.py` to fetch different papers (e.g., modify `query = 'cat:cs.* AND all:"fault tolerance"'`).
- Adjust pagination in `app.py` if needed.
- For production, use a WSGI server like Gunicorn instead of `debug=True`.

