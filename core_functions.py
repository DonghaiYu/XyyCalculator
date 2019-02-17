# coding=utf-8
"""
Author: Dylan
For my love, XYY
"""
import os
import copy
import collections


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


def label_analysis(base_path, area_suffix, interval_folders, hours):

    # read area data
    area_dict = read_cell_area(base_path, area_suffix, hours)

    # analysis each folder

    total_result = {}
    folder_cnt = 0
    total_head = [""]
    for interval_folder in interval_folders:
        print("\n************** START **************\n")
        print("analysis {}".format(interval_folder))
        folder_name = os.path.basename(interval_folder)
        area_map_dict = read_area_map(interval_folder, hours)

        avg_tmp = []
        for i in range(len(hours) - 1):
            inters = hours[i:]
            analysis_result = chain_analysis(area_dict, area_map_dict, inters)
            if analysis_result:
                print("success")
            else:
                print("failed")

            avg_data, titles = save_label_result(analysis_result, interval_folder, inters)

            if i == 0:
                avg_tmp.extend(avg_data[3::2])
                if folder_cnt == 0:
                    total_head.extend(titles[3::2])
            else:
                avg_tmp.append(avg_data[3])
                if folder_cnt == 0:
                    total_head.append(titles[3])

        total_result[folder_name] = [str(x) for x in avg_tmp]
        print("\n************** END **************\n")
        folder_cnt += 1

    with open("{}/result_collection.csv".format(base_path), "w") as total_file:
        total_file.writelines(",".join(total_head) + "\n")
        for folder_name in total_result:
            total_file.writelines(",".join([folder_name] + total_result[folder_name]) + "\n")


def save_label_result(result_dict, interval_folder, hours):
    save_lst = []
    head_title = ["{}h_label".format(hours[0]), "{}h_area".format(hours[0])]
    for h in hours[1:]:
        head_title.extend(["{}h_area".format(h), "{}/{}".format(h, hours[0])])
    save_lst.append(head_title)

    tail_title = ["average"]
    tmp_result = result_dict[hours[0], hours[1]]
    start_area_lst = []
    end_area_lst = []
    spe_value_lst = []
    for l in tmp_result:
        a, b, c = tmp_result[l]
        start_area_lst.append(a)
        end_area_lst.append(b)
        spe_value_lst.append(c)
    tail_title.extend([sum(start_area_lst) / len(start_area_lst),
                       sum(end_area_lst) / len(end_area_lst),
                       sum(spe_value_lst) / len(spe_value_lst)])

    if len(hours) > 2:
        for h in hours[2:]:
            end_area_lst = []
            spe_value_lst = []
            for k in tmp_result:
                if k in result_dict[hours[0], h]:
                    a, b, c = result_dict[hours[0], h][k]
                    tmp_result[k].extend([b, c])
                    end_area_lst.append(b)
                    spe_value_lst.append(c)
                else:
                    tmp_result[k].extend(['', ''])

            if len(end_area_lst) == 0:
                tail_title.append(0)
            else:
                tail_title.append(sum(end_area_lst) / len(end_area_lst))
            if len(spe_value_lst) == 0:
                tail_title.append(0)
            else:
                tail_title.append(sum(spe_value_lst) / len(spe_value_lst))

    for k in tmp_result:
        tmp_lst = [k] + tmp_result[k]
        tmp_lst = [str(x) for x in tmp_lst]
        save_lst.append(tmp_lst)
    tail_title = [str(x) for x in tail_title]
    save_lst.append(tail_title)

    with open("{}/result_{}-{}.csv".format(interval_folder, hours[0], hours[-1]), "w") as save_file:
        for l in save_lst:
            save_file.writelines(",".join(l) + "\n")

    return tail_title, head_title


def chain_analysis(area_dict, area_map_dict, hours):
    result_dict = {}
    for i in range(1, len(hours)):
        print("##############################\n")
        print("{}-{}".format(hours[0], hours[i]))
        tmp_result = {}
        tail_h_index = i
        pre_h_index = i - 1

        invalid_labels_set = check_invalid_label(area_dict, area_map_dict, hours, tail_h_index)

        print("invalid labels: ({})".format(len(invalid_labels_set)))
        print(invalid_labels_set)

        tmp_map_dict = copy.deepcopy(area_map_dict[hours[pre_h_index], hours[tail_h_index]])
        while pre_h_index != 0:

            pre_map = area_map_dict[hours[pre_h_index - 1], hours[tail_h_index - 1]]
            for k in tmp_map_dict:
                tmp_map_dict[k] = pre_map.get(tmp_map_dict[k], None)

            pre_h_index -= 1
            tail_h_index -= 1
        tail_area_dict = collections.defaultdict(int)
        for k in tmp_map_dict:
            v = tmp_map_dict[k]
            if k is None or v is None:
                continue
            tail_area_dict[v] += area_dict[hours[i]][k]

        x = 0
        for k in tail_area_dict:
            if k not in area_dict[hours[0]] or k in invalid_labels_set:
                continue
            start_area = area_dict[hours[0]][k]
            end_area = tail_area_dict[k]
            tmp_result[k] = [start_area, end_area, end_area / start_area]
            # print(k, area_dict[hours[0]][k], tail_area_dict[k])
            x += 1
        print("total {}".format(x))
        result_dict[hours[0], hours[i]] = tmp_result
    return result_dict


def check_invalid_label(area_dict, area_map_dict, hours, tail_index):

    invalid_label_set = set()
    start_map = area_map_dict[hours[0], hours[1]]

    map_buff = collections.defaultdict(set)
    for k in start_map:
        map_buff[start_map[k]].add(k)

    for i in range(1, tail_index):
        tmp_map = collections.defaultdict(set)
        for k in area_map_dict[hours[i], hours[i + 1]]:
            v = area_map_dict[hours[i], hours[i + 1]][k]
            tmp_map[v].add(k)

        for k in map_buff:
            value_set = map_buff[k]
            tmp_set = set()
            for v in value_set:
                if v not in tmp_map:
                    invalid_label_set.add(k)
                tmp_set |= tmp_map[v]
            map_buff[k] = tmp_set

    return invalid_label_set


def read_cell_area(base_path, area_suffix, hours):

    print("*******************************")
    print("start load cell area data")
    area_dict = {}

    for h in hours:
        area_dict[h] = {}
        with open("{}/{}{}.csv".format(base_path, h, area_suffix)) as area_data:
            i = 0
            for line in area_data:
                if i == 0:
                    i += 1
                    continue
                items = line.strip().split(",")

                if len(items) < 6:
                    continue
                area_dict[h][int(items[0])] = float(items[1])
                i += 1

            print("{} label area in {}{}.csv".format(i, h, area_suffix))
    print(area_dict.keys())
    print("finish")
    print("*******************************")
    return area_dict


def read_area_map(interval_folder, hours):

    print("load label_parent-label data ({})".format(interval_folder))
    area_map_dict = {}

    for i in range(len(hours) - 1):
        head_h = hours[i]
        tail_h = hours[i + 1]

        area_map_dict[head_h, tail_h] = {}
        map_file = "{}/{}-{}.csv".format(interval_folder, head_h, tail_h)
        with open(map_file, "r") as map_data:
            k = 0
            for line in map_data:
                if k == 0:
                    k += 1
                    continue
                items = line.strip().split(",")
                new_l = int(items[0])
                pre_l = int(items[1])
                area_map_dict[head_h, tail_h][new_l] = pre_l
                k += 1
            print("{} map data in {}".format(k, map_file))
    return area_map_dict
