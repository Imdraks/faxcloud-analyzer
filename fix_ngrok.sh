#!/bin/bash
sed -i 's|ngrok http 80|ngrok http 127.0.0.1:80|' /etc/systemd/system/ngrok.service
systemctl daemon-reload
systemctl restart ngrok
sleep 2
systemctl status ngrok --no-pager -l
