<?php

//1. load XML file info here!
$xml = simplexml_load_file('config/connections.xml');

//2. Open N clients terminals with running script 
foreach($xml->clients->client as $client_info){
	$terminal_command = "osascript -e 'tell application \"Terminal\" to do script \"cd ~/Documents/CMPSC_271/Lamport-Distributed-Solution/ && php ini_client.php " . $client_info->port . " " . $client_info->process_id . " " . $client_info->name . " " . $client_info->ip . " " . "\" ' ";

	$run = system($terminal_command, $val);
	sleep(3);
}

//3. Open 1 main blockchain terminal with running script
$terminal_command = "osascript -e 'tell application \"Terminal\" to do script \"cd ~/Documents/CMPSC_271/Lamport-Distributed-Solution/ && php ini_blockchain.php \" ' ";

$run = system($terminal_command, $val);
