<?php
include "lib/client.php";
include "lib/helper.php";
include "lib/blockchain.php";

if($argc !== 5){
	die('usage: ini_client.php (port_num) (process_id) (client_names) (ip)');
}

echo PHP_EOL . 
	'*****************************************************' . PHP_EOL
 	. 'Client Name: ' . $argv[3] . PHP_EOL . 
 	'*****************************************************' . PHP_EOL;

$client = new client($argv[1], $argv[2], $argv[3], $argv[4]);

$clients_list = helper::list_clients();

#print_r($clients_list);

$client->client_connections = array();
$client->blockchain_connection = NULL;

//1. connect to existing client if any. 
foreach($clients_list as $c_info){
	//do not connect to self!
	if($c_info['name'] == $argv[3]){
		continue;
	}

	sleep(1);

	echo "[Active Socket]Connecting to the client {$c_info['name']} > {$c_info['ip']}:{$c_info['port']}" . PHP_EOL;
	$sock = socket_create(AF_INET, SOCK_STREAM, getprotobyname('tcp'));
	$result = @socket_connect($sock, $c_info['ip'], $c_info['port']);
	//if connection TRUE, put it back in array!
	if($result){
		echo "[Active Socket]Connected to the client {$c_info['name']}" . PHP_EOL;
		@socket_write($sock, $argv[3], strlen($argv[3]));
		socket_set_nonblock($sock);
		$client->client_connections[$c_info['name']] = $sock;
	} else {
		echo "[Active Socket]Cannot reach the client {$c_info['name']}" . PHP_EOL;
		#echo PHP_EOL . 'Error_code: ' . socket_last_error() . PHP_EOL;
	}
}

//2. Done with connecting with all clients, then open listen server mode.
echo PHP_EOL . 'Client enters [Passive] connecting mode......' . PHP_EOL;
$passive_sock = socket_create(AF_INET, SOCK_STREAM, getprotobyname('tcp'));
socket_bind($passive_sock, $argv[4], $argv[1]);
socket_listen($passive_sock, 24);
socket_set_nonblock($passive_sock);
while (1) {
	//Keep checking incoming connection.
	$spawn = socket_accept($passive_sock);

	if($spawn){
		$input = @socket_read($spawn, 1024);
		$input = trim($input);

		echo PHP_EOL . "[Passive Socket]: received a socket connection from the client {$input}.". PHP_EOL; 
		if($input !== 'blockchain'){
			$client->client_connections[$input] = $spawn;
		} else {
			$client->blockchain_connection = $spawn;
		}
	} else {
		echo '. ';
		sleep(1);
	}

	if(count($client->client_connections) == count($clients_list) - 1 && $client->blockchain_connection){
	#if(count($client->client_connections) == count($clients_list) - 1){
		echo PHP_EOL . "All connections have been established!" . PHP_EOL;
		break;
	}
}

echo 'Clients Connections: ' . PHP_EOL;
print_r($client->client_connections);
echo PHP_EOL . 'Blockchain Connection: ' . PHP_EOL;
print_r($client->blockchain_connection);
echo PHP_EOL . PHP_EOL . 'Please type in command to perform Blockchain transaction or check balance.' . PHP_EOL;
echo PHP_EOL . 'Ex. To transfer $3 to clinet B, please type \'B 3\'' . PHP_EOL;
echo 'Ex. To check current balance, please type \'balance\'' . PHP_EOL;

//Read from STDIN and set it as non-blocking. 
//Yeahhhh im too lazy to deal with multi-threading.
$stdin = fopen('php://stdin', 'r');
$result = stream_set_blocking($stdin, false);

//Inifinite loop here~
while(1) {
    $x = "";
	$x = trim((string)fgets($stdin), "\n");
    if(strlen($x) > 0) {
    	//Type in format: Client balance. 
		//Ex. B 10 ==> it means that give $10 from this client to B
		$x = explode(' ', $x);
    	//TODO: perform validation here!
    	$send_to = $x[0];
    	$msg = $x[1];
    	if($send_to == 'blockchain'){
    		//do somethig blockchain here~
    	} elseif($client->client_connections[$send_to] !== NULL){
    		socket_write($client->client_connections[$send_to], $msg, strlen($msg));
    	} else {
    		echo "Invalid input. Or the client does not exist." . PHP_EOL;
    	}
    } else {
        //loop through each socket and check if there is any message from others!
    	foreach($client->client_connections as $c_name => $sock){
    		#echo "Before Socket Read ---  ";
    		$input = socket_read($sock, 1024);
    		#echo "After Socket Rread." . PHP_EOL; 
    		if($input){
	    		echo "Client $c_name sent me a message: " . trim($input, "\n") . PHP_EOL;
	    	}
    	}
    }

}








