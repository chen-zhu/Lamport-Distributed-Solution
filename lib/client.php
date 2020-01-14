<?php 

class client {

	public $port_num = 0;
    public $process_id = 0;
    public $name = "";
    public $ip = "127.0.0.1";

	//clients connections
	public $client_connections = array();

	//blockchain connection
	public $blockchain_connection = NULL;

    //todo: make this part private!
    public $lock_queue = array();

	public function __construct($port_num, $process_id, $name, $ip){ 
        $this->port_num = $port_num;
        $this->process_id = $process_id;
        $this->name = $name;
        $this->ip = $ip;
    }

    
    public function request(){

    }

    public function reply(){

    }

    public function release(){

    }




    public function check_balance(){

    }

    public function ping_blockchain(){

    }

    public function broadcast($msg){

    }

    //This funciton is used to bind a socket for this client so that he can receive msg from others.
    public function create_client_rec_msg_sockets(){


    }


}