import time

import serial

from User.Code.bishe import img_to_num

i = 1
recieveFlag = b'$'
sendFlag = b'%'
sendEndFlag = b'&'
# 连接串口
serial = serial.Serial('COM5', 115200,timeout=0.5)
if serial.isOpen():
    print('串口已打开')
    while True:
        data = serial.read(20)  # 串口读20位数据
        while (data == b'' or len(data)<=0) :
            data = serial.read(20)
        if ((data != b'') or (len(data)>0)):
            if data == b'start':
                print("开始接收照片了")
                serial.write(b'$')
                filetime = time.localtime()
                filetime = time.strftime('%Y%m%d%H%M%S')
                # filename = './Upload/' + filetime + '.bmp'
                filename = '../Upload/' + filetime + '.bmp'
                file = open(filename,'ab+')
                time.sleep(0.2)
                while True:
                    data = serial.read(1024)
                    while (data == b'' or  len(data) <= 0):
                        data = serial.read(1024)
                    if (data != b'' or len(data) > 0):
                        if (len(data) < 100):
                            data_str = data.decode("utf-8")[-3:]
                            if data_str == 'end':
                                data = data[:-3]
                                file.write(data)
                                serial.write(b'$')
                                file.close()
                                print("传输完成")
                                time.sleep(2)
                                break
                            else:
                                file.write(data)
                                serial.write(b'$')
                        else:
                            file.write(data)
                            serial.write(b'$')
                    # print(i)
                    time.sleep(0.05)
        result = img_to_num(filename)
        if result=="":
            serial.write("%没有车牌&".encode("gbk"))
        else:
            result = "%"+result+"&"
            serial.write(result.encode("gbk"))
else:
    print('串口未打开')

# 关闭串口
serial.close()

if serial.isOpen():
    print('串口未关闭')
else:
    print('串口已关闭')
