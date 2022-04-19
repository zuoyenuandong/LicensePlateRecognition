import cv2
import numpy as np
import warnings
from User.Code import MyTools
warnings.filterwarnings("ignore", category=Warning)
from User.Code.MyTools import plt_show, cv_show, sort_contours, plt_show_bw
import re
#初始化卷积核
rectKernel = cv2.getStructuringElement(cv2.MORPH_RECT,(9,3))
rectKernel2 = cv2.getStructuringElement(cv2.MORPH_RECT,(3,9))
myKernel = cv2.getStructuringElement(cv2.MORPH_RECT,(24,24))
myKernel2 = cv2.getStructuringElement(cv2.MORPH_RECT,(3,3))
myKernel3 = cv2.getStructuringElement(cv2.MORPH_RECT,(6,3))


#获取模板
Template = cv2.imread('../Template/ALLNUM.png')
Template_gray = cv2.cvtColor(Template,cv2.COLOR_BGR2GRAY)
Template_bw = cv2.threshold(Template_gray,240,255,cv2.THRESH_BINARY_INV)[1]
#膨胀
expansion = cv2.dilate(Template_bw,myKernel2,iterations = 5)
#获取轮廓
binary, contours, hierarchy = cv2.findContours(expansion.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
# print(np.array(contours).shape)
#对轮廓按照x位置进行排序
contours_sorted = sort_contours(contours,method="left-to-right")[0]
# 打印有多少个轮廓
# print(np.array(contours_sorted).shape)
digits = {}
for (i,c) in enumerate(contours_sorted): #遍历每一个轮廓，计算外界矩形并且resize成合适大小
    (x,y,w,h) = cv2.boundingRect(c)
    roi = Template_bw[y+3:y+h-3,x+3:x+w-3]
    roi = cv2.resize(roi,(114,176))
    #为每一个数字对应一个模板
    digits[i] = roi
    # cv_show(roi)
#为模板定义数组
nums_res =["京","津","沪","渝","冀","豫","云","辽","黑","湘","皖","鲁","苏","浙","赣","鄂","晋","陕","吉","闽","贵","粤","青","川","琼","甘","新","桂","蒙","藏","宁",
          "A","B","C","D","E","F","G","H","I","J","K","L","M","N","O","P","Q","R","S","T","U","V","W","X","Y","Z",
          "1","2","3","4","5","6","7","8","9","0"]



car_search = r'[京津沪渝冀豫云辽黑湘皖鲁新苏浙赣鄂桂甘晋蒙陕吉闽贵粤青藏川宁台琼使领军北南成广沈济空海]{1}[A-Z]{1}[A-Z0-9]{4}[A-Z0-9挂领学警港澳]{1}(?!\d)'



def car_ID_extract(text):
    all_car_id = re.findall(car_search, text)
    car_id = []
    car_id1 = ""
    if all_car_id:
        for i in all_car_id:
            if not i in car_id:
                car_id.append(i)
        for i in car_id:
            car_id1 = car_id1 + ' ' + "".join(tuple(i))   #将列表转字符串
    return car_id1


def img_to_num(filename):
    # 读取图片
    img = cv2.imread(filename)
    # cv_show(img)
    img = MyTools.resize(img, 700)
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 礼貌操作，突出更明亮的区域
    tophat = cv2.morphologyEx(img_gray, cv2.MORPH_TOPHAT, rectKernel)
    thresh = cv2.threshold(tophat, 20, 255, cv2.THRESH_BINARY)[1]
    # cv_show(thresh)
    # Sober显示边缘,归一化
    sobelx = cv2.Sobel(tophat, cv2.CV_32F, 1, 0, ksize=-1)
    sobelx = np.absolute(sobelx)
    (minVal, maxVal) = (np.min(sobelx), np.max(sobelx))
    sobelx = (255 * ((sobelx - minVal) / (maxVal - minVal)))
    sobelx = sobelx.astype("uint8")

    # 闭操作，将数字连在一起
    sobelx = cv2.morphologyEx(sobelx, cv2.MORPH_CLOSE, myKernel)
    # cv_show(sobelx)
    # cv_show(sobelx)
    # THRESH_OTSU会自动寻找合适的阈值，适合双峰，需把阈值参数设为0
    thresh = cv2.threshold(sobelx, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
    # 再次闭操作
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, rectKernel)
    # cv_show(thresh)
    # 计算轮廓
    binary_thresh, contours_thresh, hierarchy_thresh = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
                                                                        cv2.CHAIN_APPROX_SIMPLE)
    # 获取有用轮廓
    locs = []
    car_contour = ''
    for (i, c) in enumerate(contours_thresh):  # 遍历每一个轮廓，计算外界矩形并且resize成合适大小
        (x, y, w, h) = cv2.boundingRect(c)
        ar = w / float(h)
        if ar < 3.5 and ar > 2.5:  # 根据长宽比进行第一次筛选
            if (w > 80 and h > 30):  # 根据大小进行第二次筛选
                locs.append((x, y, w, h))
                car_contour = c
    # print(locs)
    # 定义一个结果
    (gX, gY, gW, gH) = cv2.boundingRect(car_contour)
    num_area = img_gray[gY - 2:gY + gH + 3, gX - 2:gX + gW + 3]
    num_area = cv2.resize(num_area, (0, 0), fx=3, fy=3)
    # cv_show(num_area)
    # 车牌识别
    num_area = cv2.threshold(num_area, 150, 255, cv2.THRESH_BINARY)[1]
    # cv_show(num_area)
    num_area = cv2.morphologyEx(num_area, cv2.MORPH_OPEN, myKernel2)
    num_area = cv2.morphologyEx(num_area, cv2.MORPH_OPEN, myKernel2)
    # cv_show(num_area)
    expansion = cv2.dilate(num_area, rectKernel2, iterations=2)
    # cv_show(expansion)
    binary_num, contours_num, hierarchy_num = cv2.findContours(expansion.copy(), cv2.RETR_EXTERNAL,
                                                               cv2.CHAIN_APPROX_SIMPLE)

    cnts = []
    nums = []
    result_num = []
    # 找到车牌字母
    for (i, c) in enumerate(contours_num):
        (x, y, w, h) = cv2.boundingRect(c)
        ar = w / float(h)
        if ar < 0.8 and ar > 0.05:  # 根据长宽比进行第一次筛选
            if w > 50 or h > 150:
                nums.append((x, y, w, h))
                cnts.append(c)
    # 对车牌位置进行排序
    cnts = sort_contours(cnts, method="left-to-right")[0]
    # num_area_copy = img[gY-2:gY+gH+3,gX-2:gX+gW+3]
    # num_area_copy = cv2.resize(num_area_copy,(0,0),fx=3,fy=3)
    # cv2.drawContours(num_area_copy, cnts, -1, (0,0,255), 3)
    # cv_show(num_area_copy)
    # print(np.array(cnts).shape)
    for c in cnts:
        (x, y, w, h) = cv2.boundingRect(c)
        roi = num_area[y - 5:y + h + 5, x - 5:x + w + 5]
        roi = cv2.resize(roi, (114, 176))
        # cv_show(roi)
        # cv_show(roi)
        # 每个数对模板进行匹配，并保存结果
        scores = []
        for (digit, digitROI) in digits.items():
            result = cv2.matchTemplate(roi, digitROI, cv2.TM_CCORR_NORMED)
            # print(result)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            score = max_val
            scores.append(score)
        # 对每个数匹配后找到最匹配的那一个
        result_num.append(nums_res[int(np.argmax(scores))])
        # print(nums_res[int(np.argmax(scores))])
    result = "".join(result_num)
    return result

result = img_to_num('../img/3.png')
print(result)