import os
import csv

from config import SUMMARY_FILE


def save_daily_summary(
    day,
    enter_count,
    hour_counts,
    peak_occupancy,
    dwell_times
):
    rows=[]
    found=False

    if os.path.exists(SUMMARY_FILE):
        with open(SUMMARY_FILE,"r", newline="") as f:
            reader=csv.reader(f)
            rows=list(reader)

    if not rows:
        rows=[["date","total_visits","peak_hour","peak_hour_count","avg_dwell","max_dwell","risk_score"]]

    header=rows[0]
    data_rows=rows[1:]

    if hour_counts:
        peak_hour=max(hour_counts,key=hour_counts.get)
        peak_hour_count=hour_counts[peak_hour]
    else:
        peak_hour=""
        peak_hour_count=0
    

    if dwell_times:
        avg_dwell=sum(dwell_times)/len(dwell_times)
        max_dwell=max(dwell_times)
    else:
        avg_dwell=0
        max_dwell=0

    if enter_count > 0:
        peak_ratio = peak_hour_count / enter_count
    else:
        peak_ratio = 0.0
    risk_score=(
        0.5*peak_ratio+
        0.3*min(peak_occupancy/10,1.0)+
        0.2*min(avg_dwell/300,1.0)
    )
    risk_score=min(risk_score,1.0)

    new_row=[
        day,
        enter_count,
        peak_hour,
        peak_hour_count,
        round(avg_dwell,1),
        round(max_dwell,1),
        round(risk_score,1)
    ]

    for i, row in enumerate(data_rows):
        if row[0] == day:
            data_rows[i] = new_row
            found = True
            break

    if not found:
        data_rows.append(new_row)

    with open(SUMMARY_FILE,"w",newline="") as f:
        writer=csv.writer(f)
        writer.writerow(header)
        writer.writerows(data_rows) 

    print(f"[INSIGHT] {day} → risk={risk_score:.2f}")