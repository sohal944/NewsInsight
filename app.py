import gradio as gr
from utils import fetch_news_with_analysis

def gradio_interface(company):
    """Fetch news and return structured output for Gradio with a playable audio file."""
    news_data = fetch_news_with_analysis(company)

    # If fetching news fails, return an error message
    if "error" in news_data:
        return "⚠️ Failed to fetch news. Try again.", None, None, None, None, None

    # Extract structured data
    company_name = news_data.get("Company", "N/A")
    articles = news_data.get("Articles", [])
    sentiment_score = news_data.get("Comparative Sentiment Score", {})
    coverage_differences = sentiment_score.get("Coverage Differences", [])  
    topic_overlap = news_data.get("Topic Overlap", {})
    final_sentiment = news_data.get("Final Sentiment Analysis", "N/A")
    audio_file = news_data.get("Audio", None)

    # Format articles neatly
    article_text = "\n\n".join([ 
        f"📌 **{idx + 1}. {article['Title']}**\n\n"
        f"🔹 **Summary:** {article['Summary']}\n\n"
        f"💡 **Sentiment:** {article['Sentiment']}\n\n"
        f"🏷 **Topics:** {', '.join(article['Topics'])}\n\n"
        f"🔗 [Read More]({article['URL']})\n\n"
        "------------------------------"
        for idx, article in enumerate(articles)
    ])

    # Format Sentiment Distribution
    sentiment_distribution = sentiment_score.get("Sentiment Distribution", {})
    sentiment_text = "**📊 Sentiment Distribution**\n\n"
    sentiment_text += f"✅ **Positive News:** {sentiment_distribution.get('Positive', 0)} articles\n\n"
    sentiment_text += f"⚠️ **Neutral News:** {sentiment_distribution.get('Neutral', 0)} articles\n\n"
    sentiment_text += f"❌ **Negative News:** {sentiment_distribution.get('Negative', 0)} articles\n\n"

    # Format Coverage Differences
    coverage_text = "**📊 Coverage Differences**\n\n"
    if coverage_differences:
        for diff in coverage_differences:
            coverage_text += f"🔍 **Comparison:**\n\n{diff['Comparison']}\n\n"
            coverage_text += f"⚖️ **Impact:** {diff['Impact']}\n\n"
            coverage_text += "------------------------------\n\n"
    else:
        coverage_text += "No major differences found."

    # Format Topic Overlap
    topic_text = "**🔍 Topic Overlap**\n\n"
    common_topics = topic_overlap.get("Common Topics", [])
    unique_topics = topic_overlap.get("Unique Topics", [])

    # Add common topics
    topic_text += f"📌 **Common Topics Across Articles:** {', '.join(common_topics) if common_topics else 'None'}\n\n"
    topic_text += "------------------------------\n\n"

    # Add unique topics per article
    for topic in unique_topics:
        topic_text += f"📖 **Article {topic['Article']} Unique Topics:**\n\n{', '.join(topic['Unique Topics'])}\n\n"
        topic_text += "------------------------------\n\n"

    return (
        f"## 🏢 **Company: {company_name}**\n\n### 📰 **Extracted News Articles**\n\n{article_text}",
        sentiment_text,  
        coverage_text,  
        topic_text,  
        f"### 🏁 **Final Analysis**\n\n{final_sentiment}",
        audio_file  
    )

# Gradio UI with custom heading and styles
with gr.Blocks() as iface:
    # Custom HTML for the heading and some styling
    gr.HTML("""
    <style>
        body {
            font-family: 'Arial', sans-serif;
            background-color: #4169E1;  /* Royal Blue */
            color: #fff;  /* White text */
        }
        .gradio-container {
            max-width: 900px;
            margin: 0 auto;
        }
        .gradio-title {
            font-size: 5rem;
            font-weight: bold;
            color: #fff;  /* White text */
            text-align: center;
            padding: 20px;
            background-color: #003366;  /* Dark Blue background */
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);  /* Optional: adds a subtle shadow */
        }
        .gradio-footer {
            font-size: 0.8rem;
            color: #888;
            text-align: center;
            margin-top: 20px;
        }
    </style>
    <div class="gradio-title">
            
        <h1>NewsInsight</h1>
        
    </div>
    """)

    company_input = gr.Textbox(label="Enter Company Name", placeholder="Tesla")
    
    with gr.Column():
        output_news = gr.Markdown(label="🏢 Extracted News Data")
        output_sentiment = gr.Markdown(label="📊 Sentiment Distribution")
        output_coverage = gr.Markdown(label="📊 Coverage Differences")
        output_topics = gr.Markdown(label="🔍 Topic Overlap")
        output_analysis = gr.Markdown(label="🏁 Final Sentiment Analysis")
        output_audio = gr.Audio(label="📢 Listen to Summary")

    company_input.submit(gradio_interface, inputs=company_input, outputs=[
        output_news, output_sentiment, output_coverage, output_topics, output_analysis, output_audio
    ])

iface.launch()

# from utils import fetch_news_with_analysis

# data= fetch_news_with_analysis("Tesla")
# print(data)