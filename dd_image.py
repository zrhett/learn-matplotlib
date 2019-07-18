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
            pixdata[x, y] = (255, 255, 255)

img.show()
print(time() - start)

#%%
img_l = img.convert("L")    # 转为灰度
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
start = time()
ratio = 3 / 4
page_height = int(w / ratio)

def fill_white(page_data, page_height):
    if page_data.shape[0] < page_height:
        e_h = page_height - page_data.shape[0]
        n = np.zeros((e_h, w, 3), np.uint8) + 255
        page_data = np.vstack((page_data, n))
    return page_data

def has_content_at(position, img_gray):
    """检查指定位置前10像素高度是否有内容"""
    area = img_gray[position - 10 : position]
    return np.count_nonzero(area <= 250) > 10



img_org = np.array(img)

if img_org.shape[0] <= page_height:
    page_data = fill_white(img_org, page_height)
    Image.fromarray(page_data).show()
else:
    s_position = 0
    e_position = page_height
    has_content = True
    img_gray = np.array(img.convert("L")) # 转为灰度
    lower_content = False
    upper_content = False
    s_height = 100

    while has_content:
        area = img_gray[e_position - 10 : e_position]
        s_list = np.zeros(s_height, np.int)

        if np.count_nonzero(area <= 250) > 10:
            for i, position in enumerate(range(e_position - s_height, e_position)):
                s_list[i] = np.count_nonzero(img_gray[position] <= 250)


            for i, position in enumerate(range(e_position - 1, e_position - 101, -1)):
                if i == 0:
                    if np.count_nonzero(img_gray[position] <= 250) > 0:
                        lower_content = True



        page_data = img_org[s_position : e_position]

        page_data = fill_white(page_data, page_height)



# for page in range(pages):
#     page_data = img_org[cut_h * page : cut_h * (page + 1)]
#
#     if page_data.shape[0] < cut_h:
#         e_h = cut_h - page_data.shape[0]
#         n = np.zeros((e_h, w, 3), np.uint8) + 255
#         page_data = np.vstack((page_data, n))
#
#     print(page_data.shape)
#     Image.fromarray(page_data).show()

print(time() - start)
#%%
start = time()
ratio = 3 / 4
cut_h = int(w / ratio)

croped = img.crop((0, 0, w, cut_h))

if croped.size[1] < cut_h:
    new_image = Image.new('RGB', (w, cut_h), (255, 255, 255))
    new_image.paste(croped)
    croped = new_image
    print(croped.size[1])

croped.show()
print(time() - start)

#%%
img.save(filename.split('.')[0] + '_out.jpg', quality=100)