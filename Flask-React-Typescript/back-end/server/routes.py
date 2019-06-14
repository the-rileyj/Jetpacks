import functools
import os

import flask

### Utility Functions

def wrap_route_with_decorators(app_handler_func, handler_func, *decorators):
    """wrap_route_with_decorators(...) wraps the given "handler_func" with the provided list of decorators
    "decorators" then attaches it to the app handler func "app_handler_func".

    Though the decorators are attached in the same order that they appear in the "decorators" list, they
    will be triggered in the reverse order, ex. with the "app_handler_func" being app.route("/hello") and the
    decorators list being [dec_func1, dec_func2], the order in which the functions will be registered is:

    dec_func1 -> dec_func2 -> app_handler_func

    However, the order in which the decorators will be called is

    app_handler_func -> dec_func2 -> dec_func1
    """
    for decorator in decorators:
        handler_func = decorator(handler_func)

    app_handler_func(handler_func)


### Handler Decorators

def make_authenticator(check_auth_func):
    def authenticate(func):
        @functools.wraps(func)
        def decorated_function(*args, **kwargs):
            if check_auth_func():
                return func(*args, **kwargs)

            return flask.jsonify({"data": {}, "err": True, "msg":"not authenticated"}), 403

        return decorated_function

    return authenticate


### Static File Handling

def register_static_file_serving(app, static_directory):
    @app.route("/", defaults={"path": "index.html"})
    @app.route("/<path:path>")
    def static_file_serving(path):
        """Serve static content or return index.html for GET requests that are not requesting json with
        unknown paths and return a 404 for any other kinds of request method with an unknown path"""
        # Handle serving static content
        if os.path.isfile(os.path.join(static_directory, path)):
            # Serve content if the path exists, regardless of HTTP method used
            return flask.send_from_directory(static_directory, path), 200
        elif flask.request.method == "GET" and flask.request.headers.get("Content-type", "").lower() != "json":
            # Serve "index.html" if the path requested does not exist, it was a HTTP GET request, and
            # the content-type requested is not JSON]
            return flask.send_from_directory(static_directory, "index.html"), 200

        # Return 404
        flask.abort(404)


### API Handlers

def hello():
    def handle_hello():
        """ Handles saying hello

        POST - JSON payload = {
            "name": str, => The name to say hello to
        }
        """
        try:
            if flask.request.method == "POST":
                hello_info = flask.request.get_json()

                return f"""hello {hello_info["name"]}"""

            return "hello"
        except Exception as err:
            return flask.jsonify({"err": True, "data": {}, "msg": f"Failed to say hello: {repr(err)}"}), 500

    return handle_hello
