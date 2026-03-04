# Anti-Hallucination & Inline Citation Bible AI Workflow for Antigravity

This workflow is for an Antigravity-based Bible AI chatbot. It combines **hallucination-reduction techniques** with **inline citations** and **original-language context**.

---

## 1️⃣ Prepare Your Corpus (Chunking Bible + Lexicon)

**Objective:** Break the Bible text and lexicons into small, meaningful chunks.

**Steps:**

1. Chunk Bible text by verse or 1–2 verse paragraphs.

   * Include **original language words** (Hebrew for OT, Greek for NT) in each chunk.
   * Add **transliteration and meaning** of key words in chunk metadata.
2. Include lexicon entries as separate chunks.

   * Example: `ἀγαπάω (agapáō) → unconditional love, selfless commitment`
3. Add metadata for each chunk: `book`, `chapter`, `verse`, `language`, `type` (Bible / Lexicon / Commentary).

**Example Chunk (John 21:15)**

```json
{
  "book": "John",
  "chapter": 21,
  "verse": 15,
  "language": "Greek",
  "text": "Jesus said to Simon Peter, 'Do you love me?' He said to him, 'Yes, Lord; you know that I love you.'",
  "original_words": [
    {"word": "ἀγαπάω", "transliteration": "agapáō", "meaning": "unconditional, selfless love"}
  ],
  "type": "Bible"
}
```

---

## 2️⃣ Generate Vector Embeddings for Retrieval

* Use **vector embeddings** (SentenceTransformers or OpenAI embeddings) to embed chunks.
* Store embeddings in a **vector database** (FAISS, Milvus, Pinecone).
* Include original-language words and transliterations in the text for semantic accuracy.

---

## 3️⃣ Hierarchical Retrieval (Primary Verse First)

1. Retrieve **primary verse chunk** most relevant to the user question (top 1–3 chunks).
2. Retrieve **supporting lexicon/commentary chunks** only if they match the primary verse (filter by `book` and `chapter`).
3. Feed **only these chunks** to the AI. Do not include unrelated verses.
4. Use **sliding window / overlapping chunks** for context that spans multiple verses.

---

## 4️⃣ Prompt Engineering (Anti-Hallucination + Inline Citations)

**Instructions for AI:**

```text
Answer the question using only the provided context.
Do not invent verses, words, or historical events.
Include original-language words (Greek/Hebrew) with transliteration and meaning.

Answer in the following structure:
1. Question
2. Primary Verse
3. Original Language Words
4. Contextual Explanation (integrate spiritual/theological insights directly, use inline citations like John 3:16)

If the context does not provide sufficient information, say: "The text does not provide this information."
```

**Key Points:**

* Inline citations replace a separate "Connections to Other Verses" section.
* Integrate theological takeaways **within the explanation**.
* Primary verse is always analyzed first.
* Anti-hallucination: output strictly **from retrieved chunks**.

---

## 5️⃣ Sample Output (Inline Citations + Original Language)

**Question:** Why did Jesus ask Peter, “Do you love me?” three times?

**Primary Verse:** John 21:15–17

**Original Language Words:**

* **ἀγαπάω (agapáō):** unconditional, selfless love
* **φιλέω (phileō):** brotherly, affectionate love

**Contextual Explanation:**
Peter had denied Jesus three times (John 18:15–27). Jesus asks **three times** to restore Peter and reaffirm his calling. The first question uses **agapáō**, calling Peter to selfless, God-like love, emphasizing that discipleship requires both commitment and action (John 13:34–35). The second question uses **phileō**, acknowledging Peter’s sincere emotional affection, showing that genuine love includes heartfelt devotion. The third question returns to **agapáō**, linking love directly to responsibility, as Jesus commands Peter to “feed my sheep” (Matthew 16:18–19). This demonstrates that restoration in Christ combines **grace, forgiveness, and active discipleship**, encouraging believers to love God both emotionally and practically (John 3:16).

---

## 6️⃣ Optional Enhancements

* **Confidence Scoring:** Only display output if retrieval similarity > threshold.
* **Post-Processing Verification:** Highlight original-language words; flag missing or unmatched entries.
* **Sliding Window / Overlap:** Include overlapping verses to maintain cross-verse context.
* **Metadata Filters:** Limit retrieval to the book/chapter of interest to reduce irrelevant information.

---

✅ **Result:**

* AI answers the **primary question first**.
* Includes **original-language words and their meanings**.
* Inline references integrate related passages naturally.
* Hallucinations and irrelevant outputs are minimized.

This workflow ensures your Antigravity Bible AI is **accurate, context-aware, and spiritually insightful**.
