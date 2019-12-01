# coding=utf-8
from __future__ import division
import math
from scipy.spatial import distance


def main():
    data_lst = []
    with open("data/0h+.csv", "r") as data:
        line_cnt = 0
        for line in data:
            if line_cnt == 0:
                line_cnt += 1
                continue
            items = line.strip().split(",")
            if len(items) != 10:
                continue
            # print(float(items[1]))
            tmp = [int(items[0])] + [float(x) for x in items[1:7]]
            data_lst.append(tmp)
    result = []
    for record in data_lst:
        for comp in data_lst:
            if record[0] == comp[0]:
                continue
            c = distance.cosine(record[1:4], comp[1:4])
            angle = math.degrees(math.acos(1 - c))
            result.append([record[0], comp[0], angle])
            print(record[0], comp[0], angle)
    with open("data/angle.csv", "w") as res:
        for r in result:
            res.writelines("{},{},{}\n".format(*r))


if __name__ == "__main__":
    main()

