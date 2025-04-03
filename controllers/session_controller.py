from flask import Blueprint, request, jsonify
from supabase_client.supabase_client import get_supabase_client

session_bp = Blueprint("session", __name__)
supabase = get_supabase_client()

@session_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    device_id = data.get("device_id")  # Kullanıcının cihaz ID'si

    if not device_id:
        return jsonify({"error": "Eksik bilgiler"}), 400

    try:
        # Önce bu device_id ile kayıtlı kullanıcı var mı kontrol et
        existing_user = supabase.table('users').select("*").eq("device_id", device_id).execute()

        if existing_user.data:
            # Kullanıcı zaten varsa bilgilerini döndür
            return jsonify({"message": "Kullanıcı zaten kayıtlı!", "user": existing_user.data[0]}), 201

        # Eğer kayıtlı değilse yeni kullanıcı ekle
        response = supabase.table('users').insert({
            "device_id": device_id,
            "created_at": "now()",  # Veritabanı zamanını otomatik olarak alacak
            "is_premium": False  # Varsayılan değer
        }).execute()

        return jsonify({"message": "Kullanıcı başarıyla kaydedildi!", "user": response.data[0]}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

