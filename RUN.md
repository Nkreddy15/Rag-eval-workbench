# Run the RAG Evaluation Workbench

You’ll need Git and Python 3.11 or newer. Use the commands for your operating system.

## macOS or Linux

```bash
git clone https://github.com/Nkreddy15/Rag-eval-workbench.git
cd Rag-eval-workbench
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m streamlit run app.py
```

## Windows PowerShell

```powershell
git clone https://github.com/Nkreddy15/Rag-eval-workbench.git
cd Rag-eval-workbench
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Open [localhost:8501](http://localhost:8501). Press `Ctrl+C` in the terminal to stop the app.

## Verify the app without an API key

1. In **Ask a question**, click **Search** with the default laser cutter question. Look for passage `[P1]`, which names the evening supervisor.
2. In **Evaluate retrieval**, click **Run benchmark**. You should see two retriever summaries and 80 results from 40 questions run against both retrievers.
3. Upload a text-based PDF and search for a fact from a known page. Check the retrieved text and page number. Scanned PDFs need OCR first.

## Enable optional OpenAI answers

Set `OPENAI_API_KEY` in the same terminal before launching Streamlit. Keep the key out of source files and Git commits.

**macOS or Linux (Bash or Zsh)**

```bash
printf 'OpenAI API key: '
IFS= read -rs OPENAI_API_KEY
printf '\n'
export OPENAI_API_KEY
.venv/bin/python -m streamlit run app.py
```

**Windows PowerShell**

```powershell
$env:OPENAI_API_KEY = (Get-Credential -UserName openai -Message 'Paste your API key in the password field').GetNetworkCredential().Password
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Select **Generate an answer with OpenAI** and run the default question. The expected answer names the evening supervisor and cites `[P1]`. Then ask how much it costs to reserve the laser cutter. The sample handbook omits prices, so the expected result is an abstention.

Live generation sends the question and retrieved passages to OpenAI. Enabling **Also grade live answers** can make up to 80 model requests and may incur charges.
