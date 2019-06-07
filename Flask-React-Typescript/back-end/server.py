import argparse
import os

from functools import wraps

import flask
import flask_cors


### Helper Functions

def make_authenticater(check_auth_func):
    def authenticate(func):
        @wraps(func)
        def decorated_function(*args, **kwargs):
            if check_auth_func():
                return func(*args, **kwargs)

            flask.flash("Your account has expired. Update your billing info.")
            return flask.jsonify({"data": {}, "err": True, "msg":"not authenticated"})

        return decorated_function

    return authenticate


### Routing Engine setup

parser = argparse.ArgumentParser()

parser.add_argument("-d", "--debug", action='store_true', default=False, required=False)

parser.add_argument("-p", "--port", default=80, required=False)

args = parser.parse_args()

app = flask.Flask(__name__, static_folder="static")

app.secret_key = "none"

authenticate = make_authenticater(lambda: False)


### API routes

###### Unauthenticated Routes

@app.route("/api/no_auth/items")
def un_auth_hello_world():
    return flask.jsonify({"hello": "world"})

###### Authenticated Routes

@app.route("/api/auth/hello-world")
@authenticate
def auth_hello_world():
    return flask.jsonify({"hello": "world"})


### Static file routing

@app.route("/")
@app.route("/<path:path>")
def index(path):
    """Serve static content or return index.html for GET requests that are not requesting json with
    unknown paths and return a 404 for any other kinds of request method with an unknown path"""
    # Handle serving static content
    if os.path.exists(os.path.join(app.static_folder, path)):
        # Serve content if the path exists, regardless of HTTP method used
        return flask.send_from_directory(app.static_folder, path)
    elif flask.request.method == "GET" and flask.request.headers.get("Content-type", "").lower() != "json":
        # Serve "index.html" if the path requested does not exist, it was a HTTP GET request, and
        # the content-type requested is not JSON
        return flask.send_from_directory(app.static_folder, "index.html")

    # Return 404
    flask.abort(404)


### Run the routing engine

if __name__ == "__main__":
    if args.debug:
        flask_cors.CORS(app)

    app.run(debug=args.debug, port=args.port)
