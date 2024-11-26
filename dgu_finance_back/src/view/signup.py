from flask import request, jsonify
from flask_restx import Namespace, Resource
from flask_cors import cross_origin
from util.db import get_collection
from dotenv import load_dotenv
import os
from pymongo import MongoClient

load_dotenv()
uri = os.environ.get("MONGODB_URI")
client = MongoClient(uri)
db = client.get_database(os.environ.get("MONGO_DATABASE"))
signup_ns = Namespace('signup')

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

''''
admin user 권한 설정 및 Replica Set 활성화 필요
def create_custom_role(client, user_id, db_name):
    """사용자 정의 역할 생성 및 사용자 권한 부여"""
    admin_db = client["admin"]
    try:
        # 사용자 정의 역할 생성
        admin_db.command("createRole", f"user_role_{user_id}", {
            "privileges": [
                {  # user 컬렉션에 대한 CRUD 권한
                    "resource": {"db": db_name, "collection": "user"},
                    "actions": ["find", "insert", "update", "remove"]
                },
                {  # 다른 모든 컬렉션에 대해 Read 권한
                    "resource": {"db": db_name, "collection": ""},
                    "actions": ["find"]
                }
            ],
            "roles": []  # 상속할 역할 없음
        })

        # 사용자에게 역할 부여
        admin_db.command("grantRolesToUser", user_id, [f"user_role_{user_id}"])
    except Exception as e:
        print(f"Failed to create or assign role for user {user_id}: {e}")
    finally:
        client.close()
'''

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


'''
# 권한부여 및 replica set 환경설정 완료 시 transaction 사용 가능
from flask import request, jsonify
from flask_restx import Namespace, Resource
from util.db import get_client
from bson.objectid import ObjectId
from pymongo.errors import OperationFailure

mystock_ns = Namespace('mystock')

@mystock_ns.route('/')
class MyStock(Resource):
    def post(self):
        client = None
        session = None
        try:
            data = request.get_json()
            user_id = data.get('user_id')  # 로그인된 사용자 ID
            stock_code = data.get('code')

            if not user_id or not stock_code:
                return {
                    "error": True,
                    "message": "user_id와 code가 필요합니다."
                }, 400

            # 사용자별 클라이언트 생성 (비밀번호 없이)
            client = get_client(username=user_id)  # 클라이언트 인증
            db_name = "finance_db"  # 데이터베이스 이름
            col = client[db_name]["user"]  # user 컬렉션에 접근

            # 트랜잭션 시작
            session = client.start_session()
            session.start_transaction()

            # 사용자 데이터 가져오기
            user = col.find_one({"_id": ObjectId(user_id)}, session=session)
            if not user:
                return {
                    "error": True,
                    "message": "해당 사용자를 찾을 수 없습니다."
                }, 404

            if 'mystock' not in user:
                user['mystock'] = []

            if stock_code in user['mystock']:
                return {
                    "error": True,
                    "message": "이미 관심 종목에 등록된 종목입니다."
                }, 400

            # 관심 종목 추가
            user['mystock'].append(stock_code)
            col.update_one({"_id": ObjectId(user_id)}, {"$set": {"mystock": user['mystock']}}, session=session)

            # 트랜잭션 커밋
            session.commit_transaction()

            return {
                "error": False,
                "message": "관심 종목에 성공적으로 추가되었습니다.",
                "mystock": user['mystock']
            }, 200

        except OperationFailure as op_err:
            if session:
                session.abort_transaction()
            return {
                "error": True,
                "message": f"트랜잭션 실패: {str(op_err)}"
            }, 500
        except Exception as e:
            if session:
                session.abort_transaction()
            return {
                "error": True,
                "message": f"서버 오류: {str(e)}"
            }, 500
        finally:
            if session:
                session.end_session()
            if client:
                client.close()

@mystock_ns.route('/list/<user_id>', strict_slashes=False)
class MyStockList(Resource):
    def get(self, user_id):
        client = None
        try:
            # 사용자 클라이언트 생성 (비밀번호 없이)
            client = get_client(username=user_id)
            db_name = "finance_db"  # 데이터베이스 이름
            col = client[db_name]["user"]

            # user_id를 ObjectId로 변환하여 검색
            user = col.find_one({"_id": ObjectId(user_id)})

            if not user:
                return {
                    "error": True,
                    "message": "해당 사용자를 찾을 수 없습니다."
                }, 404

            mystock = user.get('mystock', [])

            return {
                "error": False,
                "message": "관심 종목 목록을 성공적으로 가져왔습니다.",
                "mystock": mystock
            }, 200

        except Exception as e:
            return {
                "error": True,
                "message": f"서버 오류: {str(e)}"
            }, 500
        finally:
            if client:
                client.close()

@mystock_ns.route('/delete')
class MyStockDelete(Resource):
    def post(self):
        client = None
        session = None
        try:
            data = request.get_json()
            user_id = data.get('user_id')
            code = data.get('code')

            if not user_id or not code:
                return {"error": True, "message": "user_id와 code가 필요합니다."}, 400

            # 사용자 클라이언트 생성 (비밀번호 없이)
            client = get_client(username=user_id)
            db_name = "finance_db"
            col = client[db_name]["user"]

            # 트랜잭션 시작
            session = client.start_session()
            session.start_transaction()

            # 관심 종목 제거
            result = col.update_one(
                {"_id": ObjectId(user_id)},
                {"$pull": {"mystock": code}},
                session=session
            )

            if result.modified_count == 0:
                return {"error": True, "message": "해당 사용자가 없거나 종목 코드가 존재하지 않습니다."}, 404

            # 트랜잭션 커밋
            session.commit_transaction()

            return {"error": False, "message": "종목이 관심 목록에서 제거되었습니다."}, 200
        except OperationFailure as op_err:
            if session:
                session.abort_transaction()
            return {
                "error": True,
                "message": f"트랜잭션 실패: {str(op_err)}"
            }, 500
        except Exception as e:
            if session:
                session.abort_transaction()
            return {
                "error": True,
                "message": f"서버 오류: {str(e)}"
            }, 500
        finally:
            if session:
                session.end_session()
            if client:
                client.close()

'''