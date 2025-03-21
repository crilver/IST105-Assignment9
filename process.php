<?php
    $origin = escapeshellarg($_GET['origin']);
    $dest = escapeshellarg($_GET['dest']);
    $command = escapeshellcmd("python3 09_openroute_parse_json.py $origin $dest");
    $output = shell_exec($command);

    $host = gethostname();
    $host = gethostbyname($host);
    
    echo "<h1>Assignment 9:</h1>";
    echo "<h1>HOST IP: $host</h1>";
    echo "<h2>Python Script Result</h2>";
    echo "<hr>"
    echo $output;
?>