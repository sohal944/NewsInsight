import requests
from bs4 import BeautifulSoup
import spacy
from rake_nltk import Rake
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from gtts import gTTS
import os
from deep_translator import GoogleTranslator

# Ensure the spaCy model is installed
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    os.system("python -m spacy download en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

# Ensure NLTK resources are available
nltk.download('vader_lexicon')
nltk.download('stopwords')  
nltk.download('punkt_tab')

# Explicitly set the NLTK data path
nltk.data.path.append(os.path.join(os.getcwd(), ".venv", "nltk_data"))

# Test if it's accessible
nltk.download('punkt_tab', download_dir=os.path.join(os.getcwd(), ".venv", "nltk_data"))


# Initialize tools
rake = Rake()
sia = SentimentIntensityAnalyzer()



import requests
from bs4 import BeautifulSoup
import re
import json

def scrape_article(url, max_words=100):
    """Extracts content from a news article with improved filtering and multiple extraction methods."""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=20)

        # Check if request was blocked or redirected
        if response.status_code != 200 or "Reference #" in response.text or "errors.edgesuite.net" in response.url:
            print(f"❌ Access blocked or article unavailable: {url}")
            return None

        soup = BeautifulSoup(response.text, "html.parser")

        # 🔹 1. Try extracting from <article>
        article_body = soup.find("article") or soup.find("section") or soup.find("div", class_="article-content")
        if article_body:
            paragraphs = article_body.find_all("p")
        else:
            paragraphs = soup.find_all("p")  # Fallback: extract from all <p> tags

        # 🔹 2. Filter irrelevant text (ads, navigation, copyright notices)
        filtered_paragraphs = [
            p.text.strip() for p in paragraphs
            if len(p.text.split()) > 5  # Ignore very short lines
            and not re.search(r"©|copyright|subscribe|advertisement|click here|terms of service", p.text, re.I)
            and not p.text.strip().isdigit()  # Ignore single number paragraphs (e.g., "1")
        ]

        # 🔹 3. Try extracting JSON-LD structured data (if available)
        if not filtered_paragraphs:
            script_tag = soup.find("script", {"type": "application/ld+json"})
            if script_tag:
                try:
                    json_data = json.loads(script_tag.string)
                    if "articleBody" in json_data:
                        filtered_paragraphs = [json_data["articleBody"]]
                except json.JSONDecodeError:
                    pass

        # 🔹 4. Fallback: Use meta description if no content found
        if not filtered_paragraphs:
            meta_desc = soup.find("meta", {"name": "description"})
            if meta_desc and meta_desc.get("content"):
                filtered_paragraphs = [meta_desc["content"]]

        # 🔹 5. Generate summary from first 3 meaningful paragraphs
        summary = " ".join(filtered_paragraphs[:3])

        # 🔹 6. Limit the summary length
        words = summary.split()
        if len(words) > max_words:
            summary = " ".join(words[:max_words]) + "..."

        return summary if summary else "⚠️ Could not extract content."

    except Exception as e:
        print(f"⚠️ Error while scraping article: {e}")
        return None





def fetch_news(company, num_articles=25):
    """Scrapes news articles, adds sentiment analysis, and extracts topics."""
    search_url = f"https://www.bing.com/news/search?q={company}&form=QBNH"
    headers = {"User-Agent": "Mozilla/5.0"}

    response = requests.get(search_url, headers=headers)
    if response.status_code != 200:
        return {"error": "Failed to fetch news"}

    soup = BeautifulSoup(response.text, "html.parser")
    articles = []

    for idx, item in enumerate(soup.find_all("a", class_="title"), start=1):
        if idx > num_articles:
            break

        title = item.text
        link = item["href"]
        summary = scrape_article(link)

        if summary and "⚠️ Could not extract content." not in summary:  # Ensure valid summary
            sentiment = analyze_sentiment(summary)  # Apply sentiment analysis
            topics = extract_topics_combined(summary)  # Extract topics
            articles.append({
                "Title": title, 
                "Summary": summary, 
                "Sentiment": sentiment, 
                "Topics": topics,  # Include topics
                "URL": link
            })
        else:
            print(f"⚠️ Skipping article: {title} (Failed to extract summary)")

    return articles


def extract_topics(text):
    """Extracts key topics using Named Entity Recognition (NER)."""
    doc = nlp(text)
    topics = [ent.text for ent in doc.ents if ent.label_ in {"ORG", "GPE", "PRODUCT", "EVENT"}]
    return list(set(topics))  # Return unique topics


def extract_keywords(text):
    """Extracts key phrases using RAKE."""
    rake.extract_keywords_from_text(text)
    return rake.get_ranked_phrases()[:5]  # Return top 5 keywords


def extract_topics_combined(text):
    """Combines NER and RAKE for better topic extraction."""
    topics = extract_topics(text)  # NER
    keywords = extract_keywords(text)  # RAKE
    return list(set(topics + keywords))  # Merge unique topics


def analyze_sentiment(text):
    """Returns sentiment as Positive, Negative, or Neutral."""
    scores = sia.polarity_scores(text)
    compound = scores['compound']  # Main sentiment score

    if compound >= 0.05:
        return "Positive"
    elif compound <= -0.05:
        return "Negative"
    else:
        return "Neutral"


from textblob import TextBlob

def get_sentiment(text):
    """Extracts sentiment polarity score and assigns a sentiment label."""
    polarity = TextBlob(text).sentiment.polarity
    if polarity > 0.3:
        return "Positive", polarity
    elif polarity < -0.3:
        return "Negative", polarity
    else:
        return "Neutral", polarity

def compare_sentiments(articles):
    """Analyzes sentiment distribution & key coverage differences."""
    sentiment_count = {"Positive": 0, "Negative": 0, "Neutral": 0}
    coverage_differences = []

    for article in articles:
        sentiment, polarity = get_sentiment(article["Summary"])
        article["Sentiment"] = sentiment
        article["Polarity"] = polarity
        sentiment_count[sentiment] += 1

    # Compare every pair of articles
    for i in range(len(articles)):
        for j in range(i + 1, len(articles)):
            topics_i = set(articles[i]["Topics"])
            topics_j = set(articles[j]["Topics"])
            common_topics = topics_i & topics_j  # Shared topics
            unique_i = topics_i - topics_j
            unique_j = topics_j - topics_i

            # Sentiment shift calculation
            polarity_diff = abs(articles[i]["Polarity"] - articles[j]["Polarity"])
            sentiment_shift = articles[i]["Sentiment"] != articles[j]["Sentiment"]

            # Formulating Comparison
            comparison = f"🔍 **Article {i+1}** focuses on **{', '.join(unique_i) or 'similar topics'}**, " \
                         f"while **Article {j+1}** covers **{', '.join(unique_j) or 'similar topics'}**."

            # Generating Impact
            impact = "⚖️ **Impact Analysis:** "

            if common_topics and sentiment_shift:
                # If articles cover the same topics but have different sentiments
                if polarity_diff > 0.6:
                    impact += f"🚨 **Contrasting views** on {', '.join(common_topics)} may cause **polarized opinions**."
                else:
                    impact += f"🧐 **Mild sentiment difference** on {', '.join(common_topics)} could provide a **balanced view**."

            elif common_topics and not sentiment_shift:
                # If articles have similar topics and similar sentiment
                impact += f"✅ **Reinforces a shared perspective** on {', '.join(common_topics)}."

            else:
                # If topics differ, but sentiment is the same or different
                if sentiment_shift:
                    impact += "🔀 **Diverse coverage with opposing emotions**—readers may interpret the events differently."
                else:
                    impact += "🌍 **Expands coverage scope**—offers multiple angles on different aspects of the issue."

            coverage_differences.append({
                "Comparison": comparison,
                "Impact": impact
            })

    return {"Sentiment Distribution": sentiment_count, "Coverage Differences": coverage_differences}


import spacy

# Load the English NLP model for lemmatization
nlp = spacy.load("en_core_web_sm")

def normalize_topics(topics):
    """Normalize topics by converting to lowercase and lemmatizing."""
    normalized = []
    for topic in topics:
        doc = nlp(topic.lower())  # Convert to lowercase
        normalized.append(" ".join([token.lemma_ for token in doc]))  # Lemmatize the topic
    return normalized

def analyze_topic_overlap(articles):
    """Finds common & unique topics between articles."""
    all_topics = [set(normalize_topics(article["Topics"])) for article in articles]
    from collections import Counter

# Flatten all topics
    all_words = [word for topic_set in all_topics for word in topic_set]

# Count occurrences
    word_counts = Counter(all_words)

# Find words appearing in at least 3 sets
    common_topics = {word for word, count in word_counts.items() if count >= 2}

    print("Common Topics:", common_topics)





    # Calculate unique topics by subtracting common topics from each article's topics
    unique_topics = [
        {"Article": i + 1, "Unique Topics": list(topics - common_topics)}
        for i, topics in enumerate(all_topics)
    ]

    return {"Common Topics": list(common_topics), "Unique Topics": unique_topics}



def final_sentiment_summary(sentiment_data):
    """Generates a final conclusion based on sentiment distribution."""
    if sentiment_data["Sentiment Distribution"]["Positive"] > sentiment_data["Sentiment Distribution"]["Negative"]:
        return "Overall, the news sentiment is positive. Potential stock growth expected."
    elif sentiment_data["Sentiment Distribution"]["Negative"] > sentiment_data["Sentiment Distribution"]["Positive"]:
        return "Overall, the news sentiment is negative. Investors may be cautious."
    else:
        return "News coverage is balanced, with both positive and negative views."


def translate_text(text, target_lang="hi"):
    """Translates text to the target language."""
    return GoogleTranslator(source="auto", target=target_lang).translate(text)


def generate_tts(text, output_file="output.mp3"):
    """Converts text to Hindi speech."""
    hindi_text = translate_text(text)
    tts = gTTS(hindi_text, lang="hi")
    tts.save(output_file)
    return output_file  # Return file path


def fetch_news_with_analysis(company, num_articles=25):
    """Fetches news, performs sentiment & topic analysis, and generates TTS."""
    articles = fetch_news(company, num_articles)

    if "error" in articles:
        return articles  # Return error if news fetch fails

    # Perform sentiment and topic comparison
    sentiment_analysis = compare_sentiments(articles)
    topic_overlap = analyze_topic_overlap(articles)
    final_sentiment = final_sentiment_summary(sentiment_analysis)

    # Convert summary to Hindi speech
    audio_file = generate_tts(final_sentiment)

    return {
        "Company": company,
        "Articles": articles,
        "Comparative Sentiment Score": sentiment_analysis,
        "Topic Overlap": topic_overlap,
        "Final Sentiment Analysis": final_sentiment,
        "Audio": audio_file
    }