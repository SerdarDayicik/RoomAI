from supabase_client.supabase_client import get_supabase_client
import inspect
import models  # models modülünü import ettik
from models.User import User  # User modelini import ettik

supabase = get_supabase_client()

def create_tables():
    print("🔄 models/__init__.py çalıştı!")

    try:
        # models klasöründeki tüm sınıfları bul
        model_classes = [
            obj for name, obj in inspect.getmembers(models)
            if inspect.isclass(obj) and hasattr(obj, "TABLE_NAME") and hasattr(obj, "SCHEMA")
        ]

        for model in model_classes:
            table_name = model.TABLE_NAME
            print(f"🔍 '{table_name}' tablosu kontrol ediliyor...")

            # Supabase'den tablo bilgisini al
            existing_tables = supabase.table(table_name).select("id").limit(1).execute()
            print(existing_tables)

            if existing_tables.data:
                print(f"✅ '{table_name}' tablosu zaten var.")
                continue

            print(f"🚀 '{table_name}' tablosu oluşturuluyor...")

            # SQL komutuyla tabloyu oluştur
            columns = ", ".join([f"{col} {dtype}" for col, dtype in model.SCHEMA.items()])
            create_query = f"CREATE TABLE {table_name} ({columns});"

            # Supabase'de tabloyu oluştur
            supabase.rpc("sql", {"query": create_query}).execute()

            print(f"✅ '{table_name}' tablosu başarıyla oluşturuldu!")

    except Exception as e:
        print(f"⚠️ Tablo oluşturulurken hata oluştu: {e}")
