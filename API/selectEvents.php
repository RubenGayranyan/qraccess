<?php
    $MySQL_HOST = "localhost";
    $MySQL_USER = "f0658097_tg";
    $MySQL_PASSWORD = "hapaumucdi";
    $MySQL_DB = "f0658097_tg";
    
    $dbHandle = new mysqli($MySQL_HOST, $MySQL_USER, $MySQL_PASSWORD, $MySQL_DB);

    if ($dbHandle->connect_error) {
        die("Connection failed: " . $dbHandle->connect_error);
    }

    $sql_string = "SELECT eID FROM eveentList";
    $result = $dbHandle -> query($sql_string);

    if ($result->num_rows > 0) {
        while($row = $result->fetch_assoc()) {
            echo "id: " . $row["id"]. " - Name: " . $row["firstname"]. " " . $row["lastname"]. "<br>";
        }
    }
    else {
        return "No data";
    }

    $dbHandle -> close();
?>