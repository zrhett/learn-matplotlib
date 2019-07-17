#%%
from PIL import Image
import numpy as np
from time import time

filename = '1.jpg'

img = Image.open(filename)

#%%
pixdata = img.load()

# 查找灰色横线y坐标
line_y_list = []

for y in range(img.size[1]):
    if pixdata[0, y] <= (250, 250, 250) and pixdata[0, y] >= (210, 210, 210):
        line_y_list.append(y)

# 裁剪掉上下灰色横线之外的部分
img = img.crop((0, line_y_list[0], img.size[0], line_y_list[1]))

#%%
# 去掉图片中的水印
start = time()
pixdata = img.load()

for y in range(img.size[1]):
    for x in range(img.size[0]):
        if len(set(pixdata[x, y])) == 1 and pixdata[x, y] <= (250, 250, 250) and pixdata[x, y] >= (220, 220, 220):
            pixdata[x, y] = (254, 254, 254)

img.show()
print(time() - start)

#%%
img_l = img.convert("L")
pixdata_l = img_l.load()
w, h = img_l.size
h_list = [0] * h

for y in range(h):
    for x in range(w):
        if pixdata_l[x, y] < 250:
            h_list[y] += 1

hhist = np.zeros(img_l.size, np.uint8)
for y in range(h):
    for x in range(h_list[y]):
        hhist[x, y] = 255

Image.fromarray(hhist.T).show()

img_l.show()
#%%
img.save(filename.split('.')[0] + '_out.jpg', quality=100)