#!/bin/bash

HOST=$1
WG_IP=$2
PORT=$3
USER=$4
OUT="benchmark_results.txt"
SOCK="/tmp/ssh_bench_sock"

echo "--- Direct ---" >>$OUT
python3 test_suite.py --ip $HOST --port $PORT --connection_type Direct | tee -a $OUT

echo "--- WireGuard ---" >>$OUT
python3 test_suite.py --ip $WG_IP --port $PORT --connection_type WireGuard | tee -a $OUT

echo "--- SSH ---" >>$OUT
ssh -M -S $SOCK -f -N -L $PORT:127.0.0.1:$PORT -L 5201:127.0.0.1:5201 $USER@$HOST
sleep 2
python3 test_suite.py --ip 127.0.0.1 --port $PORT --connection_type SSH_Tunnel | tee -a $OUT

ssh -S $SOCK -O exit $USER@$HOST 2>/dev/null
