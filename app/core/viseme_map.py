"""
Viseme mapping logic - converts phonemes to viseme IDs
Based on Oculus OVR LipSync / ARKit standard
"""
from typing import Dict


class VisemeMapper:
    """Maps phonemes to viseme IDs for 3D mouth animation"""
    
    # Viseme mapping based on Oculus OVR LipSync standard (21 visemes)
    # Viseme 0 = sil (silence/rest)
    # This mapping covers common phonemes from Piper/eSpeak
    PHONEME_TO_VISEME: Dict[str, int] = {
        # Silence
        'pau': 0, 'sil': 0, '_': 0,
        
        # Bilabials (lips together): PP
        'p': 1, 'b': 1, 'm': 1,
        
        # Labiodentals (lip-teeth): FF
        'f': 2, 'v': 2,
        
        # Dental (tongue-teeth): TH
        'θ': 3, 'ð': 3, 'th': 3, 'dh': 3,
        
        # Dental/Alveolar: DD
        't': 4, 'd': 4, 'n': 4,
        
        # Alveolar: kk
        'k': 5, 'g': 5, 'ŋ': 5, 'ng': 5,
        
        # Palato-Alveolar: CH
        'tʃ': 6, 'dʒ': 6, 'ʃ': 6, 'ʒ': 6,
        'ch': 6, 'jh': 6, 'sh': 6, 'zh': 6,
        
        # Alveolar fricatives: SS
        's': 7, 'z': 7,
        
        # Approximants: nn
        'l': 8, 'r': 8, 'ɹ': 8,
        
        # Open vowels: aa
        'ɑ': 9, 'ɒ': 9, 'a': 9, 'aa': 9, 'ao': 9,
        
        # Mid-open vowels: E
        'ɛ': 10, 'e': 10, 'eh': 10, 'ae': 10,
        
        # Mid vowels: I
        'ɪ': 11, 'i': 11, 'ih': 11, 'iy': 11,
        
        # Close-mid back: O
        'ɔ': 12, 'o': 12, 'oh': 12, 'ow': 12,
        
        # Close back: U
        'ʊ': 13, 'u': 13, 'uh': 13, 'uw': 13,
        
        # R-colored: RR
        'ɜ': 14, 'ə': 14, 'ɚ': 14, 'ɝ': 14,
        'er': 14, 'ah': 14, 'ax': 14,
        
        # Diphthongs
        'aɪ': 15, 'ay': 15, 'ai': 15,
        'aʊ': 16, 'aw': 16, 'au': 16,
        'ɔɪ': 17, 'oy': 17, 'oi': 17,
        
        # Glides
        'w': 18, 'j': 19, 'y': 19, 'jh': 19,
        
        # Aspirated
        'h': 20, 'hh': 20,
    }
    
    @classmethod
    def map_phoneme(cls, phoneme: str) -> int:
        """
        Convert a phoneme string to a viseme ID
        
        Args:
            phoneme: IPA or eSpeak phoneme symbol
            
        Returns:
            Viseme ID (0-20), defaults to 0 (silence) for unknown phonemes
        """
        # Normalize and lookup
        phoneme_lower = phoneme.lower().strip()
        return cls.PHONEME_TO_VISEME.get(phoneme_lower, 0)
    
    @classmethod
    def get_viseme_name(cls, viseme_id: int) -> str:
        """Get the descriptive name for a viseme ID"""
        names = {
            0: "sil", 1: "PP", 2: "FF", 3: "TH", 4: "DD",
            5: "kk", 6: "CH", 7: "SS", 8: "nn", 9: "aa",
            10: "E", 11: "I", 12: "O", 13: "U", 14: "RR",
            15: "ai", 16: "au", 17: "oy", 18: "w", 19: "y", 20: "h"
        }
        return names.get(viseme_id, "sil")
