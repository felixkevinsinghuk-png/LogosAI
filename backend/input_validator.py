"""
Input Validator Module
======================
Pre-validates user questions before they reach the LLM pipeline.

Three possible results:
  - "ok"         → Question is biblical and coherent. Proceed normally.
  - "gibberish"  → Input is random characters, nonsense, or incoherent.
  - "off_topic"  → Input is coherent but unrelated to Bible/scripture.
  - "unclear"    → Input seems potentially biblical but is too vague.

These checks run BEFORE any embedding or LLM inference to save resources
and ensure the AI stays strictly within its domain.
"""

import re


# ── Canned Responses ──────────────────────────────────────────────────────────

RESPONSE_OFF_TOPIC = (
    "I am designed to provide answers strictly from a biblical perspective. "
    "Please ask a question related to the Bible, scripture, or Christian teaching."
)

RESPONSE_GIBBERISH = (
    "I'm unable to understand your message. "
    "Please provide a clear question related to the Bible or scripture."
)

RESPONSE_UNCLEAR = (
    "Could you please clarify your question so I can provide a biblical response?"
)


# ── Biblical Keyword Vocabulary ───────────────────────────────────────────────
# Broad list of terms that signal a biblical or spiritual question.

_BIBLE_KEYWORDS = {
    # Books of the Bible
    "genesis", "exodus", "leviticus", "numbers", "deuteronomy", "joshua",
    "judges", "ruth", "samuel", "kings", "chronicles", "ezra", "nehemiah",
    "esther", "job", "psalms", "psalm", "proverbs", "ecclesiastes",
    "isaiah", "jeremiah", "lamentations", "ezekiel", "daniel", "hosea",
    "joel", "amos", "obadiah", "jonah", "micah", "nahum", "habakkuk",
    "zephaniah", "haggai", "zechariah", "malachi", "matthew", "mark",
    "luke", "john", "acts", "romans", "corinthians", "galatians",
    "ephesians", "philippians", "colossians", "thessalonians", "timothy",
    "titus", "philemon", "hebrews", "james", "peter", "jude", "revelation",
    "song of solomon",

    # Core theological terms
    "bible", "biblical", "scripture", "gospel", "prayer", "worship",
    "faith", "grace", "salvation", "repentance", "baptism", "communion",
    "resurrection", "crucifixion", "atonement", "sanctification",
    "justification", "redemption", "covenant", "prophecy", "prophecies",
    "sin", "forgiveness", "eternal life", "holy spirit", "trinity",
    "incarnation", "deity", "divine", "jesus", "christ", "messiah",
    "lord", "god", "yahweh", "jehovah", "father", "son",

    # People & places
    "moses", "abraham", "isaac", "jacob", "joseph", "david", "solomon",
    "elijah", "elisha", "paul", "peter", "mary", "joseph", "adam", "eve",
    "noah", "ruth", "esther", "isaiah", "jeremiah", "daniel", "ezekiel",
    "jerusalem", "bethlehem", "nazareth", "galilee", "sinai", "eden",
    "canaan", "egypt", "israel", "judah", "zion", "temple",

    # Doctrines & practices
    "church", "sermon", "disciple", "apostle", "doctrine", "theology",
    "heresy", "commandment", "commandments", "parable", "miracle",
    "exodus", "passover", "pentecost", "sabbath", "tithe", "offering",
    "prophecy", "fulfillment", "covenant", "testament", "old testament",
    "new testament", "anointing", "blessing", "curse", "rapture",
    "tribulation", "millennium", "heaven", "hell", "purgatory", "angel",
    "demon", "satan", "devil", "spiritual", "spirit", "holy",
    "cross", "tomb", "ascension", "second coming", "end times",

    # Common question starters that imply biblical context
    "what does the bible say", "what does scripture say", "what does god say",
    "explain the verse", "explain the passage", "what does it mean in",
    "meaning of", "who is", "who was",

    # Original languages
    "hebrew", "greek", "aramaic", "strongs", "septuagint", "Torah",
    "logos", "agape", "pneuma", "kyrios", "love", "mercy", "compassion"
}

# ── Non-Biblical Domain Indicators ───────────────────────────────────────────
# Terms that strongly indicate non-biblical topics.

_OFF_TOPIC_KEYWORDS = {
    "python", "javascript", "coding", "algorithm", "machine learning",
    "sql", "database", "api", "html", "css", "programming",
    "math", "calculus", "algebra", "equation", "physics", "chemistry",
    "biology", "science", "evolution",
    "politics", "election", "president", "government", "democrat",
    "republican", "congress", "law",
    "movie", "actor", "actress", "singer", "singer", "music", "sport",
    "football", "basketball", "soccer", "nfl", "nba", "netflix",
    "stock", "invest", "crypto", "bitcoin", "finance", "economy",
    "recipe", "cooking", "food", "restaurant",
    "weather", "climate", "hurricane",
    "capital of", "country", "continent", "geography", "history of",
}


# Common English words and fragments — used to cross-check inputs
_COMMON_ENGLISH_WORDS = {
    "the", "be", "to", "of", "and", "a", "in", "that", "have", "it",
    "for", "not", "on", "with", "he", "she", "as", "you", "do", "at",
    "this", "but", "his", "by", "from", "they", "we", "say", "her", "what",
    "if", "there", "go", "when", "up", "use", "your", "how", "all", "which",
    "give", "me", "new", "first", "last", "only", "after", "often", "our",
    "some", "want", "why", "about", "can", "has", "over", "also", "into",
    "just", "see", "know", "time", "people", "way", "year", "day", "man",
    "who", "make", "like", "him", "look", "come", "think", "would", "could",
    "any", "will", "my", "one", "two", "more", "then", "than", "good", "no",
    "their", "these", "may", "her", "out", "very", "so", "each", "most",
    "ever", "even", "back", "here", "been", "old", "any", "same", "tell",
    "does", "set", "put", "end", "does", "large", "often", "hand", "high",
    "place", "between", "both", "life", "never", "next", "open", "seem",
    "together", "something", "still", "learn", "plant", "cover", "food",
    "sun", "four", "thought", "let", "keep", "children", "feet", "land",
    "side", "without", "boy", "once", "animal", "life", "enough", "took",
    "sometimes", "mountain", "cut", "young", "river", "list", "body", "music",
    "color", "stand", "remember", "love", "real", "run", "full", "city", "away",
    "mean", "world", "another", "order", "must", "change", "face", "night",
    "early", "near", "plant", "grow", "though", "kind", "hard", "far",
    "above", "below", "line", "turn", "cause", "enough", "might", "move",
    "don", "got", "letter", "set", "walk", "example", "always", "music",
    "those", "both", "mark", "book", "carry", "took", "science", "eat",
    "room", "friend", "idea", "body", "family", "direct", "pose", "leave",
    "song", "measure", "door", "product", "black", "short", "numeral", "class",
    "wind", "rock", "space", "red", "map", "rain", "rule", "govern", "pull",
    "cold", "notice", "voice", "unit", "power", "town", "fine", "drive",
    "teach", "shape", "protect", "farm", "cross", "speak", "possible"
}


def _is_gibberish(text: str) -> bool:
    """
    Detect random character strings and low-information input.

    Heuristics applied (in order):
      1. Empty / trivially short input.
      2. Input is a single long word with ZERO common English sub-sequences.
         (e.g. 'feazsvcfdrgvsazesrfvz' — 21 chars, no English word embedded)
      3. All-consonant clusters accounting for >= 50% of words.
      4. Very high proportion of non-alphabetic characters.
      5. Words with no vowels that are longer than 3 characters.
    """
    if not text or len(text.strip()) < 2:
        return True

    lower = text.lower().strip()
    words = lower.split()

    # ── Heuristic 1: Single long word with no embedded real words ────────────
    if len(words) == 1:
        word = re.sub(r"[^a-z]", "", words[0])
        if len(word) >= 12:
            # Look for any common English word embedded in the character sequence
            found_real_word = False
            for en_word in _COMMON_ENGLISH_WORDS:
                if len(en_word) >= 3 and en_word in word:
                    found_real_word = True
                    break
            if not found_real_word:
                return True

    # ── Heuristic 2: Very high consonant density across words ────────────────
    noisy_words = 0
    for word in words:
        letters = re.sub(r"[^a-z]", "", word)
        if len(letters) >= 4:
            vowel_count = sum(1 for c in letters if c in "aeiou")
            if vowel_count == 0:
                noisy_words += 1

    if words and noisy_words / len(words) >= 0.5:
        return True

    # ── Heuristic 3: Majority non-alphabetic characters ──────────────────────
    alpha_count = sum(1 for c in lower if c.isalpha())
    if len(lower) > 0 and alpha_count / len(lower) < 0.5:
        return True

    return False



def _contains_biblical_content(text: str) -> bool:
    """
    Check if the text contains recognized biblical vocabulary.
    """
    lower = text.lower()
    # Check single keywords
    words_in_text = set(re.findall(r"[a-z']+", lower))
    if words_in_text & _BIBLE_KEYWORDS:
        return True
    # Check multi-word phrases
    for phrase in _BIBLE_KEYWORDS:
        if " " in phrase and phrase in lower:
            return True
    return False


def _contains_off_topic_content(text: str) -> bool:
    """
    Check if the text strongly signals a non-biblical domain.
    """
    lower = text.lower()
    words_in_text = set(re.findall(r"[a-z]+", lower))
    return bool(words_in_text & _OFF_TOPIC_KEYWORDS)


# ── Follow-up & Transformation Patterns ───────────────────────────────────────
# Phrases that reference previous context or request transformations.

_FOLLOW_UP_PHRASES = [
    "what does that mean", "explain that", "explain the above", "above in detail",
    "summarize the previous", "simplify it", "can you elaborate", "give more explanation",
    "what can we learn from that", "break that down", "make it simple",
    "explain in simple words", "expand more", "give deeper meaning",
    "what is the spiritual meaning", "what does this teach us", "why is that important",
    "give verse reference for that", "support that with scripture", "short summary",
    "detailed explanation", "tell me more", "how so", "elaborate on that",
    "single paragraph", "one paragraph", "two paragraphs", "three paragraphs",
    "bullet points", "detailed", "brief", "summary", "expand", "elaborate",
    "rewrite", "simplify", "explain again", "rephrase", "deeper meaning",
    "spiritual meaning", "concise", "long explanation", "more", "again"
]

_FOLLOW_UP_PRONOUNS = {"that", "it", "this", "above", "previous", "earlier"}

# Regex for detecting any numeric word count request (e.g., "342 words")
_RE_WORD_COUNT = re.compile(r"(\d+)\s*words?")


def _is_transformation_request(text: str) -> bool:
    """
    Detect if the text is a structural or length transformation request.
    """
    lower = text.lower().strip()
    
    # 1. Any numeric word count request?
    if _RE_WORD_COUNT.search(lower):
        return True
    
    # 2. Any structural transition phrases?
    for phrase in _FOLLOW_UP_PHRASES:
        if phrase in lower:
            return True
            
    # 3. Very short questions using follow-up pronouns
    words = lower.split()
    if len(words) <= 3:
        if any(p in words for p in _FOLLOW_UP_PRONOUNS):
            return True
            
    return False


def validate_input(text: str, has_history: bool = False) -> str:
    """
    Validate user input before sending it to the LLM pipeline.

    Args:
        text (str): Raw user input.
        has_history (bool): Whether the current session has existing history.

    Returns:
        str: One of "ok", "gibberish", "off_topic", "unclear".
    """
    cleaned = text.strip()
    lower = cleaned.lower()

    # Step 1: Check for gibberish / nonsense
    if _is_gibberish(cleaned):
        return "gibberish"

    # Step 2: Check for conversational follow-up or dynamic transformation
    # If we have history, transformation/follow-up requests bypass domain filter.
    if has_history and _is_transformation_request(cleaned):
        return "ok"

    # Step 3: Check for strongly off-topic content
    if _contains_off_topic_content(cleaned) and not _contains_biblical_content(cleaned):
        return "off_topic"

    # Step 4: Check for some biblical signal
    if _contains_biblical_content(cleaned):
        return "ok"

    # Step 5: Input is coherent English but has no biblical signal
    words = lower.split()
    if len(words) <= 5: # Slightly expanded for phrases like "in 300 words please"
        if has_history:
             # Short context-dependent phrase with history -> Likely a follow-up
             return "ok"
        return "unclear"

    # Longer, coherent, non-biblical question → off_topic
    return "off_topic"
