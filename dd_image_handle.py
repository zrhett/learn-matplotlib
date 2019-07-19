from PIL import Image
import numpy as np
from time import time


class DedaoImage:
    def remove_head_and_tail(self, image):
        """裁剪掉上下灰色横线之外的部分"""
        pixdata = image.load()
        # 查找灰色横线y坐标
        line_y_list = []

        for y in range(image.size[1]):
            if pixdata[0, y] <= (250, 250, 250) and pixdata[0, y] >= (210, 210, 210):
                line_y_list.append(y)

        image = image.crop((0, line_y_list[0] + 2, image.size[0], line_y_list[1] - 2))
        return image

    def remove_watermark(self, image):
        """去掉图片中的水印"""
        start = time()
        pixdata = image.load()

        for y in range(image.size[1]):
            for x in range(image.size[0]):
                if len(set(pixdata[x, y])) == 1 and pixdata[x, y] <= (250, 250, 250) and pixdata[x, y] >= (220, 220, 220):
                    pixdata[x, y] = (255, 255, 255)

        print(time() - start)
        return image

    def cut_long_picture(self, image, filename, to_pdf=False, jpg_quality=100):
        start = time()
        ratio = 3 / 4
        w, h = image.size
        page_height = int(w / ratio)

        def fill_white(page_data, page_height):
            if page_data.shape[0] < page_height:
                e_h = page_height - page_data.shape[0]
                n = np.zeros((e_h, w, 3), np.uint8) + 255
                page_data = np.vstack((page_data, n))
            return page_data

        img_org = np.array(image)
        f_name = filename.split('.')[0]
        img_out_list = []

        if img_org.shape[0] <= page_height:
            page_data = fill_white(img_org, page_height)
            img_out = Image.fromarray(page_data)
            img_out_list.append(img_out)
        else:
            s_position = 0
            e_position = page_height
            has_content = True
            img_gray = np.array(image.convert("L"))  # 转为灰度
            lower_content = False
            upper_content = False
            s_height = 100

            while has_content:
                print(f'Position: {s_position} - {e_position}')
                area = img_gray[e_position - 10: e_position]

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

                page_data = img_org[s_position: e_position]
                page_data = fill_white(page_data, page_height)
                img_out = Image.fromarray(page_data)
                img_out_list.append(img_out)

                s_position = e_position
                e_position += page_height
                if s_position > h:
                    has_content = False

        if to_pdf:
            im1 = img_out_list.pop(0)
            im1.save(f'{f_name}_out.pdf', "PDF", resolution=100.0, save_all=True, append_images=img_out_list)
        else:
            for i, im in enumerate(img_out_list):
                im.save(f'{f_name}_out_{i + 1}.jpg', quality=jpg_quality)

        print(time() - start)

    def concat_pictures(self):
        filenames = self.get_files()
        imgs = []

        for filename in filenames:
            img = Image.open(filename)
            img = self.remove_head_and_tail(img)
            img = self.remove_watermark(img)
            # img.save(f'{filename.split(".")[0]}_out.jpg', quality=100)
            imgs.append(img)

        for i in range(len(imgs) - 1):
            crop_pos = self.compare_two_text(imgs[i], imgs[i + 1])
            if crop_pos > 0:
                imgs[i + 1] = imgs[i + 1].crop((0, crop_pos, imgs[i + 1].size[0], imgs[i + 1].size[1]))

        img = np.vstack(imgs)
        # Image.fromarray(img).save('out.jpg', quality=100)
        return Image.fromarray(img)


    def find_head_and_tail_content(self, image, is_top=False):
        """查找开头或结尾的文本行"""
        img_gray = np.array(image.convert("L"))  # 转为灰度
        s_height = 180
        is_content = False
        content_list = []

        r_begin = 0 if is_top else image.size[1] - s_height
        r_end = s_height if is_top else image.size[1]

        for position in range(r_begin, r_end):
            black_pix = np.count_nonzero(img_gray[position] <= 250)
            if black_pix > 0 and not is_content:
                content_list.append(position)
                is_content = True
            elif black_pix == 0 and is_content:
                content_list.append(position)
                is_content = False

        if len(content_list) % 2 == 1:
            content_list = content_list[:-1]

        content_list = np.array(content_list).reshape(-1, 2).tolist()
        print(content_list)
        # img = np.array(image)
        r = []
        for content in content_list:
            if content[1] - content[0] > 2:
                img = img_gray[content[0] : content[1]]
                img[img == 254] = 255
                r.append((img, content))
        return r

    def compare_two_text(self, image1, image2):
        """对比两张图片的开头和末位是否有相同的文本行"""
        r1 = self.find_head_and_tail_content(image1, is_top=False)
        r2 = self.find_head_and_tail_content(image2, is_top=True)
        r1.reverse()

        for r in r1:
            print(f'1.jpg - {r[1]}: {r[0].shape}')
            # Image.fromarray(r[0]).show()

        for r in r2:
            print(f'2.jpg - {r[1]}: {r[0].shape}')
            # Image.fromarray(r[0]).show()

        eq_line = 0

        for i in range(min(len(r1), len(r2))):
            if r1[i][0].shape == r2[i][0].shape:
                if np.count_nonzero(np.abs(r1[i][0].astype(np.int16) - r2[i][0].astype(np.int16)) >= 5) < 10:
                    eq_line += 1
        print(eq_line)

        return r2[eq_line - 1][1][1] + 2 if eq_line > 0 else 0

    def get_files(self):
        return ['03 论题：你有没有走题.jpg', '03 论题：你有没有走题2.jpg']


if __name__ == '__main__':
    dd = DedaoImage()
    img = dd.concat_pictures()
    dd.cut_long_picture(img, dd.get_files()[0], to_pdf=True)

    # r1 = dd.ff(Image.open('1_out.jpg'), is_top=False)
    # r2 = dd.ff(Image.open('2_out.jpg'), is_top=True)
    # r1.reverse()
    #
    # for r in r1:
    #     print(f'1.jpg - {r[1]}: {r[0].shape}')
    #     # Image.fromarray(r[0]).show()
    #
    # for r in r2:
    #     print(f'2.jpg - {r[1]}: {r[0].shape}')
    #     # Image.fromarray(r[0]).show()
    #
    # eq_line = 0
    #
    # for i in range(min(len(r1), len(r2))):
    #     if r1[i][0].shape == r2[i][0].shape:
    #         if np.count_nonzero(np.abs(r1[i][0].astype(np.int16) - r2[i][0].astype(np.int16)) >= 5) < 10:
    #             eq_line += 1
    #
    # print(eq_line)




    # Image.fromarray(r1[0][0]).show()
    #
    # print(r1[0][0].shape)
    # print(r2[0][0].shape)
    # print(np.count_nonzero(np.abs(r1[0][0].astype(np.int16)[0:r2[0][0].shape[0]] - r2[0][0].astype(np.int16)) > 5))
    # rx = np.abs(r1[0][0].astype(np.int16)[0:r2[0][0].shape[0]] - r2[0][0].astype(np.int16))
    #
    # Image.fromarray(rx).show()
