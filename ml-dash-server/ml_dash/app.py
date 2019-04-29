import os
from sanic import Sanic
from sanic.exceptions import FileNotFound
from sanic.response import file
from params_proto import cli_parse, Proto

# gets current directory
BASE = os.path.realpath(__file__)
build_path = os.path.join(os.path.dirname(BASE), "client-dist")
print(build_path)

app = Sanic()
# serve js file for webpack
app.static('/', build_path)


@app.route('/')
@app.exception(FileNotFound)
async def index(request, exception=None):
    print('hey ====', [exception])
    return await file(build_path + '/index.html')


@cli_parse
class AppServerArgs:
    """
    Configuration Arguments for the Sanic App that serves
    the static web-application.

    [Usage]

    To launch the web-app client, do

    python -m ml_dash.app port=3001 host=0.0.0.0 workers=4 debug=True
    """
    host = Proto("", help="use 0.0.0.0 if you want external clients to be able to access this.")
    port = Proto(3001, help="the port")
    workers = Proto(1, help="the number of worker processes")
    debug = False
    access_log = True


if __name__ == '__main__':
    import socket
    from termcolor import cprint, colored as c

    if AppServerArgs.host:
        from requests import get

        host_ip = get('https://api.ipify.org').text
        del get
        ip_string = f"""
      Local:       {c(f'http://localhost:{AppServerArgs.port}/', 'green')}
      External Ip: {c(f'http://{host_ip}:{AppServerArgs.port}/', 'green')}"""
    else:
        ip_string = f"""
      Local: {c(f'http://localhost:{AppServerArgs.port}/', 'green')}"""
    # try:
    #     hostname = socket.gethostname()
    #     host_ip = socket.gethostbyname(hostname)
    # except Exception as e:
    #     host_ip = "<not available>"

    print(f"""
    You can now view {c('ml-dash client', 'white')} in the browser.
{ip_string}

    To update to the newer version, do 
    {c('~>', 'blue')} {c('pip install --upgrade ml-dash', 'red')}
        
    """)
    app.run(**vars(AppServerArgs))
