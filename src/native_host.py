#!/usr/bin/env python3
"""
Native Messaging Host for Neural-Chromium Extension
Handles communication between Chrome extension and nexus_agent.py
"""

import sys
import json
import struct
import threading
import queue
import time
import os

# Message queues for bidirectional communication
outgoing_queue = queue.Queue()
incoming_queue = queue.Queue()

def log(message):
    """Log to stderr (stdout is used for Native Messaging)"""
    sys.stderr.write(f"[NativeHost] {message}\n")
    sys.stderr.flush()

def read_message():
    """Read a message from Chrome extension (stdin)"""
    try:
        # Read message length (4 bytes, little-endian)
        raw_length = sys.stdin.buffer.read(4)
        if not raw_length or len(raw_length) < 4:
            return None
        
        message_length = struct.unpack('=I', raw_length)[0]
        
        # Read message
        message = sys.stdin.buffer.read(message_length).decode('utf-8')
        return json.loads(message)
    except Exception as e:
        log(f"Read error: {e}")
        return None

def send_message(message):
    """Send a message to Chrome extension (stdout)"""
    try:
        encoded_message = json.dumps(message).encode('utf-8')
        encoded_length = struct.pack('=I', len(encoded_message))
        
        sys.stdout.buffer.write(encoded_length)
        sys.stdout.buffer.write(encoded_message)
        sys.stdout.buffer.flush()
    except Exception as e:
        log(f"Write error: {e}")

def message_reader():
    """Thread to read messages from extension"""
    while True:
        try:
            message = read_message()
            if message is None:
                log("Connection closed by extension")
                break
            
            # Filter out pong messages to avoid queue bloat
            if message.get('pong'):
                # log("Received pong") 
                continue
                
            log(f"Received: {message}")
            incoming_queue.put(message)
        except Exception as e:
            log(f"Reader error: {e}")
            break

def message_writer():
    """Thread to write messages to extension"""
    while True:
        try:
            message = outgoing_queue.get()
            if message is None:
                break
            log(f"Sending: {message}")
            send_message(message)
        except Exception as e:
            log(f"Writer error: {e}")
            break

# Global command handler (will be set by nexus_agent.py)
command_handler = None

def set_command_handler(handler):
    """Set the function to handle incoming commands"""
    global command_handler
    command_handler = handler

def send_command(action, params):
    """Send a command to the extension"""
    message_id = int(time.time() * 1000)
    message = {
        'id': message_id,
        'action': action,
        'params': params
    }
    outgoing_queue.put(message)
    
    # Wait for response (with timeout)
    timeout = 5
    start = time.time()
    while time.time() - start < timeout:
        try:
            response = incoming_queue.get(timeout=0.1)
            if response.get('id') == message_id:
                return response
        except queue.Empty:
            continue
    
    return {'success': False, 'error': 'Timeout waiting for response'}

import socket

# ... existing code ...

# Socket Server settings
HOST = '127.0.0.1'
PORT = 9223
socket_queue = queue.Queue()

def socket_handler(conn, addr):
    """Handle individual socket client connection"""
    log(f"Socket connected by {addr}")
    with conn:
        while True:
            try:
                # Read 4-byte length
                length_bytes = conn.recv(4)
                if not length_bytes: break
                length = struct.unpack('!I', length_bytes)[0]
                
                # Read data
                data = b''
                while len(data) < length:
                    packet = conn.recv(length - len(data))
                    if not packet: break
                    data += packet
                    
                if not data: break
                
                # Parse command
                command = json.loads(data.decode('utf-8'))
                log(f"Socket received: {command}")
                
                # Forward to browser (Chrome Extension)
                # We need a way to correlate responses back to socket
                # For now, simplistic approach: queue it
                send_message(command)
                
                # Wait for response from extension? 
                # Ideally we want synchronous-like behavior for the client
                # But read_message() is in another thread.
                # Let's use a response map if needed, or simple ACK for now
                response = {"status": "sent", "id": command.get("id")}
                
                # Send response back to socket
                resp_bytes = json.dumps(response).encode('utf-8')
                conn.sendall(struct.pack('!I', len(resp_bytes)) + resp_bytes)
                
            except Exception as e:
                log(f"Socket handler error: {e}")
                break
    log(f"Socket disconnected {addr}")

def socket_server():
    """Start Socket Server for IPC"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((HOST, PORT))
            s.listen()
            log(f"Socket server listening on {HOST}:{PORT}")
            while True:
                conn, addr = s.accept()
                t = threading.Thread(target=socket_handler, args=(conn, addr), daemon=True)
                t.start()
    except Exception as e:
        log(f"Socket server initialization failed: {e}")

def heartbeat_loop():
    """Send periodic heartbeats to keep extension alive"""
    log("Heartbeat thread started")
    while True:
        try:
            time.sleep(20)
            # Send ping to Extension
            # We construct the message manually since send_command waits for response
            # and we don't want to block this thread or fill the queue if stuck.
            # But outgoing_queue is safe.
            msg = {
                'id': int(time.time() * 1000),
                'action': 'ping',
                'params': {}
            }
            outgoing_queue.put(msg)
        except Exception as e:
            log(f"Heartbeat error: {e}")
            break

def main_loop():
    """Main loop to process incoming messages"""
    log("Native host started")
    
    # Start reader/writer threads
    reader_thread = threading.Thread(target=message_reader, daemon=True)
    writer_thread = threading.Thread(target=message_writer, daemon=True)
    socket_thread = threading.Thread(target=socket_server, daemon=True)
    
    reader_thread.start()
    writer_thread.start()
    socket_thread.start()
    
    # Start Heartbeat to keep Service Worker alive
    threading.Thread(target=heartbeat_loop, daemon=True).start()
    
    # Send initial connection message to Chrome
    send_message({'status': 'connected', 'version': '1.0.0'})
    
    # Keep alive and process queue
    while True:
        try:
            # Check if connection is still alive
            if not reader_thread.is_alive():
                log("Reader thread died, exiting")
                break
                
            time.sleep(1)
        except KeyboardInterrupt:
            break
        except Exception as e:
            log(f"Main loop error: {e}")
            break
    
    log("Native host exiting")
    os._exit(0) # Force exit to kill all threads


if __name__ == '__main__':
    try:
        main_loop()
    except KeyboardInterrupt:
        log("Interrupted")
    except Exception as e:
        log(f"Fatal error: {e}")
