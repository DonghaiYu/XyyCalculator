# coding=utf-8
"""
Author: Dylan
For my love, XYY
"""
import os


def sum_data(file_name):
    """
    对杨氏模量读取并求和
    :param file_name: string, 杨氏模量数据文件路径
    :return: float, int, 求和结果， 有效读取的数据行数
    """
    result = 0
    unit_level = 1
    with open(file_name, "r") as data:
        line_num = 0
        for line in data:
            if line_num == 0:
                items = line.strip().split("\t")
                unit = items[0].lower().strip()
                if unit == "kpa":
                    unit_level = 1000
                line_num += 1
                continue
            items = line.strip().split("\t")
            if len(items) < 2:
                print("please check data quality in " + file_name)
                continue
            try:
                mpa = float(items[0]) / unit_level
                per = float(items[1])
            except Exception as e:
                print("data type not float, please check " + file_name)
                continue
            result += mpa * per
            line_num += 1
        result /= 100
    return result, line_num - 1


def get_files(path, suffix):
    """
    递归获取指定路径下的所有指定后缀的文件
    :param path: string, 文件夹或文件路径
    :param suffix: string, 指定的后缀格式
    :return: list, path下有指定后缀名称的所有文件
    """
    return_result = []
    for dir_name in os.listdir(path):
        current_path = path + "/" + dir_name
        if os.path.isdir(current_path):
            childes = get_files(current_path, suffix)
            return_result.extend(childes)
        elif os.path.splitext(current_path)[1] == suffix:
                return_result.append(current_path)
    return return_result
