import socket
import subprocess
import threading
import sys
import time

# CONFIGURATION
PORT = 10000

def run_server():
    # Start a socket server to listen on ECHO_PORT
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(('0.0.0.0', PORT))
        s.listen()
        print(f"RTT listening on {PORT}")
      
        # Loop continuously to listen for incomming packets
        while True:
            try:
                conn, addr = s.accept()
                threading.Thread(target=handle_packet, args=(conn,)).start()
            except Exception as e:
                print(f"RTT Error: {e}")

def handle_packet(conn):
    with conn:
        while True:
            # Read packet
            data = conn.recv(1024)
            if not data:
                break
            conn.sendall(data)  # Bounce incoming packet back

def run_iperf():
    print(f"Starting iperf3")
    try:
        # Run standard server mode
        subprocess.run(["iperf3", "-s"], check=True)
    except FileNotFoundError:
        # Program not installed err
        print("'iperf3' not found")
        sys.exit(1)
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    # Start Socket Server
    sock_srv = threading.Thread(target=run_server, daemon=True)
    sock_srv.start()
    
    # Start iperf3 server in main thread
    run_iperf()
