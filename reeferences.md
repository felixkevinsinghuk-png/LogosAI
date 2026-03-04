Update the retrieval and response system to include contextual explanations from trusted Bible study websites while keeping Scripture as the primary authority.

The system must combine:

1) Bible Text (Primary Authority)
2) Original Language Sources
3) Trusted Bible Study Articles (Secondary Context)

------------------------------------------------

TRUSTED CONTEXT SOURCES

Add retrieval support for trusted Biblical study websites such as:

- https://www.biblestudytools.com/
- https://www.gotquestions.org/
- https://www.blueletterbible.org/
- https://enduringword.com/
- https://www.biblehub.com/

These sources should be used ONLY to explain context and theology.

They must NOT override Scripture.


------------------------------------------------

RETRIEVAL PRIORITY

The retrieval pipeline must follow this order:

Priority 1 — Direct Scripture Passages

Example:
John 21:15–17 for Peter’s restoration


Priority 2 — Original Language Sources

Example:

Greek word analysis from:

- BlueLetterBible
- BibleHub Interlinear


Priority 3 — Contextual Articles

Example:

BibleStudyTools article explaining:

"Why Jesus asked Peter three times"


Low relevance sources must be filtered out.


------------------------------------------------

CONTEXTUAL ARTICLE USAGE RULES

Context articles must:

- Explain the Biblical passage
- Support the main interpretation
- Add historical or theological insight

Context articles must NOT:

- Replace Scripture
- Introduce speculation
- Add symbolic interpretations without support
- Introduce unrelated passages


------------------------------------------------

OUTPUT FORMAT UPDATE

Add a new section AFTER the Contextual Explanation.


Contextual Insights from Trusted Sources:

Summarize the contextual explanation from trusted Bible study articles.

Example:

According to BibleStudyTools, Jesus asked Peter three times to parallel Peter’s three denials and to restore him publicly as a disciple.

BlueLetterBible explains that the Greek words "agapaō" and "phileō" reflect slightly different expressions of love in the conversation between Jesus and Peter.

EnduringWord commentary notes that each affirmation of love is followed by a command to shepherd believers, showing that love for Christ leads to service.


Rules:

- Maximum 3 insights
- Each insight must be grounded in the passage
- No speculation
- No invented interpretations


------------------------------------------------

ANTI-HALLUCINATION RULES

The system must:

- Only use retrieved articles
- Never invent commentary
- Never guess interpretations
- Never fabricate sources

If no article is found, output:

"No trusted contextual sources were found for this question."


------------------------------------------------

STRICT SOURCE CITATION

Each contextual insight must include the source name.

Example:

(BibleStudyTools)

(BlueLetterBible)

(EnduringWord)


------------------------------------------------

EXAMPLE OUTPUT

Primary Passage:
John 21:15–17


Direct Answer:

Jesus asked Peter three times because Peter denied Him three times earlier (John 18:27). The three questions represent Peter’s restoration and recommissioning.


Original Language Insight:

ἀγαπᾷς (agapas)

Meaning:
Self-giving love

Context:
Jesus asks Peter for committed love.


φιλέω (phileō)

Meaning:
Personal affection

Context:
Peter responds with personal devotion.


Contextual Explanation:

This event occurs after the resurrection when Jesus meets the disciples by the Sea of Galilee.


Contextual Insights from Trusted Sources:

BibleStudyTools explains that the three questions mirror Peter's three denials and restore Peter publicly.

BlueLetterBible notes that the Greek words for love suggest a progression in Peter’s understanding of devotion.

EnduringWord commentary explains that each affirmation is followed by a pastoral command showing that love leads to service.


Spiritual Meaning:

The passage shows that Christ restores those who repent and calls them again into service.


------------------------------------------------

FINAL RULE

Scripture must always be the primary source.

Articles must only provide supporting explanation.

The system must prioritize:

1 Scripture
2 Original Language
3 Trusted Commentary