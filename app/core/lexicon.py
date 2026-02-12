"""
Tagalog Phonetic Lexicon for Qwen3-TTS and Piper
"""
import re

# Dictionary for phonetic respelling
TAGALOG_LEXICON = {
    # --- Greetings & Etiquette ---
    "mabuhay": "ma-boo-high",
    "kamusta": "kah-moos-tah",
    "salamat": "sAH-la-matt",
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
    "mabuti": "ma-boo-tee",
    "pag-asa": "pag-ah-sah",
    "pag-ibig": "pag-ee-big",
    "kalayaan": "ka-lah-yahn",
    "bayan": "bah-yahn",
    "bayanihan": "bah-yah-nee-han",
    "kapayapaan": "ka-pah-yah-paan",
    "kalikasan": "ka-lee-kah-sahn",
    "kalusugan": "ka-loo-soo-gahn",
    "kaligtasan": "ka-lee-gta-sahn",
    "kalayaan": "ka-lah-yahn",
    "katarungan": "ka-tah-roo-ngan",
    "kagandahan": "ka-gan-dah-han",
    "kagalingan": "ka-gah-ling-an",
    "kagitingan": "ka-gee-ting-an",
    "kaginhawaan": "ka-gin-ha-wan",


    # --- Questions & Direction ---
    "saan": "sah-ahn",
    "kailan": "ka-ee-lan",
    "bakit": "bah-kit",
    "paano": "pah-ah-no",
    "kanino": "kah-nee-no",
    "dito": "dee-two",
    "doon": "doo-ohn",
    "magtanong": "mug-tah-nOng",

    # --- Time & Nature ---
    "ngayon": "ngah-yown",
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