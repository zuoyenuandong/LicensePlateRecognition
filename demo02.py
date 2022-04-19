import cv2
import numpy as np


from User.Code import MyTools




from User.Code.MyTools import plt_show, cv_show, sort_contours


#读取模板
Template = cv2.imread('./img/Template.png')
Template_gray = cv2.cvtColor(Template,cv2.COLOR_BGR2GRAY)
Template_bw = cv2.threshold(Template_gray,10,255,cv2.THRESH_BINARY_INV)[1]

#获取轮廓
binary, contours, hierarchy = cv2.findContours(Template_bw.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
#对轮廓按照x位置进行排序
contours_sorted = sort_contours(contours,method="left-to-right")[0]

digits = {}
for (i,c) in enumerate(contours_sorted): #遍历每一个轮廓，计算外界矩形并且resize成合适大小
    (x,y,w,h) = cv2.boundingRect(c)
    roi = Template_bw[y:y+h,x:x+w]
    roi = cv2.resize(roi,(57,88))
    #为每一个数字对应一个模板
    digits[i] = roi
#初始化卷积核
rectKernel = cv2.getStructuringElement(cv2.MORPH_RECT,(9,3))
sqKernel = cv2.getStructuringElement(cv2.MORPH_RECT,(5,5))

#读取图片
img = cv2.imread('./img/card3.png')
img = MyTools.resize(img,300)
img_gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

#礼貌操作，突出更明亮的区域
tophat = cv2.morphologyEx(img_gray,cv2.MORPH_TOPHAT,rectKernel)


#Sober显示边缘,归一化
sobelx = cv2.Sobel(tophat,cv2.CV_32F,1,0,ksize = -1)
sobelx = np.absolute(sobelx)
(minVal,maxVal) = (np.min(sobelx),np.max(sobelx))
sobelx = (255*((sobelx - minVal)/(maxVal - minVal)))
sobelx = sobelx.astype("uint8")

#闭操作，将数字连在一起
sobelx = cv2.morphologyEx(sobelx,cv2.MORPH_CLOSE,rectKernel)

#THRESH_OTSU会自动寻找合适的阈值，适合双峰，需把阈值参数设为0
thresh = cv2.threshold(sobelx,0,255,cv2.THRESH_BINARY|cv2.THRESH_OTSU)[1]


#再次闭操作
thresh = cv2.morphologyEx(thresh,cv2.MORPH_CLOSE,rectKernel)

#计算轮廓
binary_thresh, contours_thresh, hierarchy_thresh = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
# img_copy = img.copy()
# cv2.drawContours(img_copy,contours_thresh,-1,(0,0,255),3)

#获取有用轮廓
locs = []
for (i,c) in enumerate(contours_thresh): #遍历每一个轮廓，计算外界矩形并且resize成合适大小
    (x,y,w,h) = cv2.boundingRect(c)
    ar = w/float(h)
    if ar>2.5 and ar<4.0: #根据长宽比进行第一次筛选
        if (w>40 and w < 55) and (h>10 and h<20): #根据大小进行第二次筛选
            locs.append((x,y,w,h))
#将符合的轮廓从做到右进行排序
locs = sorted(locs,key=lambda  x:x[0])

#定义一个结果
output = []
#对每一个轮廓进行处理
for (i,(gX,gY,gW,gH)) in enumerate(locs):
    groupOutput = []
    #根据坐标提取每一个组
    group = img_gray[gY-5:gY+gH+5,gX-5:gX+gW+5]
    group = cv2.threshold(group, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
    #每一个小矩形轮廓
    binary_group, contours_group, hierarchy_group = cv2.findContours(group.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    contours_group = sort_contours(contours_group,method="left-to-right")[0]

    #计算每一组中的每一个数值
    for c in contours_group:
        (x,y,w,h) = cv2.boundingRect(c)
        roi = group[y:y + h, x:x + w]
        roi = cv2.resize(roi, (57, 88))
        #每个数对模板进行匹配，并保存结果
        scores = []
        for (digit,digitROI) in digits.items():
            result = cv2.matchTemplate(roi,digitROI,cv2.TM_CCOEFF)
            (min_val, max_val, min_loc, max_loc) = cv2.minMaxLoc(result)
            score = max_val
            scores.append(score)
        #对每个数匹配后找到最匹配的那一个
        groupOutput.append(str(np.argmax(scores)))
    output.extend(groupOutput)
result = "".join(output)
print(result)