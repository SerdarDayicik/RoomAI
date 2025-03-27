from flask import Blueprint, request, jsonify
from supabase_client.supabase_client import get_supabase_client

model_bp = Blueprint("model", __name__)
supabase = get_supabase_client()


@model_bp.route('/create-room', methods=['POST'])
def create_room():
    pass