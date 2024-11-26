from flask import jsonify, request
from flask_restx import Namespace, Resource
from util.db import get_collection
from bson.objectid import ObjectId

item_ns = Namespace('item')

@item_ns.route('/list')
class ItemList(Resource):
    def get(self):
        col = get_collection('Item')
        
        # 필요한 필드만 조회하도록 쿼리
        items = col.find({}, {
            '_id': 1,
            'code': 1,
            'name': 1,
            'country': 1, 
            'market': 1
        })
        
        # ObjectId를 문자열로 변환하고 article_list로 변환
        item_list = []
        for item in items:
            item['_id'] = str(item['_id'])  # ObjectId를 문자열로 변환
            item_list.append(item)
        
        return jsonify(item_list)

@item_ns.route('/search')
class SearchItem(Resource):
    def post(self):
        try:
            # 요청에서 검색어 가져오기
            data = request.get_json()
            search_name = data.get('item')  # 'item' 필드에서 검색어 추출

            if not search_name or not search_name.strip():
                return {"error": True, "message": "검색어를 입력하세요"}, 400

            col = get_collection('Item')

            # 검색어로 종목명 부분 일치 검색
            query = {"name": {"$regex": search_name, "$options": "i"}}
            items = col.find(query, {
                '_id': 1,
                'code': 1,
                'name': 1,
                'country': 1,
                'market': 1, 
                'sector_name': 1,
                'type': 1
            })

            # 검색 결과를 리스트로 변환
            result = []
            for item in items:
                item['_id'] = str(item['_id'])  # ObjectId를 문자열로 변환
                result.append(item)

            if not result:
                return {"error": False, "message": "검색 결과가 없습니다", "data": []}, 200

            return {"error": False, "message": "검색 성공", "data": result}, 200
        except Exception as e:
            return {"error": True, "message": f"서버 오류: {str(e)}"}, 500
