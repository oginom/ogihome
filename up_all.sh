tmux new -d -s logger "python3 logger/worker.py"
tmux new -d -s monitor "python3 monitor/app.py"
tmux new -d -s notify "python3 notify/worker.py"
tmux new -d -s co2 "python3 co2/worker.py"
