import socket
import signal
import sys

class GameClient:
    def __init__(self, host, port):
        self.server_address = (host, port)
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect(self.server_address)
        # Register the signal handler for CTRL+C
        signal.signal(signal.SIGINT, self.signal_handler)

    def send_command(self, command):
        self.client_socket.send(command.encode())
        response = self.client_socket.recv(1024).decode()
        return response

    def close(self):
        self.client_socket.close()

    def signal_handler(self, signal, frame):
        print("Received Ctrl+C. Closing connection...")
        self.close()
        sys.exit(0)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print('usage: ', sys.argv[0], 'host port')
        sys.exit(-1)

    host = sys.argv[1]
    port = int(sys.argv[2])

    client = GameClient(host, port)

    try:
        while True:
            user_input = input("Enter command (or 'exit' to quit): ")

            if user_input.lower() == 'exit':
                break

            response = client.send_command(user_input)
            print(response)

    except KeyboardInterrupt:
        pass
    finally:
        client.close()
