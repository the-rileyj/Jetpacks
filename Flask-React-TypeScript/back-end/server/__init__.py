from .routes import *
from .server import *


main = __name__ == "__main__"

app, run_server = get_server(main, os.path.join(os.getcwd(), "static"))
