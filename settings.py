from enum import Enum

BANNED_JIDS = [
    "JID_不明", # Unknown
    "JID_マージカノン" # Magic cannon
]

BANNED_WEAPONS = [
    "IID_フォルクヴァング", # Folkvangr
    "IID_フェンサリル", # Fensalir
    "IID_ノーアトゥーン", # Noatun
    "IID_ミセリコルデ", # Misericorde
    "IID_オヴスキュリテ", # Obscurite
    "IID_リベラシオン", # Liberation
    "IID_ヴィレグランツ", # Wille Glanz
]

class RecruitmentOrder(Enum):
    NORMAL = 0
    RANDOM = 1
    REVERSE = 2

class GenericSetting(Enum):
    KEEP = 0
    RANDOM = 1
