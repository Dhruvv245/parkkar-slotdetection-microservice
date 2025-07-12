import cv2 as cv
import pickle #its used to save the data and move it to some file 

try:
    with open("workshopposn",'rb') as f:
        poslist=pickle.load(f)
except:
    poslist=[]

width,height=300,250
def rescaleframe(frame,scale=0.5):
    width=int(frame.shape[1]*scale)
    height=int(frame.shape[0]*scale)
    dimensions=(width,height)
    return cv.resize(frame,dimensions,interpolation=cv.INTER_AREA)
def mouseclick(events,x,y,flags,params):
    if events==cv.EVENT_LBUTTONDOWN:
        poslist.append((x,y))
    if events==cv.EVENT_RBUTTONDOWN:
        for i,pos in enumerate(poslist):
            x1,y1=pos
            if x1<x<x1+width and y1<y<y1+height:
                poslist.pop(i)
    with open("workshopposn",'wb') as f:
        pickle.dump(poslist,f)

while True:
    image=cv.imread("171257379740342.jpg")#new frames aren't generated
    image_r=rescaleframe(image)
    #we are not saving them
    for pos in poslist:
        cv.rectangle(image_r,pos,(pos[0]+width,pos[1]+height),(255,0,255),2)
    cv.imshow("img",image_r)
    cv.setMouseCallback("img",mouseclick)
    if cv.waitKey(1) &0xFF==ord("q"):
        break
