# Tester for latency and throughput
# Runs and measures ping/pong (RTT) time for latency and iperf3 for throughput
# Establish IP/Port before making connection

import subprocess
import json
import time
import socket
import psutil
import threading
import argparse
from datetime import datetime

class NetworkBenchmark:
    def __init__(self, ip, port, connection_type):
        self.ip = ip
        self.port = port
        self.type = connection_type
        self.results = []

    def measure_latency(self, cycles=20):
        print(f"Measuring RTT for {self.type}")
        
        latencies = []
        payload = b'x' * 64  # 64 byte packet
        
        try:
            # Connect make intial connection (removes handshake time from the equation) 
            s = socket.create_connection((self.ip, self.port), timeout=5)
           
            # Repeat cycles times
            for _ in range(cycles):
                # Start timer
                start = time.perf_counter()
                
                # Send packet
                s.sendall(payload)
                
                # Wait for pong
                data = s.recv(1024)
               
                # Stop timer
                end = time.perf_counter()
               
                # Check for errors
                if data == payload:
                    rtt_ms = (end - start) * 1000
                    latencies.append(rtt_ms)
                else:
                    print("Packet mismatch or loss")
                
                time.sleep(0.1) # Slight buffer
            
            s.close()
            
            avg_latency = sum(latencies) / len(latencies)
            
            print(f"Avg RTT: {avg_latency} ms")
            return avg_latency
            
        except Exception as e:
            print(f"RTT failed: {e}")
            return None

    def measure_throughput(self, duration=10):
        print(f"Measuring Throughput for {self.type}")
       
        # Command: iperf3 -c <IP> -t <TIME> -J
        cmd = ["iperf3", "-c", self.ip, "-t", str(duration), "-J"]
       
        # Run iperf3 and get the output
        result = subprocess.run(cmd, capture_output=True, text=True)
       
        # Parse JSON output
        try:
            data = json.loads(result.stdout)
            
            # Extract bits_per_second from the end summary
            bps = data['end']['sum_sent']['bits_per_second']
            mbps = bps / 1e6
            cpu_util = data['end']['cpu_utilization_percent']['host_total']
            
            print(f"Throughput: {mbps} Mbps")
            print(f"CPU Load: {cpu_util}%")
            return mbps, cpu_util

        except json.JSONDecodeError:
            print("Error in JSON Parse")
            return 0, 0

    def run_tests(self):
        latency = self.measure_latency()
        throughput, cpu = self.measure_throughput()
        
        return {
            "timestamp": datetime.now().isoformat(),
            "connection_type": self.type,
            "latency_ms": round(latency, 3),
            "throughput_mbps": round(throughput, 3),
            "cpu_load": round(cpu, 2)
        }

if __name__ == "__main__":
    # Get args
    parser = argparse.ArgumentParser(description="Run tests on latency and throughput of VPN vs SSH Tunnel")
    
    parser.add_argument("--ip")
    parser.add_argument("--port", type=int, default=5201)

    parser.add_argument("--connection_type")

    args= parser.parse_args()

    # Make obj
    tester = NetworkBenchmark(args.ip, args.port, args.connection_type)

    # Run
    print(tester.run_tests())
