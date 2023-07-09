Simpleperf is a command-line based network performance test tool, designed to evaluate the bandwidth between a server and client.

Server Mode
To run Simpleperf in server mode, execute the following command:

python simpleperf.py -s

By default, the server will bind to 127.0.0.1 and listen on port 8088. 
You can specify a different IP address and port using the -b and -p flags:

python simpleperf.py -s -b 192.168.1.2 -p 8088

Server Options
-b, --bind: The IP address of the server interface to bind to. The default value is 8088.
-p, --port: The port number to listen on. The default value is "127.0.0.1".
-f, --format: The output data format (B, KB, or MB). The default value is "MB".

Client Mode
To run Simpleperf in client mode, execute the following command:

python simpleperf.py -c

By default, the client will connect to a server at 127.0.0.1 on port 8088. 
You can specify a different server IP address and port using the -I and -p flags.

python simpleperf.py -c -I 192.168.1.2 -p 8088

Client Options
-I, --serverip: The IP address of the server to connect to.
-p, --port: The port number to connect to.
-t, --time: The total duration in seconds for which data should be generated.
-i, --interval: The interval in seconds at which to print statistics.
-f, --format: The output data format (B, KB, or MB).
-P, --parallel: The number of parallel connections to create.
-n, --num: The total number of bytes to transfer in B, KB, or MB.

Tests
To generate test data, you can run the server and client on the same machine, or on different machines connected to the same network. 
Here are a few examples of tests you can perform:

Run the server and client on the same machine:

Start the server in one terminal window
Start the client in another terminal window

Run the server and client on different machines:

Start the server on the first machine
Start the client on the second machine, specifying the server's IP address with the -I flag.

The program will generate the data automaticly after the client is connected to server.
You can specify the path of the output by adding "> output.txt" at the end of the command. Example:

python simpleperf.py -c -t 25 > output.txt



