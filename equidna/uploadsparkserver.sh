#!/bin/bash 
rsync -vaz -e 'ssh -i /Users/alasarr/Downloads/spark.pem'  --exclude='*.pyc' --exclude='.DS_Store' --exclude='*.mbtiles' . root@ec2-54-221-143-202.compute-1.amazonaws.com:/root/equidna/ 