# RAG Evaluation Workbench

A Streamlit app for comparing retrieval methods and inspecting grounded answers.
Run the included 40-question benchmark locally, or upload a searchable PDF to try
document Q&A. Every answer is instructed to cite the passages it used.

## Run locally

```sh
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Set `OPENAI_API_KEY` in your environment to enable optional generation.
Enabling live generation sends the question and retrieved passages to OpenAI.
A full live benchmark can make up to 80 model requests.

## What the benchmark measures

- **Retrieval recall@k** is the fraction of expected passage IDs present in the
  top k on answerable questions.
- **Citation precision** is the fraction of emitted passage IDs that are both
  expected and actually retrieved. Rows with zero citations are excluded.
- **Correct or abstained** checks for the expected phrase on answerable
  questions and exact abstention on the ten unanswerable questions.
- **Retrieval latency** measures in-memory search after index construction.

The benchmark uses a fictional makerspace handbook and ten independent station
records. Several questions share the same evidence. Phrase matching is a simple
check and can misclassify paraphrases or contradictory answers. Inspect the
downloadable per-question results for failure analysis. API errors are counted
separately and excluded from answer metric averages.

Both retrieval methods are local lexical baselines. The app extracts selectable
PDF text and splits it into overlapping chunks within each page. Scanned PDFs
require OCR before upload.
