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

    public function process_request($to_client, $amount, $time){
        $req = array(
                'time' => $time,
                'from' => $this->name, 
                'to' => $to_client, 
                'process_id' => $this->process_id, 
                'amount' => $amount, 
                'reply_count' => 0 //the # of reply from all other clients~
            );

        //1. insert into client's own queue. 
        $this->lock_queue[] = $req;

        //2. Sort array here!
        usort($this->lock_queue, array('client','order_by_time_id'));

        //3. Broadcast the request to all other clients. 
        $this->broadcasst($req);

        //4. waiting for reply.

        //5. check if it is my turn. 

        //6. release & remove from queue.

    }

    public function broadcasst($req){
        foreach($this->client_connections as $c_name => $sock){
            $json_string = json_encode($req);
            socket_write($sock, $json_string, strlen($json_string));
        }
    }

    static public function order_by_time_id($a, $b){
        if($a['time'] < $b['time']){
            return false; 
        } elseif($a['time'] == $b['time']){
            if($a['process_id'] < $b['process_id']){
                return false;
            } else {
                return true;
            }
        } else {
            return true;
        }
    }    


    public function its_my_turn(){

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

    //This funciton is used to bind a socket for this client so that he can receive msg from others.
    public function create_client_rec_msg_sockets(){


    }


}