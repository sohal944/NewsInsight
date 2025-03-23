# 📰 NewsInsight - AI-Powered News Summarizer & TTS  

link:-https://huggingface.co/spaces/sohal944/News-Insights (deploment)

![image](https://github.com/user-attachments/assets/95bff5a1-5c42-476d-bfca-9c45541197fb)

NewsInsight is an AI-driven application that scrapes news articles, extracts key insights, generates concise summaries, and converts them into speech using Text-to-Speech (TTS).  

## 🚀 Features  
- **Web Scraping**: Extracts news content from multiple sources.  
- **Smart Summarization**: Filters irrelevant content and provides meaningful summaries.  
- **Text-to-Speech (TTS)**: Converts news summaries into speech output (MP3).  
- **Error Handling**: Skips blocked articles and handles inaccessible pages gracefully.  

## 🏗 Tech Stack  
- **Python** 🐍  
- **Requests** - For fetching web pages  
- **BeautifulSoup** - For HTML parsing  
- **NLTK** - For text processing  
- **Gradio** - For UI (Optional)
- Check Requirements.txt file

## 📌 Installation  

Clone the repository:  
```bash
git clone https://github.com/sohal944/NewsInsight.git
cd NewsInsight


python -m venv .venv
source .venv/bin/activate  # Mac/Linux
.\.venv\Scripts\activate   # Windows

pip install -r requirements.txt

import nltk
nltk.download('punkt')

python app.py


