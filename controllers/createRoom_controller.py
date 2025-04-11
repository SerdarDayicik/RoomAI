from flask import Blueprint, request, jsonify, send_from_directory
from google import genai
from google.genai import types
import PIL
import os
import uuid
from io import BytesIO
from dotenv import load_dotenv
from supabase_client.supabase_client import get_supabase_client

# .env dosyasını yüklüyoruz
load_dotenv()

model_bp = Blueprint("model", __name__)
supabase = get_supabase_client()

# Google Gemini API Anahtarı
GOOGLE_API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_ID = "gemini-2.0-flash-exp"

# Uploads klasörünü oluşturuyoruz (eğer yoksa)
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@model_bp.route('/create-room', methods=['POST'])
def create_room():
    try:
        # Form-data içinden verileri alıyoruz
        device_id = request.form.get("device_id")
        prompt = request.form.get("prompt")
        image_file = request.files.get("image")

        # Hataları kontrol ediyoruz
        if not device_id or not prompt or not image_file:
            return jsonify({"error": "Eksik bilgi! 'device_id', 'prompt' ve 'image' zorunludur."}), 400

        # Kullanıcı resmini kaydediyoruz (benzersiz isimle)
        user_image_filename = f"{uuid.uuid4().hex}_user.png"
        user_image_path = os.path.join(UPLOAD_FOLDER, user_image_filename)
        image_file.save(user_image_path)

        # Resmi PIL Image nesnesine dönüştürüyoruz
        image = PIL.Image.open(image_file)

        # Gemini API istemcisini başlatıyoruz
        client = genai.Client(api_key=GOOGLE_API_KEY)

        # Gemini API'ye istek gönderiyoruz
        response = client.models.generate_content(
            model=MODEL_ID,
            contents=[ 
                prompt,  # Prompt'u doğrudan gönderiyoruz
                image  # Resmi PIL Image nesnesi olarak gönderiyoruz
            ],
            config=types.GenerateContentConfig(
                response_modalities=['Text', 'Image']
            )
        )
        
        # Modelden gelen resim verisini alıyoruz ve kaydediyoruz
        for part in response.candidates[0].content.parts:
            if part.inline_data is not None:
                image_data = part.inline_data.data

                # Benzersiz bir dosya ismi oluşturuyoruz (UUID kullanıyoruz)
                unique_filename = f"{uuid.uuid4().hex}.png"
                image_path = os.path.join(UPLOAD_FOLDER, unique_filename)

                # Modelden gelen resmi kaydediyoruz
                with open(image_path, "wb") as f:
                    f.write(image_data)

                # Supabase'e veri ekliyoruz
                result = supabase.table("imagegeneration").insert({
                    "device_id": device_id,
                    "prompt": prompt,
                    "user_image_filename": user_image_filename,
                    "generated_image_filename": unique_filename
                }).execute()

                # Supabase işlemi başarılıysa, yanıt dönüyoruz
                if result.data:  # başarılı bir insert yanıtı
                    return jsonify({
                        "message": "Resim başarıyla oluşturuldu ve kaydedildi.",
                        "generated_image": f"http://10.33.41.110:5001/model/get-image/{unique_filename}",
                        "user_image": f"http://10.33.41.110:5001/model/get-image/{user_image_filename}"
                    }), 200
                else:
                    return jsonify({"error": "Supabase veritabanına kayıt yapılırken bir hata oluştu.", "details": result}), 500

        # Eğer response'dan resim verisi alınamadıysa
        return jsonify({"error": "Gemini API yanıtında resim verisi bulunamadı."}), 500

    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500


# Görseli almak için yeni bir route ekliyoruz
@model_bp.route("/get-image/<image_name>", methods=["GET"])
def get_image(image_name):
    try:
        # Görselin bulunduğu yolu belirliyoruz
        image_path = os.path.join(UPLOAD_FOLDER, image_name)
        
        # Eğer dosya mevcutsa, dosyayı gönderiyoruz
        if os.path.exists(image_path):
            return send_from_directory(UPLOAD_FOLDER, image_name)
        else:
            return jsonify({"error": "Görsel bulunamadı!"}), 404
    except Exception as e:
        return jsonify({"error": f"An error occurred while retrieving the image: {str(e)}"}), 500



@model_bp.route('/delete-room', methods=['DELETE'])
def delete_room():
    try:
        # JSON formatında gelen verileri alıyoruz
        data = request.get_json()
        
        device_id = data.get("device_id")
        room_id = data.get("room_id")
        
        if not device_id or not room_id:
            return jsonify({"error": "'device_id' ve 'room_id' zorunludur."}), 400
        
        # Veritabanında bu device_id ve room_id'ye sahip kaydı siliyoruz
        result = supabase.table("imagegeneration").delete().eq("device_id", device_id).eq("id", room_id).execute()
        
        # Supabase yanıtını kontrol ediyoruz
        if result.data:
            return jsonify({"message": "Veri başarıyla silindi."}), 200
        else:
            return jsonify({"error": "Veri bulunamadı veya silinemedi."}), 404

    except Exception as e:
        return jsonify({"error": f"Bir hata oluştu: {str(e)}"}), 500
