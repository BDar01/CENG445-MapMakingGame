import socket

class GameClient:
    def __init__(self, host, port):
        self.server_address = (host, port)
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect(self.server_address)

    def send_command(self, command):
        self.client_socket.send(command.encode())
        response = self.client_socket.recv(1024).decode()
        return response

    def close(self):
        self.client_socket.close()

# Example Usage:

if __name__ == "__main__":
    # Replace 'localhost' and 1423 with the actual server address and port
    client = GameClient('localhost', 1423)

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
        # Close the client connection on exit
        client.close()