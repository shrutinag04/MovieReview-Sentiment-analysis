import streamlit as st
import google.generativeai as genai
from google.generativeai.types import GenerationConfig
import os
import enum
from google.api_core import retry

# --- Configure Retry Logic ---
is_retriable = lambda e: (isinstance(e, genai.errors.APIError) and e.code in {429, 503})
genai.GenerativeModel.generate_content = retry.Retry(predicate=is_retriable)(genai.GenerativeModel.generate_content)

# --- Set up Google GenAI ---
key = st.secrets.get("GOOGLE_API_KEY")
if not key:
    st.error("Please set the GOOGLE_API_KEY in Streamlit secrets.")
    st.stop()

genai.configure(api_key=key)
model = genai.GenerativeModel('gemini-2.0-flash')

# --- Define Sentiment Enum ---
class Sentiment(enum.Enum):
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"

# --- Streamlit App UI ---
st.title("🎬 Movie Review Sentiment Classifier")

review_text = st.text_area("Enter a movie review:", 
    "Her is a disturbing study revealing the direction humanity is headed if AI is allowed to keep evolving, unchecked. I wish there were more movies like this masterpiece."
)

if st.button("Classify Sentiment"):
    if review_text:
        zero_shot_prompt = f"""Classify movie reviews as POSITIVE, NEUTRAL or NEGATIVE.
Review: "{review_text}"
Sentiment:"""

        try:
            response = model.generate_content(
                contents=zero_shot_prompt,
                generation_config=GenerationConfig(
                    temperature=0.3  # More consistent output
                )
            )

            sentiment_text = response.text.strip().upper()
            # Normalize and check match
            if sentiment_text in Sentiment.__members__:
                sentiment = Sentiment[sentiment_text]
                st.subheader("Sentiment:")
                st.write(f"The sentiment of the review is: **{sentiment.name}**")
            else:
                st.warning(f"🤔 Unexpected response: {sentiment_text}")

        except Exception as e:
            st.error(f"❌ An error occurred: {e}")
    else:
        st.warning("⚠️ Please enter a movie review.")
