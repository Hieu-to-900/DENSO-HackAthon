"""
Seed database with forecast and action data for testing.
Run this script to populate the database with sample data.

Usage:
    python scripts/seed_database.py
"""

import asyncio
import random
import math
import json
from datetime import datetime, timedelta, date
from uuid import uuid4

import asyncpg


# Database connection config
DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "denso_forecast",
    "user": "denso_user",
    "password": "denso_password_2025",
}


def generate_weekly_timeseries(
    base_value: int,
    historical_weeks: int = 12,
    forecast_weeks: int = 8,
    trend_direction: str = 'up',
    seasonal_strength: float = 0.15,
    volatility: float = 0.1,
    growth_rate: float = 0.02
):
    """Generate weekly time series data for a product."""
    data = []
    today = datetime.utcnow().date()
    
    # Historical data
    for i in range(-historical_weeks, 0):
        week_date = today + timedelta(weeks=i)
        
        # Seasonal variation
        seasonal_factor = 1 + math.sin((i / 4) + (base_value % 10)) * seasonal_strength
        
        # Trend factor
        trend_factor = 1
        if trend_direction == 'up':
            trend_factor = 1 + ((-i / historical_weeks) * growth_rate * 3)
        elif trend_direction == 'down':
            trend_factor = 1 - ((-i / historical_weeks) * growth_rate * 2)
        
        actual = round(
            base_value * seasonal_factor * trend_factor +
            random.randint(int(-base_value * volatility), int(base_value * volatility))
        )
        
        data.append({
            "date": week_date,
            "actual": actual,
            "forecast": None,
            "upper_bound": None,
            "lower_bound": None,
            "is_historical": True
        })
    
    # Forecast data
    last_actual = data[-1]["actual"] if data else base_value
    for i in range(forecast_weeks):
        week_date = today + timedelta(weeks=i)
        
        trend_factor = 1
        if trend_direction == 'up':
            trend_factor = 1 + (i * growth_rate)
        elif trend_direction == 'down':
            trend_factor = 1 - (i * growth_rate * 0.8)
        else:
            trend_factor = 1 + (i * growth_rate * 0.3)
        
        forecast_val = round(last_actual * trend_factor)
        confidence_width = 0.08 if trend_direction == 'stable' else 0.12
        
        data.append({
            "date": week_date,
            "actual": None,
            "forecast": forecast_val,
            "upper_bound": round(forecast_val * (1 + confidence_width)),
            "lower_bound": round(forecast_val * (1 - confidence_width)),
            "is_historical": False
        })
    
    return data


async def seed_forecasts(conn):
    """Seed forecast data."""
    print("🌱 Seeding forecasts...")
    
    products = [
        {
            "product_id": "BUGI-IRIDIUM-VCH20",
            "product_code": "VCH20",
            "product_name": "Bugi Iridium Tough VCH20",
            "category": "Spark_Plugs",
            "forecast_units": 25000,
            "current_stock": 18500,
            "trend": "up",
            "change_percent": 12.5,
            "confidence": 94.2,
            "timeseries_params": {
                "base_value": 750,
                "trend_direction": "up",
                "seasonal_strength": 0.12,
                "volatility": 0.08,
                "growth_rate": 0.025
            }
        },
        {
            "product_id": "BUGI-PLATIN-VK20",
            "product_code": "VK20",
            "product_name": "Bugi Platinum VK20",
            "category": "Spark_Plugs",
            "forecast_units": 22000,
            "current_stock": 19200,
            "trend": "up",
            "change_percent": 8.3,
            "confidence": 91.8,
            "timeseries_params": {
                "base_value": 550,
                "trend_direction": "up",
                "seasonal_strength": 0.18,
                "volatility": 0.12,
                "growth_rate": 0.03
            }
        },
        {
            "product_id": "AC-COMPRESSOR-447220",
            "product_code": "447220-1510",
            "product_name": "Compressor điều hòa 10PA17C",
            "category": "AC_System",
            "forecast_units": 18000,
            "current_stock": 12400,
            "trend": "up",
            "change_percent": 16.7,
            "confidence": 88.5,
            "timeseries_params": {
                "base_value": 480,
                "trend_direction": "up",
                "seasonal_strength": 0.25,
                "volatility": 0.15,
                "growth_rate": 0.035
            }
        },
        {
            "product_id": "FILTER-AIR-DEN5656",
            "product_code": "DEN-5656",
            "product_name": "Lọc gió động cơ DENSO 5656",
            "category": "Filters",
            "forecast_units": 32000,
            "current_stock": 28400,
            "trend": "stable",
            "change_percent": 1.2,
            "confidence": 92.3,
            "timeseries_params": {
                "base_value": 800,
                "trend_direction": "stable",
                "seasonal_strength": 0.10,
                "volatility": 0.08,
                "growth_rate": 0.01
            }
        },
        {
            "product_id": "SENSOR-O2-234-9065",
            "product_code": "234-9065",
            "product_name": "Cảm biến oxy (O2 Sensor)",
            "category": "Sensors",
            "forecast_units": 15000,
            "current_stock": 11200,
            "trend": "up",
            "change_percent": 15.8,
            "confidence": 89.7,
            "timeseries_params": {
                "base_value": 375,
                "trend_direction": "up",
                "seasonal_strength": 0.15,
                "volatility": 0.11,
                "growth_rate": 0.028
            }
        }
    ]
    
    forecast_ids = []
    today = datetime.utcnow().date()
    
    for product in products:
        forecast_id = uuid4()
        forecast_ids.append((forecast_id, product["product_code"]))
        
        # Generate timeseries first to get start/end dates
        timeseries = generate_weekly_timeseries(**product["timeseries_params"])
        forecast_start_date = timeseries[0]["date"]
        forecast_end_date = timeseries[-1]["date"]
        
        # Insert forecast with all required fields
        await conn.execute(
            """
            INSERT INTO forecasts (
                id, product_id, product_code, product_name, category,
                forecast_units, current_stock, trend, change_percent, confidence,
                forecast_horizon, forecast_start_date, forecast_end_date, created_at
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14)
            """,
            forecast_id,
            product["product_id"],
            product["product_code"],
            product["product_name"],
            product["category"],
            product["forecast_units"],
            product["current_stock"],
            product["trend"],
            product["change_percent"],
            product["confidence"],
            "60_days",
            forecast_start_date,
            forecast_end_date,
            datetime.utcnow()
        )
        
        # Insert timeseries (already generated above)
        for point in timeseries:
            await conn.execute(
                """
                INSERT INTO forecast_timeseries (
                    id, forecast_id, date, actual, forecast, 
                    upper_bound, lower_bound, is_historical
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                """,
                uuid4(),
                forecast_id,
                point["date"],
                point["actual"],
                point["forecast"],
                point["upper_bound"],
                point["lower_bound"],
                point["is_historical"]
            )
        
        # Insert forecast metrics
        await conn.execute(
            """
            INSERT INTO forecast_metrics (
                id, forecast_id, mape, rmse, mae, r_squared,
                training_data_points, test_data_points
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            """,
            uuid4(),
            forecast_id,
            5.8 + random.uniform(-1, 1),  # MAPE
            287 + random.uniform(-50, 50),  # RMSE
            180 + random.uniform(-30, 30),  # MAE
            0.94 + random.uniform(-0.02, 0.02),  # R²
            450,
            120
        )
        
        print(f"  ✓ Created forecast for {product['product_name']}")
    
    return forecast_ids


async def seed_actions(conn, forecast_ids):
    """Seed action recommendations."""
    print("🌱 Seeding action recommendations...")
    
    actions = [
        {
            "priority": "high",
            "category": "supply_chain",
            "title": "Bảo đảm tuyến vận tải thay thế từ cảng Busan",
            "description": "Tắc nghẽn cảng Yokohama ảnh hưởng lịch trình Q1. Cần chuyển sang tuyến vận tải dự phòng.",
            "impact": "Tránh chậm trễ giao hàng trị giá 450K USD",
            "estimated_cost": 45000.0,
            "deadline": datetime.utcnow() + timedelta(days=5),
            "affected_products": ["VCH20", "VK20", "447220-1510"],
            "status": "pending",
            "action_items": [
                {"step": "Liên hệ đối tác vận tải Busan Express", "completed": False},
                {"step": "Đàm phán giá cước vận chuyển khẩn cấp", "completed": False},
                {"step": "Xác nhận lịch trình giao hàng thay thế", "completed": False}
            ]
        },
        {
            "priority": "high",
            "category": "inventory",
            "title": "Tăng tồn kho dự phòng Bugi Iridium VCH20",
            "description": "Dự báo tăng 12.5% nhu cầu Q1 do ra mắt xe mới. Tồn kho hiện tại không đủ.",
            "impact": "Đáp ứng nhu cầu tăng đột biến, tránh mất doanh thu 280K USD",
            "estimated_cost": 85000.0,
            "deadline": datetime.utcnow() + timedelta(days=10),
            "affected_products": ["VCH20"],
            "status": "pending",
            "action_items": [
                {"step": "Đặt hàng 3000 units bổ sung từ nhà máy", "completed": False},
                {"step": "Mở rộng kho lưu trữ tại warehouse 2", "completed": False},
                {"step": "Update forecast cho Q1 2025", "completed": False}
            ]
        },
        {
            "priority": "medium",
            "category": "pricing",
            "title": "Điều chỉnh giá Compressor 447220 do biến động thép",
            "description": "Giá thép tăng 8% trong Q4, ảnh hưởng margin của dòng Compressor điều hòa.",
            "impact": "Duy trì margin 18%, tránh lỗ 120K USD/tháng",
            "estimated_cost": 0.0,
            "deadline": datetime.utcnow() + timedelta(days=15),
            "affected_products": ["447220-1510"],
            "status": "in_progress",
            "action_items": [
                {"step": "Phân tích chi phí nguyên vật liệu", "completed": True},
                {"step": "Đề xuất tăng giá 5-7% cho sales team", "completed": False},
                {"step": "Thông báo khách hàng chính về điều chỉnh giá", "completed": False}
            ]
        },
        {
            "priority": "medium",
            "category": "production",
            "title": "Tăng ca sản xuất Lọc gió DENSO 5656",
            "description": "Nhu cầu ổn định cao, công suất hiện tại 87% - cần tăng để đáp ứng đơn hàng mới.",
            "impact": "Tăng output 15%, tối ưu chi phí đơn vị sản xuất",
            "estimated_cost": 45000.0,
            "deadline": datetime.utcnow() + timedelta(days=20),
            "affected_products": ["DEN-5656"],
            "status": "pending",
            "action_items": [
                {"step": "Lên lịch tăng ca cho 2 tuần tới", "completed": False},
                {"step": "Đảm bảo nguyên vật liệu đủ cho tăng ca", "completed": False},
                {"step": "Kiểm tra máy móc trước khi tăng sản lượng", "completed": False}
            ]
        },
        {
            "priority": "low",
            "category": "marketing",
            "title": "Campaign marketing cho O2 Sensor mùa bảo dưỡng",
            "description": "Tháng 12-1 là mùa cao điểm bảo dưỡng xe. Cơ hội tăng trưởng 15%.",
            "impact": "Tăng 15% doanh thu segment Sensors (225K USD)",
            "estimated_cost": 25000.0,
            "deadline": datetime.utcnow() + timedelta(days=25),
            "affected_products": ["234-9065"],
            "status": "pending",
            "action_items": [
                {"step": "Thiết kế creative cho social media campaign", "completed": False},
                {"step": "Chuẩn bị promotion bundle với oil filter", "completed": False},
                {"step": "Training cho dealer network về sản phẩm", "completed": False}
            ]
        }
    ]
    
    for action in actions:
        # Find related forecast_id if applicable
        forecast_id = None
        if action["affected_products"]:
            for fid, product_code in forecast_ids:
                if product_code in action["affected_products"]:
                    forecast_id = fid
                    break
        
        action_id = uuid4()
        await conn.execute(
            """
            INSERT INTO action_recommendations (
                id, priority, category, title, description,
                impact, estimated_cost, deadline, affected_products, action_items, status
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
            """,
            action_id,
            action["priority"],
            action["category"],
            action["title"],
            action["description"],
            action["impact"],
            action["estimated_cost"],
            action["deadline"],
            action["affected_products"],
            json.dumps(action["action_items"]),  # Convert to JSON string
            action["status"]
        )
        
        print(f"  ✓ Created action: {action['title'][:50]}...")


async def main():
    """Main seed function."""
    print("=" * 60)
    print("🌱 DENSO Database Seeder")
    print("=" * 60)
    
    try:
        # Connect to database
        print("\n📡 Connecting to database...")
        conn = await asyncpg.connect(**DB_CONFIG)
        print("  ✓ Connected successfully")
        
        # Clear existing data (optional)
        print("\n🗑️  Clearing existing data...")
        await conn.execute("DELETE FROM forecast_metrics")
        await conn.execute("DELETE FROM forecast_timeseries")
        await conn.execute("DELETE FROM action_recommendations")
        await conn.execute("DELETE FROM forecasts")
        print("  ✓ Cleared")
        
        # Seed data
        forecast_ids = await seed_forecasts(conn)
        await seed_actions(conn, forecast_ids)
        
        # Verify
        print("\n✅ Verification:")
        forecast_count = await conn.fetchval("SELECT COUNT(*) FROM forecasts")
        timeseries_count = await conn.fetchval("SELECT COUNT(*) FROM forecast_timeseries")
        action_count = await conn.fetchval("SELECT COUNT(*) FROM action_recommendations")
        
        print(f"  • Forecasts: {forecast_count}")
        print(f"  • Timeseries points: {timeseries_count}")
        print(f"  • Actions: {action_count}")
        
        await conn.close()
        
        print("\n" + "=" * 60)
        print("✅ Database seeded successfully!")
        print("=" * 60)
        
    except asyncpg.PostgresError as e:
        print(f"\n❌ Database error: {e}")
        print("\nMake sure:")
        print("  1. PostgreSQL is running")
        print("  2. Database 'denso_forecast' exists")
        print("  3. Tables are created (run migrations)")
        print("  4. Credentials in DB_CONFIG are correct")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
