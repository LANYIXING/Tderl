import cv2
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import time
import keyboard

def draw_bounding_box_on_image(image, box, display_str_list=('0'),
                               color='red', thickness=4, use_normalized_coordinates=True):
    """
    Args:
      image: a cv2 object.
      BOX{
      ymin: ymin of bounding box.
      xmin: xmin of bounding box.
      ymax: ymax of bounding box.
      xmax: xmax of bounding box.}
      color: color to draw bounding box. Default is red.
      thickness: line thickness. Default value is 4.
      display_str_list: list of strings to display in box
                        (each to be shown on its own line).
      use_normalized_coordinates: If True (default), treat coordinates
        ymin, xmin, ymax, xmax as relative to the image.  Otherwise treat
        coordinates as absolute.
    """
    image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    ymin, xmin, ymax, xmax = box
    draw = ImageDraw.Draw(image)
    # 获取图像的宽度与高度
    im_width, im_height = image.size
    if use_normalized_coordinates:
        (left, right, top, bottom) = (xmin * im_width, xmax * im_width,
                                      ymin * im_height, ymax * im_height)
    else:
        (left, right, top, bottom) = (xmin, xmax, ymin, ymax)

    # 绘制Box框
    draw.line([(left, top), (left, bottom), (right, bottom),
               (right, top), (left, top)], width=thickness, fill=color)

    # 加载字体
    try:
        font = ImageFont.truetype("font/simsun.ttc", 24, encoding="utf-8")
    except IOError:
        font = ImageFont.load_default()

    # 计算显示文字的宽度集合 、高度集合
    display_str_width = [font.getsize(ds)[0] for ds in display_str_list]
    display_str_height = [font.getsize(ds)[1] for ds in display_str_list]
    # 计算显示文字的总宽度
    total_display_str_width = sum(
        display_str_width) + max(display_str_width) * 1.1
    # 计算显示文字的最大高度
    total_display_str_height = max(display_str_height)

    if top > total_display_str_height:
        text_bottom = top
    else:
        text_bottom = bottom + total_display_str_height

    # 计算文字背景框最右侧可到达的像素位置
    if right < (left + total_display_str_width):
        text_right = right
    else:
        text_right = left + total_display_str_width

    # 绘制文字背景框
    draw.rectangle(
        [(left, text_bottom), (text_right, text_bottom - total_display_str_height)],
        fill=color)

    # 计算文字背景框可容纳的文字，若超出部分不显示，改为补充“..”
    for index in range(len(display_str_list[::1])):
        current_right = (left + (max(display_str_width)) +
                         sum(display_str_width[0:index + 1]))

        if current_right < text_right:
            # print(current_right)
            display_str = display_str_list[:index + 1]
        else:
            display_str = display_str_list[0:index - 1] + '...'
            break

            # 绘制文字
    draw.text(
        (left +
         max(display_str_width) /
         2,
         text_bottom -
         total_display_str_height),
        display_str,
        fill='black',
        font=font)

    return cv2.cvtColor(np.asarray(image), cv2.COLOR_RGB2BGR)


def get_center_position(box):
    y_min, x_min, y_max, x_max = box
    y_center = (y_min + y_max) / 2
    x_center = (x_min + x_max) / 2
    return x_center, y_center


def select_roi(img, showCrosshair=True, fromCenter=False):
    """
    Args：
    img 需要处理的图像
    showCrosshair = True  # 是否显示交叉线
    # if true, then from the center
    # if false, then from the left-top
    fromCenter = False  # 是否从中心开始选择

    """
    rect = cv2.selectROI('image', img, showCrosshair, fromCenter)
    # 也可以是 rect = cv2.selectROI('image', img, False, False)#记得改掉上面的语句不要设置为
    # rect = cv2.selectROI('image', img, showCrosshair=False, fromCenter=False)
    # get the ROI
    (x, y, w, h) = rect
    x_min = x
    x_max = x + w
    y_min = y
    y_max = y + h
    img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))

    im_width, im_height = img.size
    x_min_n = x_min/im_width
    x_max_n = x_max/im_width
    y_min_n = y_min/im_height
    y_max_n = y_max/im_height
    return y_min_n, x_min_n, y_max_n, x_max_n


def init_select_roi(img):
    box = []
    roi_number = 0
    while True:
        print("请选择感兴趣区域，确认完成请按Y，否则继续添加")
        rect = select_roi(img)
        img = draw_bounding_box_on_image(img, rect, '%s' % (roi_number + 1))
        box.append(rect)
        print(box)
        name = input('Please select Rois and then press Y button. Otherwise another roi will be added！')
        roi_number += 1
        if name == "y" or name == "Y":
            break
    return box


def show_roi(img,box_list):
    """
    输入图像和框，显示并返回位置状态
    """
    state = []
    for i, box in enumerate(box_list):
        img = draw_bounding_box_on_image(img, box, '%s' % (i + 1))
        state.append(get_center_position(box))
        print(state)
    state = [x for y in state for x in y]  # flatten the list
    print(state)
    cv2.imshow("image", img)
    cv2.imwrite("roi_image.jpg", img)
    cv2.waitKey(0)
    return state


if __name__ == '__main__':

    img = cv2.imread("01.png", cv2.IMREAD_COLOR)
    img = cv2.resize(img,(84,84))
    box_list = init_select_roi(img)
    print(box_list)
    state = show_roi(img, box_list)
