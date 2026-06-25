import csv
import json
from datetime import date, datetime

def save_state(state_file, enter_count, exit_count):
    state={
        "entered":enter_count,
        "exited":exit_count,
        "date":date.today().isoformat() 
    } 
    with open(state_file,"w") as f:
        json.dump(state,f)

def log_event(log_file, enter_count, exit_count):
        inside=enter_count-exit_count
        with open(log_file,"a",newline="") as f:
            writer=csv.writer(f)
            writer.writerow([
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                enter_count,
                exit_count,
                inside
                  ])