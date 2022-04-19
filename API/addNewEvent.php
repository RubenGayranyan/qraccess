<?php
    $MySQL_HOST = "localhost";
    $MySQL_USER = "f0658097_tg";
    $MySQL_PASSWORD = "hapaumucdi";
    $MySQL_DB = "f0658097_tg";
    
    $dbHandle = new mysqli($MySQL_HOST, $MySQL_USER, $MySQL_PASSWORD, $MySQL_DB);

    if ($dbHandle->connect_error) {
        die("Connection failed: " . $dbHandle->connect_error);
    }

    $sql_string = "CREATE TABLE " . $_POST['eID'] . " (
        `rKey` int(11) NOT NULL,
        `unicalID` varchar(24) COLLATE utf8mb4_unicode_ci NOT NULL,
        `userID` int(11) NOT NULL,
        `userName` varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL,
        `fName` varchar(24) COLLATE utf8mb4_unicode_ci NOT NULL,
        `lName` varchar(24) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
        `rDate` varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL,
        `cDate` varchar(64) COLLATE utf8mb4_unicode_ci DEFAULT NULL
      ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;";
    $result = $dbHandle -> query($sql_string);

    $sql_string = "INSERT INTO eventsList (eID, eCreator, cDate, rDate) VALUES ('" . $_POST['eID'] . "', '" . $_POST['eCreator'] . "', NOW(), '" . $_POST['rDate'] . "')";
    $result = $dbHandle -> query($sql_string);

    $dbHandle -> close();
?>