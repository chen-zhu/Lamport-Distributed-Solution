<?php

class helper {
	
	public static function non_block_read($fd, &$data) {
	    $read = array($fd);
	    $write = array();
	    $except = array();
	    $result = stream_select($read, $write, $except, 0);
	    if($result === false) throw new Exception('stream_select failed');
	    if($result === 0) return false;
	    $data = stream_get_line($fd, 1024, "\n");
	    return true;
	}

#	public static function non_blocking(){
#		$stdin = fopen('php://stdin', 'r');
#		$result = stream_set_blocking($stdin, false);
#	}

	public static function list_clients(){
		$xml = simplexml_load_file(__DIR__.'/../config/connections.xml');
		$clients_info = array();

		foreach($xml->clients->client as $client_info){
			$clients_info[(string)$client_info->name] = array(
				'name' => (string)$client_info->name,
				'process_id' => (int)$client_info->process_id,
				'ip' => (string)$client_info->ip, 
				'port' => (int)$client_info->port, 
			);
		} 

		return $clients_info;
	}



}
