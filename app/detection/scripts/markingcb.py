import cv2 as cv
import pickle #its used to save the data and move it to some file 

try:
    with open("cbposn",'rb') as f:
        poslist=pickle.load(f)
except:
    poslist=[]

width,height=250,500
def mouseclick(events,x,y,flags,params):
    if events==cv.EVENT_LBUTTONDOWN:
        poslist.append((x,y))
    if events==cv.EVENT_RBUTTONDOWN:
        for i,pos in enumerate(poslist):
            x1,y1=pos
            if x1<x<x1+width and y1<y<y1+height:
                poslist.pop(i)
    with open("cbposn",'wb') as f:
        pickle.dump(poslist,f)

while True:
    image=cv.imread("final.jpg")#new frames aren't generated
    #we are not saving them
    for pos in poslist:
        cv.rectangle(image,pos,(pos[0]+width,pos[1]+height),(255,0,255),2)
    cv.imshow("img",image)
    cv.setMouseCallback("img",mouseclick)
    if cv.waitKey(1) &0xFF==ord("q"):
        break
