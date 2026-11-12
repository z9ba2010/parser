import re
from typing import Dict, List, Optional, Tuple

# Exact taxonomy defined in Technical Specification Section 3
TAXONOMY_CATEGORIES: Dict[str, List[str]] = {
    "Носки": ["Compressport", "CEP", "X-Bionic", "Falke", "Balega", "Injinji", "Nike", "Asics"],
    "Обувь": ["Nike", "Hoka", "Salomon", "Asics", "Brooks", "Saucony", "New Balance", "Puma", "Adidas"],
    "Гетры (Компрессия)": ["CEP", "Compressport", "2XU", "X-Bionic", "BV Sport", "Nike", "Salomon"],
    "Нижнее белье / Спортивные бра": ["Shock Absorber", "Nike", "Under Armour", "Adidas", "Reebok", "2XU", "Odlo", "Craft"],
    "Шорты": ["Nike", "Adidas", "Salomon", "Asics", "Puma", "Under Armour", "Brooks", "New Balance", "Craft"],
    "Тайтсы": ["2XU", "Nike", "Asics", "Salomon", "Under Armour", "Skins", "Gore Wear", "Craft"],
    "Брюки": ["Nike", "Adidas", "Puma", "Asics", "Salomon", "The North Face", "Under Armour"],
    "Майки": ["Nike", "Asics", "Salomon", "Adidas", "Puma", "Saucony", "Brooks", "Under Armour", "Ciele"],
    "Футболки": ["Nike", "Asics", "Salomon", "Adidas", "Under Armour", "Puma", "Brooks", "Hoka", "Craft"],
    "Лонгсливы": ["Nike", "Asics", "Salomon", "Adidas", "Under Armour", "Gore Wear", "Craft", "The North Face"],
    "Термобелье": ["Craft", "X-Bionic", "Odlo", "Brubeck", "Icebreaker", "The North Face", "Salomon"],
    "Кофты / Мидлееры": ["Nike", "Salomon", "Asics", "The North Face", "Adidas", "Under Armour", "Columbia"],
    "Жилеты": ["Nike", "Salomon", "Asics", "Gore Wear", "Craft", "The North Face", "Adidas"],
    "Ветровки": ["Salomon", "Nike", "Asics", "Gore Wear", "The North Face", "Dynafit", "Adidas", "Craft"],
    "Куртки (Мембраны)": ["Gore Wear", "Salomon", "The North Face", "Nike", "Dynafit", "Arcteryx", "Asics"],
    "Перчатки": ["Salomon", "Nike", "Asics", "Craft", "Gore Wear", "The North Face", "Under Armour"],
    "Баффы (Гейтеры)": ["Buff", "Salomon", "Nike", "Asics", "Craft", "The North Face", "Dynafit"],
    "Кепки / Козырьки": ["Compressport", "Salomon", "Nike", "Buff", "Asics", "Ciele", "Under Armour"],
    "Повязки": ["Buff", "Salomon", "Nike", "Asics", "Compressport", "Craft", "Under Armour"],
    "Шапки": ["Buff", "Salomon", "Asics", "Nike", "Craft", "The North Face", "Gore Wear"],
}

# Canonical list of all allowed categories
CANONICAL_CATEGORIES = list(TAXONOMY_CATEGORIES.keys())

# Comprehensive brand aliases for normalization (sanitization)
BRAND_ALIASES: Dict[str, str] = {
    # Nike
    "nike": "Nike", "найк": "Nike", "nike running": "Nike", "nike pro": "Nike",
    # Asics
    "asics": "Asics", "асикс": "Asics", "asics running": "Asics", "asic": "Asics",
    # Adidas
    "adidas": "Adidas", "адидас": "Adidas", "adidas performance": "Adidas", "adidas terrex": "Adidas",
    # Salomon
    "salomon": "Salomon", "саломон": "Salomon", "salomon running": "Salomon", "s-lab": "Salomon",
    # Hoka
    "hoka": "Hoka", "хока": "Hoka", "hoka one one": "Hoka", "hoka one-one": "Hoka",
    # Puma
    "puma": "Puma", "пума": "Puma", "puma running": "Puma",
    # Brooks
    "brooks": "Brooks", "брукс": "Brooks", "brooks running": "Brooks",
    # Saucony
    "saucony": "Saucony", "сокони": "Saucony", "сакони": "Saucony",
    # New Balance
    "new balance": "New Balance", "нью бэланс": "New Balance", "нью баланс": "New Balance", "nb": "New Balance",
    # Under Armour
    "under armour": "Under Armour", "under armor": "Under Armour", "андер армор": "Under Armour", "ua": "Under Armour",
    # The North Face
    "the north face": "The North Face", "north face": "The North Face", "норт фейс": "The North Face", "tnf": "The North Face",
    # Craft
    "craft": "Craft", "крафт": "Craft", "craft sport": "Craft",
    # Gore Wear
    "gore wear": "Gore Wear", "gore-wear": "Gore Wear", "gore running": "Gore Wear", "gore": "Gore Wear", "гор вер": "Gore Wear",
    # 2XU
    "2xu": "2XU", "two times you": "2XU",
    # Compressport
    "compressport": "Compressport", "компресс порт": "Compressport", "компрессспорт": "Compressport",
    # CEP
    "cep": "CEP", "цеп": "CEP", "cep compression": "CEP",
    # X-Bionic
    "x-bionic": "X-Bionic", "xbionic": "X-Bionic", "x bionic": "X-Bionic", "икс бионик": "X-Bionic",
    # Falke
    "falke": "Falke", "фальке": "Falke",
    # Balega
    "balega": "Balega", "балега": "Balega",
    # Injinji
    "injinji": "Injinji", "инжинджи": "Injinji",
    # BV Sport
    "bv sport": "BV Sport", "bvsport": "BV Sport", "бв спорт": "BV Sport",
    # Shock Absorber
    "shock absorber": "Shock Absorber", "shockabsorber": "Shock Absorber", "шок абсорбер": "Shock Absorber",
    # Reebok
    "reebok": "Reebok", "рибок": "Reebok",
    # Odlo
    "odlo": "Odlo", "одло": "Odlo",
    # Skins
    "skins": "Skins", "скинс": "Skins",
    # Ciele
    "ciele": "Ciele", "ciele athletics": "Ciele", "сиеле": "Ciele",
    # Brubeck
    "brubeck": "Brubeck", "брубек": "Brubeck",
    # Icebreaker
    "icebreaker": "Icebreaker", "айсбрекер": "Icebreaker",
    # Columbia
    "columbia": "Columbia", "колумбия": "Columbia",
    # Dynafit
    "dynafit": "Dynafit", "динафит": "Dynafit",
    # Arcteryx
    "arcteryx": "Arcteryx", "arc'teryx": "Arcteryx", "арктерикс": "Arcteryx",
    # Buff
    "buff": "Buff", "бафф": "Buff",
}

# Category keyword pattern matching
CATEGORY_RULES: List[Tuple[str, List[str]]] = [
    ("Носки", ["носки", "socks", "носок", "полуноски", "следы"]),
    ("Гетры (Компрессия)", ["гетры", "компрессионные гетры", "sleeves", "calf sleeves", "компрессия голени"]),
    ("Нижнее белье / Спортивные бра", ["бра", "спортивный бра", "топ-бра", "спортивный бюстгальтер", "трусы", "боксеры", "sports bra", "underwear"]),
    ("Тайтсы", ["тайтсы", "легинсы", "леггинсы", "лосины", "tights", "leggings"]),
    ("Шорты", ["шорты", "shorts", "велосипедки"]),
    ("Брюки", ["брюки", "штаны", "pants", "trousers", "джоггеры", "joggers", "спортивные брюки"]),
    ("Майки", ["майка", "майка-борцовка", "синглет", "singlet", "tank", "sleeveless"]),
    ("Лонгсливы", ["лонгслив", "longsleeve", "футболка с длинным рукавом", "лонг"]),
    ("Футболки", ["футболка", "футболка с коротким рукавом", "t-shirt", "tee"]),
    ("Термобелье", ["термобелье", "термоштаны", "терморубашка", "термокофта", "baselayer", "thermal"]),
    ("Кофты / Мидлееры", ["кофта", "мидлеер", "джемпер", "свитшот", "худи", "толстовка", "флиска", "midlayer", "fleece", "hoodie"]),
    ("Жилеты", ["жилет", "жилетка", "vest", "gilet"]),
    ("Ветровки", ["ветровка", "ветрозащитная", "windbreaker", "wind jacket"]),
    ("Куртки (Мембраны)", ["мембранная куртка", "куртка gore-tex", "дождевик", "куртка", "jacket", "waterproof", "мембрана"]),
    ("Перчатки", ["перчатки", "варежки", "gloves", "mittens"]),
    ("Баффы (Гейтеры)", ["бафф", "гейтер", "труба на шею", "buff", "neck gaiter"]),
    ("Кепки / Козырьки", ["кепка", "козырек", "бейсболка", "cap", "visor"]),
    ("Повязки", ["повязка на голову", "повязка", "налобная повязка", "headband"]),
    ("Шапки", ["шапка", "бини", "beanie", "hat"]),
    ("Обувь", ["кроссовки", "обувь", "шиповки", "кеды", "марафонки", "полумарафонки", "shoes", "sneakers", "footwear", "running shoes"]),
]

class SanitizerService:
    @staticmethod
    def normalize_brand(raw_brand: Optional[str]) -> str:
        """
        Cleans and maps raw brand names to the canonical brand identifier.
        e.g., 'ASICS', 'асикс', 'Asics Running' -> 'Asics'
        """
        if not raw_brand:
            return "Unknown"

        clean = raw_brand.strip().lower()
        # Remove extra punctuation
        clean = re.sub(r"[^\w\s-]", "", clean).strip()

        if clean in BRAND_ALIASES:
            return BRAND_ALIASES[clean]

        # Substring / word check
        for alias, canonical in BRAND_ALIASES.items():
            if alias in clean or clean in alias:
                return canonical

        # Fallback: title-case the cleaned string
        return raw_brand.strip().title()

    @staticmethod
    def normalize_category(raw_category: Optional[str], title_or_breadcrumbs: str = "") -> str:
        """
        Strictly maps product category / breadcrumbs / title into one of the 20 target categories.
        """
        combined = f"{raw_category or ''} {title_or_breadcrumbs}".lower()

        # Check in rule priority order (more specific items like 'Гетры (Компрессия)' before 'Обувь' or 'Носки')
        for canonical_cat, keywords in CATEGORY_RULES:
            for kw in keywords:
                # Word boundary or inclusion match
                pattern = r"(?:\b|_)" + re.escape(kw) + r"(?:\b|_)"
                if re.search(pattern, combined):
                    return canonical_cat

        # Default fallback if nothing matches
        if raw_category and raw_category in CANONICAL_CATEGORIES:
            return raw_category
        return "Обувь"

    @staticmethod
    def normalize_gender(raw_gender: Optional[str], context_text: str = "") -> str:
        """
        Normalizes gender to: 'Мужской', 'Женский', 'Унисекс'.
        """
        text = f"{raw_gender or ''} {context_text}".lower()

        if any(w in text for w in ["мужск", "мужчин", "men", "male", "man"]) and not any(w in text for w in ["женск", "women", "female"]):
            return "Мужской"
        elif any(w in text for w in ["женск", "женщин", "women", "female", "woman"]):
            return "Женский"
        return "Унисекс"

    @staticmethod
    def is_brand_allowed_for_category(category: str, brand: str) -> bool:
        """Checks if a brand is part of the target taxonomy for a given category."""
        target_brands = TAXONOMY_CATEGORIES.get(category, [])
        return brand in target_brands

sanitizer = SanitizerService()
