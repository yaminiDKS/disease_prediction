import os
import numpy as np
import pandas as pd
import streamlit as st
from groq import Groq

client = Groq(api_key=st.secrets["GROQ_API_KEY"])


# --------------------------
# Convert row to text
# --------------------------
def row_to_text(row, city):
    return (
        f"City: {city}, "
        f"Name: {row.get('Name','')}, "
        f"Address: {row.get('Address','')}, "
        f"Phone: {row.get('Justdial Phone','')}, "
        f"Rating: {row.get('Rating','')}, "
        f"Reviews: {row.get('Reviews','')}"
    )


# --------------------------
# Simple bag-of-words embedding
# --------------------------
def build_vocab(texts):
    vocab = {}
    idx = 0
    for text in texts:
        for word in text.lower().split():
            if word not in vocab:
                vocab[word] = idx
                idx += 1
    return vocab


def text_to_vec(text, vocab):
    vec = np.zeros(len(vocab))
    for word in text.lower().split():
        if word in vocab:
            vec[vocab[word]] += 1
    return vec


# --------------------------
# Load data
# --------------------------
@st.cache_data
def load_data():
    data_dir = "data"
    csv_files = [f for f in os.listdir(data_dir) if f.endswith(".csv")]

    all_texts = []

    for csv in csv_files:
        city = os.path.splitext(csv)[0]
        df = pd.read_csv(os.path.join(data_dir, csv))
        texts = df.apply(lambda r: row_to_text(r, city), axis=1).tolist()
        all_texts.extend(texts)

    vocab = build_vocab(all_texts)
    embeddings = np.array([text_to_vec(t, vocab) for t in all_texts])

    return all_texts, embeddings, vocab


# --------------------------
# Search
# --------------------------
def search(query, embeddings, texts, vocab, top_k):
    q_vec = text_to_vec(query, vocab)

    sims = np.dot(embeddings, q_vec)

    top_idx = np.argsort(sims)[-top_k:][::-1]
    return [texts[i] for i in top_idx]


# --------------------------
# UI
# --------------------------
st.title("Vet Finder")

texts, embeddings, vocab = load_data()

query = st.text_input("Search veterinarians")
top_k = st.slider("Top results", 1, 10, 3)

if st.button("Search"):

    results = search(query, embeddings, texts, vocab, top_k)

    context = "\n".join(results)

    prompt = f"""
Find best veterinarians.

Records:
{context}

User query:
{query}

Give bullet points with contact details.
"""

    completion = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[{"role": "user", "content": prompt}],
        stream=True,
    )

    placeholder = st.empty()
    text = ""

    for chunk in completion:
        delta = chunk.choices[0].delta.content
        if delta:
            text += delta
            placeholder.markdown(text)

    st.subheader("Raw Matches")
    for r in results:
        st.write(r)
