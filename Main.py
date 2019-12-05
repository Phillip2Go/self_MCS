from application.server.Server import Server

CSV_PATH = "resources/cameras.csv"


if __name__ == '__main__':
    """
    Main class to start the server application
    """
    server = Server(CSV_PATH)
    server.start()
