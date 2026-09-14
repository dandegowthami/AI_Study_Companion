# AI Tools & Usage Documentation

## 1. AI/ML Stack

| Component | Library / Provider | Model | Purpose |
|---|---|---|---|
| LLM | Groq API (`groq` Python SDK) | `openai/gpt-oss-20b` | Tutoring, concept extraction, quiz generation/grading, recommendations |
| Embeddings | `sentence-transformers` | `all-MiniLM-L6-v2` | Turns material chunks and tutor questions into vectors |
| Vector store | ChromaDB | — | Stores/retrieves embedded chunks per project for the Tutor |
| PDF text extraction | PyPDF2 | — | Extracts per-page text from uploaded PDFs before chunking/embedding |

All LLM calls go through one function, `llm_service.call_llm`. Every call uses the same fixed setup: model `openai/gpt-oss-20b`, a single `user`-role message (no system prompt), `max_tokens=1024`, and JSON-mode output only where the feature needs structured data. No `temperature`, `top_p`, or `stream` overrides are used.

## 2. Where AI Is Used

**Concept Extraction** — After a material is chunked and embedded, its first few chunks are sent to the LLM to identify 4–6 main concepts, which are stored and each seeded with a starting mastery score of 30%.

**Tutor (RAG)** — A student's question is embedded and matched against the project's material chunks in ChromaDB. If no sufficiently relevant chunk is found, the app replies with a fixed "not enough information" message and skips the LLM entirely. Otherwise, the matched chunks (with material name + page number) are passed to the LLM as context, along with a short note on the student's weak concepts, and the answer is returned with its sources cited.

**Quiz Generation** — A concept is picked with a mastery-weighted random selection (weaker concepts come up more often), and the LLM generates one multiple-choice or open-ended question calibrated to the student's mastery level for that concept.

**Quiz Grading** — Multiple-choice answers are graded by plain string comparison, no LLM involved. Open-ended answers are graded by the LLM, which returns a correct/incorrect verdict, short feedback, and any missing concepts.

**Growth Recommendations** — Once a student has mastery history, the LLM turns their concept trends into 1–2 sentences of specific, encouraging guidance. This runs automatically when a quiz is completed, and on demand from the Analytics tab.

## 3. AI Observability

Every LLM call is logged with its feature, model, latency, token counts, and success/failure status. This log powers per-project Analytics, the Admin "AI Usage" dashboard (requests, tokens, latency, estimated cost), and Admin "System Health" (recent error rate, recent failures).

## 4. Heuristic AI-Quality Evaluation

An Admin "Evaluation" view computes quality signals purely from logged data (no human-labeled eval set): Tutor groundedness rate and unsupported-question handling rate, quiz generation/grading failure rates, and recommendation failure rate. Snapshots can be saved for comparison over time.

## 5. Vector Storage

Each project has its own ChromaDB collection, so retrieval never crosses project boundaries. Chunks are embedded with `all-MiniLM-L6-v2`, with material name and page number stored alongside each embedding — this is what lets the Tutor cite its sources.
