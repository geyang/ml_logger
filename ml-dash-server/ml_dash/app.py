import os
from sanic import Sanic
from sanic.exceptions import FileNotFound
from sanic.response import file

# gets current directory
BASE = os.path.realpath(__file__)
print(BASE)
print(os.path.dirname(BASE))

build_path = os.path.join(os.path.dirname(BASE), "../app-build")
print(build_path)

app = Sanic()
# serve js file for webpack
app.static('/', build_path)


# app.static('/main.js', './app-build/main.js', name='main.js')

@app.route('/')
@app.exception(FileNotFound)
async def index(request, exception=None):
    print('hey ====', [exception])
    return await file(build_path + '/index.html')


if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 3002)),
        workers=int(os.environ.get('WEB_CONCURRENCY', 1)),
        debug=bool(os.environ.get('DEBUG', '')))
