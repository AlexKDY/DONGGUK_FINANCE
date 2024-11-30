from flask import request, jsonify
from flask_restx import Namespace, Resource
from flask_cors import cross_origin
from util.db import get_collection
from dotenv import load_dotenv
import os
from pymongo import MongoClient
from bson import ObjectId
from pymongo import ASCENDING, errors

load_dotenv()
uri = os.environ.get("MONGODB_URI")
client = MongoClient(uri)
db = client.get_database(os.environ.get("MONGO_DATABASE"))
signup_ns = Namespace('signup')

def ensure_indexes():
    """user 컬렉션의 unique index 생성"""
    col = get_collection('user')
    try:
        col.create_index([("username", ASCENDING)], unique=True)
        col.create_index([("password", ASCENDING)], unique=True)
        print("Indexes created successfully")
    except errors.OperationFailure as e:
        print(f"Index creation failed: {e}")
    except Exception as e:
        print(f"Unexpected error during index creation: {e}")

ensure_indexes()

# 컬렉션 스키마 정의 (유효성 검사용)
COLLECTION_SCHEMA = {
    "username": {"type": "string", "minlength": 8, "required": True},
    "name": {"type": "string", "required": True},
    "phone": {"type": "string", "pattern": r"^\d{3}-\d{4}-\d{4}$", "required": True},
    "password": {"type": "string", "minlength": 8, "required": True},
}

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

@signup_ns.route('/')
class Signup(Resource):
    def options(self):
        """CORS 사전 요청 처리"""
        return {}, 200  # JSON 응답을 반환

    def post(self):
        try:
            # 요청 데이터 확인
            data = request.get_json()
            print(f"Received data: {data}")

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

            col = get_collection('user')

            # 중복 확인 (username 또는 password 중복)
            existing_user = col.find_one({
                "$or": [
                    {"username": data.get("username")},
                    {"password": data.get("password")}
                ]
            })
            if existing_user:
                if existing_user.get("username") == data.get("username"):
                    return {
                        "error": True,
                        "message": "Username already exists. Please use a different username."
                    }, 400
                if existing_user.get("password") == data.get("password"):
                    return {
                        "error": True,
                        "message": "Password already exists. Please use a different password."
                    }, 400

            # 데이터 삽입
            result = col.insert_one(data)
            inserted_id = str(result.inserted_id)
            # create_custom_role(client, inserted_id, "dgu_finance")
            
            # 성공 응답
            return {
                "message": "Signup successful!",
                "user_id": inserted_id
            }, 200

        except Exception as e:
            print(f"Error: {e}")
            # 에러 응답을 JSON으로 반환
            return {"error": True, "message": str(e)}, 500

@signup_ns.route('/delete/<user_id>')
class DeleteAccount(Resource):
    def delete(self, user_id):
        try:
            col = get_collection('user')

            # 사용자 ID에 해당하는 계정 삭제
            result = col.delete_one({"_id": ObjectId(user_id)})
            if result.deleted_count == 0:
                return {"error": True, "message": "사용자를 찾을 수 없습니다."}, 404

            return {"error": False, "message": "계정이 성공적으로 삭제되었습니다."}, 200
        except Exception as e:
            return {"error": True, "message": f"서버 오류: {str(e)}"}, 500
