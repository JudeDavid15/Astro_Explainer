#  Astro Event Explainer

An agentic astronomy Q&A app. A LangGraph router decides whether each question should be answered from a RAG index over an astronomy textbook, from a live NASA API call, or with a clarifying question.

## How it works

The app is a LangGraph `StateGraph` with a **classify → route** pattern:

```text
                    ┌─────────────┐
                    │  classify   │
                    └──────┬──────┘
                           │
         ┌─────────────────┼─────────────────┐
         │                 │                 │
         ▼                 ▼                 ▼
   ┌───────────┐    ┌────────────┐    ┌────────────┐
   │ retrieve  │    │  call_api  │    │  clarify   │
   │ (RAG)     │    │ (NASA APOD)│    │ (ask user) │
   └─────┬─────┘    └─────┬──────┘    └─────┬──────┘
         │                │                 │
         └────────────────┴─────────────────┘
                          │
                         END
```

| Route | Used for | What happens |
|---|---|---|
| `retrieve` | Specific conceptual or factual astronomy questions ("Why do stars twinkle?") | Similarity search over ChromaDB, then an answer grounded in the retrieved passages |
| `call_api` | Requests for today's astronomy picture | Calls NASA's Astronomy Picture of the Day API through a LangChain tool |
| `clarify` | Questions too broad to answer well ("Tell me about space") | Asks the user to be more specific instead of guessing |

The classifier is a single low-temperature LLM call that returns one label, and LangGraph's conditional edges branch on it. The retrieval answer prompt is instructed to use only the retrieved context, and I checked this by swapping in an irrelevant context and confirming the model declined to answer.

**Stack:** LangGraph · LangChain · ChromaDB · Groq (`openai/gpt-oss-20b`) · Hugging Face embeddings (`all-MiniLM-L6-v2`) · FastAPI · Gradio

## Data

The knowledge base is *Astronomy 2e* from [OpenStax](https://openstax.org/details/books/astronomy-2e). The PDF was loaded with `PyPDFLoader`, cleaned (line-wrap and whitespace artifacts removed), split into chunks, embedded, and stored in ChromaDB. The finished index (about 3,800 chunks) is committed in `chroma_db/`, so you don't need the PDF to run the app.

The textbook is licensed by OpenStax under a Creative Commons Attribution license. The index is derived from it, so please credit OpenStax if you reuse it.

## Repository layout

```text
.
├── app.py             # Entrypoint: FastAPI app with the Gradio UI mounted at /
├── src/
│   ├── graph.py       # LangGraph StateGraph wiring
│   ├── nodes.py       # classify / retrieve / call_api / clarify nodes
│   ├── state.py       # AgentState definition
│   └── tools.py       # NASA APOD tool
├── chroma_db/         # Prebuilt vector index (read-only at runtime)
├── requirements.txt
├── .env.example
└── README.md
```

## Run locally

```bash
git clone https://github.com/JudeDavid15/astro-explainer.git
cd astro-explainer
python -m venv venv
venv\Scripts\activate 
pip install -r requirements.txt
cp .env.example .env         
python app.py
```

Then open <http://127.0.0.1:7860>. The interactive API docs are at `/docs`.

`.env`:

```dotenv
GROQ_API_KEY=your_groq_api_key
NASA_API_KEY=your_nasa_api_key
```

Free keys: [Groq console](https://console.groq.com) and [api.nasa.gov](https://api.nasa.gov).

## API

The same graph is exposed as a JSON endpoint:

```bash
curl -X POST http://127.0.0.1:7860/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "Why do stars twinkle?"}'
```

```json
{
  "question": "Why do stars twinkle?",
  "route": "retrieve",
  "answer": "Stars appear to twinkle because..."
}
```

## Known limitations

- The router is a single LLM call, and it sometimes sends vague questions to `retrieve` instead of `clarify`.
- NASA's APOD only returns the current picture, so there is no "what's visible tonight" capability.
- NASA's image URLs have been returning a placeholder logo for some requests, so the APOD route returns the explanation text with a link rather than relying on the embedded image.
- Retrieval quality depends on PDF extraction: sidebar boxes and figure captions occasionally bleed into chunks.

## Roadmap

A multimodal version: image-based retrieval over astronomy imagery using CLIP-style embeddings, so a user can query with a photo or a description.

## License

The original source code in this repository is licensed under the [MIT License](LICENSE).

See the [`LICENSE`](LICENSE) file for the full license text.