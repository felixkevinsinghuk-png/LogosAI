"""
generate_dataset.py
===================
Synthesizes a high-quality PEFT (LoRA) training dataset for the RhemaLight AI Bible Assistant.

This script procedurally generates Question-Context-Answer triplets that perfectly
mirror the 6-part Theological Output format defined in Ways.md. It uses the existing
Bible Database and Strong's Lexicon to ensure the training data is grounded
in real scripture and original language definitions.
"""
import os
import json
import random
import sys

# Add parent directory to path so we can import backend modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.bible_loader import load_bible, get_book_name
from database.original_language import lookup_strongs


def generate_theological_qa_pairs(num_samples=500) -> list[dict]:
    """
    Generate synthetic Q&A training pairs based on key Biblical themes.
    Matches the Ways.md formatting requirements (6-part structure).
    """
    print(f"Loading Bible data...")
    verses = load_bible()
    print(f"Loaded {len(verses)} verses.")
    
    # Expanded conceptual themes and their corresponding Strong's keywords
    themes = [
        {"theme": "Love", "keyword": "love", "strongs": ["G0026", "G5368", "H0157"], "question": "What is the biblical definition of love based on this passage?"},
        {"theme": "Faith", "keyword": "faith", "strongs": ["G4102", "H0530"], "question": "How does this passage describe faith?"},
        {"theme": "Grace", "keyword": "grace", "strongs": ["G5485", "H2580"], "question": "What does this passage teach about God's grace?"},
        {"theme": "Peace", "keyword": "peace", "strongs": ["G1515", "H7965"], "question": "How is peace understood in this scriptural context?"},
        {"theme": "Truth", "keyword": "truth", "strongs": ["G0225", "H0571"], "question": "What is the nature of truth according to this verse?"},
        {"theme": "Salvation", "keyword": "sav", "strongs": ["G4982", "H3467"], "question": "Explain the concept of salvation shown here."},
        {"theme": "Wisdom", "keyword": "wisdom", "strongs": ["G4678", "H2451"], "question": "How does this entry define divine wisdom?"},
        {"theme": "Hope", "keyword": "hope", "strongs": ["G1680", "H8615"], "question": "What is the basis of hope in this context?"},
        {"theme": "Justice", "keyword": "justice", "strongs": ["G1343", "H4941"], "question": "How is righteousness and justice presented here?"},
        {"theme": "Holiness", "keyword": "holy", "strongs": ["G0040", "H6944"], "question": "What does it mean to be 'holy' according to this text?"},
        {"theme": "Prayer", "keyword": "pray", "strongs": ["G4336", "H6419"], "question": "What can we learn about prayer from this passage?"},
        {"theme": "Worship", "keyword": "worship", "strongs": ["G4352", "H7812"], "question": "How should we worship based on this scripture?"}
    ]

    training_data = []
    
    print(f"Synthesizing {num_samples} training pairs...")
    
    attempted: int = 0
    generated: int = 0
    
    while generated < num_samples and attempted < num_samples * 5:
        attempted += 1
        theme_def = random.choice(themes)
        keyword = theme_def["keyword"]
        
        # Find a random verse containing the keyword
        matching_verses = [v for v in verses if keyword in v["t"].lower()]
        if not matching_verses:
            continue
            
        target_verse = random.choice(matching_verses)
        b, c, v_num, text = target_verse["b"], target_verse["c"], target_verse["v"], target_verse["t"]
        ref = f"{get_book_name(b)} {c}:{v_num}"
        
        # Pick a random strong's word related to the theme
        strongs_id = random.choice(theme_def["strongs"])
        lexicon_entry = lookup_strongs(strongs_id)
        
        if not lexicon_entry:
            continue
            
        lang = lexicon_entry.get("language", "Unknown")
        lemma = lexicon_entry.get("lemma", "Unknown")
        xlit = lexicon_entry.get("xlit", "")
        definition = str(lexicon_entry.get("strongs_def", lexicon_entry.get("kjv_def", "No definition.")))
        
        # Extract clauses for varied explanations
        clause_dot = definition.split('.')[0] if '.' in definition else definition
        clause_semi = definition.split(';')[0] if ';' in definition else definition
        clause_dash = definition.split('--')[0] if '--' in definition else definition
        
        # Construct the System Prompt (Mirroring Ways.md)
        system_prompt = (
            "You are RhemaLight AI, an expert Bible assistant. Answer the question using only the retrieved context. "
            "Do not invent verses or explanations. Include original-language words (Greek/Hebrew) with transliteration and meaning.\n\n"
            "OUTPUT FORMAT REQUIREMENTS:\n"
            "You MUST structure your response EXACTLY with these numbered and bolded headings:\n"
            "1. **Question:** [Restate the user's question briefly]\n"
            "2. **Primary Verse:** [Reference the main passage]\n"
            "3. **Original Language Words:**\n"
            "   - **[Word] ([Transliteration]):** [Meaning]\n"
            "4. **Contextual Explanation:** [Integrate theological/spiritual insights directly into the explanation]\n"
            "5. **Inline citations:** [List inline citations if relevant, or brief cross-references]\n"
            "6. **Summary/Spiritual Takeaway:** [Final takeaway]"
        )
        
        # Construct the RAG Context
        user_input = theme_def["question"]
        rag_context = (
            "[Primary Bible Passage]\n"
            f"• {ref}: \"{text}\"\n\n"
            "[Original Language Information]\n"
            f"[{strongs_id} — {lang}] {lemma} ({xlit}): {definition}\n\n"
            f"[User Question]\n{user_input}"
        )
        
        # Varied Explanation Templates
        explanations = [
            f"In {ref}, the text highlights the vital role of {theme_def['theme'].lower()}. The {lang} term *{xlit}* signifies {clause_dot.lower()}, suggesting that the author intended to emphasize a deep, spiritual reality. This forces the reader to look beyond surface meanings.",
            f"The passage {ref} provides a profound look at {theme_def['theme'].lower()}. Through the {lang} word *{xlit}* (meaning {clause_semi.lower()}), we see God's standard for His people. It connects the literal command to a broader theological framework.",
            f"Examining {ref} reveals the weight of {theme_def['theme'].lower()} in the believer's life. The original {lang} word *{xlit}* underscores {clause_dash.lower().strip()}. This context is essential for understanding the biblical narrative."
        ]
        
        # Construct the TARGET ideal AI answer
        ideal_answer = (
            f"1. **Question:** {user_input}\n\n"
            f"2. **Primary Verse:** {ref}\n\n"
            f"3. **Original Language Words:**\n"
            f"   - **{lemma} ({xlit}):** {definition}\n\n"
            f"4. **Contextual Explanation:** {random.choice(explanations)}\n\n"
            f"5. **Inline citations:** (See {get_book_name(b)} {c})\n\n"
            f"6. **Summary/Spiritual Takeaway:** Biblical {theme_def['theme'].lower()} is grounded in the reality of *{xlit}*, calling us to direct obedience and faith."
        )

        # Build Mistral [INST] format triplet
        full_prompt = f"<s>[INST] {system_prompt}\n\n{rag_context} [/INST] "
        
        training_data.append({
            "text": full_prompt + ideal_answer + "</s>"
        })
        
        generated += 1
        print(f"Generated sample {generated}/{num_samples} ({theme_def['theme']})", end="\r")

    print(f"\nGeneration complete. Total pairs: {len(training_data)}")
    return training_data


if __name__ == "__main__":
    out_dir = os.path.dirname(__file__)
    data_dir = os.path.join(out_dir, "data")
    os.makedirs(data_dir, exist_ok=True)
    
    print("--- RhemaLight AI PEFT Dataset Generator ---")
    data = generate_theological_qa_pairs(500)
    
    # Split 90/10 for train/valid
    random.shuffle(data)
    split = int(0.9 * len(data))
    train_data = data[:split]
    valid_data = data[split:]
    
    with open(os.path.join(data_dir, "train.jsonl"), "w", encoding="utf-8") as f:
        for item in train_data:
            f.write(json.dumps(item) + "\n")
            
    with open(os.path.join(data_dir, "valid.jsonl"), "w", encoding="utf-8") as f:
        for item in valid_data:
            f.write(json.dumps(item) + "\n")
            
    print(f"Successfully saved {len(train_data)} train samples and {len(valid_data)} valid samples to {data_dir}")
