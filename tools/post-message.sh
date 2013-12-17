#! /bin/sh

COOKIES='cookies.txt'
# USER_AGENT='Firefox/25'
USER_AGENT='Mozilla/5.0'

curl \
-F 'fb_dtsg=AQBRa6P3' \
-F 'body=cel' \
-F 'tids=...' \
-X POST 'https://m.facebook.com//messages/send/?icm=1&refid=12' --user-agent $USER_AGENT --cookie $COOKIES --cookie-jar $COOKIES --location
