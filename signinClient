#!/bin/bash

# Read username and password
read -p "username: " username
read -s -p "password: " password

# substitute into the curl command
curl -i -H "Content-Type: application/json" -X POST -d '{"username": "'$username'", "password": "'$password'"}' -c cookie-jar http://info3103.cs.unb.ca:35669/signin
