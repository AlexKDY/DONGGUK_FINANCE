from flask import request, jsonify
from flask_restx import Namespace, Resource
from flask_cors import cross_origin
from util.db import get_collection

ohlcv_ns = Namespace('ohlcv')

@ohlcv_ns.route('/')
class OhlcvData(Resource):
    @cross_origin()  # CORS 허용
    def post(self):
        try:
            # 요청에서 종목코드 추출
            data = request.get_json()
            code = data.get('code')

            if not code or not code.strip():
                return {"error": True, "message": "종목코드를 입력하세요."}, 400

            # ohlcv 컬렉션 연결
            col = get_collection('OHLCV')

            # 종목코드로 데이터 조회
            results = col.find({"code": code})

            # 결과를 리스트로 변환
            ohlcv_list = []
            for result in results:
                # ObjectId를 문자열로 변환
                result['_id'] = str(result['_id'])
                ohlcv_list.append(result)

            if not ohlcv_list:
                return {"error": False, "message": "해당 종목코드의 데이터가 없습니다.", "data": []}, 200

            return {"error": False, "message": "데이터 조회 성공", "data": ohlcv_list}, 200

        except Exception as e:
            return {"error": True, "message": f"서버 오류: {str(e)}"}, 500
