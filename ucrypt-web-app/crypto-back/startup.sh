#!/bin/bash
   #start SQL Server
   sh -c " 
   
   sleep 20s

   echo 'Starting setup script'

   
#   /opt/mssql-tools/bin/sqlcmd -S localhost -U sa -P \$SA_PASSWORD -Q
#   \"CREATE DATABASE $DB_NAME\"
#
#    echo 'Finished setup script'
#    exit
#    " &
#    exec /opt/mssql/bin/sqlservr
    java -jar app.war
