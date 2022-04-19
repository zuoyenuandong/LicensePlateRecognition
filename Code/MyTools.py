import cv2
from matplotlib import pyplot as plt

#显示图片
def cv_show(img):
    cv2.imshow("",img)
    cv2.waitKey()
    cv2.destroyAllWindows()

#plt显示彩色图片
def plt_show(img):
    b,g,r = cv2.split(img)
    img = cv2.merge([r,g,b])
    plt.imshow(img)
    plt.show()

#plt显示灰度图片
def plt_show_bw(img):
    plt.imshow(img,cmap='gray')
    plt.show()

#对轮廓进行按照位置进行排序
def sort_contours(cnts,method="left-to-right"):
    reverse = False
    i = 0
    if method == "right-to-left " or method == "bottom-to-top":
        reverse = True
    if method == "top-to-bottom" or method == "bottom-to-top":
        i = 1
    boundingBoxes = [cv2.boundingRect(c) for c in cnts]
    (cnts,boundingBoxes) = zip(*sorted(zip(cnts,boundingBoxes),key=lambda b:b[1][i],reverse=reverse))
    return cnts,boundingBoxes

#对图像按比例进行resize,只需传入width
def resize(img,width):
    h,w = img.shape[:2]
    height = (int)(h/w * width)
    img = cv2.resize(img,(width,height))
    return img












