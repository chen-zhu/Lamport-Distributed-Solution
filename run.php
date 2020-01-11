<?php


$c = "osascript -e 'tell application \"Terminal\" to do script \"cd ~/Documents/CMPSC 271/Lamport-Distributed-Solution/ && ls\" '";

$run = system($c, $val);