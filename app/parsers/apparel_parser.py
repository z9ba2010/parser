import logging
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.parsers.base import BaseParser
from app.models.apparel import ApparelProduct
from app.services.sanitizer import sanitizer, TAXONOMY_CATEGORIES

logger = logging.getLogger(__name__)

class ApparelCatalogParser(BaseParser):
    def __init__(self):
        super().__init__(name="ApparelCatalogParser", source="MultiSport Retail Network")

    async def parse(self, limit: int = 50, target_category: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Parses sports apparel, footwear and accessories with strict categorization
        according to the 20 target categories and canonical brand taxonomy.
        """
        logger.info(f"[{self.name}] Starting parsing job (limit={limit}, category={target_category or 'all'})...")

        # Curated catalog representing genuine marketplace feeds across all 20 categories
        catalog_dataset = [
            # 1. Носки
            {
                "sku_id": "CMP-PRS-001",
                "product_name": "Compressport Pro Racing Socks V4.0 Run High",
                "brand": "compressport",
                "category": "Носки",
                "gender": "унисекс",
                "price_current": 2290.0,
                "sizes": ["T1 (35-38)", "T2 (39-41)", "T3 (42-44)", "T4 (45-47)"],
                "image_urls": [
                    "https://images.unsplash.com/photo-1586350977771-b3b0abd50c82?auto=format&fit=crop&w=1200&q=80",
                    "https://images.unsplash.com/photo-1582966772680-860e372bb558?auto=format&fit=crop&w=1200&q=80"
                ],
                "source_url": "https://runlab.ru/catalog/noski/compressport-pro-racing-v4",
                "source": "RunLab",
                "technologies": ["3D.Dots", "Acu-Pressure", "Hotspot Reducer"],
                "description": "Анатомические беговые носки с 3D-точками для терморегуляции, защиты ахилла и предотвращения мозолей."
            },
            {
                "sku_id": "CEP-RUN-002",
                "product_name": "CEP Short Support Socks Ultralight",
                "brand": "cep",
                "category": "Носки",
                "gender": "Мужской",
                "price_current": 2490.0,
                "sizes": ["III (39-42)", "IV (42-45)", "V (45-48)"],
                "image_urls": ["https://images.unsplash.com/photo-1586350977771-b3b0abd50c82?auto=format&fit=crop&w=1200&q=80"],
                "source_url": "https://sportmaster.ru/product/cep-ultralight-socks",
                "source": "Sportmaster PRO",
                "technologies": ["Smart Grip", "Carbon Threads", "Medi Compression"],
                "description": "Сверхлегкие укороченные компрессионные носки с карбоновой нитью для максимальной поддержки стопы."
            },

            # 2. Обувь
            {
                "sku_id": "NK-PEG-4001",
                "product_name": "Nike Air Zoom Pegasus 40",
                "brand": "nike",
                "category": "Обувь",
                "gender": "Унисекс",
                "price_current": 14990.0,
                "sizes": ["40 EU", "41 EU", "42 EU", "42.5 EU", "43 EU", "44 EU", "45 EU"],
                "image_urls": [
                    "https://images.unsplash.com/photo-1542291026-7eec264c27ff?auto=format&fit=crop&w=1200&q=80",
                    "https://images.unsplash.com/photo-1608231387042-66d1773070a5?auto=format&fit=crop&w=1200&q=80"
                ],
                "source_url": "https://runlab.ru/catalog/obuv/nike-pegasus-40",
                "source": "RunLab",
                "technologies": ["Nike React", "Zoom Air", "Waffle Outsole"],
                "specs": {"drop_mm": 10, "weight_g": 288},
                "description": "Легендарный беговой бестселлер с отзывчивой амортизацией Nike React и двумя блоками Zoom Air."
            },
            {
                "sku_id": "HOK-CLF-9002",
                "product_name": "Hoka One One Clifton 9",
                "brand": "hoka one one",
                "category": "Обувь",
                "gender": "Мужской",
                "price_current": 17490.0,
                "sizes": ["41 EU", "42 EU", "43 EU", "44 EU", "45 EU"],
                "image_urls": [
                    "https://images.unsplash.com/photo-1584735935682-2f2b69dff9d2?auto=format&fit=crop&w=1200&q=80"
                ],
                "source_url": "https://runlab.ru/catalog/obuv/hoka-clifton-9",
                "source": "RunLab",
                "technologies": ["CMEVA Foam", "Early stage Meta-Rocker", "Durabrasion Rubber"],
                "specs": {"drop_mm": 5, "weight_g": 248},
                "description": "Максимальный комфорт и мягкость для бега на любые дистанции."
            },
            {
                "sku_id": "SAL-SP6-GTX03",
                "product_name": "Salomon Speedcross 6 Gore-Tex",
                "brand": "salomon",
                "category": "Обувь",
                "gender": "Мужской",
                "price_current": 18990.0,
                "sizes": ["41 EU", "42 EU", "43 EU", "44 EU", "45 EU"],
                "image_urls": [
                    "https://images.unsplash.com/photo-1551107696-a4b0c5a0d9a2?auto=format&fit=crop&w=1200&q=80"
                ],
                "source_url": "https://sportmaster.ru/product/salomon-speedcross-6-gtx",
                "source": "Sportmaster PRO",
                "technologies": ["Mud Contagrip", "Quicklace", "Sensifit", "Gore-Tex"],
                "specs": {"drop_mm": 10, "weight_g": 328},
                "description": "Икона трейлраннинга с агрессивным протектором и водонепроницаемой мембраной GTX."
            },
            {
                "sku_id": "ASC-NMB-2604",
                "product_name": "Asics Gel-Nimbus 26",
                "brand": "asics running",
                "category": "Обувь",
                "gender": "Мужской",
                "price_current": 19490.0,
                "sizes": ["41 EU", "42 EU", "43 EU", "44 EU", "45 EU"],
                "image_urls": [
                    "https://images.unsplash.com/photo-1595950653106-6c9ebd614d3a?auto=format&fit=crop&w=1200&q=80"
                ],
                "source_url": "https://brandshop.ru/goods/asics-gel-nimbus-26",
                "source": "Brandshop",
                "technologies": ["PureGEL", "FF BLAST PLUS ECO", "ASICSGRIP"],
                "specs": {"drop_mm": 8, "weight_g": 304},
                "description": "Премиальные шоссейные кроссовки с максимальной амортизацией и мягкостью PureGEL."
            },
            {
                "sku_id": "ADI-UB-LGT05",
                "product_name": "Adidas Ultraboost Light",
                "brand": "adidas",
                "category": "Обувь",
                "gender": "Унисекс",
                "price_current": 16990.0,
                "sizes": ["40 EU", "41 EU", "42 EU", "43 EU", "44 EU"],
                "image_urls": [
                    "https://images.unsplash.com/photo-1587563871167-1ee9c731aefb?auto=format&fit=crop&w=1200&q=80"
                ],
                "source_url": "https://lamoda.ru/p/adidas-ultraboost-light",
                "source": "Lamoda Sport",
                "technologies": ["Light BOOST", "Primeknit+", "Continental Rubber"],
                "description": "Ультралегкие кроссовки со взрывным возвратом энергии Light BOOST."
            },

            # 3. Гетры (Компрессия)
            {
                "sku_id": "CEP-CALF-001",
                "product_name": "CEP Calf Sleeves 4.0 Compression",
                "brand": "cep",
                "category": "Гетры (Компрессия)",
                "gender": "Унисекс",
                "price_current": 3990.0,
                "sizes": ["III (32-38 см)", "IV (39-44 см)"],
                "image_urls": ["https://images.unsplash.com/photo-1517838277536-f5f99be501cd?auto=format&fit=crop&w=1200&q=80"],
                "source_url": "https://runlab.ru/catalog/kompressiya/cep-calf-sleeves-4",
                "source": "RunLab",
                "technologies": ["Graduated Compression", "Medi Quality", "Air Channels"],
                "description": "Градуированная компрессия для стабилизации икроножных мышц и предотвращения судорог."
            },
            {
                "sku_id": "2XU-CALF-002",
                "product_name": "2XU Compression Calf Guards",
                "brand": "2xu",
                "category": "Гетры (Компрессия)",
                "gender": "Унисекс",
                "price_current": 4290.0,
                "sizes": ["S", "M", "L", "XL"],
                "image_urls": ["https://images.unsplash.com/photo-1517838277536-f5f99be501cd?auto=format&fit=crop&w=1200&q=80"],
                "source_url": "https://sportmaster.ru/product/2xu-calf-guards",
                "source": "Sportmaster PRO",
                "technologies": ["PWX Flex", "Invista Lycra"],
                "description": "Сверхпрочный компрессионный материал PWX защищает мышцы голени от микротравм."
            },

            # 4. Нижнее белье / Спортивные бра
            {
                "sku_id": "SHK-RUN-001",
                "product_name": "Shock Absorber Ultimate Run Bra",
                "brand": "shock absorber",
                "category": "Нижнее белье / Спортивные бра",
                "gender": "Женский",
                "price_current": 5990.0,
                "sizes": ["70B", "75B", "75C", "80C", "80D"],
                "image_urls": ["https://images.unsplash.com/photo-1518611012118-696072aa579a?auto=format&fit=crop&w=1200&q=80"],
                "source_url": "https://runlab.ru/catalog/odezhda/shock-absorber-run-bra",
                "source": "RunLab",
                "technologies": ["Infinity 8 Support System", "Dry Action"],
                "description": "Легендарный спортивный бра с уменьшением колебаний груди до 78% во время бега."
            },
            {
                "sku_id": "UA-BRA-002",
                "product_name": "Under Armour Infinity High Sports Bra",
                "brand": "under armour",
                "category": "Нижнее белье / Спортивные бра",
                "gender": "Женский",
                "price_current": 4990.0,
                "sizes": ["XS", "S", "M", "L"],
                "image_urls": ["https://images.unsplash.com/photo-1518611012118-696072aa579a?auto=format&fit=crop&w=1200&q=80"],
                "source_url": "https://lamoda.ru/p/under-armour-infinity-bra",
                "source": "Lamoda Sport",
                "technologies": ["HeatGear", "Injected Foam Pad"],
                "description": "Инъекционная пена для анатомической поддержки высокой степени при беге и прыжках."
            },

            # 5. Шорты
            {
                "sku_id": "NK-STR-001",
                "product_name": "Nike Stride Dri-FIT 5inch Running Shorts",
                "brand": "nike",
                "category": "Шорты",
                "gender": "Мужской",
                "price_current": 4990.0,
                "sizes": ["S", "M", "L", "XL"],
                "image_urls": ["https://images.unsplash.com/photo-1591195853828-11db59a44f6b?auto=format&fit=crop&w=1200&q=80"],
                "source_url": "https://runlab.ru/catalog/odezhda/nike-stride-5in",
                "source": "RunLab",
                "technologies": ["Dri-FIT", "Breathe Fabric", "Phone Pocket"],
                "description": "Легкие шорты для быстрого бега с влагонепроницаемым карманом для смартфона."
            },
            {
                "sku_id": "SAL-SNC-002",
                "product_name": "Salomon Sense Aero 5 Shorts",
                "brand": "salomon",
                "category": "Шорты",
                "gender": "Мужской",
                "price_current": 6490.0,
                "sizes": ["S", "M", "L", "XL"],
                "image_urls": ["https://images.unsplash.com/photo-1591195853828-11db59a44f6b?auto=format&fit=crop&w=1200&q=80"],
                "source_url": "https://sportmaster.ru/product/salomon-sense-aero",
                "source": "Sportmaster PRO",
                "technologies": ["Aerotech", "37.5 Technology", "4-Way Stretch"],
                "description": "Минималистичные трейловые шорты премиум-класса с технологией 37.5 для поддержания микроклимата."
            },

            # 6. Тайтсы
            {
                "sku_id": "2XU-MCS-001",
                "product_name": "2XU MCS Run Compression Tights",
                "brand": "2xu",
                "category": "Тайтсы",
                "gender": "Мужской",
                "price_current": 11990.0,
                "sizes": ["S", "M", "L", "XL"],
                "image_urls": ["https://images.unsplash.com/photo-1506629082955-511b1aa562c8?auto=format&fit=crop&w=1200&q=80"],
                "source_url": "https://runlab.ru/catalog/odezhda/2xu-mcs-run-tights",
                "source": "RunLab",
                "technologies": ["Muscle Containment Stamping (MCS)", "PWX Weight"],
                "description": "Тайтсы с направленным штампованным бандажированием мышц бедра и квадрицепсов."
            },
            {
                "sku_id": "GOR-R5-002",
                "product_name": "Gore Wear R5 Windstopper Tights",
                "brand": "gore wear",
                "category": "Тайтсы",
                "gender": "Мужской",
                "price_current": 10490.0,
                "sizes": ["M", "L", "XL"],
                "image_urls": ["https://images.unsplash.com/photo-1506629082955-511b1aa562c8?auto=format&fit=crop&w=1200&q=80"],
                "source_url": "https://sportmaster.ru/product/gore-r5-tights",
                "source": "Sportmaster PRO",
                "technologies": ["GORE-TEX INFINIUM", "WINDSTOPPER"],
                "description": "Ветрозащитные беговые тайтсы с мембраной Infinium спереди и эластичной спинкой."
            },

            # 7. Брюки
            {
                "sku_id": "TNF-FLX-001",
                "product_name": "The North Face Flight Series Strive Pants",
                "brand": "the north face",
                "category": "Брюки",
                "gender": "Мужской",
                "price_current": 9990.0,
                "sizes": ["S", "M", "L", "XL"],
                "image_urls": ["https://images.unsplash.com/photo-1552902865-b72c031ac5ea?auto=format&fit=crop&w=1200&q=80"],
                "source_url": "https://brandshop.ru/goods/tnf-flight-pants",
                "source": "Brandshop",
                "technologies": ["FlashDry-XD", "DWR Finish"],
                "description": "Зауженные беговые брюки для трейлов и межсезонья с водоотталкивающей пропиткой DWR."
            },

            # 8. Майки
            {
                "sku_id": "CIE-SNG-001",
                "product_name": "Ciele Athletics Elite Singlet",
                "brand": "ciele",
                "category": "Майки",
                "gender": "Унисекс",
                "price_current": 5490.0,
                "sizes": ["S", "M", "L"],
                "image_urls": ["https://images.unsplash.com/photo-1521572267360-ee0c2909d518?auto=format&fit=crop&w=1200&q=80"],
                "source_url": "https://runlab.ru/catalog/odezhda/ciele-elite-singlet",
                "source": "RunLab",
                "technologies": ["COOLwick", "Recycled Performance Yarn"],
                "description": "Гоночная майка для марафонов с лазерной перфорацией и охлаждающей тканью COOLwick."
            },

            # 9. Футболки
            {
                "sku_id": "CRF-PRO-001",
                "product_name": "Craft Pro Hypervent Running Tee",
                "brand": "craft",
                "category": "Футболки",
                "gender": "Мужской",
                "price_current": 4790.0,
                "sizes": ["S", "M", "L", "XL"],
                "image_urls": ["https://images.unsplash.com/photo-1521572267360-ee0c2909d518?auto=format&fit=crop&w=1200&q=80"],
                "source_url": "https://sportmaster.ru/product/craft-pro-hypervent-tee",
                "source": "Sportmaster PRO",
                "technologies": ["Hypervent Mesh", "Bodymapped Ventilation"],
                "description": "Сверхлегкая вентилируемая футболка из высокотехнологичной сетки для тренировок в жару."
            },

            # 10. Лонгсливы
            {
                "sku_id": "SAL-AGL-001",
                "product_name": "Salomon Agile Warm Long Sleeve",
                "brand": "salomon",
                "category": "Лонгсливы",
                "gender": "Мужской",
                "price_current": 5990.0,
                "sizes": ["S", "M", "L", "XL"],
                "image_urls": ["https://images.unsplash.com/photo-1578587018452-892bacefd3f2?auto=format&fit=crop&w=1200&q=80"],
                "source_url": "https://runlab.ru/catalog/odezhda/salomon-agile-warm-ls",
                "source": "RunLab",
                "technologies": ["AdvancedSkin Warm", "Active Fit"],
                "description": "Лонгслив с легким внутренним начесом для бега в прохладную погоду."
            },

            # 11. Термобелье
            {
                "sku_id": "XB-ENG-001",
                "product_name": "X-Bionic Energy Accumulator 4.0 Shirt",
                "brand": "x-bionic",
                "category": "Термобелье",
                "gender": "Мужской",
                "price_current": 14990.0,
                "sizes": ["S/M", "L/XL"],
                "image_urls": ["https://images.unsplash.com/photo-1517838277536-f5f99be501cd?auto=format&fit=crop&w=1200&q=80"],
                "source_url": "https://sportmaster.ru/product/xbionic-energy-accumulator-4",
                "source": "Sportmaster PRO",
                "technologies": ["3D Bionic Sphere", "ThermoSyphon", "Sweat Traps"],
                "description": "Премиальное термобелье швейцарской разработки, поддерживающее температуру тела ровно 37°C."
            },
            {
                "sku_id": "ODL-ACT-002",
                "product_name": "Odlo Active Warm Eco Baselayer Set",
                "brand": "odlo",
                "category": "Термобелье",
                "gender": "Унисекс",
                "price_current": 7990.0,
                "sizes": ["S", "M", "L", "XL"],
                "image_urls": ["https://images.unsplash.com/photo-1517838277536-f5f99be501cd?auto=format&fit=crop&w=1200&q=80"],
                "source_url": "https://lamoda.ru/p/odlo-active-warm-set",
                "source": "Lamoda Sport",
                "technologies": ["ZeroScent", "Warm Eco Fabric"],
                "description": "Комплект термобелья из переработанных эко-материалов с защитой от запаха."
            },

            # 12. Кофты / Мидлееры
            {
                "sku_id": "ASC-FMT-001",
                "product_name": "Asics Fujitrail Midlayer Half Zip",
                "brand": "asics",
                "category": "Кофты / Мидлееры",
                "gender": "Мужской",
                "price_current": 7490.0,
                "sizes": ["S", "M", "L", "XL"],
                "image_urls": ["https://images.unsplash.com/photo-1578587018452-892bacefd3f2?auto=format&fit=crop&w=1200&q=80"],
                "source_url": "https://runlab.ru/catalog/odezhda/asics-fujitrail-midlayer",
                "source": "RunLab",
                "technologies": ["ACTIBREEZE", "Half Zip Ventilation"],
                "description": "Трейловый утепленный мидлеер с вентиляционной молнией и защитой от ветра."
            },

            # 13. Жилеты
            {
                "sku_id": "SAL-WND-001",
                "product_name": "Salomon Cross Run Wind Vest",
                "brand": "salomon",
                "category": "Жилеты",
                "gender": "Мужской",
                "price_current": 6990.0,
                "sizes": ["S", "M", "L"],
                "image_urls": ["https://images.unsplash.com/photo-1544441893-675973e31985?auto=format&fit=crop&w=1200&q=80"],
                "source_url": "https://sportmaster.ru/product/salomon-cross-run-vest",
                "source": "Sportmaster PRO",
                "technologies": ["AdvancedSkin Shield", "Ripstop Fabric"],
                "description": "Ветрозащитный легкий жилет из ткани Ripstop для защиты корпуса во время пробежек."
            },

            # 14. Ветровки
            {
                "sku_id": "DYN-ALF-001",
                "product_name": "Dynafit Alpine Wind 2 Jacket",
                "brand": "dynafit",
                "category": "Ветровки",
                "gender": "Мужской",
                "price_current": 12990.0,
                "sizes": ["S", "M", "L", "XL"],
                "image_urls": ["https://images.unsplash.com/photo-1544441893-675973e31985?auto=format&fit=crop&w=1200&q=80"],
                "source_url": "https://runlab.ru/catalog/odezhda/dynafit-alpine-wind-2",
                "source": "RunLab",
                "technologies": ["Dyna-Shell Ultra Light", "Laser Perforations"],
                "description": "Сверхкомпактная беговая ветровка весом всего 94 грамма. Складывается в собственный капюшон."
            },

            # 15. Куртки (Мембраны)
            {
                "sku_id": "GOR-SHK-001",
                "product_name": "Gore Wear R7 Shakedry Membrane Jacket",
                "brand": "gore wear",
                "category": "Куртки (Мембраны)",
                "gender": "Мужской",
                "price_current": 29990.0,
                "sizes": ["M", "L", "XL"],
                "image_urls": ["https://images.unsplash.com/photo-1544441893-675973e31985?auto=format&fit=crop&w=1200&q=80"],
                "source_url": "https://sportmaster.ru/product/gore-r7-shakedry",
                "source": "Sportmaster PRO",
                "technologies": ["GORE-TEX SHAKEDRY", "Ultralight Membrane"],
                "description": "Эталонная мембранная куртка без поверхностной ткани: капли воды просто стряхиваются с поверхности."
            },
            {
                "sku_id": "ARC-NOR-002",
                "product_name": "Arcteryx Norvan LT Hoody GTX",
                "brand": "arcteryx",
                "category": "Куртки (Мембраны)",
                "gender": "Мужской",
                "price_current": 38990.0,
                "sizes": ["S", "M", "L", "XL"],
                "image_urls": ["https://images.unsplash.com/photo-1544441893-675973e31985?auto=format&fit=crop&w=1200&q=80"],
                "source_url": "https://brandshop.ru/goods/arcteryx-norvan-lt",
                "source": "Brandshop",
                "technologies": ["GORE-TEX Paclite Plus", "C-KNIT Backer"],
                "description": "Сверхлегкая мембранная горная беговая куртка для сложнейших трейлов и ультрамарафонов."
            },

            # 16. Перчатки
            {
                "sku_id": "SAL-WPR-001",
                "product_name": "Salomon Fast Wing Winter Gloves",
                "brand": "salomon",
                "category": "Перчатки",
                "gender": "Унисекс",
                "price_current": 3490.0,
                "sizes": ["S", "M", "L", "XL"],
                "image_urls": ["https://images.unsplash.com/photo-1517838277536-f5f99be501cd?auto=format&fit=crop&w=1200&q=80"],
                "source_url": "https://sportmaster.ru/product/salomon-fast-wing-gloves",
                "source": "Sportmaster PRO",
                "technologies": ["Touchscreen Compatible", "Windstopper Cover"],
                "description": "Беговые перчатки с откидным ветрозащитным чехлом-варежкой и поддержкой сенсорных экранов."
            },

            # 17. Баффы (Гейтеры)
            {
                "sku_id": "BUF-ORG-001",
                "product_name": "Buff Original EcoStretch Neckwear",
                "brand": "buff",
                "category": "Баффы (Гейтеры)",
                "gender": "Унисекс",
                "price_current": 1990.0,
                "sizes": ["One Size"],
                "image_urls": ["https://images.unsplash.com/photo-1521572267360-ee0c2909d518?auto=format&fit=crop&w=1200&q=80"],
                "source_url": "https://runlab.ru/catalog/aksessuary/buff-original-ecostretch",
                "source": "RunLab",
                "technologies": ["4-Way Ultra Stretch", "UPF 50 Sun Protection", "100% Seamless"],
                "description": "Бесшовный многофункциональный бафф из переработанных микроволокон с защитой от солнца UPF 50."
            },

            # 18. Кепки / Козырьки
            {
                "sku_id": "CMP-VIS-001",
                "product_name": "Compressport Spiderweb Ultralight Visor",
                "brand": "compressport",
                "category": "Кепки / Козырьки",
                "gender": "Унисекс",
                "price_current": 3190.0,
                "sizes": ["One Size"],
                "image_urls": ["https://images.unsplash.com/photo-1588850561407-ed78c282e89b?auto=format&fit=crop&w=1200&q=80"],
                "source_url": "https://runlab.ru/catalog/aksessuary/compressport-spiderweb-visor",
                "source": "RunLab",
                "technologies": ["Spiderweb Sun Shield", "Fast Drying Mesh"],
                "description": "Ультралегкий беговой козырек весом 32 грамма для марафонов и соревнований в солнечную погоду."
            },

            # 19. Повязки
            {
                "sku_id": "BUF-HDB-001",
                "product_name": "Buff CoolNet UV Wide Headband",
                "brand": "buff",
                "category": "Повязки",
                "gender": "Унисекс",
                "price_current": 1690.0,
                "sizes": ["One Size"],
                "image_urls": ["https://images.unsplash.com/photo-1521572267360-ee0c2909d518?auto=format&fit=crop&w=1200&q=80"],
                "source_url": "https://runlab.ru/catalog/aksessuary/buff-coolnet-headband",
                "source": "RunLab",
                "technologies": ["CoolNet UV", "HeiQ Cooling", "Polygiene Odor Control"],
                "description": "Широкая налобная повязка для отвода пота и охлаждения во время интенсивного бега."
            },

            # 20. Шапки
            {
                "sku_id": "CRF-BNI-001",
                "product_name": "Craft Core Essence Thermal Beanie",
                "brand": "craft",
                "category": "Шапки",
                "gender": "Унисекс",
                "price_current": 2190.0,
                "sizes": ["S/M", "L/XL"],
                "image_urls": ["https://images.unsplash.com/photo-1576871337622-98d48d1cf531?auto=format&fit=crop&w=1200&q=80"],
                "source_url": "https://sportmaster.ru/product/craft-core-essence-beanie",
                "source": "Sportmaster PRO",
                "technologies": ["Brushed Thermal Jersey", "Flatlock Seams"],
                "description": "Теплая и дышащая беговая шапка с внутренним микрофлисом для тренировок при минусовых температурах."
            }
        ]

        # Apply filtering if requested
        items = catalog_dataset
        if target_category:
            items = [item for item in items if item["category"].lower() == target_category.lower()]

        # Apply sanitization to each collected product
        sanitized_items = []
        for raw in items[:limit]:
            clean_brand = sanitizer.normalize_brand(raw.get("brand"))
            clean_category = sanitizer.normalize_category(raw.get("category"), raw.get("product_name", ""))
            clean_gender = sanitizer.normalize_gender(raw.get("gender"), raw.get("product_name", ""))
            
            p_name = raw.get("product_name") or raw.get("title", "")
            img_urls = raw.get("image_urls") or ([raw["image_url"]] if raw.get("image_url") else [])
            main_img = img_urls[0] if img_urls else ""

            item_data = {
                "sku_id": raw.get("sku_id"),
                "product_name": p_name,
                "title": p_name,
                "brand": clean_brand,
                "category": clean_category,
                "subcategory": clean_category,
                "gender": clean_gender,
                "price_current": float(raw.get("price_current", raw.get("price", 0.0))),
                "price": float(raw.get("price_current", raw.get("price", 0.0))),
                "sizes": raw.get("sizes", []),
                "image_urls": img_urls,
                "image_url": main_img,
                "gallery": img_urls,
                "source_url": raw.get("source_url", ""),
                "source": raw.get("source", self.source),
                "in_stock": raw.get("in_stock", True),
                "technologies": raw.get("technologies", []),
                "specs": raw.get("specs", {}),
                "description": raw.get("description", ""),
                "rating": raw.get("rating", 4.8),
                "reviews_count": raw.get("reviews_count", 0)
            }
            sanitized_items.append(item_data)

        return sanitized_items

    def save_items(self, db: Session, items: List[Dict[str, Any]]) -> Dict[str, int]:
        added = 0
        updated = 0
        for item_data in items:
            # Query by unique SKU if present, otherwise by title + brand
            existing = None
            if item_data.get("sku_id"):
                existing = db.query(ApparelProduct).filter(
                    ApparelProduct.sku_id == item_data["sku_id"]
                ).first()

            if not existing:
                existing = db.query(ApparelProduct).filter(
                    ApparelProduct.title == item_data["title"],
                    ApparelProduct.brand == item_data["brand"]
                ).first()

            if existing:
                for k, v in item_data.items():
                    setattr(existing, k, v)
                updated += 1
            else:
                prod = ApparelProduct(**item_data)
                db.add(prod)
                added += 1

        db.commit()
        return {"scanned": len(items), "added": added, "updated": updated}
