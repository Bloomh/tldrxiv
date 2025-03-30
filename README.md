# TLDRxiv: Your AI-powered research assistant for exploring arXiv papers

## 🚀 Overview

TLDRxiv is an interactive platform designed to enhance the academic research experience by providing AI-assisted exploration of arXiv papers. It combines the comprehensive database of arXiv with modern AI capabilities to help researchers quickly understand, analyze, and discover scientific literature.

### Key Features

- **Paper Summaries**: Get concise TLDRs of complex research papers
- **Interactive Chat**: Ask questions about papers and get AI-powered responses
- **Citation Analysis**: Explore paper citations and references with detailed metadata
- **BibTeX Citations**: Easily copy properly formatted citations for your research
- **Podcast Generation**: Convert papers to podcasts for on-the-go learning

## 🔧 Technology Stack

- **Backend**: FastAPI (Python)
- **Frontend**: HTML, Tailwind CSS, JavaScript
- **AI Integration**: Google Gemini API for chat capabilities, OpenAI API for text-to-speech
- **Data Sources**: arXiv API, Semantic Scholar API
- **Rendering**: KaTeX for LaTeX equations, Marked.js for Markdown

## 🛠️ Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/Bloomh/tldrxiv.git
   cd tldrxiv
   ```

2. **Set up a virtual environment**

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.template .env
   ```
   Edit the `.env` file and add your API keys and configuration settings.

## 🚀 Running the Application

```bash
python main.py
```

The application will be available at http://localhost:8000

## 📊 Project Structure

```
tldrxiv/
├── main.py                # FastAPI application entry point
├── utils/                 # Utility functions
│   ├── arxiv_utils.py     # arXiv API integration
│   ├── sem_scholar_utils.py  # Semantic Scholar API integration
│   └── gemini_utils.py    # Google Gemini API integration
├── templates/             # HTML templates
│   ├── home.html          # Homepage template
│   ├── paper.html         # Paper view template
│   └── components/        # Reusable UI components
├── static/                # Static assets
│   ├── css/               # CSS files
│   ├── js/                # JavaScript files
│   └── images/            # Image assets
└── requirements.txt       # Python dependencies
```
