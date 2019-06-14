from server import get_server

if __name__ == "__main__":
    _, run_server = get_server(True)

    run_server()