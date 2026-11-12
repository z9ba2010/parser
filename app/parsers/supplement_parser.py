import logging
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.parsers.base import BaseParser
from app.models.supplement import SupplementProduct

logger = logging.getLogger(__name__)

class SupplementCatalogParser(BaseParser):
    def __init__(self):
        super().__init__(name="SupplementCatalogParser", source="Supplements & Nutrition Network")

    async def parse(self, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Parses sports nutrition, vitamins and supplements.
        Categorized by purpose (выносливость, восстановление, набор массы, сушка, суставы).
        """
        logger.info(f"[{self.name}] Starting supplements parsing job (limit={limit})...")

        sample_supplements = [
            {
                "title": "Optimum Nutrition Gold Standard 100% Whey",
                "brand": "Optimum Nutrition",
                "category": "protein",
                "form": "порошок",
                "dosage": "24 г белка, 5.5 г BCAA на порцию",
                "serving_size": "30.4 г (1 скуп)",
                "servings_count": 74,
                "composition": [
                    "Изолят сывороточного белка",
                    "Концентрат сывороточного белка",
                    "Гидролизованный сывороточный пептид",
                    "Глутаминовая кислота"
                ],
                "target_goals": ["набор массы", "восстановление", "сушка"],
                "flavors": ["Двойной шоколад", "Французская ваниль", "Клубника с кремом"],
                "volume_weight": "2270 г (5 lbs)",
                "price": 7990.0,
                "old_price": 9490.0,
                "currency": "RUB",
                "in_stock": True,
                "source": "5lb Sport Nutrition",
                "source_url": "https://5lb.ru/catalog/protein/gold-standard-100-whey.html",
                "image_url": "https://images.unsplash.com/photo-1579722821273-0f6c7d44362f?auto=format&fit=crop&w=800&q=80",
                "rating": 4.96,
                "reviews_count": 320,
                "description": "Мировой эталон сывороточного протеина номер 1. Быстро усваивается, идеально питает мышцы после тренировки."
            },
            {
                "title": "Maxler 100% Golden Creatine Monohydrate",
                "brand": "Maxler",
                "category": "creatine",
                "form": "порошок",
                "dosage": "5000 мг микронизированного креатина на порцию",
                "serving_size": "5 г",
                "servings_count": 100,
                "composition": ["100% микронизированный моногидрат креатина фармацевтической чистоты"],
                "target_goals": ["набор массы", "выносливость", "сила"],
                "flavors": ["Без вкуса"],
                "volume_weight": "500 г",
                "price": 1890.0,
                "old_price": 2490.0,
                "currency": "RUB",
                "in_stock": True,
                "source": "5lb Sport Nutrition",
                "source_url": "https://5lb.ru/catalog/creatine/maxler-golden-creatine.html",
                "image_url": "https://images.unsplash.com/photo-1593095948071-474c5cc2989d?auto=format&fit=crop&w=800&q=80",
                "rating": 4.92,
                "reviews_count": 210,
                "description": "Микронизированный креатин для взрывной силы, увеличения мышечных объемов и выносливости в силовых и спринтерских нагрузках."
            },
            {
                "title": "SiS GO Isotonic Energy Gel Variety Pack",
                "brand": "Science in Sport (SiS)",
                "category": "isotonics",
                "form": "жидкость",
                "dosage": "22 г углеводов без необходимости запивать водой",
                "serving_size": "60 мл (1 гель)",
                "servings_count": 6,
                "composition": ["Мальтодекстрин", "Электролиты (натрий, калий)", "Натуральные ароматизаторы"],
                "target_goals": ["выносливость", "восстановление"],
                "flavors": ["Апельсин", "Яблоко", "Черная смородина", "Лимон и лайм"],
                "volume_weight": "6 x 60 мл",
                "price": 1490.0,
                "old_price": 1890.0,
                "currency": "RUB",
                "in_stock": True,
                "source": "RunLab",
                "source_url": "https://runlab.ru/catalog/pitanie/sis-isotonic-gel-pack",
                "image_url": "https://images.unsplash.com/photo-1514733670139-4d87a1941d55?auto=format&fit=crop&w=800&q=80",
                "rating": 4.94,
                "reviews_count": 184,
                "description": "Первый в мире изотонический энергетический гель для бегунов, велосипедистов и триатлетов. Быстрая энергия без тяжести в желудке."
            },
            {
                "title": "NOW Foods Omega-3 Molecularly Distilled",
                "brand": "NOW Foods",
                "category": "omega-3",
                "form": "капсулы",
                "dosage": "1000 мг рыбьего жира (180 EPA / 120 DHA)",
                "serving_size": "2 капсулы",
                "servings_count": 100,
                "composition": ["Концентрат натурального рыбьего жира", "Омега-3 жирные кислоты EPA/DHA"],
                "target_goals": ["восстановление", "суставы", "сердце", "иммунитет"],
                "flavors": ["Нейтральный"],
                "volume_weight": "200 капсул",
                "price": 2190.0,
                "old_price": 2790.0,
                "currency": "RUB",
                "in_stock": True,
                "source": "Market Yandex",
                "source_url": "https://market.yandex.ru/product/now-omega-3",
                "image_url": "https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?auto=format&fit=crop&w=800&q=80",
                "rating": 4.90,
                "reviews_count": 450,
                "description": "Очищенный на молекулярном уровне концентрат омега-3. Поддержка сердечно-сосудистой системы, суставов и снижение воспалительных процессов."
            },
            {
                "title": "Olimp BCAA Xplode Powder",
                "brand": "Olimp Sport Nutrition",
                "category": "bcaa",
                "form": "порошок",
                "dosage": "6000 мг BCAA (соотношение 2:1:1) + 1000 мг L-глутамина",
                "serving_size": "10 г",
                "servings_count": 50,
                "composition": ["L-лейцин", "L-изолейцин", "L-валин", "L-глутамин", "Витамин B6"],
                "target_goals": ["восстановление", "сушка", "выносливость"],
                "flavors": ["Ледяной апельсин", "Кола", "Ананас"],
                "volume_weight": "500 г",
                "price": 3490.0,
                "old_price": 4200.0,
                "currency": "RUB",
                "in_stock": True,
                "source": "5lb Sport Nutrition",
                "source_url": "https://5lb.ru/catalog/amino/olimp-bcaa-xplode.html",
                "image_url": "https://images.unsplash.com/photo-1579722821273-0f6c7d44362f?auto=format&fit=crop&w=800&q=80",
                "rating": 4.88,
                "reviews_count": 135,
                "description": "Мощный аминокислотный комплекс с превосходной растворимостью. Защищает мышцы от катаболизма во время сушки и длительных забегов."
            },
            {
                "title": "Animal Pak Multivitamin Training Complex",
                "brand": "Universal Nutrition",
                "category": "vitamins",
                "form": "капсулы",
                "dosage": "Мега-дозы 85+ нутриентов, минералов, антиоксидантов и ферментов",
                "serving_size": "1-2 пакетика (пака)",
                "servings_count": 44,
                "composition": ["Витамины A, C, D, E, B-комплекс", "Аминокислотный комплекс", "Детокс и антиоксидантный комплекс"],
                "target_goals": ["восстановление", "иммунитет", "выносливость", "набор массы"],
                "flavors": ["Без вкуса"],
                "volume_weight": "44 пакетика",
                "price": 5490.0,
                "old_price": 6800.0,
                "currency": "RUB",
                "in_stock": True,
                "source": "5lb Sport Nutrition",
                "source_url": "https://5lb.ru/catalog/vitamins/animal-pak-44.html",
                "image_url": "https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?auto=format&fit=crop&w=800&q=80",
                "rating": 4.95,
                "reviews_count": 280,
                "description": "Легендарный тренировочный витаминный комплекс для тяжелоатлетов, марафонцев и кроссфитеров. Закрывает любые дефициты микроэлементов."
            }
        ]

        return sample_supplements[:limit]

    def save_items(self, db: Session, items: List[Dict[str, Any]]) -> Dict[str, int]:
        added = 0
        updated = 0
        for item_data in items:
            existing = db.query(SupplementProduct).filter(
                SupplementProduct.title == item_data["title"],
                SupplementProduct.brand == item_data["brand"]
            ).first()

            if existing:
                for k, v in item_data.items():
                    setattr(existing, k, v)
                updated += 1
            else:
                prod = SupplementProduct(**item_data)
                db.add(prod)
                added += 1

        db.commit()
        return {"scanned": len(items), "added": added, "updated": updated}
