import time

filetime = time.localtime()
filetime = time.strftime('%Y%m%d%H%M%S')
filename = '/Upload/'+filetime+'.bmp'
print(filename)

file = open('./Upload/a.txt','w',encoding='utf-8')
file.write("helloworld")