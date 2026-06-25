def getcenter(box):
    x1,y1,x2,y2=box
    cx=(x1+x2)/2
    cy=(y1+y2)/2
    return cx,cy

def inside_zone(cx, cy, zone):
    x1, y1, x2, y2 = zone

    return x1 <= cx <= x2 and y1 <= cy <= y2




def iou(boxA,boxB):
    x1=max(boxA[0],boxB[0])
    y1=max(boxA[1],boxB[1])
    x2=min(boxA[2],boxB[2])
    y2=min(boxA[3],boxB[3])    

    inter_w = max(0, x2 - x1)
    inter_h = max(0, y2 - y1)
    inter_area = inter_w * inter_h

    boxAarea=(boxA[2]-boxA[0])*(boxA[3]-boxA[1])
    boxBarea=(boxB[2]-boxB[0])*(boxB[3]-boxB[1])

    union= boxAarea+boxBarea- inter_area

    if union==0:
        return 0
    
    return inter_area/union 
