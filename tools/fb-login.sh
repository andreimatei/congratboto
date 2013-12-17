#!/bin/bash
 
# If it redirects to http://www.facebook.com/login.php at the end, wait a few minutes and try again
 
EMAIL='x@y.com'
PASS='pwd'
 
COOKIES='cookies.txt'
# USER_AGENT='Firefox/25'
USER_AGENT='Mozilla/5.0'
 
curl -X GET 'https://m.facebook.com' --verbose --user-agent $USER_AGENT --cookie $COOKIES --cookie-jar $COOKIES --location > /dev/null # redirects to https://login.facebook.com/login.php
curl -X POST 'https://m.facebook.com/login.php' --verbose --user-agent $USER_AGENT --data-urlencode "email=${EMAIL}" --data-urlencode "pass=${PASS}" --cookie $COOKIES --cookie-jar $COOKIES > /dev/null
curl -X GET 'https://m.facebook.com/messages/read/?tid=mid.1384722860563%3A3932eedf826bf6c982' --verbose --user-agent $USER_AGENT --cookie $COOKIES --cookie-jar $COOKIES > out.html
