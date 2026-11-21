import json
import os
from pathlib import Path
from time import perf_counter

import streamlit as st
from openai import OpenAI
from pypdf import PdfReader

from workbench import Index, Passage, answer, grade

st.set_page_config(page_title="RAG Evaluation Workbench", layout="wide")
st.title("RAG Evaluation Workbench")
st.caption("Ask questions with citations and inspect what each retriever gets right.")
demo = json.loads(Path(__file__).with_name("demo.json").read_text(encoding="utf-8"))
methods = ["Keyword overlap", "TF-IDF cosine"]

with st.sidebar:
    st.header("Configuration")
    model = st.text_input("OpenAI model", "gpt-4.1-mini")
    k = st.slider("Passages per question", 1, 6, 3)
    api_key = os.getenv("OPENAI_API_KEY")
    st.caption("Live answers use OPENAI_API_KEY. Retrieval runs locally without a key.")

ask_tab, evaluate_tab = st.tabs(["Ask a question", "Evaluate retrieval"])

with ask_tab:
    uploaded = st.file_uploader("Use your own text-based PDF", type=["pdf"])
    passages = [Passage(**item) for item in demo["passages"]]
    can_search = True
    if uploaded is not None:
        try:
            passages = []
            for page_number, page in enumerate(PdfReader(uploaded).pages, start=1):
                words = (page.extract_text() or "").split()
                for start in range(0, len(words), 200):
                    chunk = " ".join(words[max(0, start - 30):start + 200])
                    passages.append(Passage(f"P{len(passages) + 1}", f"Page {page_number}. {chunk}"))
            if not passages:
                st.warning("No selectable text found. Upload a PDF with a text layer.")
                can_search = False
        except Exception:
            st.error("Could not read this PDF. Try an unlocked, text-based file.")
            can_search = False
    else:
        st.caption("Using the included fictional makerspace handbook.")

    with st.form("ask"):
        question = st.text_input("Question", "Who can assist with the laser cutter?")
        method = st.selectbox("Retriever", methods)
        generate = st.checkbox("Generate an answer with OpenAI", disabled=not api_key)
        submit = st.form_submit_button("Search", disabled=not can_search)
    if submit and question.strip():
        retrieved = Index(passages).retrieve(question, method, k)
        if generate:
            try:
                st.subheader("Answer")
                st.text(answer(question, retrieved, OpenAI(api_key=api_key), model))
            except Exception as error:
                st.error(f"OpenAI request failed ({type(error).__name__}). Check the API key and model.")
        st.subheader("Retrieved passages")
        if not retrieved:
            st.info("No matching passages.")
        for passage in retrieved:
            st.text(f"[{passage.id}] {passage.text}")

with evaluate_tab:
    st.caption("Compare both retrievers against 40 labeled questions from the sample handbook.")
    use_model = st.checkbox("Also grade live answers", disabled=not api_key,
                            help="Runs up to 80 API requests and may incur charges.")
    if st.button("Run benchmark", type="primary"):
        index = Index([Passage(**item) for item in demo["passages"]])
        client = OpenAI(api_key=api_key) if use_model else None
        rows, summary = [], []
        progress = st.progress(0)
        for method in methods:
            start_index = len(rows)
            for case in demo["cases"]:
                start = perf_counter()
                results = index.retrieve(case["question"], method, k)
                elapsed = (perf_counter() - start) * 1000
                try:
                    generated = answer(case["question"], results, client, model) if client else None
                    error = ""
                except Exception as exc:
                    generated, error = None, type(exc).__name__
                recall, precision, correct = grade(
                    generated, results, case["expected_ids"], case["expected_phrase"]
                )
                rows.append({
                    "Retriever": method, "Question": case["question"],
                    "Answerable": bool(case["expected_ids"]),
                    "Expected": ", ".join(case["expected_ids"]),
                    "Retrieved": ", ".join(p.id for p in results),
                    "Recall": recall, "Citation precision": precision,
                    "Correct or abstained": correct, "Retrieval ms": round(elapsed, 3),
                    "Answer": generated or "", "API error": error,
                })
                progress.progress(len(rows) / (len(methods) * len(demo["cases"])))
            group = rows[start_index:]
            metrics = ["Recall", "Retrieval ms"]
            if client:
                metrics.extend(["Citation precision", "Correct or abstained"])
            result = {"Retriever": method, "API errors": sum(bool(row["API error"]) for row in group)}
            for metric in metrics:
                values = [row[metric] for row in group if row[metric] is not None]
                result[f"Mean {metric}"] = round(sum(values) / len(values), 4) if values else None
            summary.append(result)
        st.session_state["benchmark"] = (summary, rows)
    if "benchmark" in st.session_state:
        summary, rows = st.session_state["benchmark"]
        st.dataframe(summary, hide_index=True)
        st.dataframe(rows, hide_index=True)
        st.download_button("Download results", json.dumps(rows, indent=2),
                           file_name="benchmark-results.json", mime="application/json")
