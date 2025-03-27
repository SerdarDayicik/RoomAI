from flask import Flask
from flask_cors import CORS


#controller importları
from controllers.session_controller import session_bp
from controllers.createRoom_controller import model_bp





app = Flask(__name__)
CORS(app)





# Controller'lar
app.register_blueprint(session_bp, url_prefix='/session')
app.register_blueprint(model_bp, url_prefix='/model')



@app.route('/')
def home():
    return {"message": "Merhaba, API'ye hoşgeldin!"}

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
