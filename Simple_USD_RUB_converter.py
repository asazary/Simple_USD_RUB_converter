import SVC_server
import sys

if __name__ == "__main__":
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError as e:
            print("Wrong parameter (port)! Will use default port (8080).")
            port = 8080
    else:
        port = 8080
    SVC_server.server(port)
