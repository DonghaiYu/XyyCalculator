# coding=utf-8
import cv2
import numpy as np
import math

global point1, point2, zoomed_img, is_selected, zoom_ratio


def on_mouse(event, x, y, flags, param):
    global point1, point2
    img = zoomed_img.copy()
    if event == cv2.EVENT_LBUTTONDOWN:  # 左键点击
        point1 = (x, y)
    elif event == cv2.EVENT_MOUSEMOVE and (flags & cv2.EVENT_FLAG_LBUTTON):  # 按住左键拖曳
        cv2.rectangle(img, point1, (x, y), (255, 0, 0), 2)
        cv2.imshow('image', img)
    elif event == cv2.EVENT_LBUTTONUP:  # 左键释放
        point2 = (x, y)
        cv2.rectangle(img, point1, point2, (0, 122, 255), 2)
        cv2.imshow('image', img)


def img_prepare(img_path, zoom_w, select_rec):
    """
    图片预处理
    :param img_path:
    :param zoom_w: 框选缩略图宽度
    :return:
    """
    global zoomed_img, is_selected, zoom_ratio
    # 读取图片
    original = cv2.imread(img_path)
    if select_rec:
        is_selected = True
        zoomed_img = original.copy()
        h, w, c = zoomed_img.shape
        zoom_ratio = zoom_w / w
        # 放缩后图片高度
        zoomed_img = cv2.resize(zoomed_img, (zoom_w, int(zoom_ratio * h)))
        cv2.namedWindow('image', cv2.WINDOW_AUTOSIZE)
        cv2.setMouseCallback('image', on_mouse)
        cv2.imshow('image', zoomed_img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    # 利用hSV格式提取红色部分
    # 设置hsv格式下的红色的值
    hsv_red = np.array([0, 255, 255], np.uint8)

    # 设置hsv格式下的红色的上下限
    hsv_red_lowerb = np.array([hsv_red[0], 100, 100], np.uint8)
    hsv_red_upperb = np.array([hsv_red[0] + 10, 255, 255], np.uint8)

    # 原图转成hsv
    hsv_img = cv2.cvtColor(original, cv2.COLOR_BGR2HSV)
    # 产生mask
    mask_red = cv2.inRange(hsv_img, hsv_red_lowerb, hsv_red_upperb)

    # 根据mask生成提取的图片
    red_region_img = cv2.bitwise_and(original, original, mask=mask_red)
    # 转回bgr格式
    bgr_img = cv2.cvtColor(red_region_img, cv2.COLOR_HSV2BGR)
    # 转成灰度图
    gray_img = cv2.cvtColor(bgr_img, cv2.COLOR_BGR2GRAY)

    # 高斯模糊预处理
    blur_img = cv2.GaussianBlur(gray_img, (3, 3), 0)
    return original, blur_img


def line_detector(img):
    global point1, point2, zoom_ratio
    fld = cv2.ximgproc.createFastLineDetector(10, 1.4, 50, 150, 3, True)
    lines = fld.detect(img)
    lines = [[[x[0][0], x[0][1]], [x[0][2], x[0][3]]] for x in lines]

    if is_selected:
        x_range = sorted([point1[0] / zoom_ratio, point2[0] / zoom_ratio])
        y_range = sorted([point1[1] / zoom_ratio, point2[1] / zoom_ratio])
        in_lines = []
        for l in lines:
            h, t = l
            if all([x_range[0] <= h[0] <= x_range[1],
                    x_range[0] <= t[0] <= x_range[1],
                    y_range[0] <= h[1] <= y_range[1],
                    y_range[0] <= t[1] <= y_range[1]]):
                in_lines.append([[h[0], h[1]], [t[0], t[1]]])
        return in_lines

    return lines


# Draw detected lines in the image
# drawn_img = cv2.line(original, (0, 0), (1, 1), (0, 255, 0), 2)
# cv2.namedWindow('fld', cv2.WINDOW_NORMAL)
# cv2.imshow("fld", drawn_img)
# cv2.waitKey(0)

def p2line_distance(p, line):
    """
    点到直线距离
    :param p: dict<{'x': x_value, 'y': y_value}> 点坐标
    :param line: list<[{'x': x_value, 'y': y_value},]> 直线的两点
    :return: distance, float, 点到直线的垂直距离
    """
    distance = None
    if not isinstance(line, list) or len(line) != 2:
        return distance
    line_vec = np.array([line[1][0] - line[0][0], line[1][1] - line[0][1]])
    p_vec = np.array([p[0] - line[0][0], p[1] - line[0][1]])
    line_mod_square = float(line_vec.dot(line_vec))
    if line_mod_square == 0:
        return distance
    shadow_vec_len = line_vec.dot(p_vec) / line_mod_square
    shadow_vec = line_vec.dot(shadow_vec_len)
    distance_vec = p_vec - shadow_vec
    distance = np.sqrt(distance_vec.dot(distance_vec))
    return distance


def ps_distance(p1, p2):
    """
    两点距离
    :param p1: dict<{'x': x_value, 'y': y_value}> 点坐标
    :param p2: dict<{'x': x_value, 'y': y_value}> 点坐标
    :return: dist, float, 两点直线距离
    """
    vec1 = np.array([p1[0], p1[1]], dtype=float)
    vec2 = np.array([p2[0], p2[1]], dtype=float)
    dist = np.linalg.norm(vec1 - vec2)
    return dist


def line_angle(line_a, line_b):
    """
    两条线的夹角余弦值
    :param line_a: list<[{'x': x_value, 'y': y_value},{.}]> 直线的两点
    :param line_b: list<[{'x': x_value, 'y': y_value},{.}]> 直线的两点
    :return: cosin_value, float, 夹角余弦值
    """
    a_h = line_a[0]
    a_t = line_a[1]
    b_h = line_b[0]
    b_t = line_b[1]
    v1 = np.array([a_t[0] - a_h[0], a_t[1] - a_h[1]])
    v2 = np.array([b_t[0] - b_h[0], b_t[1] - b_h[1]])
    cosin_value = v1.dot(v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
    return cosin_value


def clean_lines(lines, max_th=10, min_th=20):
    """
    删除太近的或重复的直线
    :param lines:
    :param max_th: 两线段端点投影到彼此的垂直距离最大阈值
    :param min_th: 两线段端点彼此间直线距离最小阈值
    :return:
    """
    del_lines_index = set()
    lines_len = len(lines)
    for i in range(lines_len):
        if i in del_lines_index:
            continue
        for j in range(i + 1, lines_len):

            d1 = p2line_distance(lines[j][0], lines[i])
            d2 = p2line_distance(lines[j][1], lines[i])
            d3 = p2line_distance(lines[i][0], lines[j])
            d4 = p2line_distance(lines[i][1], lines[j])
            # 彼此之间投影距离最大值
            d_max = max(d1, d2, d3, d4)

            fars = []
            for h, t in [[0, 0], [0, 1], [1, 0], [1, 1]]:
                fars.append(ps_distance(lines[i][h], lines[j][t]))
            # 彼此之间端点距离最小值
            min_far = min(*fars)
            # 如果两条直线之间垂直最大投影距离小于 max_th 并且，
            # 两条直线两两端点之间的最小距离小于 min_th（如果大于这个值，则认为可能是两条线段在一条直线上）,
            # 则删除后一条直线

            if d_max < max_th and min_far < min_th:
                del_lines_index.add(j)
    new_lines = []
    del_lines = []
    for i in range(lines_len):
        x1, y1 = lines[i][0]
        x2, y2 = lines[i][1]
        if i not in del_lines_index:
            new_lines.append([[x1, y1], [x2, y2]])
        else:
            del_lines.append([[x1, y1], [x2, y2]])
    return new_lines, del_lines


def format_result(origin_img, cleaned_lines, save_path):
    draw_img = origin_img
    result_lst = []
    for i, line_item in enumerate(cleaned_lines):
        x1, y1 = line_item[0]
        x2, y2 = line_item[1]
        draw_img = cv2.line(draw_img, (x1, y1), (x2, y2), (0, 255, 0), 2)
        draw_img = cv2.putText(draw_img, "{}".format(i), (int((x1 + x2) / 2 + 3), int((y1 + y2)/2)), cv2.FONT_HERSHEY_PLAIN, 1.0, (0, 255, 30), 1)
        angle = math.degrees(math.acos(line_angle([[0, 0], [0, 10]], line_item)))
        result_lst.append([i, angle])

    cv2.imwrite(save_path + "/line_result.png", draw_img)
    with open(save_path + "/line_result.csv", "w") as lrd:
        for idx, ag in result_lst:
            lrd.writelines(",".join([str(idx), str(ag)]) + "\n")


def do_detect(path, zoom_w, select_rec):
    """
    :param path:  图片路径
    :param zoom_w: 框选缩略图宽度
    :param select_rec: 是否框选
    :return:
    """
    raw_img, blur_img = img_prepare(path, zoom_w, select_rec)
    lines = line_detector(blur_img)
    result_lines, del_lines = clean_lines(lines)
    format_result(raw_img, result_lines, "data")


if __name__ == "__main__":
    do_detect("data/cells.png", 800, True)

