import json
import os
import sys
import tempfile
import warnings

# For ignoring warnings due to deprecated import method used in jinja2
warnings.filterwarnings("ignore")

import flask
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import server


### Testing Fixtures and Functions

@pytest.fixture
def static_file_fixture(tmpdir):
    app = flask.Flask(__name__, static_folder=None)

    app.config["TESTING"] = True

    server.register_static_file_serving(app, tmpdir)

    serveFile = tempfile.NamedTemporaryFile(dir=tmpdir, delete=False)

    index_content = "this is index.html"
    index_file = os.path.join(tmpdir, "index.html")

    with open(index_file, "w") as index_file_writer:
        index_file_writer.write(index_content)

    yield (app.test_client(), os.path.normpath(serveFile.name), index_content)


def get_server_test_fixture(*register_funcs):
    app = flask.Flask(__name__)

    for register_func in register_funcs:
        register_func(app)

    app.config["TESTING"] = True

    client = app.test_client()

    return client


### Testing Decorator Functions

def test_make_authenticator():
    allow_authenticator = server.make_authenticator(lambda: True)
    deny_authenticator = server.make_authenticator(lambda: False)

    test_content = "test"

    def test_route():
        return test_content, 200

    def register_allow_authenticator_route(app):
        server.wrap_route_with_decorators(
            app.route("/test"),
            test_route,
            allow_authenticator,
        )

    def register_deny_authenticator_route(app):
        server.wrap_route_with_decorators(
            app.route("/test"),
            test_route,
            deny_authenticator,
        )

    allow_client = get_server_test_fixture(register_allow_authenticator_route)
    deny_client = get_server_test_fixture(register_deny_authenticator_route)

    ### Test Allowing Requests

    allow_response = allow_client.get("/test")

    assert allow_response.status_code == 200 and allow_response.data == bytes(test_content, encoding="utf-8")


    ### Test Denying Requests

    deny_response = deny_client.get("/test")

    assert deny_response.status_code == 403 and deny_response.data != bytes(test_content, encoding="utf-8")


### Testing Various Handler Functions

def test_static_file_serving(static_file_fixture):
    client, serveFile, index_content = static_file_fixture

    # Test that only GET requests are handled
    response = client.post("/test")

    assert response.status_code == 405

    # Test that GET requests with Content-type JSON returns HTTP/404
    response = client.get("/test", headers={"Content-type": "JSON"})

    assert response.status_code == 404

    # Test that GET requests for content that exists in the static folder returns HTTP/200
    response = client.get(f"/{os.path.basename(serveFile)}")

    assert response.status_code == 200

    # Test that GET requests for content that doesn't exist in the static folder returns HTTP/200
    # with the index file
    response = client.get(f"/i_dont_exist")

    assert response.status_code == 200 and response.data == bytes(index_content, encoding="utf-8")

    # Test that GET requests for the index file via "/" returns HTTP/200 with the index file content
    response = client.get(f"/")

    assert response.status_code == 200 and response.data == bytes(index_content, encoding="utf-8")


### Testing API Handlers

def test_hello():
    def register_hello(app):
        server.wrap_route_with_decorators(
            app.route("/hello", methods=("GET", "POST")),
            server.hello(),
        )

    client = get_server_test_fixture(register_hello)

    ### Test Requests that should return a normal response

    response = client.get("/hello")

    assert response.status_code == 200 and response.get_data(as_text=True) == "hello"

    ### Test Requests that should return "hello {name}"

    response = client.post(
        "/hello",
        data=json.dumps(dict(name="rj")),
        content_type="application/json",
    )

    assert response.status_code == 200 and response.get_data(as_text=True) == "hello rj"

    ### Test Requests that will raise an error, POST'ing with no name

    response = client.post(
        "/hello",
        data=json.dumps(dict(notname="ha")),
        content_type="application/json",
    )

    assert response.status_code == 500
