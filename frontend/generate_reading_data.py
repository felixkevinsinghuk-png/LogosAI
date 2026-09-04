import json
import math

# Bible Book Chapter Counts
OT_BOOKS = [
    ("Genesis", 50), ("Exodus", 40), ("Leviticus", 27), ("Numbers", 36), ("Deuteronomy", 34),
    ("Joshua", 24), ("Judges", 21), ("Ruth", 4), ("1 Samuel", 31), ("2 Samuel", 24),
    ("1 Kings", 22), ("2 Kings", 25), ("1 Chronicles", 29), ("2 Chronicles", 36),
    ("Ezra", 10), ("Nehemiah", 13), ("Esther", 10), ("Job", 42), ("Psalms", 150),
    ("Proverbs", 31), ("Ecclesiastes", 12), ("Song of Solomon", 8), ("Isaiah", 66),
    ("Jeremiah", 52), ("Lamentations", 5), ("Ezekiel", 48), ("Daniel", 12),
    ("Hosea", 14), ("Joel", 3), ("Amos", 9), ("Obadiah", 1), ("Jonah", 4),
    ("Micah", 7), ("Nahum", 3), ("Habakkuk", 3), ("Zephaniah", 3), ("Haggai", 2),
    ("Zechariah", 14), ("Malachi", 4)
]

NT_BOOKS = [
    ("Matthew", 28), ("Mark", 16), ("Luke", 24), ("John", 21), ("Acts", 28),
    ("Romans", 16), ("1 Corinthians", 16), ("2 Corinthians", 13), ("Galatians", 6),
    ("Ephesians", 6), ("Philippians", 4), ("Colossians", 4), ("1 Thessalonians", 5),
    ("2 Thessalonians", 3), ("1 Timothy", 6), ("2 Timothy", 4), ("Titus", 3),
    ("Philemon", 1), ("Hebrews", 13), ("James", 5), ("1 Peter", 5), ("2 Peter", 3),
    ("1 John", 5), ("2 John", 1), ("3 John", 1), ("Jude", 1), ("Revelation", 22)
]

def generate_chapters(books):
    chapters = []
    for book, count in books:
        for ch in range(1, count + 1):
            chapters.append({"book": book, "chapter": ch})
    return chapters

ot_all = generate_chapters(OT_BOOKS)
nt_all = generate_chapters(NT_BOOKS)

# Build Gospels list
gospels = []
for book in ["Matthew", "Mark", "Luke", "John"]:
    count = dict(NT_BOOKS)[book]
    for ch in range(1, count + 1):
        gospels.append({"book": book, "chapter": ch})

# Build Romans list
romans = []
count = dict(NT_BOOKS)["Romans"]
for ch in range(1, count + 1):
    romans.append({"book": "Romans", "chapter": ch})

# 1. Full Bible in One Year (365 days)
# OT: 929 chapters -> 199 days of 3 chapters, 166 days of 2 chapters
ot_distribution = []
idx = 0
for i in range(365):
    count = 3 if i < 199 else 2
    ot_distribution.append(ot_all[idx:idx+count])
    idx += count

# NT List augmented to exactly 365 items: NT (260) + Gospels (89) + Romans (16) = 365
nt_augmented = nt_all + gospels + romans
assert len(nt_augmented) == 365, f"NT Augmented length is {len(nt_augmented)}"

full_bible_365 = {}
for day in range(1, 366):
    i = day - 1
    daily_ot = ot_distribution[i]
    daily_nt = [nt_augmented[i]]
    
    # Format OT Display String (e.g., Genesis 1-3)
    ot_dict = {}
    for item in daily_ot:
        ot_dict.setdefault(item["book"], []).append(item["chapter"])
    
    ot_strs = []
    for b, chs in ot_dict.items():
        if len(chs) > 1:
            ot_strs.append(f"{b} {chs[0]}-{chs[-1]}")
        else:
            ot_strs.append(f"{b} {chs[0]}")
            
    nt_ref = f"{daily_nt[0]['book']} {daily_nt[0]['chapter']}"
    
    display_str = ", ".join(ot_strs) + "\n" + nt_ref
    
    full_bible_365[day] = {
        "display": display_str,
        "readings": daily_ot + daily_nt
    }

# 2. Gospels in 4 Months (120 Days)
# First 89 days = 1 chapter
gospels_120 = {}
for day in range(1, 90):
    item = gospels[day-1]
    gospels_120[day] = {
        "display": f"{item['book']} {item['chapter']}",
        "readings": [item]
    }

# Remaining 31 days
# Re-read Matthew 5-7 (Sermon on the Mount) - 3 days
# Re-read John 14-17 (Upper Room) - 4 days
# We want to fill 31 days with meaningful readings. We can just repeat important chunks.
key_chapters = (
    [{"book": "Matthew", "chapter": ch} for ch in range(5, 8)] + # 3
    [{"book": "John", "chapter": ch} for ch in range(14, 18)] +  # 4
    [{"book": "Luke", "chapter": ch} for ch in range(1, 3)] +    # 2
    [{"book": "Matthew", "chapter": ch} for ch in range(26, 29)] + # 3
    [{"book": "Mark", "chapter": ch} for ch in range(14, 17)] +    # 3
    [{"book": "Luke", "chapter": ch} for ch in range(22, 25)] +    # 3
    [{"book": "John", "chapter": ch} for ch in range(18, 22)] +    # 4
    [{"book": "John", "chapter": ch} for ch in range(1, 10)]       # 9 (Total: 3+4+2+3+3+3+4+9 = 31 exactly!)
)

for i in range(31):
    day = 90 + i
    item = key_chapters[i]
    gospels_120[day] = {
        "display": f"Review: {item['book']} {item['chapter']}",
        "readings": [item]
    }


# 3. NT in One Year (365 Days)
# Day 1-365 maps exactly to our `nt_augmented` list which is NT + Gospels + Romans.
nt_year = {}
for day in range(1, 366):
    item = nt_augmented[day-1]
    # To differentiate the review portion:
    prefix = "Review: " if day > 260 else ""
    nt_year[day] = {
        "display": f"{prefix}{item['book']} {item['chapter']}",
        "readings": [item]
    }

# Export
READING_DATA = {
    "full-bible-365": full_bible_365,
    "gospels-120": gospels_120,
    "nt-year": nt_year
}

js_content = "/**\n * reading-data.js — Static data for EXACT Bible Reading Plans\n * Generated procedurally to ensure 100% theological accuracy.\n */\n\nconst READING_DATA = " + json.dumps(READING_DATA, indent=2) + ";\n\nwindow.READING_DATA = READING_DATA;\n"

with open("/Volumes/FELIX SSD/LogosAI/frontend/static/reading-data.js", "w") as f:
    f.write(js_content)
print("Successfully generated /Volumes/FELIX SSD/LogosAI/frontend/static/reading-data.js")
