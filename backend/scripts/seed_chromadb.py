"""
Seed ChromaDB with mock market intelligence data for testing.
Run this script to populate the ChromaDB collection with 20+ news articles.
"""

import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

import chromadb
from chromadb.config import Settings


def create_mock_news_data():
    """Generate 50 mock news articles for DENSO market intelligence."""
    # Use current date for recent news
    base_date = datetime.now()
    
    news_articles = [
        {
            "id": "news-002",
            "document": "Giá thép thô tại Trung Quốc tăng 8% trong tháng 11 do chính sách hạn chế sản xuất của chính phủ. Điều này tác động trực tiếp đến chi phí sản xuất AC compressor, dự kiến giảm margin 3-5% trong Q1 2025.",
            "metadata": {
                "title": "Giá thép Trung Quốc tăng 8% trong tháng 11",
                "source": "Bloomberg",
                "article_date": (base_date - timedelta(days=12)).isoformat(),
                "category": "supply_chain",
                "sentiment": "negative",
                "risk_score": 0.72,
                "related_products": ["447220-1510", "447260-5020"],
                "tags": ["thép", "nguyên liệu", "Trung Quốc", "giá cả"],
                "language": "vi",
            }
        },
        {
            "id": "news-003",
            "document": "NGK Spark Plugs announces investment of $50 million to build new manufacturing plant in Thailand with capacity of 10 million units per year. This increases competition in ASEAN market.",
            "metadata": {
                "title": "NGK mở nhà máy mới tại Thái Lan",
                "source": "Reuters",
                "article_date": (base_date - timedelta(days=8)).isoformat(),
                "category": "competition",
                "sentiment": "negative",
                "risk_score": 0.68,
                "related_products": ["VCH20", "VK20", "PK16TT"],
                "tags": ["NGK", "cạnh tranh", "Thái Lan", "bugi"],
                "language": "en",
            }
        },
        {
            "id": "news-004",
            "document": "Toyota Vietnam công bố kế hoạch ra mắt 3 mẫu xe điện vào năm 2025, dự kiến giảm nhu cầu spark plugs truyền thống nhưng tăng nhu cầu sensors và inverters.",
            "metadata": {
                "title": "Toyota VN công bố dự án xe điện 2025",
                "source": "VnExpress",
                "article_date": (base_date - timedelta(days=15)).isoformat(),
                "category": "market_trend",
                "sentiment": "neutral",
                "risk_score": 0.55,
                "related_products": ["VCH20", "PK16TT", "O2-SENSOR-234"],
                "tags": ["Toyota", "xe điện", "EV", "Vietnam"],
                "language": "vi",
            }
        },
        {
            "id": "news-005",
            "document": "Shortage of semiconductor chips continues to impact automotive production in Q4 2024. DENSO suppliers report 20% delay in delivery of electronic components for AC systems.",
            "metadata": {
                "title": "Thiếu hụt chip bán dẫn ảnh hưởng sản xuất ô tô",
                "source": "Automotive News",
                "article_date": (base_date - timedelta(days=20)).isoformat(),
                "category": "supply_chain",
                "sentiment": "negative",
                "risk_score": 0.78,
                "related_products": ["447220-1510", "ECU-MODULE-89"],
                "tags": ["chip shortage", "semiconductor", "delay"],
                "language": "en",
            }
        },
        {
            "id": "news-006",
            "document": "Chính phủ Indonesia tăng thuế nhập khẩu phụ tùng ô tô từ 5% lên 8%, nhằm bảo vệ ngành sản xuất nội địa. DENSO dự kiến tăng giá bán 3-4% tại thị trường Indonesia.",
            "metadata": {
                "title": "Indonesia tăng thuế nhập khẩu phụ tùng ô tô",
                "source": "Jakarta Post",
                "article_date": (base_date - timedelta(days=3)).isoformat(),
                "category": "regulation",
                "sentiment": "negative",
                "risk_score": 0.62,
                "related_products": ["VCH20", "447220-1510", "PK16TT"],
                "tags": ["thuế", "Indonesia", "regulation"],
                "language": "vi",
            }
        },
        {
            "id": "news-007",
            "document": "Bosch announces breakthrough in Iridium spark plug technology with 30% longer lifespan. Market analysts predict pressure on DENSO to upgrade product line by Q2 2025.",
            "metadata": {
                "title": "Bosch ra mắt công nghệ bugi Iridium mới",
                "source": "Automotive Engineering",
                "article_date": (base_date - timedelta(days=10)).isoformat(),
                "category": "competition",
                "sentiment": "negative",
                "risk_score": 0.70,
                "related_products": ["VCH20", "VK20"],
                "tags": ["Bosch", "innovation", "technology"],
                "language": "en",
            }
        },
        {
            "id": "news-008",
            "document": "Đình công tại nhà máy của nhà cung cấp iridium chính ở Nam Phi, dự kiến thiếu hụt 15% nguồn cung nguyên liệu trong tháng 12. DENSO đang tìm kiếm nhà cung cấp thay thế.",
            "metadata": {
                "title": "Đình công tại nhà máy iridium Nam Phi",
                "source": "Mining Weekly",
                "article_date": (base_date - timedelta(days=7)).isoformat(),
                "category": "supply_chain",
                "sentiment": "negative",
                "risk_score": 0.82,
                "related_products": ["VCH20", "VK20"],
                "tags": ["đình công", "iridium", "Nam Phi", "nguyên liệu"],
                "language": "vi",
            }
        },
        {
            "id": "news-009",
            "document": "Vietnam automotive market grows 18% in 2024, driven by rising middle class and urbanization. Demand for AC systems and filters expected to increase 20% in 2025.",
            "metadata": {
                "title": "Thị trường ô tô Việt Nam tăng trưởng 18%",
                "source": "Vietnam Investment Review",
                "article_date": (base_date - timedelta(days=25)).isoformat(),
                "category": "market_trend",
                "sentiment": "positive",
                "risk_score": 0.25,
                "related_products": ["447220-1510", "FILTER-AIR-123", "FILTER-CABIN-456"],
                "tags": ["Vietnam", "growth", "market expansion"],
                "language": "en",
            }
        },
        {
            "id": "news-010",
            "document": "Cảnh báo sóng thần tại bờ biển Đông Nhật Bản sau động đất 6.8 độ Richter. Các cảng biển Sendai và Niigata tạm đóng cửa, ảnh hưởng logistics khu vực.",
            "metadata": {
                "title": "Động đất và cảnh báo sóng thần tại Nhật Bản",
                "source": "Japan Times",
                "article_date": (base_date - timedelta(days=2)).isoformat(),
                "category": "logistics",
                "sentiment": "negative",
                "risk_score": 0.88,
                "related_products": ["ALL"],
                "tags": ["động đất", "sóng thần", "Nhật Bản", "cảng biển"],
                "language": "vi",
            }
        },
        {
            "id": "news-011",
            "document": "EU announces stricter emission standards for 2026, requiring advanced O2 sensors and catalytic converters. DENSO R&D investing $100M in sensor technology.",
            "metadata": {
                "title": "EU tăng cường tiêu chuẩn khí thải 2026",
                "source": "European Automobile",
                "article_date": (base_date - timedelta(days=18)).isoformat(),
                "category": "regulation",
                "sentiment": "neutral",
                "risk_score": 0.45,
                "related_products": ["O2-SENSOR-234", "CATALYTIC-CONV-789"],
                "tags": ["EU", "emission", "regulation", "sensor"],
                "language": "en",
            }
        },
        {
            "id": "news-012",
            "document": "Tập đoàn Hyundai mở rộng nhà máy tại Indonesia, tăng công suất lên 300,000 xe/năm. Cơ hội cho DENSO tăng đơn hàng OEM AC compressor và spark plugs.",
            "metadata": {
                "title": "Hyundai mở rộng nhà máy Indonesia",
                "source": "Korea Herald",
                "article_date": (base_date - timedelta(days=14)).isoformat(),
                "category": "market_trend",
                "sentiment": "positive",
                "risk_score": 0.20,
                "related_products": ["447220-1510", "VCH20", "PK16TT"],
                "tags": ["Hyundai", "Indonesia", "expansion", "OEM"],
                "language": "vi",
            }
        },
        {
            "id": "news-013",
            "document": "Cyber attack on major shipping company Maersk causes delays at Singapore port. Container ships rerouted, adding 3-5 days to ASEAN delivery schedules.",
            "metadata": {
                "title": "Tấn công mạng gây gián đoạn cảng Singapore",
                "source": "Maritime Executive",
                "article_date": (base_date - timedelta(days=4)).isoformat(),
                "category": "logistics",
                "sentiment": "negative",
                "risk_score": 0.75,
                "related_products": ["ALL"],
                "tags": ["cyber attack", "Singapore", "logistics", "delay"],
                "language": "en",
            }
        },
        {
            "id": "news-014",
            "document": "Giá dầu thô tăng 12% trong tháng 11 do OPEC cắt giảm sản lượng. Chi phí vận chuyển và sản xuất nhựa tăng, ảnh hưởng đến filter và plastic components.",
            "metadata": {
                "title": "Giá dầu tăng 12% do OPEC cắt giảm sản lượng",
                "source": "Oil Price",
                "article_date": (base_date - timedelta(days=9)).isoformat(),
                "category": "supply_chain",
                "sentiment": "negative",
                "risk_score": 0.68,
                "related_products": ["FILTER-OIL-999", "FILTER-AIR-123", "PLASTIC-PART-555"],
                "tags": ["oil price", "OPEC", "transportation cost"],
                "language": "vi",
            }
        },
        {
            "id": "news-015",
            "document": "Continental AG recalls 500,000 defective fuel injectors due to quality issues. Opportunity for DENSO to gain market share in fuel system components.",
            "metadata": {
                "title": "Continental thu hồi 500,000 kim phun nhiên liệu",
                "source": "Automotive News Europe",
                "article_date": (base_date - timedelta(days=11)).isoformat(),
                "category": "competition",
                "sentiment": "positive",
                "risk_score": 0.30,
                "related_products": ["FUEL-INJ-777", "FUEL-PUMP-888"],
                "tags": ["recall", "Continental", "opportunity"],
                "language": "en",
            }
        },
        {
            "id": "news-016",
            "document": "Thái Lan triển khai chương trình trợ cấp mua xe hybrid, dự kiến tăng 40% doanh số hybrid vehicles trong 2025. Nhu cầu high-efficiency spark plugs và sensors tăng mạnh.",
            "metadata": {
                "title": "Thái Lan trợ cấp xe hybrid 2025",
                "source": "Bangkok Post",
                "article_date": (base_date - timedelta(days=6)).isoformat(),
                "category": "market_trend",
                "sentiment": "positive",
                "risk_score": 0.22,
                "related_products": ["VCH20", "VK20", "O2-SENSOR-234"],
                "tags": ["Thailand", "hybrid", "subsidy", "government"],
                "language": "vi",
            }
        },
        {
            "id": "news-017",
            "document": "Major warehouse fire at DENSO distributor in Manila destroys inventory worth $2M. Spark plugs and filters stock depleted, expected 4-6 weeks to restock.",
            "metadata": {
                "title": "Cháy kho phân phối DENSO tại Manila",
                "source": "Philippines Star",
                "article_date": (base_date - timedelta(days=1)).isoformat(),
                "category": "supply_chain",
                "sentiment": "negative",
                "risk_score": 0.90,
                "related_products": ["VCH20", "PK16TT", "FILTER-AIR-123"],
                "tags": ["fire", "Manila", "inventory loss", "Philippines"],
                "language": "en",
            }
        },
        {
            "id": "news-018",
            "document": "Tesla opens Gigafactory in Malaysia, plans to produce 100,000 EVs annually. While threatening traditional spark plug demand, creates opportunities for EV sensors and cooling systems.",
            "metadata": {
                "title": "Tesla mở Gigafactory tại Malaysia",
                "source": "Electrek",
                "article_date": (base_date - timedelta(days=13)).isoformat(),
                "category": "market_trend",
                "sentiment": "neutral",
                "risk_score": 0.50,
                "related_products": ["SENSOR-TEMP-456", "COOLANT-PUMP-789"],
                "tags": ["Tesla", "Malaysia", "EV", "Gigafactory"],
                "language": "en",
            }
        },
        {
            "id": "news-019",
            "document": "Chính phủ Việt Nam giảm thuế tiêu thụ đặc biệt cho xe hybrid từ 15% xuống 10%, có hiệu lực từ tháng 1/2025. Dự kiến tăng 25% nhu cầu phụ tùng hybrid.",
            "metadata": {
                "title": "Việt Nam giảm thuế xe hybrid",
                "source": "Vietnam News",
                "article_date": (base_date - timedelta(days=16)).isoformat(),
                "category": "regulation",
                "sentiment": "positive",
                "risk_score": 0.18,
                "related_products": ["VCH20", "O2-SENSOR-234", "HYBRID-BATTERY-999"],
                "tags": ["Vietnam", "tax reduction", "hybrid", "government policy"],
                "language": "vi",
            }
        },
        {
            "id": "news-020",
            "document": "Global platinum price drops 15% due to oversupply from South African mines. Opportunity to reduce production cost of catalytic converters and O2 sensors.",
            "metadata": {
                "title": "Giá platinum toàn cầu giảm 15%",
                "source": "Financial Times",
                "article_date": (base_date - timedelta(days=22)).isoformat(),
                "category": "supply_chain",
                "sentiment": "positive",
                "risk_score": 0.25,
                "related_products": ["CATALYTIC-CONV-789", "O2-SENSOR-234"],
                "tags": ["platinum", "commodity price", "cost reduction"],
                "language": "en",
            }
        },
        {
            "id": "news-021",
            "document": "China announces 5-year plan to dominate EV battery market, targeting 70% global market share by 2027. CATL and BYD expanding production capacity aggressively.",
            "metadata": {
                "title": "China targets 70% EV battery market dominance",
                "source": "South China Morning Post",
                "article_date": (base_date - timedelta(days=19)).isoformat(),
                "category": "competition",
                "sentiment": "negative",
                "risk_score": 0.66,
                "related_products": ["HYBRID-BATTERY-999", "EV-INVERTER-888"],
                "tags": ["China", "EV battery", "competition", "market share"],
                "language": "en",
            }
        },
        {
            "id": "news-022",
            "document": "Đài Loan hạn chế xuất khẩu chip bán dẫn sang một số quốc gia do vấn đề an ninh quốc gia. Ảnh hưởng đến chuỗi cung ứng điện tử ô tô toàn cầu.",
            "metadata": {
                "title": "Đài Loan hạn chế xuất khẩu chip bán dẫn",
                "source": "Taiwan News",
                "article_date": (base_date - timedelta(days=17)).isoformat(),
                "category": "supply_chain",
                "sentiment": "negative",
                "risk_score": 0.79,
                "related_products": ["ECU-MODULE-89", "SENSOR-TEMP-456"],
                "tags": ["Taiwan", "semiconductor", "export restriction", "geopolitics"],
                "language": "vi",
            }
        },
        {
            "id": "news-023",
            "document": "Malaysia offers 10-year tax incentives for automotive parts manufacturers. Expected to attract $5B investment and create 50,000 jobs by 2028.",
            "metadata": {
                "title": "Malaysia khuyến khích đầu tư sản xuất phụ tùng ô tô",
                "source": "The Star Malaysia",
                "article_date": (base_date - timedelta(days=21)).isoformat(),
                "category": "market_trend",
                "sentiment": "positive",
                "risk_score": 0.15,
                "related_products": ["ALL"],
                "tags": ["Malaysia", "investment", "tax incentive", "expansion"],
                "language": "en",
            }
        },
        {
            "id": "news-024",
            "document": "Hạn hán nghiêm trọng tại Panama gây tắc nghẽn kênh đào Panama, thời gian vận chuyển container tăng 15-20 ngày. Chi phí logistics tăng 30%.",
            "metadata": {
                "title": "Hạn hán Panama gây tắc nghẽn kênh đào",
                "source": "Lloyd's List",
                "article_date": (base_date - timedelta(days=24)).isoformat(),
                "category": "logistics",
                "sentiment": "negative",
                "risk_score": 0.81,
                "related_products": ["ALL"],
                "tags": ["Panama Canal", "drought", "shipping delay", "logistics"],
                "language": "vi",
            }
        },
        {
            "id": "news-025",
            "document": "Ford recalls 2.3M vehicles globally due to defective brake system. Opportunity for DENSO to gain market share in brake components and sensors.",
            "metadata": {
                "title": "Ford thu hồi 2.3 triệu xe do lỗi phanh",
                "source": "Automotive News",
                "article_date": (base_date - timedelta(days=26)).isoformat(),
                "category": "competition",
                "sentiment": "positive",
                "risk_score": 0.28,
                "related_products": ["BRAKE-SENSOR-567", "ABS-MODULE-234"],
                "tags": ["Ford", "recall", "brake system", "opportunity"],
                "language": "en",
            }
        },
        {
            "id": "news-026",
            "document": "Vingroup announces $1.2B investment in VinFast EV expansion to US and Europe. Plans to produce 300,000 EVs annually by 2026, seeking tier-1 suppliers.",
            "metadata": {
                "title": "VinFast mở rộng sản xuất EV ra thị trường Mỹ và Châu Âu",
                "source": "VnExpress",
                "article_date": (base_date - timedelta(days=23)).isoformat(),
                "category": "market_trend",
                "sentiment": "positive",
                "risk_score": 0.18,
                "related_products": ["EV-INVERTER-888", "SENSOR-TEMP-456", "COOLANT-PUMP-789"],
                "tags": ["VinFast", "Vietnam", "EV", "expansion", "OEM opportunity"],
                "language": "en",
            }
        },
        {
            "id": "news-027",
            "document": "Đức ban hành quy định mới về tái chế phụ tùng ô tô, yêu cầu 80% linh kiện phải có khả năng tái chế từ năm 2026. Ảnh hưởng đến thiết kế sản phẩm.",
            "metadata": {
                "title": "Đức yêu cầu 80% linh kiện ô tô có thể tái chế",
                "source": "Deutsche Welle",
                "article_date": (base_date - timedelta(days=28)).isoformat(),
                "category": "regulation",
                "sentiment": "neutral",
                "risk_score": 0.52,
                "related_products": ["ALL"],
                "tags": ["Germany", "recycling", "regulation", "sustainability"],
                "language": "vi",
            }
        },
        {
            "id": "news-028",
            "document": "Indian automotive market grows 22% in Q3 2025, driven by rising middle class and government EV subsidies. Tata Motors and Mahindra leading domestic sales.",
            "metadata": {
                "title": "Thị trường ô tô Ấn Độ tăng trưởng 22%",
                "source": "Economic Times India",
                "article_date": (base_date - timedelta(days=30)).isoformat(),
                "category": "market_trend",
                "sentiment": "positive",
                "risk_score": 0.20,
                "related_products": ["VCH20", "447220-1510", "FILTER-AIR-123"],
                "tags": ["India", "growth", "market expansion", "EV subsidy"],
                "language": "en",
            }
        },
        {
            "id": "news-029",
            "document": "Đình công lan rộng tại các nhà máy Stellantis ở Ý và Pháp, ảnh hưởng đến 15 nhà máy sản xuất ô tô. Dự kiến giảm 200,000 xe trong Q4.",
            "metadata": {
                "title": "Đình công Stellantis ảnh hưởng 15 nhà máy châu Âu",
                "source": "Reuters",
                "article_date": (base_date - timedelta(days=6)).isoformat(),
                "category": "supply_chain",
                "sentiment": "negative",
                "risk_score": 0.73,
                "related_products": ["ALL"],
                "tags": ["strike", "Stellantis", "Europe", "production halt"],
                "language": "vi",
            }
        },
        {
            "id": "news-030",
            "document": "Breakthrough in solid-state battery technology by Toyota promises 1,200km range and 10-minute charging. Commercial production expected 2027. Game-changer for EV market.",
            "metadata": {
                "title": "Toyota đột phá pin rắn cho xe điện",
                "source": "Nikkei Asia",
                "article_date": (base_date - timedelta(days=4)).isoformat(),
                "category": "competition",
                "sentiment": "negative",
                "risk_score": 0.64,
                "related_products": ["HYBRID-BATTERY-999", "EV-INVERTER-888"],
                "tags": ["Toyota", "solid-state battery", "breakthrough", "EV technology"],
                "language": "en",
            }
        },
        {
            "id": "news-031",
            "document": "Philippines signs free trade agreement with Japan, reducing import tariffs on automotive parts to 0% over 5 years. Expected to boost bilateral trade by 40%.",
            "metadata": {
                "title": "Philippines ký hiệp định thương mại tự do với Nhật Bản",
                "source": "Manila Bulletin",
                "article_date": (base_date - timedelta(days=27)).isoformat(),
                "category": "regulation",
                "sentiment": "positive",
                "risk_score": 0.12,
                "related_products": ["ALL"],
                "tags": ["Philippines", "Japan", "FTA", "tariff reduction"],
                "language": "en",
            }
        },
        {
            "id": "news-032",
            "document": "Bão Typhoon Mawar tàn phá Guam và Mariana Islands, phá hủy kho hàng của nhiều nhà phân phối phụ tùng ô tô. Dự kiến thiệt hại $150M.",
            "metadata": {
                "title": "Bão Mawar phá hủy kho phụ tùng tại Guam",
                "source": "Pacific Daily News",
                "article_date": (base_date - timedelta(days=11)).isoformat(),
                "category": "logistics",
                "sentiment": "negative",
                "risk_score": 0.86,
                "related_products": ["ALL"],
                "tags": ["typhoon", "Guam", "warehouse damage", "inventory loss"],
                "language": "vi",
            }
        },
        {
            "id": "news-033",
            "document": "Samsung invests $3B in automotive semiconductor fab in Korea. Expected to supply advanced chips for autonomous driving and EV systems starting 2026.",
            "metadata": {
                "title": "Samsung đầu tư 3 tỷ USD vào chip ô tô",
                "source": "Korea Times",
                "article_date": (base_date - timedelta(days=32)).isoformat(),
                "category": "market_trend",
                "sentiment": "neutral",
                "risk_score": 0.35,
                "related_products": ["ECU-MODULE-89", "SENSOR-TEMP-456"],
                "tags": ["Samsung", "semiconductor", "investment", "autonomous driving"],
                "language": "en",
            }
        },
        {
            "id": "news-034",
            "document": "Giá cao su thiên nhiên tăng 18% trong tháng 11 do mưa lớn tại Thái Lan và Indonesia ảnh hưởng khai thác. Tác động đến chi phí sản xuất seals và gaskets.",
            "metadata": {
                "title": "Giá cao su thiên nhiên tăng 18%",
                "source": "Rubber Journal Asia",
                "article_date": (base_date - timedelta(days=8)).isoformat(),
                "category": "supply_chain",
                "sentiment": "negative",
                "risk_score": 0.61,
                "related_products": ["SEAL-GASKET-345", "RUBBER-MOUNT-678"],
                "tags": ["rubber", "commodity price", "Thailand", "Indonesia"],
                "language": "vi",
            }
        },
        {
            "id": "news-035",
            "document": "GM announces partnership with Honda to co-develop affordable EVs under $25,000. Joint venture targets 500,000 units annually for emerging markets.",
            "metadata": {
                "title": "GM và Honda hợp tác phát triển EV giá rẻ",
                "source": "Automotive News",
                "article_date": (base_date - timedelta(days=35)).isoformat(),
                "category": "competition",
                "sentiment": "negative",
                "risk_score": 0.58,
                "related_products": ["EV-INVERTER-888", "COOLANT-PUMP-789"],
                "tags": ["GM", "Honda", "EV", "joint venture", "affordable"],
                "language": "en",
            }
        },
        {
            "id": "news-036",
            "document": "Trung Quốc cấm vận xuất khẩu rare earth minerals sang các quốc gia phương Tây. Ảnh hưởng nghiêm trọng đến sản xuất motors và sensors cho EV.",
            "metadata": {
                "title": "Trung Quốc cấm xuất khẩu rare earth minerals",
                "source": "South China Morning Post",
                "article_date": (base_date - timedelta(days=3)).isoformat(),
                "category": "supply_chain",
                "sentiment": "negative",
                "risk_score": 0.92,
                "related_products": ["EV-MOTOR-999", "SENSOR-TEMP-456", "MAGNET-ASSEMBLY-777"],
                "tags": ["China", "rare earth", "export ban", "geopolitics"],
                "language": "vi",
            }
        },
        {
            "id": "news-037",
            "document": "Australia announces $2B fund to support local battery manufacturing and rare earth processing. Aims to reduce dependence on Chinese supply chain.",
            "metadata": {
                "title": "Australia đầu tư 2 tỷ USD vào sản xuất pin",
                "source": "Sydney Morning Herald",
                "article_date": (base_date - timedelta(days=37)).isoformat(),
                "category": "market_trend",
                "sentiment": "positive",
                "risk_score": 0.22,
                "related_products": ["HYBRID-BATTERY-999", "EV-INVERTER-888"],
                "tags": ["Australia", "battery", "rare earth", "supply chain diversification"],
                "language": "en",
            }
        },
        {
            "id": "news-038",
            "document": "Hackers target automotive supply chain with ransomware attacks on tier-2 suppliers. 8 companies affected including injection molding and electronics manufacturers.",
            "metadata": {
                "title": "Tấn công ransomware vào nhà cung cấp phụ tùng ô tô",
                "source": "Cybersecurity News",
                "article_date": (base_date - timedelta(days=9)).isoformat(),
                "category": "supply_chain",
                "sentiment": "negative",
                "risk_score": 0.77,
                "related_products": ["ALL"],
                "tags": ["cyber attack", "ransomware", "supply chain", "security"],
                "language": "en",
            }
        },
        {
            "id": "news-039",
            "document": "Nhật Bản giảm thuế tiêu thụ xe hybrid xuống 3% để khuyến khích người dân chuyển đổi từ xe xăng truyền thống. Dự kiến tăng 35% doanh số hybrid.",
            "metadata": {
                "title": "Nhật Bản giảm thuế xe hybrid xuống 3%",
                "source": "Japan Today",
                "article_date": (base_date - timedelta(days=33)).isoformat(),
                "category": "regulation",
                "sentiment": "positive",
                "risk_score": 0.16,
                "related_products": ["VCH20", "VK20", "HYBRID-BATTERY-999"],
                "tags": ["Japan", "hybrid", "tax reduction", "government policy"],
                "language": "vi",
            }
        },
        {
            "id": "news-040",
            "document": "New lithium deposits discovered in Bolivia estimated at 21 million tons, potentially world's largest reserve. Could reshape global EV battery supply chain by 2028.",
            "metadata": {
                "title": "Bolivia phát hiện mỏ lithium lớn nhất thế giới",
                "source": "Bloomberg",
                "article_date": (base_date - timedelta(days=40)).isoformat(),
                "category": "market_trend",
                "sentiment": "positive",
                "risk_score": 0.25,
                "related_products": ["HYBRID-BATTERY-999", "EV-INVERTER-888"],
                "tags": ["Bolivia", "lithium", "discovery", "battery supply"],
                "language": "en",
            }
        },
        {
            "id": "news-041",
            "document": "Cháy rừng Amazon ảnh hưởng đến hoạt động khai thác aluminum tại Brazil. Giá aluminum tăng 14%, tác động đến chi phí sản xuất radiators và heat exchangers.",
            "metadata": {
                "title": "Cháy rừng Amazon làm tăng giá aluminum",
                "source": "Reuters",
                "article_date": (base_date - timedelta(days=29)).isoformat(),
                "category": "supply_chain",
                "sentiment": "negative",
                "risk_score": 0.69,
                "related_products": ["RADIATOR-CORE-555", "HEAT-EXCHANGER-666"],
                "tags": ["Amazon", "wildfire", "aluminum", "commodity price"],
                "language": "vi",
            }
        },
        {
            "id": "news-042",
            "document": "BYD overtakes Tesla as world's largest EV manufacturer in Q3 2025 with 1.8M units sold. Expanding aggressively into ASEAN markets with competitive pricing.",
            "metadata": {
                "title": "BYD vượt Tesla trở thành nhà sản xuất EV lớn nhất",
                "source": "Financial Times",
                "article_date": (base_date - timedelta(days=36)).isoformat(),
                "category": "competition",
                "sentiment": "negative",
                "risk_score": 0.71,
                "related_products": ["EV-INVERTER-888", "HYBRID-BATTERY-999", "COOLANT-PUMP-789"],
                "tags": ["BYD", "Tesla", "EV market leader", "ASEAN expansion"],
                "language": "en",
            }
        },
        {
            "id": "news-043",
            "document": "Singapore launches smart mobility initiative, investing $500M in autonomous vehicle infrastructure. Public testing corridors opening in 2026.",
            "metadata": {
                "title": "Singapore đầu tư 500 triệu USD vào xe tự lái",
                "source": "The Straits Times",
                "article_date": (base_date - timedelta(days=38)).isoformat(),
                "category": "market_trend",
                "sentiment": "positive",
                "risk_score": 0.19,
                "related_products": ["SENSOR-TEMP-456", "LIDAR-MODULE-999", "ECU-MODULE-89"],
                "tags": ["Singapore", "autonomous vehicle", "smart city", "infrastructure"],
                "language": "en",
            }
        },
        {
            "id": "news-044",
            "document": "Đài Loan bị động đất 7.2 độ Richter, ảnh hưởng đến 40% công suất sản xuất chip bán dẫn toàn cầu. TSMC tạm ngừng hoạt động 3 nhà máy.",
            "metadata": {
                "title": "Động đất Đài Loan ảnh hưởng sản xuất chip toàn cầu",
                "source": "Taiwan News",
                "article_date": (base_date - timedelta(days=2)).isoformat(),
                "category": "supply_chain",
                "sentiment": "negative",
                "risk_score": 0.95,
                "related_products": ["ECU-MODULE-89", "SENSOR-TEMP-456", "DISPLAY-MODULE-777"],
                "tags": ["earthquake", "Taiwan", "TSMC", "semiconductor shortage"],
                "language": "vi",
            }
        },
        {
            "id": "news-045",
            "document": "US and EU announce joint critical minerals partnership to counter China's dominance. $10B fund to secure lithium, cobalt, and rare earth supplies.",
            "metadata": {
                "title": "Mỹ và EU hợp tác đảm bảo nguồn khoáng sản quan trọng",
                "source": "Wall Street Journal",
                "article_date": (base_date - timedelta(days=41)).isoformat(),
                "category": "regulation",
                "sentiment": "positive",
                "risk_score": 0.31,
                "related_products": ["HYBRID-BATTERY-999", "MAGNET-ASSEMBLY-777"],
                "tags": ["US", "EU", "critical minerals", "supply chain security"],
                "language": "en",
            }
        },
        {
            "id": "news-046",
            "document": "Indonesia mở rộng trợ cấp cho xe điện, tăng từ 7 triệu lên 15 triệu rupiah/xe. Kỳ vọng tăng trưởng 80% doanh số EV trong năm 2026.",
            "metadata": {
                "title": "Indonesia tăng gấp đôi trợ cấp xe điện",
                "source": "Jakarta Post",
                "article_date": (base_date - timedelta(days=31)).isoformat(),
                "category": "regulation",
                "sentiment": "positive",
                "risk_score": 0.14,
                "related_products": ["EV-INVERTER-888", "HYBRID-BATTERY-999"],
                "tags": ["Indonesia", "EV subsidy", "government incentive"],
                "language": "vi",
            }
        },
        {
            "id": "news-047",
            "document": "Magna International announces closure of 5 manufacturing plants in Europe due to declining ICE vehicle demand. 8,000 jobs affected. Restructuring toward EV components.",
            "metadata": {
                "title": "Magna đóng cửa 5 nhà máy tại châu Âu",
                "source": "Automotive News Europe",
                "article_date": (base_date - timedelta(days=34)).isoformat(),
                "category": "market_trend",
                "sentiment": "negative",
                "risk_score": 0.54,
                "related_products": ["VCH20", "FUEL-INJ-777"],
                "tags": ["Magna", "plant closure", "ICE decline", "EV transition"],
                "language": "en",
            }
        },
        {
            "id": "news-048",
            "document": "Thái Lan ký thỏa thuận với Tesla để xây dựng Gigafactory tại Eastern Economic Corridor. Công suất 500,000 xe/năm, khởi công 2026.",
            "metadata": {
                "title": "Tesla xây Gigafactory tại Thái Lan",
                "source": "Bangkok Post",
                "article_date": (base_date - timedelta(days=25)).isoformat(),
                "category": "market_trend",
                "sentiment": "negative",
                "risk_score": 0.63,
                "related_products": ["EV-INVERTER-888", "COOLANT-PUMP-789", "SENSOR-TEMP-456"],
                "tags": ["Tesla", "Thailand", "Gigafactory", "EV production"],
                "language": "vi",
            }
        },
        {
            "id": "news-049",
            "document": "Global copper shortage intensifies as mining output declines. Prices surge 25% affecting wiring harness and electrical component costs.",
            "metadata": {
                "title": "Thiếu hụt đồng toàn cầu làm tăng giá 25%",
                "source": "Bloomberg Metals",
                "article_date": (base_date - timedelta(days=12)).isoformat(),
                "category": "supply_chain",
                "sentiment": "negative",
                "risk_score": 0.74,
                "related_products": ["WIRING-HARNESS-888", "ALTERNATOR-999"],
                "tags": ["copper", "shortage", "commodity price", "wiring"],
                "language": "en",
            }
        },
        {
            "id": "news-050",
            "document": "Hyundai Motor Group cam kết đầu tư 20 tỷ USD vào công nghệ hydro và pin nhiên liệu trong 5 năm tới. Mục tiêu dẫn đầu thị trường FCEV.",
            "metadata": {
                "title": "Hyundai đầu tư 20 tỷ USD vào công nghệ hydro",
                "source": "Korea Herald",
                "article_date": (base_date - timedelta(days=39)).isoformat(),
                "category": "competition",
                "sentiment": "neutral",
                "risk_score": 0.47,
                "related_products": ["FUEL-CELL-MODULE-555", "HYDROGEN-TANK-666"],
                "tags": ["Hyundai", "hydrogen", "fuel cell", "FCEV investment"],
                "language": "vi",
            }
        },
    ]
    
    return news_articles


def seed_chromadb():
    """Seed ChromaDB with mock data."""
    print("🌱 Starting ChromaDB seeding process...")
    
    # Connect to ChromaDB Docker container
    CHROMADB_HOST = os.getenv("CHROMADB_HOST", "localhost")
    CHROMADB_PORT = int(os.getenv("CHROMADB_PORT", "8001"))
    
    try:
        client = chromadb.HttpClient(
            host=CHROMADB_HOST,
            port=CHROMADB_PORT,
            settings=Settings(anonymized_telemetry=False),
        )
        print(f"✅ Connected to ChromaDB at {CHROMADB_HOST}:{CHROMADB_PORT}")
    except Exception as e:
        print(f"❌ Failed to connect to ChromaDB: {e}")
        print("💡 Make sure ChromaDB container is running: docker-compose up -d chromadb")
        return
    
    # Get or create collection
    collection_name = "denso_market_intelligence"
    
    try:
        collection = client.get_collection(collection_name)
        print(f"📦 Found existing collection: {collection_name}")
        
        # Check if already seeded
        existing_count = collection.count()
        if existing_count > 0:
            print(f"⚠️ Collection already has {existing_count} documents")
            response = input("Do you want to delete and reseed? (y/n): ")
            if response.lower() == 'y':
                client.delete_collection(collection_name)
                print("🗑️ Deleted existing collection")
                collection = client.create_collection(
                    name=collection_name,
                    metadata={"description": "DENSO market intelligence and risk news"}
                )
            else:
                print("❌ Seeding cancelled")
                return
        
    except Exception:
        # Collection doesn't exist, create it
        collection = client.create_collection(
            name=collection_name,
            metadata={"description": "DENSO market intelligence and risk news"}
        )
        print(f"✨ Created new collection: {collection_name}")
    
    # Generate mock data
    news_articles = create_mock_news_data()
    print(f"📄 Generated {len(news_articles)} mock news articles")
    
    # Add to ChromaDB (convert lists to comma-separated strings for metadata)
    ids = [article["id"] for article in news_articles]
    documents = [article["document"] for article in news_articles]
    
    # ChromaDB doesn't support list/array in metadata, convert to strings
    metadatas = []
    for article in news_articles:
        metadata = article["metadata"].copy()
        # Convert arrays to comma-separated strings
        if "related_products" in metadata and isinstance(metadata["related_products"], list):
            metadata["related_products"] = ",".join(metadata["related_products"])
        if "tags" in metadata and isinstance(metadata["tags"], list):
            metadata["tags"] = ",".join(metadata["tags"])
        metadatas.append(metadata)
    
    try:
        collection.add(
            ids=ids,
            documents=documents,
            metadatas=metadatas,
        )
        print(f"✅ Successfully added {len(news_articles)} documents to ChromaDB")
        
        # Verify
        final_count = collection.count()
        print(f"📊 Collection now contains {final_count} documents")
        
        # Test query
        print("\n🔍 Testing semantic search...")
        results = collection.query(
            query_texts=["supply chain risks and logistics delays"],
            n_results=3,
        )
        
        print(f"\n📰 Sample query results (top 3):")
        for i, (doc_id, distance, metadata) in enumerate(zip(
            results["ids"][0], 
            results["distances"][0],
            results["metadatas"][0]
        )):
            print(f"\n  {i+1}. {metadata['title']}")
            print(f"     Risk Score: {metadata['risk_score']}")
            print(f"     Category: {metadata['category']}")
            print(f"     Similarity: {1 - distance:.3f}")
        
        print("\n✅ ChromaDB seeding completed successfully!")
        print(f"💡 Collection: {collection_name}")
        print(f"💡 Documents: {final_count}")
        print(f"💡 Test with: curl http://{CHROMADB_HOST}:{CHROMADB_PORT}/api/v1/collections")
        
    except Exception as e:
        print(f"❌ Failed to add documents: {e}")


if __name__ == "__main__":
    seed_chromadb()
