import os
from datetime import date, datetime
from bson import Timestamp, ObjectId
from flask import Flask
from flask.json.provider import DefaultJSONProvider
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_restx import Api

import config


# 커스텀 JSON encoder 생성
class UpdatedJSONProvider(DefaultJSONProvider):
    def default(self, o):
        if isinstance(o, date) or isinstance(o, datetime):
            return o.isoformat()
        elif isinstance(o, Timestamp):
            return o.as_datetime().isoformat()
        elif isinstance(o, bytes):
            return o.hex()
        elif isinstance(o, ObjectId):
            return str(o)
        return super().default(o)


authorizations = {
    'bearer_auth': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization'
    }, }
app = Flask(__name__)
app.json = UpdatedJSONProvider(app)
app.debug = True
api = Api(app,
          authorizations=authorizations,
          security='bearer_auth'
          )
jwt = JWTManager(app)
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY')

CORS(
    app,
    resources={r"/api/*": {"origins": "*"}},  # /api/* 경로에 대해 모든 출처 허용
    methods=["OPTIONS", "GET", "POST", "PATCH", "DELETE"],  # 허용 메소드 추가
    supports_credentials=True
)



from view.item import item_ns
api.add_namespace(item_ns, '/api/v1/item')
from view.signup import signup_ns
api.add_namespace(signup_ns, '/api/v1/signup')
from view.login import login_ns
api.add_namespace(login_ns, '/api/v1/login')
from view.mystock import mystock_ns
api.add_namespace(mystock_ns, '/api/v1/mystock')
from view.ohlcv import ohlcv_ns
api.add_namespace(ohlcv_ns, '/api/v1/ohlcv')
from view.fundamental import fundamental_ns
api.add_namespace(fundamental_ns, '/api/v1/fundamental')
from view.article import article_ns
api.add_namespace(article_ns, '/api/v1/article')

if __name__ == '__main__':
    app.run(port=config.PORT, debug=config.DEBUG)
