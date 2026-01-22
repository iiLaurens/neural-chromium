import socket
import json
import struct
import time

HOST = '127.0.0.1'
PORT = 9223

def send_command(action, params):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            
            command = {
                "id": int(time.time()),
                "action": action,
                "params": params
            }
            
            # Send length-prefixed message
            data = json.dumps(command).encode('utf-8')
            s.sendall(struct.pack('!I', len(data)) + data)
            print(f"Sent: {command}")
            
            # Read response
            length_bytes = s.recv(4)
            if length_bytes:
                length = struct.unpack('!I', length_bytes)[0]
                resp_data = s.recv(length)
                response = json.loads(resp_data.decode('utf-8'))
                print(f"Received: {response}")
                return response
                
    except ConnectionRefusedError:
        print("Connection failed: Is the extension (native host) running?")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print(f"Testing connection to {HOST}:{PORT}...")
    
    # Test typing into the search box
    send_command("type", {"text": "hello from python socket"})
    
    # Test getting DOM info
    # send_command("get_dom", {})
