import socket
import threading
import sys
import time

class P2PNode:
    def __init__(self, host, port):
        """
        Initialize the node.
        :param host: Host IP address (e.g., "127.0.0.1")
        :param port: Port number to listen on
        """
        self.host = host
        self.port = port
        self.peers = []  # List of connected peer sockets
        self.running = True
        self.lock = threading.Lock()
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.server_socket.bind((self.host, self.port))
        except Exception as e:
            print(f"[ERROR] Error binding to {self.host}:{self.port}: {e}")
            sys.exit(1)
        self.server_socket.listen(5)
        print(f"[INFO] Node listening on {self.host}:{self.port}")

    def start(self):
        """Starts the node's server thread."""
        server_thread = threading.Thread(target=self._server_loop, daemon=True)
        server_thread.start()
        print("[INFO] Server thread started.")

    def _server_loop(self):
        """Accept incoming connections and handle them."""
        while self.running:
            try:
                client_socket, addr = self.server_socket.accept()
                print(f"[INFO] Accepted connection from {addr}")
                handler_thread = threading.Thread(
                    target=self._handle_client, args=(client_socket, addr), daemon=True
                )
                handler_thread.start()
            except Exception as e:
                if self.running:
                    print(f"[ERROR] Error accepting connections: {e}")
                    
    def _handle_client(self, client_socket, addr):
        """Receive and display messages from a connected peer."""
        while self.running:
            try:
                data = client_socket.recv(1024)
                if not data:
                    print(f"[INFO] Connection closed by {addr}")
                    break

                message = data.decode('utf-8')
                print(f"[RECEIVED] From {addr}:{message}")

                # Extract sender IP and Port from message format "<peer_ip>:<peer_port>:<actual_message>"
                parts = str(message).split(":", 2)
                print(parts)
                if len(parts) == 3:
                    sender_ip, sender_port, actual_message = parts
                    sender_port = int(sender_port)  # Convert port to int
                    # Add peer using extracted IP and Port
                    # self.add_peer_if_needed(client_socket, (sender_ip, sender_port))
                    self.connect_to_peer(sender_ip, sender_port)
                    # Process QUERY_PEERS request
                    if actual_message == "QUERY_PEERS":
                        peer_list = self.get_peer_list()
                        client_socket.sendall(peer_list.encode('utf-8'))
                    elif len(actual_message) > 4 and actual_message.startswith("exit"):
                        peer_ip = actual_message.split()[1]
                        peer_port = int(actual_message.split()[2])
                        self.remove_peer(peer_ip, peer_port)
                    else:
                        print(f"[MESSAGE] {sender_ip}:{sender_port}:{actual_message}")
                elif message == "QUERY_PEERS":
                    peer_list = self.get_peer_list()
                    client_socket.sendall(peer_list.encode('utf-8'))
                else:
                    print(f"[ERROR] Invalid message format received: {message}")

            except Exception as e:
                print(f"[ERROR] Error reading from {addr}: {e}")
                break
        client_socket.close()


    def connect_to_peer(self, peer_ip, peer_port):
        """
        Connect to another peer.
        :param peer_ip: The IP address of the peer.
        :param peer_port: The port number of the peer.
        """
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((peer_ip, peer_port))
            with self.lock:
                self.peers.append(s)
            print(f"[INFO] Connected to peer {peer_ip}:{peer_port}")
        except Exception as e:
            print(f"[ERROR] Unable to connect to peer {peer_ip}:{peer_port}: {e}")

    def add_peer_if_needed(self, client_socket, addr):
        """Automatically add the peer to the list if it's not already there."""
        peer_ip, peer_port = addr
        with self.lock:
            # Check if the peer is already in the list
            for peer_socket in self.peers:
                if peer_socket.getpeername() == (peer_ip, peer_port):
                    print(f"[INFO] Peer {peer_ip}:{peer_port} is already connected.")
                    return  # Peer is already in the list, no need to add again
            # If not already in the list, add it
            print(f"[INFO] Adding new peer {peer_ip}:{peer_port} to the list.")
            self.peers.append(client_socket)

    def query_peer(self, peer_ip, peer_port):
        """
        Query a connected peer.
        :param peer_ip: The IP address of the peer.
        :param peer_port: The port number of the peer.
        """
        with self.lock:
            for peer_socket in self.peers:
                try:
                    if peer_socket.getpeername() == (peer_ip, peer_port):
                        print(f"Found peer {peer_ip}:{peer_port}")
                        return peer_socket
                except Exception as e:
                    print(f"[ERROR] Error querying peer {peer_ip}:{peer_port}: {e}")
            print(f"[WARN] Peer {peer_ip}:{peer_port} not found.")
            return None

    def select_peer(self, peer_ip, peer_port):
        """Retrieve the peer list from another peer."""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((peer_ip, peer_port))
            s.sendall(b"QUERY_PEERS")
            response = s.recv(4096).decode('utf-8')
            s.close()
            print(f"[INFO] Peer list from {peer_ip}:{peer_port}:\n{response}")
        except Exception as e:
            print(f"[ERROR] Unable to query peer {peer_ip}:{peer_port}: {e}")

    def remove_peer(self, peer_ip, peer_port):
        """
        Remove a connected peer by IP and port.
        :param peer_ip: The IP address of the peer.
        :param peer_port: The port number of the peer.
        """
        with self.lock:
            for peer_socket in self.peers:
                try:
                    if peer_socket.getpeername() == (peer_ip, peer_port):
                        self.peers.remove(peer_socket)
                        peer_socket.close()
                        print(f"[INFO] Removed peer {peer_ip}:{peer_port}")
                        return
                except Exception as e:
                    print(f"[ERROR] Error removing peer {peer_ip}:{peer_port}: {e}")
            print(f"[WARN] Peer {peer_ip}:{peer_port} not found.")

    def list_peers(self):
        """Display all connected peers."""
        with self.lock:
            if self.peers:
                print("[INFO] Connected peers:")
                unique_peers = set()
                for peer_socket in self.peers:
                    try:
                        # print(f" - {peer_socket.getpeername()}")
                        unique_peers.add(f" - {peer_socket.getpeername()}")
                    except Exception as e:
                        print(f"[ERROR] Could not retrieve peer address: {e}")
                for peer in sorted(unique_peers):
                    print(peer)
            else:
                print("[INFO] No connected peers.")


    def send_to_peers(self, message):
        """
        Send a message to all connected peers.
        :param message: The message string to send.
        """
        message = f"{self.host}:{self.port}:{message}"
        with self.lock:
            for peer_socket in self.peers:
                try:
                    peer_socket.sendall(message.encode('utf-8'))
                    print(f"[SENT] To {peer_socket.getpeername()}: {message}")
                except Exception as e:
                    print(f"[ERROR] Error sending to {peer_socket.getpeername()}: {e}")

    def get_peer_list(self):
        """Return a string representation of connected peers."""
        peer_list = []
        with self.lock:
            for peer_socket in self.peers:
                try:
                    peer_list.append(f"{peer_socket.getpeername()[0]}:{peer_socket.getpeername()[1]}")
                except Exception as e:
                    print(f"[ERROR] Could not retrieve peer address: {e}")
        return "\n".join(peer_list) if peer_list else "No peers connected."

    def stop(self):
        """Stop the node and close all connections."""
        self.running = False
        self.server_socket.close()
        with self.lock:
            for peer_socket in self.peers:
                peer_socket.close()
        print("[INFO] Node stopped.")


if __name__ == '__main__':
    # Usage: python p2p_node.py <host> <port> [<peer_ip> <peer_port> ...]
    if len(sys.argv) < 3:
        print("Usage: python p2p_node.py <host> <port> [<peer_ip> <peer_port> ...]")
        sys.exit(1)

    host = sys.argv[1]
    port = int(sys.argv[2])
    node = P2PNode(host, port)
    node.start()

    # Give the server a moment to start
    time.sleep(1)

    # Optionally connect to any peers provided as additional arguments.
    if len(sys.argv) > 3:
        if (len(sys.argv) - 3) % 2 != 0:
            print("Peers must be provided in pairs: <peer_ip> <peer_port>")
            sys.exit(1)
        for i in range(3, len(sys.argv), 2):
            peer_ip = sys.argv[i]
            peer_port = int(sys.argv[i+1])
            node.connect_to_peer(peer_ip, peer_port)

    # Interactive loop for commands.
    try:
        while True:
            print('''List Of Commands : 
                  1) Send (send a message to the connected peers. Usage : send <your_message>)
                  2) Add (add a peer to your network. Usage : add <peer_ip> <peer_port>)
                  3) Delete (Remove a peer from your network. Usage : delete <peer_ip> <peer_port>)
                  4) List (display the list of your peers. Usage : list)
                  5) Query (check whether a peer is connected on your network. Usage : query <peer_ip> <peer_port)
                  6) Select (see the list of peers connected to a peer of yours. Usage : selecty <peer_ip> <peer_port>)
                  7) Exit (exit the network. Usage : exit)''')
            command = input("Enter command (send/add/del/list/query/select/exit): ").strip()
            if not command:
                continue
            parts = command.split()
            cmd = parts[0].lower()

            if cmd == 'exit':
                break
            elif cmd == 'query':
                if len(parts) != 3:
                    print("Usage: query <peer_ip> <peer_port>")
                    continue
                peer_ip = parts[1]
                try:
                    peer_port = int(parts[2])
                except ValueError:
                    print("Invalid port number.")
                    continue
                node.query_peer(peer_ip, peer_port)
            elif cmd == 'send':
                if len(parts) < 2:
                    print("Usage: send <message>")
                    continue
                message = " ".join(parts[1:])
                node.send_to_peers(message)
                # After sending message, listen for peers or send add request
                print("[INFO] Listening for connections...")
                time.sleep(1)  # Simulate short time before checking
                node.list_peers()
            elif cmd == 'select':
                if len(parts) != 3:
                    print("Usage: select <peer_ip> <peer_port>")
                    continue
                peer_ip = parts[1]
                peer_port = int(parts[2])
                node.select_peer(peer_ip, peer_port)
            elif cmd == 'add':
                if len(parts) != 3:
                    print("Usage: add <peer_ip> <peer_port>")
                    continue
                peer_ip = parts[1]
                try:
                    peer_port = int(parts[2])
                except ValueError:
                    print("Invalid port number.")
                    continue
                node.connect_to_peer(peer_ip, peer_port)
            elif cmd in ('del', 'delete', 'remove'):
                if len(parts) != 3:
                    print("Usage: del <peer_ip> <peer_port>")
                    continue
                peer_ip = parts[1]
                try:
                    peer_port = int(parts[2])
                except ValueError:
                    print("Invalid port number.")
                    continue
                node.remove_peer(peer_ip, peer_port)
            elif cmd == 'list':
                node.list_peers()
            else:
                print("Unknown command. Valid commands: send, add, del, list, exit")
        node.send_to_peers(f"exit {host} {port}")
    except KeyboardInterrupt:
        print("\n[INFO] KeyboardInterrupt received.")

    node.stop()


#Team Hashverse
