<?php 

class client {

	$port_num = 0;

	//clients connections
	$snd_msg_sockets = array();
	$rcv_msg_socket = NULL;


	//blockchain connection
	$bc_socket = NULL;

	public function __construct($port_num){ 
        //TODO:create client object here!
    }

    public function check_balance(){

    }

    public function ping_blockchain(){

    }

    public function broadcast($msg){

    }



}