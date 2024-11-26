from flask import request, jsonify
from flask_restx import Namespace, Resource
from util.db import get_collection

fundamental_ns = Namespace('fundamental')

@fundamental_ns.route('/')
class Fundamental(Resource):
    def post(self):
        try:
            # 요청 데이터 가져오기
            data = request.get_json()
            code = data.get('code')  # 종목코드 추출

            if not code:
                return {"error": True, "message": "종목코드가 제공되지 않았습니다."}, 400

            # Fundamental 컬렉션에서 해당 데이터 찾기
            col = get_collection('Fundamental')
            result = col.find_one({"code": code})

            if not result:
                return {"error": False, "message": "해당 데이터가 없습니다."}, 200

            # ObjectId를 문자열로 변환
            result["_id"] = str(result["_id"])
            return {"error": False, "message": "데이터 조회 성공", "data": result}, 200

        except Exception as e:
            return {"error": True, "message": f"서버 오류: {str(e)}"}, 500
