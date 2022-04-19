import cv2
from numpy import shape

from User.Code.MyTools import plt_show, cv_show

img = cv2.imread('./img/all.png')
template = cv2.imread('./img/girl.png')
h,w = template.shape[:2]
res = cv2.matchTemplate(img, template, cv2.TM_SQDIFF)
min_val,max_val,min_loc,max_loc = cv2.minMaxLoc(res)
img_copy = img.copy()
res = cv2.rectangle(img_copy,min_loc,(min_loc[0]+w,min_loc[1]+h),(0,0,255),2)
cv_show(res)

