#!/bin/env python
# coding=utf-8
from __future__ import division
import collections
import sys


def main(hour_flags, data_path):
    area_dict = collections.defaultdict(dict)
    maps = {}
    file_path = data_path
    for i, h in enumerate(hour_flags[:-1]):
        map_file = file_path + "{}-{}.csv".format(h, hour_flags[i + 1])
        start_area_file = file_path + "{}h_area.csv".format(h)
        end_area_file = file_path + "{}h_area.csv".format(hour_flags[i + 1])
        print(map_file, start_area_file, end_area_file)

        map_dict = {}
        with open(map_file, "r") as raw_data:
            for j, line in enumerate(raw_data):
                if j == 0:
                    continue
                else:
                    items = line.strip().split(",")
                    if len(items) != 2:
                        continue
                    map_dict[items[0]] = items[1]
        maps["{}-{}".format(h, hour_flags[i + 1])] = map_dict

        if i == 0:
            with open(start_area_file, "r") as raw_data:
                for j, line in enumerate(raw_data):
                    if j == 0:
                        continue
                    else:
                        items = line.strip().split(",")
                        if len(items) != 6:
                            continue
                        area_dict[h][items[0]] = float(items[2])

        with open(end_area_file, "r") as raw_data:
            for j, line in enumerate(raw_data):
                if j == 0:
                    continue
                else:
                    items = line.strip().split(",")
                    if len(items) != 6:
                        continue
                    area_dict[hour_flags[i + 1]][items[0]] = float(items[2])
    print(area_dict)

    map_x = {}
    desc_hours = hour_flags[::-1]
    change_sum_dict = collections.defaultdict(float)
    change_lst_dict = collections.defaultdict(list)

    for i, h in enumerate(desc_hours[:-1]):
        map_key = "{}-{}".format(desc_hours[i + 1], h)
        print(map_key)
        if i == 0:
            map_x = maps[map_key]
        else:
            tmp = {}
            for l in map_x:
                p = map_x[l]
                new_l = maps[map_key].get(p, None)
                if new_l is None:
                    continue
                tmp[l] = new_l
            map_x = tmp
    for end in map_x:
        start = map_x[end]
        tmp_are = area_dict[desc_hours[0]].get(end, None)
        if tmp_are is None:
            change_lst_dict[start].append((None, None))
            continue
        change_sum_dict[start] += float(tmp_are)
        change_lst_dict[start].append((end, float(tmp_are)))

    result_dict = {}

    for k in change_sum_dict:
        # print(k, area_dict[desc_hours[-1]].get(k, None), change_sum_dict[k])
        start_area = area_dict[desc_hours[-1]].get(k, None)
        end_area = change_sum_dict[k]
        if start_area is None or end_area is None:
            result_dict[k] = [start_area, end_area, 0, 0]
        else:
            result_dict[k] = [start_area, end_area, end_area - start_area, end_area / start_area]
    return result_dict


if __name__ == '__main__':

    args = sys.argv
    path = sys.argv[1] + "/"
    hs = sys.argv[2:]

    all_len = len(hs)

    result_collect_dict = None
    for i in range(len(hs) - 1):
        print(hs[:i + 2])
        result = main(hs[:i + 2], path)
        if result_collect_dict is None:
            result_collect_dict = result
        else:
            for k in result_collect_dict:
                result_collect_dict[k].extend(result.get(k, [-1, -1, -1, -1])[1:])

    with open(path + "diff.csv", "w") as save_f:
        head = ["label", "0h_area"]
        for h in hs[1:]:
            head.extend(["{}h_area".format(h), "{}h_sub_0h_area".format(h), "{}h_div_0h".format(h)])
        save_f.writelines(",".join(head) + "\n")
        for k in result_collect_dict:
            tmp = [k] + result_collect_dict[k]
            tmp = [str(x) for x in tmp]
            save_f.writelines(",".join(tmp) + "\n")


