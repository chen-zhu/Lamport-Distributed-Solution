<?php
include "lib/client.php";
include "lib/helper.php";
include "lib/blockchain.php";
//Initialize clients and make sure every client is actively listening.

//obtain list of ports and cleint names. 

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
		$client->client_connections[$c_info['name']] = $sock;
	} else {
		echo "[Active Socket]Cannot reach the client {$c_info['name']}" . PHP_EOL;
		#echo PHP_EOL . 'Error_code: ' . socket_last_error() . PHP_EOL;
	}
}

//2. Done with connecting with all clients, then open listen server mode.
echo PHP_EOL . 'Client enters passive connecting mode......' . PHP_EOL;
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
echo PHP_EOL;



//Inifinite loop here~
/*while(1) {
    $x = "";
    if(helper::non_block_read(STDIN, $x)) {
        echo "Input: " . $x . "\n";
    } else {
        echo "I am waiting for your input~." . PHP_EOL;
        sleep(2); 
    }








}

*/