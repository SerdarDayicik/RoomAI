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

@session_bp.route('/get-premium-info', methods=['POST'])
def get_premium_info():
    data = request.get_json()
    device_id = data.get("device_id")

    if not device_id:
        return jsonify({"error": "Eksik bilgiler! 'device_id' zorunludur."}), 400

    try:
        # device_id ile kullanıcıyı buluyoruz
        user_info = supabase.table('users').select("is_premium").eq("device_id", device_id).execute()

        if not user_info.data:
            return jsonify({"error": "Kullanıcı bulunamadı!"}), 404

        # is_premium bilgisini döndürüyoruz
        return jsonify({"is_premium": user_info.data[0]["is_premium"]}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500



