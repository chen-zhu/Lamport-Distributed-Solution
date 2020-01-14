<?php

class blockchain {

	public $client_connections = array();

	public $transactions = array();

	public function __construct($client_list = array()){ 
        if($client_list){
        	foreach($client_list as $c_info){
        		$this->transactions[] = array(
        			'from' => '_ini_',
        			'to' => $c_info['name'],
        			'amount' => 10,
        		);
        	}
        }
    }

   	public function balance($client_name){
   		//loop through each single node aand calculate balance~
   		//If client name is under 'from', deduct.
   		//Else, if client is under 'to', add!
   		if($client_name){
   			$balance = 0;
   			//client_name
   			$calc = array_reduce($this->transactions, function($balance, $trx) use ($client_name){
   				if($trx['from'] == $client_name){
   					$balance -= $trx['amount'];
   				} elseif($trx['to'] == $client_name) {
					$balance += $trx['amount'];
   				}
   				return $balance;
   			});
	   		return $calc;
   		}
   	}

   	public function insert_trx($from_client_name, $to_client_name, $amount){
   		$this->transactions[] = array(
   			'from' => $from_client_name, 
   			'to' => $to_client_name, 
   			'amount' => $amount
   		);
   	}




} 