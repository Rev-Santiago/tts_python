"""
Tagalog Phonetic Lexicon for Qwen3-TTS and Piper
"""
import re

# Dictionary for phonetic respelling
TAGALOG_LEXICON = {
    # --- Greetings & Etiquette ---
    "mabuhay": "ma-boo-high",
    "kumusta": "koo-moos-tah",
    "salamat": "sah-LAH-matt",
    "paalam": "pah-ah-lam",
    "po": "poh",
    "opo": "oh-poh",
    "walang": "wah-lang",
    "anuman": "ah-noo-mahn",

    # --- Common Particles & Grammar (Crucial for flow) ---
    "ng": "nang",
    "mga": "ma-nga",
    "atbp": "at iba pa",
    "ay": "ai",
    "si": "see",
    "na": "nah",
    "din": "deen",
    "rin": "reen",

    # --- Pronouns ---
    "ako": "ah-koh",
    "ikaw": "ee-kaoo",
    "tayo": "tah-yoh",
    "kami": "kah-mee",
    "siya": "shah",  # Neural models often struggle with 'si-ya'
    "nila": "nee-lah",

    # --- Problematic Neural Words (Common in DGSI context) ---
    "buhay": "boo-hay",
    "puso": "poo-soh",
    "gabi": "gah-bee",
    "ganda": "gan-dah",
    "gusto": "goos-toh",
    "sakit": "sah-kit",
    "lakas": "la-kass",
    "lambing": "lam-bing",
    "wika": "wee-kah",
    "bayani": "bah-yah-nee",
    "dangal": "dah-ngahl",
    "tulong": "too-long",

    # --- Questions & Direction ---
    "saan": "sah-ahn",
    "kailan": "kah-ee-lan",
    "bakit": "bah-kit",
    "paano": "pah-ah-no",
    "kanino": "kah-nee-no",
    "dito": "dee-toh",
    "doon": "doh-ohn",

    # --- Time & Nature ---
    "ngayon": "ngah-yohn",
    "bukas": "boo-kahs",
    "hapon": "hah-pohn",
    "tanghali": "tang-hah-lee",
    "umaga": "oo-mah-gah",
    "dagat": "dah-gaht",
    "langit": "lah-ngit",
}

def apply_custom_phonetics(text: str) -> str:
    """
    Normalizes Tagalog text using phonetic respelling 
    to improve TTS pronunciation.
    """
    processed_text = text.lower()
    for word, phonetic in TAGALOG_LEXICON.items():
        # Uses word boundaries to ensure we don't replace parts of other words
        processed_text = re.sub(rf'\b{word}\b', phonetic, processed_text)
    return processed_text