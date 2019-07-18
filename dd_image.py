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
#%% 按页面高度分割图片
jpg_quality = 100
start = time()
ratio = 3 / 4
w, h = img.size
page_height = int(w / ratio)

def fill_white(page_data, page_height):
    if page_data.shape[0] < page_height:
        e_h = page_height - page_data.shape[0]
        n = np.zeros((e_h, w, 3), np.uint8) + 255
        page_data = np.vstack((page_data, n))
    return page_data

img_org = np.array(img)
f_name = filename.split('.')[0]

if img_org.shape[0] <= page_height:
    page_data = fill_white(img_org, page_height)
    img_out = Image.fromarray(page_data)
    img_out.save(f'{f_name}_out.jpg', quality=jpg_quality)
else:
    s_position = 0
    e_position = page_height
    has_content = True
    img_gray = np.array(img.convert("L")) # 转为灰度
    lower_content = False
    upper_content = False
    s_height = 100
    f_name_index = 0

    while has_content:
        print(f'Position: {s_position} - {e_position}')
        area = img_gray[e_position - 10 : e_position]
        s_list = np.zeros(s_height, np.int)

        # 如果分页最下面10个像素高度有内容，则查找空白进行分割
        if np.count_nonzero(area <= 250) > 10:
            is_blank = False
            blank_list = []

            for position in range(e_position - s_height, e_position):
                black_pix = np.count_nonzero(img_gray[position] <= 250)
                if black_pix == 0 and not is_blank:
                    blank_list.append(position)
                    is_blank = True
                elif black_pix > 0 and is_blank:
                    blank_list.append(position)
                    is_blank = False

            if len(blank_list) % 2 == 1:
                blank_list = blank_list[:-1]

            blank_list = np.array(blank_list).reshape(-1, 2).tolist()
            print(blank_list)
            e_position = (blank_list[-1][1] - blank_list[-1][0]) // 2 + blank_list[-1][0]
            print(f'Change position: {s_position} - {e_position}')

        page_data = img_org[s_position : e_position]
        page_data = fill_white(page_data, page_height)
        img_out = Image.fromarray(page_data)
        f_name_index += 1
        img_out.save(f'{f_name}_out_{f_name_index}.jpg', quality=jpg_quality)

        s_position = e_position
        e_position += page_height
        if s_position > h:
            has_content = False

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