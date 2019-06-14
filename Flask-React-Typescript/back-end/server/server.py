import argparse
import os
import sys

import flask
import flask_cors

try:
    # Importing in a package context
    from . import routes
except:
    # Importing in a "__main__" context
    import routes


def get_server(main, static_folder=None):
    if static_folder is None:
        static_folder = os.path.join(os.getcwd(), "static")

    connect_host = None
    connect_port = None
    debug = False
    port = 80

    if main:
        parser = argparse.ArgumentParser()

        parser.add_argument("-ch", "--connect-host", default=connect_host, dest="connect_host", help="Host used for connecting to the Banyan server", required=False, type=str)
        parser.add_argument("-cp", "--connect-port", default=connect_port, dest="connect_port", help="Port used for connecting to the Banyan server", required=False, type=str)
        parser.add_argument("-d", "--debug", action='store_true', default=debug, help="Enable handling CORS requests and enable Flask debugging", required=False)
        parser.add_argument("-p", "--port", default=port, help="Port to run the webserver on", required=False, type=int)

        args = parser.parse_args()

        connect_host = args.connect_host
        connect_port = args.connect_port
        debug = args.debug
        port = args.port

    ### Web App Setup

    ### Not setting the static folder will have it default to "static", which causes any route
    ### with "static" in it to be overridden and handled as though the request wants static content
    app = flask.Flask(__name__, static_folder=None)

    if debug:
        flask_cors.CORS(app)

    app.secret_key = "none"

    ### Route Registration

    authenticate = routes.make_authenticator(lambda: False)

    ###### Unautheticated Routes

    routes.wrap_route_with_decorators(
        app.route("/api/hello", methods=["GET", "POST"]),
        routes.hello()
    )

    ###### Autheticated Routes

    # routes.wrap_route_with_decorators(
    #     app.route("/api/no_auth/banyan/env/create", methods=["GET", "POST"]),
    #     routes.hello(),
    #     authenticate,
    # )

    ### Register Static File Serving

    routes.register_static_file_serving(app, static_folder)

    return app, lambda: app.run(debug=debug, port=port)
