import cv2
import time
from ultralytics import YOLO
import csv
from datetime import datetime
from datetime import date
import json
import os 
from detector import detect_people
from storage import save_state, log_event
from heatmap import initialize, add_point, get_heatmap, update
from visualization import draw_ui
from dashboard import hourly_chart
from graphs import save_hourly_graph
from reports import save_daily_summary






from config import (
    ZONE,
    DIST_THRESHOLD,
    REMOVE_AFTER,
    MODEL_NAME
)

from ultralytics import YOLO


model = YOLO(MODEL_NAME)


import cv2


cap = cv2.VideoCapture(0)
ret, frame = cap.read()

if ret:
    h, w = frame.shape[:2]
    initialize(w, h)

cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

today=date.today().isoformat()
current_day = today
hour_counts = {}
peak_occupancy = 0

if today!=current_day:
      
    enter_count=0
    exit_count=0
    hour_counts.clear() 
    current_day=today
   


people={}

next_id=0

state_file="state.json"
if os.path.exists(state_file):
    with open(state_file,"r") as f:
        state=json.load(f)
    saved_data=state.get("date") 
    if saved_data==today:
        enter_count=state.get("entered",0)
        exit_count=state.get("exited",0)
    else:
        enter_count=0
        exit_count=0
else:
    enter_count=0
    exit_count=0




log_file=f"people_log_{date.today().isoformat()}.csv" 
try:
    open (log_file,"x").write("timestamp,entered,exited,inside\n")
except:
    pass


summary_file="daily_summary.csv"
if not os.path.exists(summary_file):
    with open(summary_file ,"w",newline="") as f:
        writer=csv.writer(f)
        writer.writerow(["date",
                        "total_visits",
                        "peak_hour",
                        "peak_hour_count",
                        "avg_dwell",
                        "max_dwell",
                        "risk_score"
                        ])

from reports import save_daily_summary
 
    

    


    
from utils import (
    getcenter,
    inside_zone,
    iou
)





while True:
    ret,frame=cap.read()
    if not ret:
        break 

    now_date=date.today().isoformat()
    if now_date!=current_day:
        dwell_times = [
    p["total_time"]
    for p in people.values()
    if p["total_time"] > 0
]
        save_daily_summary(
    today,
    enter_count,
    hour_counts,
    peak_occupancy,
    dwell_times
)

        enter_count=0
        exit_count=0
        hour_counts.clear()
        current_day=now_date

    now=time.time()
    update()
    detections = detect_people(frame, model)
    
    matched=set()
    
    for (x1,y1,x2,y2) in detections:
        cx,cy=getcenter((x1,y1,x2,y2))
        if int(now * 5) != int((now - 0.03) * 5):
            add_point(cx, cy)

        best=None
        best_score=0
        for pid,p in people.items():
            if "box" not in p:
                continue

            iou_score=iou((x1,y1,x2,y2),p["box"])
            px,py=p["center"]
            dist = abs(px-cx) + abs(py-cy)
            dist_score = max(0, 1 - dist/300)  
            score = 0.6*iou_score + 0.4*dist_score


            if score>best_score:
                best_score=score
                best=pid 
            


        if best is None or best_score<0.15:
            pid=next_id
            next_id+=1
            people[pid] = {
    "center": (cx, cy),
    "last": now,
    "inside": False,
    "enter_time": None,
    "total_time": 0,
    "box": (x1, y1, x2, y2),
    "outside_time": None,
    "path": []
}
            
        else:
            pid=best





        people[pid]["box"] = (x1,y1,x2,y2)

        
        matched.add(pid)
        people[pid]["center"] = (cx,cy)
        people[pid]["path"].append((int(cx), int(cy)))

        if len(people[pid]["path"]) > 100:
            people[pid]["path"].pop(0)
        people[pid]["last"] = now

       
        in_zone=inside_zone(cx,cy,ZONE)

        if in_zone and not people[pid]["inside"]:
            people[pid]["inside"]=True
            people[pid]["enter_time"] = now
            people[pid]["outside_time"] = None 
            hour=datetime.now().hour
            hour_counts[hour]=hour_counts.get(hour,0)+1
            enter_count+=1
            log_event(log_file, enter_count, exit_count)
            save_state(state_file, enter_count, exit_count)

        
        if not in_zone and people[pid]["inside"]==True:
            if people[pid]["outside_time"]==None:
                people[pid]["outside_time"] = now
            elif now - people[pid]["outside_time"] > 2:
                people[pid]["inside"]=False 
                people[pid]["total_time"]+=now-people[pid]["enter_time"]
                people[pid]["enter_time"]=None
                exit_count+=1
                people[pid]["outside_time"] = None
                log_event(log_file, enter_count, exit_count)
                save_state(state_file, enter_count, exit_count)


        color=(0,255,0) if in_zone else (0,0,255)
        bx1,by1,bx2,by2 = people[pid]["box"]
        cv2.rectangle(frame,(bx1,by1),(bx2,by2),color,2)




    to_delete=[]
    for pid,p in people.items():
        if pid not in matched:
            if now-p["last"]>REMOVE_AFTER:
                if p["inside"]:
                    p["inside"]=False
                    exit_count+=1
                    log_event(log_file, enter_count, exit_count)
                    save_state(state_file, enter_count, exit_count)
                to_delete.append(pid)
                
        
    for pid in to_delete:
        del people[pid]


    x1,y1,x2,y2=ZONE
    cv2.rectangle(frame,(x1,y1),(x2,y2),(255,255,0),2)

    y=30
    for pid,p in people.items():
        t=p["total_time"]
        if p["inside"] and p["enter_time"]:
            t+=now-p["enter_time"]
            
        cv2.putText(frame,f" ID{pid}: {t:.1f}s",
                (10,y),cv2.FONT_HERSHEY_SIMPLEX,0.6,(0,255,255),2)
            
        y+=25

    cv2.putText(frame, f"Visits Today: {enter_count}", (400,30),
             cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)

    cv2.putText(frame, f"Exited: {exit_count}", (400,60),
               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,0,255), 2)

    cv2.putText(frame, f"Current Occupancy: {sum(1 for p in people.values() if p["inside"])}", (390,90),
             cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,0), 2)
    
    current_occupancy=sum(1 for p in people.values() if p["inside"])
    peak_occupancy=max(peak_occupancy,current_occupancy)

    heat = get_heatmap()

    frame = cv2.addWeighted(
    frame,
    0.85,
    heat,
    0.15,
    0
)
    
     
    cv2.imshow("Pluto",frame)
    if cv2.waitKey(1) & 0xFF==ord("q"):
        break

if hour_counts:
        peak_hour=max(hour_counts,key=hour_counts.get,default=None)
        print("Peak Hour:",peak_hour,"with",hour_counts[peak_hour],"visits")
dwell_times = [
    p["total_time"]
    for p in people.values()
    if p["total_time"] > 0
]


save_daily_summary(
    today,
    enter_count,
    hour_counts,
    peak_occupancy,
    dwell_times
)
hourly_chart(hour_counts)
print(hour_counts)
save_hourly_graph(hour_counts)
cap.release()
cv2.destroyAllWindows()

