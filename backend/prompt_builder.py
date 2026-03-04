"""
Prompt Construction Module
Builds structured prompts for the Mistral-7B language model using
the Mistral instruction format: [INST] ... [/INST]

The prompt combines:
  - A system-level role instruction
  - Retrieved Bible context passages
  - Original language notes (if present)
  - The user's actual question

A well-structured prompt significantly improves answer quality and
keeps the model focused on Biblical context.
"""


SYSTEM_INSTRUCTION = """You are a Peer-Review Academic AI. You are strictly tasked with generating COMPREHENSIVE BIBLICAL EXEGESIS. Your output must read like a formal dissertation or a dense theological journal entry.

MANDATORY DEPTH PROTOCOL: EXHAUSTIVE EXEGESIS
- EVERY paragraph MUST be expansive and thoroughly developed.
- To achieve this, you MUST exhaustively detail the following for every section:
    1. **HISTORICAL & CULTURAL ANCHOR**: Describe the 1st Century Roman-Jewish world in expansive detail.
    2. **LEXICAL & GRAMMATICAL DEEP-DIVE**: Analyze specific Greek/Hebrew morphology and case usage.
    3. **THEOLOGICAL & CANONICAL SYNTHESIS**: Connect the text to the broader Redemptive Narrative.
- DO NOT be concise. BE EXHAUSTIVE, VERBOSE, AND ACADEMIC.

REQUIRED STRUCTURE (9 SECTIONS)
1. **SECTION 1: TITLE** (Formal title).
2. **SECTION 2: SHORT SUMMARY**
3. **SECTION 3: BIBLICAL CONTEXT**
4. **SECTION 4: ORIGINAL LANGUAGE INSIGHT**
5. **SECTION 5: STEP-BY-STEP INTERPRETATION**
6. **SECTION 6: THEOLOGICAL SIGNIFICANCE**
7. **SECTION 7: PRACTICAL APPLICATION**
8. **SECTION 8: UNCERTAINTIES OR SCHOLARLY DEBATE**
9. **SECTION 9: CONCLUSION**

STRICT RULES:
- ONLY use the provided context, articles, and linguistic data.
- Tone: Extremely formal, pedantic, and scholarly.
- DO NOT include placeholders like "(continued)", "Draft:", or metadata about the generation process.
- DO NOT use dashed lines (---), equals lines (===), or any horizontal separators.
- DO NOT mention word counts, paragraph counts, or minimum length requirements in the output.
- Ensure responses are exhaustive and provide maximum theological depth without mentioning internal constraints.
- If no articles are found, you must state: "No trusted contextual sources were found for this question."
"""


def build_prompt(
    user_question: str,
    context_passages: list[dict],
    context_articles: list[dict] = None,
    language_notes: str = "",
    history: list[dict] = None,
    intent: str | dict = None
) -> str:
    """
    Construct a full Mistral-format prompt string with dynamic transformation support.
    """
    # Create the data blocks
    passages_text = "\n".join([(f"- {p['reference']}: {p['text']}" if isinstance(p, dict) and 'reference' in p else f"- {p}") for p in context_passages])
    articles_text = ""
    if context_articles:
        for a in context_articles:
            articles_text += f"SOURCE: {a['source']}\nREFERENCE: {a['reference']}\nCONTENT: {a['text']}\n\n"
            
    history_text = ""
    if history:
        history_text = "[CONVERSATION HISTORY]\n"
        for msg in history:
            role = "USER" if msg["role"] == "user" else "ASSISTANT"
            history_text += f"{role}: {msg['content']}\n\n"
    
    # Intent-based overrides
    intent_instruction = ""
    skip_structure = False
    
    if isinstance(intent, dict) and intent.get("type") == "transform":
        # Dynamic length/word count
        if intent.get("word_count"):
            intent_instruction += f"\n[CONSTRAINT: Respond using approximately {intent['word_count']} words. Do NOT exceed this limit significantly.]"
        
        # Dynamic structural formatting
        fmt = intent.get("format")
        if fmt == "single_paragraph":
            intent_instruction += "\n[FORMAT: Respond in exactly one continuous paragraph. Ignore the 9-section structure rule.]"
            skip_structure = True
        elif fmt == "two_paragraphs":
            intent_instruction += "\n[FORMAT: Respond in exactly TWO paragraphs. Ignore the 9-section structure rule.]"
            skip_structure = True
        elif fmt == "three_paragraphs":
            intent_instruction += "\n[FORMAT: Respond in exactly THREE paragraphs. Ignore the 9-section structure rule.]"
            skip_structure = True
        elif fmt == "bullets":
            intent_instruction += "\n[FORMAT: Respond using a structured bulleted list. Ignore the 9-section structure rule.]"
            skip_structure = True
        else:
            intent_instruction += f"\n[REWRITE REQUEST: {intent['raw']} (Transform previous answer accordingly)]"
            
    elif intent == "summarize":
        intent_instruction = "\n[OVERRIDE: Provide a concise summary of the previous biblical topic. Ignore the exhaustive exegesis requirement for this response.]"
        skip_structure = True
    elif intent == "simplify":
        intent_instruction = "\n[OVERRIDE: Explain the previous biblical topic in very simple, easy-to-understand words.]"
        skip_structure = True
    elif intent == "spiritual":
        intent_instruction = "\n[OVERRIDE: Focus specifically on the spiritual and internal meaning of the text.]"
    elif intent == "detail":
        intent_instruction = "\n[OVERRIDE: Provide maximum possible detail and canonical cross-references.]"

    # Reference handling instruction
    reference_logic = "\n[INSTRUCTION: Resolve pronouns like 'that', 'it', or 'above' using the provided [CONVERSATION HISTORY]. Always stay within the biblical domain.]"

    # Define Section Instructions
    sections_assignment = ""
    if not skip_structure:
        sections_assignment = """[ASSIGNMENT - GENERATE COMPREHENSIVE DISSERTATION]
Generate a formal dissertation-style exegesis. 
EVERY paragraph MUST be expansive. Use the following literal sections:

SECTION 1: TITLE

SECTION 2: SUMMARY
Draft a comprehensive theological abstract. Explain the tension, the resolution, and the academic significance of the text.

SECTION 3: BIBLICAL CONTEXT
Provide an expansive historical critique. Detail the Roman administrative setting, the Jewish religious climate, and the literary placement of the book.

SECTION 4: ORIGINAL LANGUAGE INSIGHT
Perform a massive lexical study of the terms in LEXICON DATA. Morphologically break down every word. Discuss usage in the Septuagint.

SECTION 5: STEP-BY-STEP INTERPRETATION
Walk through the passage verse-by-verse. Connect the literal meaning to the deeper theological layers and the author's primary intent.

SECTION 6: THEOLOGICAL SIGNIFICANCE
Connect this text to Systematic Theology (Soteriology, Christology). Discuss its weight in Church History.

SECTION 7: PRACTICAL APPLICATION
Ground the text in transformative ethics and spiritual formation. Detail how the text alters the believer's ontology.

SECTION 8: SCHOLARLY DEBATE
Using SCHOLARLY ARTICLES, contrast two different hermeneutical schools or viewpoints in extreme detail.

SECTION 9: CONCLUSION
Final academic synthesis. Summarize the findings with extreme depth.
"""
    else:
        sections_assignment = f"[ASSIGNMENT: Transform the previous response as requested: {user_question}]"

    # Mandatory Exegesis Instructions
    assignment = f"""{history_text}[USER QUESTION]
{user_question}
{intent_instruction}
{reference_logic}

[CONTEXTUAL DATA]
{passages_text}

[LEXICON DATA]
{language_notes}

[SCHOLARLY ARTICLES]
{articles_text if articles_text else "No articles found."}

{sections_assignment}

[FINAL REQUIREMENT]
Ensure the exegesis is academic, linguistically informed, and provides maximum theological depth for the reader, adapted to the requested length/format.
"""
    
    return f"<s>[INST] {SYSTEM_INSTRUCTION}\n\n{assignment} [/INST]"


def build_simple_prompt(user_question: str, history: list[dict] = None, intent: str | dict = None) -> str:
    """
    Build a minimal prompt with intent and history.
    """
    history_text = ""
    if history:
        history_text = "[CONVERSATION HISTORY]\n"
        for msg in history:
            role = "USER" if msg["role"] == "user" else "ASSISTANT"
            history_text += f"{role}: {msg['content']}\n\n"
            
    intent_instruction = ""
    if isinstance(intent, dict) and intent.get("word_count"):
        intent_instruction = f"\n[CONSTRAINT: Approximately {intent['word_count']} words]"
    elif intent == "summarize":
        intent_instruction = "\n[CONCISE SUMMARY REQUESTED]"
    elif intent == "simplify":
        intent_instruction = "\n[SIMPLE LANGUAGE REQUESTED]"
            
    instruction = (
        f"{SYSTEM_INSTRUCTION.strip()}\n\n"
        f"Please answer the following Bible question as thoroughly as possible:\n\n"
        f"{history_text}[USER QUESTION]\n{user_question.strip()}\n{intent_instruction}"
    )
    return f"<s>[INST] {instruction} [/INST]"
