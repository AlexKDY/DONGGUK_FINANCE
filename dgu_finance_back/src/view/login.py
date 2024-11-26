from flask import request, jsonify
from flask_restx import Namespace, Resource
from flask_cors import cross_origin
from util.db import get_collection

login_ns = Namespace('login')

@login_ns.route('/')
class Signup(Resource):
    def options(self):
        """CORS 사전 요청 처리"""
        return {}, 200  # JSON 응답을 반환

    def post(self):
        try:
            # 요청 데이터 가져오기
            data = request.get_json()
            print(f"Received login data: {data}")

            if not data or not data.get("username") or not data.get("password"):
                return {"error": True, "message": "Username and password are required"}, 400

            # MongoDB 컬렉션 연결
            col = get_collection('user')

            # 사용자 인증 (username과 password 확인)
            user = col.find_one({
                "username": data.get("username"),
                "password": data.get("password")
            })

            if user:
                # 로그인 성공
                return {
                    "error": False,
                    "message": "Login successful!",
                    "user": {
                    "error": False,
                    "message": "Login successful!",
                    "user_id": str(user["_id"]),  
                    "name": user.get("name", "")}
                }, 200

            # 로그인 실패 (사용자 없음)
            return {"error": True, "message": "Invalid username or password"}, 401

        except Exception as e:
            print(f"Error during login: {e}")
            return {"error": True, "message": "An error occurred during login"}, 500