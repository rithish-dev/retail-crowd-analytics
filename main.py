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
from graphs import save_hourly_graph
from reports import save_daily_summary
from flask import Flask, Response, render_template_string
from dashboard_data import get_latest_summary
from live_data import live_metrics
from recommendations import get_recommendation
from dashboard import start_dashboard
import dashboard
from tracker_bytetrack import update_tracker
import supervision as sv
from analytics_engine import calculate_metrics
from config import ZONES 
from threading import Thread



with open("dashboard.html", "r", encoding="utf-8") as f:
    HTML = f.read()






last_dashboard_update = 0

from config import (
    ZONE,
    DIST_THRESHOLD,
    REMOVE_AFTER,
    MODEL_NAME
)


model = YOLO(MODEL_NAME)

model.overrides["conf"] = 0.4
model.overrides["iou"] = 0.5


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
zone_counts = {
    "Entrance": 0,
    "Shelf A": 0,
    "Checkout": 0
}
flow_counts = {}
zone_dwell = {}

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

def get_zone(cx, cy):
    for name, (x1, y1, x2, y2) in ZONES.items():
        if x1 <= cx <= x2 and y1 <= cy <= y2:
            return name
    return None


def run_detector():
    
    global enter_count, exit_count
    global next_id
    global current_day
    global peak_occupancy
    
    global last_dashboard_update

    print("RUN DETECTOR STARTED")

    while True:
        ret,frame=cap.read()
        if not ret:
            continue 

        now_date=date.today().isoformat()
        if now_date!=current_day:
            dwell_times = [
        p["total_time"]
        for p in people.values()
        if p["total_time"] > 0
    ]
        
    
    
        
            enter_count=0
            exit_count=0
            hour_counts.clear()
            current_day=now_date

        now=time.time()
        update()
        results = model(frame)[0]
        # detections = detect_people(frame, model)

        detections = sv.Detections.from_ultralytics(results)

        tracked_objects = update_tracker(detections)
        # Remove invalid tracks
        valid = tracked_objects.tracker_id != -1

        tracked_objects = tracked_objects[valid]

        print(tracked_objects)
       
        
    
        for i, (x1, y1, x2, y2) in enumerate(tracked_objects.xyxy):
            pid = int(tracked_objects.tracker_id[i])
            cx,cy=getcenter((x1,y1,x2,y2))
            zone = get_zone(cx, cy)

            



            if int(now * 5) != int((now - 0.03) * 5):
                add_point(cx, cy)

            if pid not in people:
                people[pid] = {
        "center": (cx, cy),
        "last": now,
        "inside": False,
        "enter_time": None,
        "total_time": 0,
        "box": (x1, y1, x2, y2),
        "outside_time": None,
        "path": [],
                }

            people[pid]["box"] = (
            int(x1),
            int(y1),
            int(x2),
            int(y2)
            )


            people[pid]["center"] = (cx, cy)


            current_zone = get_zone(cx, cy)

            if current_zone:
                if people[pid].get("zone_enter_time") is None:
                    people[pid]["zone_enter_time"] = now

                previous_zone = people[pid].get("zone")

                if previous_zone != current_zone:

                    if previous_zone:
                        duration = now - people[pid]["zone_enter_time"]
                        zone_dwell[previous_zone] = (
                            zone_dwell.get(previous_zone, 0) + duration
                        )

                    people[pid]["zone"] = current_zone
                    people[pid]["zone_enter_time"] = now





            if zone:
                previous = people[pid].get("zone")

                if previous != zone:

                    if previous is not None:
                        route = f"{previous} → {zone}"
                        flow_counts[route] = flow_counts.get(route, 0) + 1

                    people[pid]["zone"] = zone

                    if "visited" not in people[pid]:
                        people[pid]["visited"] = set()

                    if zone not in people[pid]["visited"]:
                        zone_counts[zone] += 1
                        people[pid]["visited"].add(zone)

            people[pid]["path"].append((int(cx), int(cy)))
            for i in range(1, len(people[pid]["path"])):
                cv2.line(
                    frame,
                    people[pid]["path"][i - 1],
                    people[pid]["path"][i],
                    (0, 255, 255),
                    2
                )
            if len(people[pid]["path"]) > 50:
                people[pid]["path"].pop(0)
            people[pid]["last"] = now
            
            in_zone=inside_zone(cx,cy,ZONE)

            if in_zone and not people[pid]["inside"]:
                people[pid]["inside"]=True
                people[pid]["enter_time"] = now
                people[pid]["outside_time"] = None 
                hour=datetime.now().hour
                hour_counts[hour]=hour_counts.get(hour,0)+1
                print(hour_counts)
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
            bx1 = int(bx1)
            by1 = int(by1)
            bx2 = int(bx2)
            by2 = int(by2)
            cv2.rectangle(frame,(bx1,by1),(bx2,by2),color,2)




        current_ids = set(tracked_objects.tracker_id.astype(int))

        to_delete = []

        for pid, p in people.items():
            if pid not in current_ids:
                if now - p["last"] > max(REMOVE_AFTER, 5):
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

        cv2.putText(frame, f"Current Occupancy: {sum(1 for p in people.values() if p['inside'])}", (390,90),
                 cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,0), 2)
    
        current_occupancy=sum(1 for p in people.values() if p["inside"])
        peak_occupancy=max(peak_occupancy,current_occupancy)

        live_metrics["visitors"] = enter_count
        live_metrics["occupancy"] = current_occupancy
        
        
        zone_live = {}

        for name, (zx1, zy1, zx2, zy2) in ZONES.items():
            count = 0

            for p in people.values():
                if not p["inside"]:
                    continue

                cx, cy = p["center"]

                if zx1 <= cx <= zx2 and zy1 <= cy <= zy2:
                    count += 1

            zone_live[name] = count

        live_metrics["zones"] = zone_live

        live_metrics["zone_dwell"] = {
            k: round(v, 1)
            for k, v in zone_dwell.items()
        }
        



        live_metrics["peak_hour"] = (
            max(hour_counts, key=hour_counts.get)
            if hour_counts else "Loading..."
        )

        dwell_times = [
            p["total_time"] + (
                now - p["enter_time"]
                if p["inside"] and p["enter_time"]
                else 0
            )
            for p in people.values()
        ]

        if time.time() - last_dashboard_update > 10:

            save_daily_summary(
        today,
        enter_count,
        hour_counts,
        peak_occupancy,
        dwell_times
            )
            save_hourly_graph()

            last_dashboard_update = time.time()



        people_metrics = {}

        for pid, p in people.items():

            if p["inside"] and p["enter_time"]:
                live_time = p["total_time"] + (now - p["enter_time"])
            else:
                live_time = p["total_time"]

            people_metrics[pid] = p.copy()
            people_metrics[pid]["total_time"] = live_time


        metrics = calculate_metrics(
        people_metrics,
        enter_count,
        current_occupancy
        )



        for p in people.values():
            if p["inside"] and p["enter_time"]:
                p["live_time"] = p["total_time"] + (now - p["enter_time"])
            else:
                p["live_time"] = p["total_time"]

        top_visitors = sorted(
        people.items(),
        key=lambda x: x[1]["live_time"],
        reverse=True
        )[:5]
        live_metrics["flows"] = flow_counts
        live_metrics["top_visitors"] = [
            {
                "id": pid,
                "time": round(data["live_time"], 1)
            }
            for pid, data in top_visitors
        ]












        live_metrics["avg_dwell"] = metrics["avg_dwell"]
        live_metrics["risk_score"] = metrics["risk"]
        
        live_metrics["recommendation"] = get_recommendation(live_metrics)
     

        heat = get_heatmap()
       
        cv2.imwrite(
        "static/heatmap.png",
        heat
        )


        frame = cv2.addWeighted(
        frame,
        0.85,
        heat,
        0.15,
        0
    )
    
        dashboard.processed_frame = frame.copy()

        dwell_times = [
        p["total_time"] + (now - p["enter_time"] if p["inside"] and p["enter_time"] else 0)
        for p in people.values()
        ]

    
        cv2.imshow("Pluto", frame)

        if cv2.waitKey(1) & 0xFF == ord("q") :
            break


        if hour_counts:
            peak_hour=max(hour_counts,key=hour_counts.get,default=None)
            print("Peak Hour:",peak_hour,"with",hour_counts[peak_hour],"visits")
        dwell_times = [
            p["total_time"]
            for p in people.values()
            if p["total_time"] > 0
        ]


    
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":

    detector = Thread(
        target=run_detector,
        daemon=True
    )
    detector.start()

    start_dashboard(HTML)
