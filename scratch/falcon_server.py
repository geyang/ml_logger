import json
import falcon


class Files(object):
    def on_get(self, req, resp):
        doc = {
            'images': [
                {
                    'href': '/images/some.png'
                }
            ]
        }

        resp.body = json.dumps(doc, ensure_ascii=False)
        resp.status = falcon.HTTP_200

api = application = falcon.API()

images = Files()
api.add_route('/raw', images)
