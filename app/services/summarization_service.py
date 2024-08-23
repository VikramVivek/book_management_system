from typing import List

from transformers import pipeline

# Initialize the summarization pipeline using a smaller model
# summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")
summarizer = None


def get_summarizer():
    # return pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")
    return pipeline("summarization", model="t5-small")


def generate_summary_for_content(content: str) -> str:
    """Generate a summary for the book content with added context."""
    summarizer = get_summarizer()
    # Add context to indicate that this is a book content summary
    context = "Summarize the following book content:"
    input_text = f"{context} {content}"

    summary = summarizer(input_text, max_length=150, min_length=40, do_sample=False)
    return summary[0]["summary_text"]


def generate_summary_for_reviews(reviews: List[str]) -> str:
    """Generate a summary for a list of reviews with added context."""
    summarizer = get_summarizer()
    # Combine reviews into one text and add context
    combined_reviews = " ".join(reviews)
    context = "Summarize the following book reviews:"
    input_text = f"{context} {combined_reviews}"

    summary = summarizer(input_text, max_length=150, min_length=40, do_sample=False)
    return summary[0]["summary_text"]
