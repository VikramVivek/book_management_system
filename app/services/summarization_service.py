import asyncio
import logging
from functools import partial
from typing import List

from transformers import pipeline

# Set up logger
logger = logging.getLogger("app.summarization_service")

# Initialize the summarization pipeline using a smaller model
summarizer = None


def get_summarizer():
    """
    Initialize the summarization pipeline using a specified model.

    Returns:
        transformers.pipeline: A pipeline object for text summarization.
    """
    logger.info("Initializing summarizer model")
    return pipeline("summarization", model="t5-small")


async def generate_summary_for_content(content: str) -> str:
    """
    Generate a summary for the book content with added context.

    Args:
        content (str): The content of the book to be summarized.

    Returns:
        str: The generated summary of the book content.
    """
    logger.info("Generating summary for book content")
    summarizer = get_summarizer()

    # Add context to indicate that this is a book content summary
    context = "Summarize the following book content:"
    input_text = f"{context} {content}"

    loop = asyncio.get_event_loop()
    try:
        summary = await loop.run_in_executor(
            None,
            partial(
                summarizer, input_text, max_length=150, min_length=40, do_sample=False
            ),
        )
        logger.info("Summary generation for content successful")
        return summary[0]["summary_text"]
    except Exception as e:
        logger.error(f"Error generating summary for content: {e}")
        raise


def generate_summary_for_reviews(reviews: List[str]) -> str:
    """
    Generate a summary for a list of reviews with added context.

    Args:
        reviews (List[str]): A list of review texts to be summarized.

    Returns:
        str: The generated summary of the reviews.
    """
    logger.info("Generating summary for reviews")
    summarizer = get_summarizer()

    # Combine reviews into one text and add context
    combined_reviews = " ".join(reviews)
    context = (
        "Summarize the following book reviews: It is in the format "
        "User Review: some_review_text || User Rating: number_out_of_5"
    )
    input_text = f"{context} {combined_reviews}"

    try:
        summary = summarizer(input_text, max_length=150, min_length=40, do_sample=False)
        logger.info("Summary generation for reviews successful")
        return summary[0]["summary_text"]
    except Exception as e:
        logger.error(f"Error generating summary for reviews: {e}")
        raise
