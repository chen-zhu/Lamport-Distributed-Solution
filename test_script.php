<?php
/*
function non_block_read($fd, &$data) {
    $read = array($fd);
    $write = array();
    $except = array();
    $result = stream_select($read, $write, $except, 0);
    if($result === false) throw new Exception('stream_select failed');
    if($result === 0) return false;
    $data = stream_get_line($fd, 1024, "\n");
    return true;
}

while(1) {
    $x = "";
    if(non_block_read(STDIN, $x)) {
        echo "Input: " . $x . "\n";
        // handle your input here
    } else {
        echo ".";
        sleep(2); 
        // perform your processing here
    }
}
*/




/*
$sock = socket_create(AF_INET, SOCK_STREAM, getprotobyname('tcp'));
$result = @socket_connect($sock, '127.0.0.1', 3001);

echo $result ? '1' : '0';
*/



$stdin = fopen('php://stdin', 'r');
$result = stream_set_blocking($stdin, false);

do {
  $line = fgets($stdin);

  // No input right now
  if (empty($line)) {
    echo 'nothing input here';
  }
  else {
    echo 'Input:' . $line;
  }

  sleep(2);
} while (1);
