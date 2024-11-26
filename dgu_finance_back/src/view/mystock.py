from flask import request, jsonify
from flask_restx import Namespace, Resource
from util.db import get_collection
from bson.objectid import ObjectId  # ObjectId를 처리하기 위해 필요

mystock_ns = Namespace('mystock')

@mystock_ns.route('/')
class MyStock(Resource):
    def post(self):
        try:
            data = request.get_json()
            user_id = data.get('user_id')
            stock_code = data.get('code')

            if not user_id or not stock_code:
                return {
                    "error": True,
                    "message": "user_id와 code가 필요합니다."
                }, 400

            col = get_collection('user')

            user = col.find_one({"_id": ObjectId(user_id)})

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

            user['mystock'].append(stock_code)
            col.update_one({"_id": ObjectId(user_id)}, {"$set": {"mystock": user['mystock']}})

            return {
                "error": False,
                "message": "관심 종목에 성공적으로 추가되었습니다.",
                "mystock": user['mystock']
            }, 200

        except Exception as e:
            return {
                "error": True,
                "message": f"서버 오류: {str(e)}"
            }, 500


@mystock_ns.route('/list/<user_id>', strict_slashes=False)
class MyStockList(Resource):
    def get(self, user_id):
        try:
            col = get_collection('user')

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

@mystock_ns.route('/delete')
class MyStockDelete(Resource):
    def post(self):
        try:
            # 요청에서 데이터 추출
            data = request.get_json()
            user_id = data.get('user_id')
            code = data.get('code')

            if not user_id or not code:
                return {"error": True, "message": "user_id와 code가 필요합니다."}, 400

            # User collection에서 데이터 업데이트
            col = get_collection('user')
            result = col.update_one(
                {"_id": ObjectId(user_id)},  # 사용자 ID와 일치하는 문서
                {"$pull": {"mystock": code}}  # mystock 리스트에서 종목 코드 제거
            )

            if result.modified_count == 0:
                return {"error": True, "message": "해당 사용자가 없거나 종목 코드가 존재하지 않습니다."}, 404

            return {"error": False, "message": "종목이 관심 목록에서 제거되었습니다."}, 200
        except Exception as e:
            return {"error": True, "message": f"서버 오류: {str(e)}"}, 500