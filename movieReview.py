import streamlit as st
from google import genai
from google.genai import types
import os
import enum
from google.api_core import retry

# --- Configure Retry ---
is_retriable = lambda e: (isinstance(e, genai.errors.APIError) and e.code in {429, 503})
genai.models.Models.generate_content = retry.Retry(predicate=is_retriable)(genai.models.Models.generate_content)

# --- Set up Google GenAI ---
key = st.secrets.get("GOOGLE_API_KEY")
if not key:
    st.error("Please set the GOOGLE_API_KEY in Streamlit secrets.")
    st.stop()
client = genai.Client(api_key=key)
#genai.configure(api_key=key)
#client = genai.GenerativeModel('gemini-2.0-flash')

# --- Define Sentiment Enum ---
class Sentiment(enum.Enum):
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"

# --- Streamlit App ---
st.title("Movie Review Sentiment Classifier")

review_text = st.text_area("Enter a movie review:", "Her is a disturbing study revealing the direction humanity is headed if AI is allowed to keep evolving, unchecked. I wish there were more movies like this masterpiece.")

if st.button("Classify Sentiment"):
    if review_text:
        zero_shot_prompt = f"""Classify movie reviews as POSITIVE, NEUTRAL or NEGATIVE.
Review: "{review_text}"
Sentiment: """

        try:
            response = client.models.generate_content(
                model='gemini-2.0-flash',
                config=types.GenerateContentConfig(
                    response_mime_type="text/x.enum",
                    response_schema=Sentiment
                ),
                contents=zero_shot_prompt
            )

            
            enum_response=response.parsed
            if response.parsed in Sentiment:
                    st.subheader("Sentiment:")
                    st.write(f"The sentiment of the review is: **{response.parsed.name}**") # Use the enum member's name
        except Exception as e:
            st.error(f"An error occurred: {e}")
    else:
        st.warning("Please enter a movie review.")