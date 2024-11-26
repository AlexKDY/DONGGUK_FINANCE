from flask import request, jsonify
from flask_restx import Namespace, Resource
from flask_cors import cross_origin  # cross_origin 데코레이터 사용
from util.db import get_collection

article_ns = Namespace('article')

@article_ns.route('/')
class Article(Resource):
    @cross_origin()  # CORS 허용
    def options(self):
        # CORS 사전 요청 처리
        return {}, 200  # 빈 응답 반환

    @cross_origin()  # CORS 허용
    def post(self):
        try:
            data = request.get_json()
            code = data.get('code')

            if not code:
                return {"error": True, "message": "code가 제공되지 않았습니다."}, 400

            col = get_collection('article')
            document = col.find_one({"code": code})

            print(f"Document found: {document}")  # 디버깅: 반환 데이터 확인

            if not document:
                return {
                    "error": True,
                    "message": f"Code '{code}'에 대한 데이터를 찾을 수 없습니다."
                }, 404

            return {
                "error": False,
                "message": "성공적으로 데이터를 가져왔습니다.",
                "data": document.get('article', [])
            }, 200

        except Exception as e:
            return {"error": True, "message": f"서버 오류: {str(e)}"}, 500

