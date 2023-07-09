import argparse
import socket
import time
import threading

CHUNK_SIZE = 1000 # Sets the size of the data chunks to 1000 bytes

def print_statistics(client_address, bytes_sent, interval_number, interval_size, format):
    """
    Description:
    Prints statistics for the data transfer, including the client's IP address, 
    the number of bytes sent/received, the time interval, and the transfer rate.

    Arguments:
    None

    Input Parameters:
    client_address (tuple): The IP address and port number of the client.
    bytes_sent (int): The number of bytes sent or received.
    interval_number (int): The interval number.
    interval_size (float): The interval size in seconds.
    format (str): The output data format (B, KB, or MB).

    Output Parameters:
    None

    Returns:
    None

    Exceptions:
    ValueError: Ensures that the 'bytes_sent' and 'interval_size' input parameters are valid.
    """
    # Ensures that the 'bytes_sent' and 'interval_size' input parameters are valid.
    if bytes_sent < 0 or interval_size <= 0:
        raise ValueError("Invalid input parameters: bytes_sent must positive, interval_size must be positive")
    
    # Determines how to format the bytes_sent value based on the format parameter
    if format == "B":
        bytes_transfered = f"{bytes_sent} B"
    elif format == "KB":
        bytes_transfered = f"{bytes_sent/CHUNK_SIZE:.0f} KB"
    else:
        bytes_transfered = f"{bytes_sent/CHUNK_SIZE/CHUNK_SIZE:.2f} MB"
    
    # Creates a string identifier for the client using their IP address and port number
    id = f"{client_address[0]}:{client_address[1]}"
    
    # Calculates the start and end times of the current interval
    interval = f"{interval_number * interval_size:.1f} - {interval_number * interval_size + interval_size:.1f}"
    
    # Calculates the bandwidth for the current interval
    bandwidth = f"{(bytes_sent/CHUNK_SIZE/CHUNK_SIZE/interval_size)*8:.1f} Mbps"

    # Prints out the statistics in a formatted string
    print(f"{id:<16} {interval:<12} {bytes_transfered:<12} {bandwidth:<12}")

def server(args):
    """
    Description:
    Listen for incoming client connections and spawn a new thread to handle each connection.

    Arguments:
    -b, --bind: The IP address of the server interface to bind to. The default value is 8088.
    -p, --port: The port number to listen on. The default value is "127.0.0.1".
    -f, --format: The output data format (B, KB, or MB). The default value is "MB".

    Input Parameters:
    args: an object containing the values of the arguments that were 
    specified on the command line when the server flag was used. Example:
    - args.bind: IP address of the server interface
    - args.port: Port number on which the server should listen

    Output Parameters:
    None

    Returns:
    None

    Exceptions:
    If an exception is caught, the function 
    closes the client socket and prints an error message to the console,
    but it does not terminate the entire program. Instead, it continues 
    listening for incoming connections from other clients.
    """
    # Creates a new socket object using the IPv4 address family and TCP protocol
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        # Sets the SO_REUSEADDR socket option to avoid "Address already in use" errors
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # Binds the socket to the specified address and port
        server_socket.bind((args.bind, args.port))
        # Start listening for incoming connections
        server_socket.listen()

        # Prints out a message indicating that the server is now listening
        print("-----------------------------------------------------------")
        print(f"A simpleperf server listening on {args.bind}, port {args.port}")
        print("-----------------------------------------------------------\n")

        # Enters an infinite loop to handle incoming client connections
        while True:
            # Waits for a client to connect
            client_socket, client_address = server_socket.accept()
            # Prints out a message indicating that a new client has connected
            print(f"A simpleperf client with {client_address[0]}:{client_address[1]} is connected with {args.bind}:{args.port}")

            # Starts a new thread to handle the client
            client_thread = threading.Thread(target=handle_client, args=(client_socket,))
            client_thread.start()


def handle_client(client_socket: socket):
    """
    Description:
    Receive data from the client in chunks and send an ACK message 
    back to the client when the BYE message is received.

    Arguments:
    -f, --format: The output data format (B, KB, or MB).

    Input Parameters:
    client_socket: socket: The socket object representing the client connection.
    
    Output Parameters:
    None

    Returns:
    None

    Exceptions:
    If an error occurs while receiving data from the client, 
    the function will exit the while loop and close the client socket.
    """
    # Initializes variables to keep track of the number of bytes received,
    # the client's address, and the start time
    bytes_received = 0
    client_address = client_socket.getpeername()
    start_time = time.time()
    
    try:
        # Enters a loop to receive data from the client
        while True:
            # Receives data from the client in chunks of size CHUNK_SIZE
            data = client_socket.recv(CHUNK_SIZE)
            # Keeps track of the number of bytes received
            bytes_received += len(data)
            # Checks if the client has sent the "BYE" message to indicate the end of the connection
            if data[-3:] == b'BYE':
                # Sends an acknowledgement message to the client
                client_socket.send(b'ACK:BYE')

                # Calculates the elapsed time since the start of the connection
                end_time = time.time() - start_time
                
                # Prints out statistics for the connection
                print(f"\n{'Id':<16} {'Interval':<12} {'Received':<12} {'Rate':<12}")
                print_statistics(client_address, bytes_received, 0, end_time, args.format)
                
                # Exits the loop
                break
    finally:
        # Closes the client socket when the connection is finished
        client_socket.close()

def client(args):
    """
    Description:
    Connect to the server and send data in chunks for a specified duration or number of bytes.

    Arguments:
    
    -I, --serverip: The IP address of the server to connect to.
    -p, --port: The port number to connect to.
    -t, --time: The total duration in seconds for which data should be generated.
    -i, --interval: The interval in seconds at which to print statistics.
    -f, --format: The output data format (B, KB, or MB).
    -P, --parallel: The number of parallel connections to create.
    -n, --num: The total number of bytes to transfer in B, KB, or MB.

    Input Parameters:
    args: an object containing the values of the arguments that were
    specified on the command line when the client was started.

    Output Parameters:
    None

    Returns:
    None

    Exceptions:
    socket.error: A subclass of OSError that is raised when there is an error 
    communicating with the server, such as a broken pipe or a connection reset by the server.
    KeyboardInterrupt: Raised when the user presses Ctrl+C to terminate the program.
    """
    # Creates a new socket object using the IPv4 address family and TCP protocol
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Connects to the server at the specified address and port
    client_socket.connect((args.serverip, args.port))
    # Gets the IP address and port number of the client socket
    client_address = client_socket.getsockname()
    # Gets the interval duration from the command-line arguments
    interval_duration = args.interval
    
    # Prints out a message indicating that the client has connected to the server
    print(f"{client_address[0]}:{client_address[1]} connected with {args.serverip} port {args.port}")

    # Sends the "START" command to the server, specifying the duration of the connection
    client_socket.sendall(f"START {args.time}".encode())

    # Prepares data to send in chunks of size CHUNK_SIZE
    data = b'0' * CHUNK_SIZE
    total_bytes_sent = 0
    interval_sent = 0
    start_time = time.time()
    total_time = 0
    interval_number = 0
    last_interval_start_time = start_time

    # Prints out a header for the statistics table if interval_duration is specified
    if interval_duration:
        print(f"{'Id':<16} {'Interval':<12} {'Received':<12} {'Rate':<12}")

    # Converts the num argument to bytes if it is specified
    if args.num:
        num_bytes = int(args.num[:-2])
        if args.num.endswith('KB'):
            num_bytes *= CHUNK_SIZE
        elif args.num.endswith('MB'):
            num_bytes *= CHUNK_SIZE * CHUNK_SIZE

    # Enters a loop to send data to the server in chunks
    while True:
        # Stops sending when the time or byte limit is reached
        if total_time > args.time or (args.num and total_bytes_sent > num_bytes):
            break

        # Sends data to the server in chunks of size CHUNK_SIZE
        client_socket.sendall(data)
        total_bytes_sent += CHUNK_SIZE
        interval_sent += CHUNK_SIZE
        total_time = time.time() - start_time
        time_since_last_interval = time.time() - last_interval_start_time

        # Prints out statistics for the current interval if interval_duration is specified and the interval has ended
        if interval_duration and time_since_last_interval > interval_duration:
            print_statistics(client_address, interval_sent, interval_number, interval_duration, args.format)
            interval_number += 1
            interval_sent = 0
            last_interval_start_time = time.time()

    # Prints out statistics for the final interval if interval_duration is specified
    if interval_duration:
        print_statistics(client_address, interval_sent, interval_number, interval_duration, args.format)
        print("-"*60)
    
    # Sends the "BYE" command to the server and receive an acknowledgement
    client_socket.send(b'BYE')
    ack = client_socket.recv(1024)
    # Closes the client socket
    client_socket.close()
    
    # Prints out total statistics for the connection
    print(f"\n{'Id':<16} {'Interval':<12} {'Received':<12} {'Rate':<12}")
    print_statistics(client_address, total_bytes_sent, 0, total_time, args.format)

if __name__ == '__main__':
    # Creates an argument parser object and add command-line arguments
    parser = argparse.ArgumentParser(description='Simple network performance test.')
    
    # Adds common arguments for both server and client
    parser.add_argument('-s', '--server', action='store_true', help='Enable server mode.')
    parser.add_argument('-c', '--client', action='store_true', help='Enable client mode.')
    parser.add_argument('-p', '--port', type=int, default=8088, help='Port number on which the server should listen.')
    parser.add_argument('-f', '--format', choices=['B', 'KB', 'MB'], default='MB', help='Output data format.')
    
    # Adds server-specific arguments
    parser.add_argument('-b', '--bind', default='127.0.0.1', help='IP address of the server interface.')
    
    # Adds client-specific arguments
    parser.add_argument('-I', '--serverip', default='127.0.0.1', help='IP address of the server.')
    parser.add_argument('-t', '--time', type=float, default=25, help='Total duration in seconds for which data should be generated.')
    parser.add_argument('-i', '--interval', type=int, default=None, help='Print statistics per interval seconds')
    parser.add_argument('-P', '--parallel', type=int, default=1, help='Number of parallel connections to create (default 1)')
    parser.add_argument('-n', '--num', type=str, default=None, help='Total number of bytes to transfer in B, KB, or MB')
    
    # Parses the command-line arguments and store them in the args object
    args = parser.parse_args()

    # Checks if server mode is enabled
    if args.server:
        # Sets the start_time attribute to the current time
        args.start_time = time.time()
        # Runs the server function with the command-line arguments
        server(args)
    # Checks if client mode is enabled
    elif args.client:
        # Prints a message indicating that the client is connecting to the server
        print("-----------------------------------------------------------")
        print(f"A simpleperf client connecting to server {args.serverip}, port {args.port}")
        print("-----------------------------------------------------------\n")
        # Checks if parallel mode is enabled
        if args.parallel > 1:
            # Creates a separate client thread for each parallel connection
            for i in range(args.parallel):
                t = threading.Thread(target=client, args=(args,))
                t.start()
        # Runs a single client connection if parallel mode is not specified
        else:
            client(args)
    # Prints an error message if neither server nor client mode is specified
    else:
        print("You need to specify either client or server mode.")
        exit()
