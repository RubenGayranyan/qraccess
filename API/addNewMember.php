<?php
    $MySQL_HOST = "localhost";
    $MySQL_USER = "f0658097_tg";
    $MySQL_PASSWORD = "hapaumucdi";
    $MySQL_DB = "f0658097_tg";
    
    $dbHandle = new mysqli($MySQL_HOST, $MySQL_USER, $MySQL_PASSWORD, $MySQL_DB);

    if ($dbHandle->connect_error) {
        die("Connection failed: " . $dbHandle->connect_error);
    }

    $sql_string = "INSERT INTO " . $_POST['eventID'] . " (unicalID, userID, userName, fName, lName, rDate) VALUES ('" . $_POST['unicalID'] . "', '" . $_POST['userID'] . "', '" . $_POST['userName'] . "', '" . $_POST['fName'] . "', '" . $_POST['lName'] . "', NOW())";
    $result = $dbHandle -> query($sql_string);

    $dbHandle -> close();
?>