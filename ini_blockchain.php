<?php 
include "lib/client.php";
include "lib/helper.php";
include "lib/blockchain.php";

echo PHP_EOL . 
	'*****************************************************' . PHP_EOL
 	. 'Blockchain Main Server' . PHP_EOL . 
 	'*****************************************************' . PHP_EOL;

$clients_list = helper::list_clients();
$blockchain = new blockchain;


//blockchain server will issue connections to all clients one by one!
foreach($clients_list as $c_info){

	sleep(1);

	echo "[Active Socket]Connecting to the client {$c_info['name']} > {$c_info['ip']}:{$c_info['port']}" . PHP_EOL;
	$sock = socket_create(AF_INET, SOCK_STREAM, getprotobyname('tcp'));
	$result = @socket_connect($sock, $c_info['ip'], $c_info['port']);
	//if connection TRUE, put it back in array!
	if($result){
		echo "[Active Socket]Connected to the client {$c_info['name']}" . PHP_EOL;
		@socket_write($sock, 'blockchain', strlen('blockchain'));
		$blockchain->client_connections[$c_info['name']] = $sock;
	} 
}

echo 'Blockchain\'s all clients connections: ' . PHP_EOL;
print_r($blockchain->client_connections);
echo PHP_EOL;