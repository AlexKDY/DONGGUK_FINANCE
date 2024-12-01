from flask import request, jsonify
from flask_restx import Namespace, Resource
from flask_cors import cross_origin
from util.db import get_collection
from bson import ObjectId

login_ns = Namespace('login')

COLLECTION_SCHEMA = {
    "username": {"type": "string", "minlength": 8, "required": True},
    "name": {"type": "string", "required": True},
    "phone": {"type": "string", "pattern": r"^\d{3}-\d{4}-\d{4}$", "required": True},
    "password": {"type": "string", "minlength": 8, "required": True},
}


@login_ns.route('/')
class Login(Resource):
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
        

def validate_data(data):
    """입력 데이터 유효성 검사"""
    errors = {}
    for field, rules in COLLECTION_SCHEMA.items():
        value = data.get(field)

        # 필수 필드 검사
        if rules.get("required") and not value:
            errors[field] = f"{field} is required."
            continue

        # 타입 검사
        if value and rules.get("type") and not isinstance(value, str):
            errors[field] = f"{field} must be a string."
            continue

        # 길이 검사
        if value and rules.get("minlength") and len(value) < rules["minlength"]:
            errors[field] = f"{field} must be at least {rules['minlength']} characters long."
            continue

        # 정규식 검사
        if value and rules.get("pattern"):
            import re
            if not re.match(rules["pattern"], value):
                errors[field] = f"{field} format is invalid."
    
    return errors

@login_ns.route('/update/<string:user_id>')
class UpdateUser(Resource):
    @cross_origin(methods=["PATCH", "OPTIONS"]) 
    def patch(self, user_id):
        try:
            # 요청 데이터 가져오기
            data = request.get_json()
            print(f"Received update data: {data}")

            if not data:
                raise ValueError("No data received")

            # 데이터 유효성 검사 호출
            validation_errors = validate_data(data)
            if validation_errors:
                return {
                    "error": True,
                    "message": "회원가입 조건을 확인하세요!",
                    "details": validation_errors
                }, 400

            # MongoDB 컬렉션 연결
            col = get_collection('user')

            # ObjectId로 user 찾기
            try:
                user = col.find_one({"_id": ObjectId(user_id)})
            except Exception:
                return {"error": True, "message": "Invalid user ID format"}, 400

            if not user:
                return {"error": True, "message": "User not found"}, 404

            # 중복 데이터 확인
            if data.get("username"):
                duplicate_username = col.find_one({
                    "username": data["username"],
                    "_id": {"$ne": ObjectId(user_id)}  # 현재 user_id는 제외
                })
                if duplicate_username:
                    return {
                        "error": True,
                        "message": f"Username '{data['username']}' is already in use."
                    }, 400

            if data.get("password"):
                duplicate_password = col.find_one({
                    "password": data["password"],
                    "_id": {"$ne": ObjectId(user_id)}  # 현재 user_id는 제외
                })
                if duplicate_password:
                    return {
                        "error": True,
                        "message": "Password is already in use by another account."
                    }, 400

            # 업데이트 데이터 준비
            update_fields = {}
            if data.get("username"):
                update_fields["username"] = data["username"]
            if data.get("name"):
                update_fields["name"] = data["name"]
            if data.get("phone"):  # 중복 확인 없음
                update_fields["phone"] = data["phone"]
            if data.get("password"):
                update_fields["password"] = data["password"]

            if not update_fields:
                return {"error": True, "message": "No valid fields to update"}, 400

            # 데이터베이스 업데이트
            result = col.update_one({"_id": ObjectId(user_id)}, {"$set": update_fields})

            if result.modified_count == 0:
                return {"error": True, "message": "No changes made"}, 400

            # 업데이트된 데이터 가져오기
            updated_user = col.find_one({"_id": ObjectId(user_id)}, {"password": 0})  # 보안상의 이유로 password 제외

            return {
                "error": False,
                "message": "User updated successfully",
                "user": updated_user  
            }, 200

        except Exception as e:
            print(f"Error during user update: {e}")
            return {"error": True, "message": "An error occurred during user update"}, 500
