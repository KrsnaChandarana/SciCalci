import socket
from threading import Thread

class CalculatorServer:
    def __init__(self, host='localhost', port=12345):
        self.host = host
        self.port = port
        self.server_socket = None
        self.running = False

    def start(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_socket.bind((self.host, self.port))
        self.running = True
        print(f"Calculator RPC Server running on {self.host}:{self.port}")

        while self.running:
            try:
                message, client_addr = self.server_socket.recvfrom(1024)
                Thread(target=self.handle_request, args=(message, client_addr)).start()
            except OSError:
                break

    def handle_request(self, message, client_addr):
        try:
            decoded = message.decode()
            print(f"Request from {client_addr}: {decoded}")
            
            operation, num1, num2 = decoded.split(',')
            num1, num2 = float(num1), float(num2)

            if operation == 'add':
                result = num1 + num2
            elif operation == 'subtract':
                result = num1 - num2
            elif operation == 'multiply':
                result = num1 * num2
            elif operation == 'divide':
                result = num1 / num2 if num2 != 0 else "Error: Division by zero"
            else:
                result = "Error: Invalid operation"
                
            self.server_socket.sendto(str(result).encode(), client_addr)
            print(f"Sent to {client_addr}: {result}")

        except Exception as e:
            error_msg = f"Error: {str(e)}"
            self.server_socket.sendto(error_msg.encode(), client_addr)

    def stop(self):
        self.running = False
        if self.server_socket:
            # Unblock the server
            temp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            temp_sock.sendto(b'', (self.host, self.port))
            temp_sock.close()
        print("Server stopped")

if __name__ == "__main__":
    server = CalculatorServer()
    try:
        server.start()
    except KeyboardInterrupt:
        server.stop()