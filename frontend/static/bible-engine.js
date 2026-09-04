class BibleEngine {
    constructor() {
        console.log("BibleEngine: Initialized (Static/cPanel Mode)");
        // Protestant Canon Chapter Counts
        this.chapterCounts = {
            'Genesis': 50, 'Exodus': 40, 'Leviticus': 27, 'Numbers': 36, 'Deuteronomy': 34,
            'Joshua': 24, 'Judges': 21, 'Ruth': 4, '1 Samuel': 31, '2 Samuel': 24,
            '1 Kings': 22, '2 Kings': 25, '1 Chronicles': 29, '2 Chronicles': 36,
            'Ezra': 10, 'Nehemiah': 13, 'Esther': 10, 'Job': 42, 'Psalms': 150,
            'Proverbs': 31, 'Ecclesiastes': 12, 'Song of Solomon': 8, 'Isaiah': 66,
            'Jeremiah': 52, 'Lamentations': 5, 'Ezekiel': 48, 'Daniel': 12, 'Hosea': 14,
            'Joel': 3, 'Amos': 9, 'Obadiah': 1, 'Jonah': 4, 'Micah': 7, 'Nahum': 3,
            'Habakkuk': 3, 'Zephaniah': 3, 'Haggai': 2, 'Zechariah': 14, 'Malachi': 4,
            'Matthew': 28, 'Mark': 16, 'Luke': 24, 'John': 21, 'Acts': 28, 'Romans': 16,
            '1 Corinthians': 16, '2 Corinthians': 13, 'Galatians': 6, 'Ephesians': 6,
            'Philippians': 4, 'Colossians': 4, '1 Thessalonians': 5, '2 Thessalonians': 3,
            '1 Timothy': 6, '2 Timothy': 4, 'Titus': 3, 'Philemon': 1, 'Hebrews': 13,
            'James': 5, '1 Peter': 5, '2 Peter': 3, '1 John': 5, '2 John': 1,
            '3 John': 1, 'Jude': 1, 'Revelation': 22
        };
    }

    /**
     * Get a specific chapter from local static JSON files
     * Normalizes different JSON structures into a consistent array of { verse: n, text: "..." }
     */
    async getChapter(versionId, bookName, chapterNum) {
        try {
            const jsonUrl = `/static/bible/${versionId}.json`;
            console.log(`BibleEngine: Fetching ${bookName} ${chapterNum} from ${jsonUrl}`);
            
            const response = await fetch(jsonUrl);
            if (!response.ok) {
                console.error(`BibleEngine: Failed to load ${versionId}.json (Status: ${response.status})`);
                return [];
            }
            
            const data = await response.json();
            const bookList = Object.keys(this.chapterCounts);
            const bookIndex = bookList.indexOf(bookName);
            
            if (bookIndex === -1) {
                console.error(`BibleEngine: Unknown book name: ${bookName}`);
                return [];
            }

            // Normalization logic based on version
            if (versionId === 'en_kjv') {
                // English format: Array of books, each with "chapters" as array of verse-string arrays
                // data is the array ([ {id: "gn", name: "Genesis", chapters: [...]}, ... ])
                const bookData = data[bookIndex];
                if (bookData && bookData.chapters && bookData.chapters[chapterNum - 1]) {
                    const verses = bookData.chapters[chapterNum - 1];
                    return verses.map((text, idx) => ({
                        verse: idx + 1,
                        text: text.replace(/\{[^}]*\}/g, '').replace(/\s+/g, ' ').trim()
                    }));
                }
            } else if (versionId === 'en_esv') {
                // ESV format: Flat array of objects { o: n, r: "version:book:chap:verse", t: "text" }
                // Example: { "o": 3, "r": "esv:Genesis:1:1", "t": "..." }
                // We need to filter and map to { verse: n, text: "..." }
                const prefix = `esv:${bookName}:${chapterNum}:`;
                return data
                    .filter(v => v.r && v.r.startsWith(prefix))
                    .map(v => {
                        const parts = v.r.split(':');
                        return {
                            verse: parseInt(parts[3]),
                            text: v.t
                        };
                    })
                    .filter(v => v.verse > 0); // Skip chapter headers/titles (verse 0)
            } else if (versionId === 'ta_bsi') {
                // Tamil format: { "Book": [ { "Chapter": [ { "Verse": [...] } ] } ] }
                // data.Book[bookIndex].Chapter[chapterIndex].Verse[verseIndex].Verse
                const bookData = data.Book ? data.Book[bookIndex] : null;
                const chapterIndex = parseInt(chapterNum) - 1;
                
                if (bookData && bookData.Chapter && bookData.Chapter[chapterIndex]) {
                    const chapterData = bookData.Chapter[chapterIndex];
                    if (chapterData.Verse) {
                        return chapterData.Verse.map((v, idx) => ({
                            verse: idx + 1,
                            text: v.Verse
                        }));
                    }
                }
            } else {
                // Fallback / legacy support if needed
                if (data[bookName] && data[bookName][chapterNum]) {
                    const verses = data[bookName][chapterNum];
                    return verses.map(v => ({
                        verse: v.v || v.verse,
                        text: v.t || v.text
                    }));
                }
            }

            console.warn(`BibleEngine: Passage not found in JSON: ${bookName} ${chapterNum}`);
            return [];
        } catch (err) {
            console.error("BibleEngine: Static fetch error:", err);
            return [];
        }
    }

    /**
     * Get the number of chapters for a specific book (static mapping)
     */
    getChapterCount(bookName) {
        return this.chapterCounts[bookName] || 0;
    }

    /**
     * Get a specific verse from a chapter
     */
    async getVerse(versionId, bookName, chapterNum, verseNum) {
        const verses = await this.getChapter(versionId, bookName, chapterNum);
        const match = verses.find(v => v.verse === parseInt(verseNum));
        return match ? match.text : null;
    }
}

// Initialize global instance
window.bibleEngine = new BibleEngine();

