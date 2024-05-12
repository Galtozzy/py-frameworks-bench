import time
from uuid import uuid4

from blacksheep import Application, get, post, put, FromFiles
from blacksheep.server.responses import html, json, bad_request, text, unauthorized


app = Application()


# first add ten more routes to load routing system
# ------------------------------------------------
def req_ok(request):
    return html('ok')


for n in range(5):
    app.router.add_get(f"/route-{n}", req_ok)
    app.router.add_get(f"/route-dyn-{n}/<part>", req_ok)


# then prepare endpoints for the benchmark
# ----------------------------------------
@get('/html')
async def view_html(request):
    """Return HTML content and a custom header."""
    response = html("<b>HTML OK</b>")
    response.add_header(b'x-time', f"{time.time()}".encode())
    return response


@post('/upload')
async def view_upload(files: FromFiles):
    """Load multipart data and store it as a file."""
    formdata = files.value
    if formdata is None:
        return bad_request()

    with open(f"./{uuid4().hex}", 'w', encoding='utf-8') as target:
        target.write(formdata[0].data.decode())

    return text(target.name)


@put('/api/users/{int:user}/records/{int:record}')
async def view_api(request):
    """Check headers for authorization, load JSON/query data and return as JSON."""
    if not request.headers.get(b'authorization'):
        return unauthorized()

    return json({
        'params': {k: int(v) for k, v in request.route_values.items()},
        'query': dict(request.query),
        'data': await request.json(),
    })
