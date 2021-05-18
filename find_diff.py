#!/bin/env python3
# coding=utf-8
# Copyright (c) 2021 Dylan, Inc. All Rights Reserved
"""
Authors: Dylan
Date: 2021/5/16
"""
# -*- coding: utf-8 -*-
import logging
import re
import platform

import pandas as pd
import math
import scipy.stats as stats


# 这写列表用于指定从哪个sheet取那几列数据
col_followup = ["疾病亚型", "病理分期", "手术病理分期（pTNM）", "是否复发"]
col_OncoS = ["PN校正为阳性，H3-H6调VAF下限", "Driver阳性", "ctDNA 阳性 or 阴性", "姓名"]
col_clinic = ["吸烟史", "姓名", "性别", "确诊年龄", "MSI"]
col_zzSNV = ["姓名", "基因", "功能"]
col_CNV = ["姓名", "基因", "扩增/缺失"]
col_SV = ["姓名", "融合基因"]
col_peixi = ["姓名", "基因"]


def process_data1(data_df):
    group = data_df.groupby(by="姓名")
    new_data_1 = []
    for name, g in group:
        item_cnt = len(g)
        item_dict = dict()
        for c in ["姓名"] + col_followup:
            cur_value = None
            for i in range(item_cnt):
                v = g[c].iloc[i]
                v = None if v == "nan" else v
                if type(v) is not str:
                    v = None if math.isnan(v) else v
                if v is not None:
                    if cur_value is None:
                        cur_value = v
                    elif cur_value != v:
                        print("error! {}患者的{}特征冲突: {} vs {}".format(name, c, str(cur_value), str(v)))
            if c == "病理分期" and cur_value is not None and type(cur_value) is str:
                if "IV" in cur_value:
                    cur_value = "IV"
                elif cur_value.startswith("I"):
                    v_items = []
                    for x in cur_value:
                        if x == "I":
                            v_items.append(x)
                        else:
                            break
                    cur_value = "".join(v_items)
                if cur_value == "IIII":
                    print(g["姓名"])
            elif c == "手术病理分期（pTNM）":
                t, n, m = [], [], []
                if type(cur_value) is str:
                    t = re.findall(r"T\d", cur_value)
                    n = re.findall(r"N\d", cur_value)
                    m = re.findall(r"M\d", cur_value)

                item_dict.update({"T": t[0] if t else None, "N": n[0] if n else None, "M": m[0] if m else None})
            elif c == "是否复发" and cur_value is not None:
                if cur_value == 1:
                    cur_value = True
                elif cur_value == 0:
                    cur_value = False

            item_dict[c] = cur_value
        new_data_1.append(item_dict)
    new_data_1 = pd.DataFrame(new_data_1)
    return new_data_1


def process_data2(data_df):
    group = data_df.groupby(by="姓名")
    new_data_2 = []
    for name, g in group:
        item_cnt = len(g)
        item_dict = dict()
        for c in col_OncoS:
            cur_value = None
            for i in range(item_cnt):
                v = g[c].iloc[i]
                v = None if v == "nan" else v
                if type(v) is not str:
                    v = None if math.isnan(v) else v
                if v is not None:
                    if cur_value is None:
                        cur_value = v
                    elif cur_value != v:
                        print("error! {}患者的{}特征冲突: {} vs {}".format(name, c, str(cur_value), str(v)))

            item_dict[c] = cur_value
        new_data_2.append(item_dict)
    new_data_2 = pd.DataFrame(new_data_2)
    return new_data_2


def process_linchuangxinxi(data_df, cols):
    """
    临床信息数据预处理
    :param data_df:
    :param cols:
    :return:
    """
    group = data_df.groupby(by="姓名")
    new_data = []
    for name, g in group:
        item_cnt = len(g)
        item_dict = dict()
        for c in cols:
            cur_value = None
            for i in range(item_cnt):
                v = g[c].iloc[i]
                v = None if v == "nan" else v
                if type(v) is not str:
                    v = None if math.isnan(v) else v
                if v is not None:
                    if cur_value is None:
                        cur_value = v
                    elif cur_value != v:
                        print("error! {}患者的{}特征冲突: {} vs {}".format(name, c, str(cur_value), str(v)))
                        if c == "吸烟史":
                            if cur_value == "不详" and v != "不详":
                                cur_value = v
                                print("但是在‘吸烟史’数据上尊重有/无数据，选择{}".format(v))
            if c == "确诊年龄":
                if cur_value is not None:
                    ages = sorted([int(x) for x in re.findall(r"\d+", cur_value)])
                    age1, age2 = None, None
                    if len(ages) >= 1:
                        age1 = ages[0]
                    if len(ages) >= 2:
                        age2 = ages[1]
                    item_dict.update({"age1": age1, "age2": age2})

            item_dict[c] = cur_value
        new_data.append(item_dict)
    new_data = pd.DataFrame(new_data)
    return new_data


def enum_report(data, columns):
    """
    枚举特征的分布统计，比如性别
    :param data: 包含统计列的dataframe
    :param columns: 列名列表，可以只有一个， 如 ["基因"]
    :return: result， dict<列名：[[值1，出现次数], [值2，出现次数]]>
    """
    result = {}
    for c in columns:
        item_result = []
        groups = data[[c]].fillna("None").groupby(by=c)
        for c_name, g in groups:
            item_result.append([c_name, len(g)])
        result[c] = item_result
    return result


def load_data(file_name, sheet_names):
    """
    加载excel数据
    :param file_name: string, 文件路径
    :param sheet_names: list, 需要读取的sheet名称
    :return:
    """
    sys_type = platform.system()
    xls_engine = None
    if sys_type != "Windows":
        xls_engine = "openpyxl"

    data_df = dict()
    try:
        data_df = pd.read_excel(file_name, engine=xls_engine, sheet_name=sheet_names)
        logging.info("read {} sheet(s) in Calculator".format(str(sheet_names)))
    except KeyError as e:
        logging.error(str(e))
    return data_df


def run_analysis(data_dict):
    """

    :param data_dict:
    :return:
    """
    all_data = dict()

    base_df = data_dict["临床信息"]

    users = base_df[["patientID"]].drop_duplicates()
    logging.info("共读取到 {} 位患者数据，概况如下：".format(len(users)))
    logging.info(users)

    # fisher检验的列名: （此列考察的两种取值）
    fisher_objects = {
        "性别": ("男", "女"),
        "吸烟史": ("有", "无"),
        "N": (0, 1),
        "M": (0, 1)
    }

    # t检验的列名
    t_objects = ["确诊年龄"]

    for sheet in ["胚系", "SNV", "SV"]:
        tmp_df = data_dict[sheet]
        if sheet == "SNV":
            tmp_df = tmp_df[tmp_df["基因"] == "TERT"]
        elif sheet == "SV":
            tmp_df = tmp_df[tmp_df["是否有药物提示"] == "是"]
        tmp_df.loc[:, "exist_flag"] = 1

        item_df = pd.merge(base_df, tmp_df, how="outer", on="patientID")

        pair_df = {
            0: item_df[item_df["exist_flag"] != 1].drop_duplicates(subset=["patientID"]),
            1: item_df[item_df["exist_flag"] == 1].drop_duplicates(subset=["patientID"])
        }

        all_data[sheet] = pair_df
        logging.info("in {}".format(sheet))
        logging.info("{}(exist) vs {}(not exist)".format(len(pair_df[1]), len(pair_df[0])))

        with open("data/{}_fisher_data.txt".format(sheet), "w") as ff:
            ff.writelines(",".join(["column_name", "exist_0", "exist_1", "not_exist_0", "not_exist_1", "p", "oddsratio"]) + "\n")
            for col in fisher_objects:
                e_df, ne_df = pair_df[1], pair_df[0]
                a = len(e_df[e_df[col] == fisher_objects[col][0]])
                b = len(e_df[e_df[col] == fisher_objects[col][1]])
                c = len(ne_df[ne_df[col] == fisher_objects[col][0]])
                d = len(ne_df[ne_df[col] == fisher_objects[col][1]])
                oddsratio, p = stats.fisher_exact([[a, b], [c, d]])
                logging.info("{} - {}: p={},oddr={}".format(sheet, col, p, oddsratio))
                ff.writelines(",".join([col, str(a), str(b), str(c), str(d), str(p), str(oddsratio)]) + "\n")

        for col in t_objects:
            e_df, ne_df = pair_df[1], pair_df[0]
            tmp = stats.ttest_ind(e_df[col].to_list(), ne_df[col].to_list())
            print()


def main():

    # 读取数据，注意指定Excel表名和sheet名
    data1 = pd.read_excel('g_data/需要随访的案例210427.xlsx', engine='openpyxl', sheet_name="Sheet1")[col_followup + ["姓名"]]
    data2 = pd.read_excel('g_data/OncoS 样本信息汇总 肺癌 20201123更新.xlsx', engine='openpyxl', sheet_name="肺癌 临床 疗效数据")[col_OncoS]
    data_linchuangxinxi = pd.read_excel('g_data/重新下载_VUSE.xlsx', engine='openpyxl', sheet_name="临床信息")[col_clinic]
    data_zzSNV = pd.read_excel('g_data/重新下载_VUSE_all mutation.xlsx', engine='openpyxl', sheet_name="组织SNV")[col_zzSNV]

    clean_data1 = process_data1(data1)
    print("data1 处理完成：")
    print(clean_data1.describe())

    clean_data2 = process_data2(data2)
    print("\ndata2 处理完成: ")
    print(clean_data2.describe())

    clean_data_linchuangxinxi = process_linchuangxinxi(data_linchuangxinxi, col_clinic)
    print("\n临床信息 处理完成: ")
    print(clean_data_linchuangxinxi.describe())
    print(clean_data_linchuangxinxi[["吸烟史", "性别", "确诊年龄"]].describe())

    # merge 将 几个表sheet数据合并到一起
    all_data = pd.merge(clean_data1, clean_data2, how="outer", on="姓名")
    all_data = pd.merge(all_data, clean_data_linchuangxinxi, how="outer", on="姓名")
    all_data = pd.merge(all_data, data_zzSNV, how="outer", on="姓名")

    x = all_data[["姓名", "基因"]].drop_duplicates()

    zzSNV_cnts_all = enum_report(x, ["基因"])
    zzSNV_cnts_all = sorted(zzSNV_cnts_all["基因"], key=lambda x: x[1], reverse=True)
    zzSNV_cnts_all = [item[0] for item in zzSNV_cnts_all]
    zzSNV_set = set(zzSNV_cnts_all)

    # groupby 就是按后边指定的特征分组，指定特征相同的在一组

    # 按ctDNA 分组
    pn_columns = ["PN校正为阳性，H3-H6调VAF下限"]
    print("按 {} 分组".format(str(pn_columns)))
    all_groups = all_data.groupby(by=pn_columns)
    for g_type, g in all_groups:
        # g_type, 组名，以指定的分组特征的值作为组名
        # g, 组数据
        x = g[["姓名", "基因"]].drop_duplicates()
        users = g[["姓名"]].drop_duplicates()
        all_user = len(users)
        print("{}-{}人".format(g_type, all_user))

        # 下面统计基因突变量
        zzSNV_cnts = enum_report(x, ["基因"])["基因"]
        zzSNV_cnts = {item[0]: item[1] for item in zzSNV_cnts if item[0] in zzSNV_set}

        with open("g_data/zzSNV_gene_{}_freq.txt".format(g_type), "w") as f:
            for k in zzSNV_cnts_all:
                f.writelines("{}\t{}\t{}\n".format(k, zzSNV_cnts.get(k, 0), all_user))
        with open("g_data/zzSNV_gene_{}_freq_ratio.txt".format(g_type), "w") as f:
            for k in zzSNV_cnts_all:
                f.writelines("{}\t{}\t{}\n".format(k, zzSNV_cnts.get(k, 0) / all_user, all_user))

    # ctDNA 分别为 Positive 和 Negative 时再按是否复发分组
    for ct_status in ["Positive", "Negative"]:
        print("ctDNA 为 {} 时".format(ct_status))
        pn_columns = ["是否复发"]
        print("按 {} 分组".format(str(pn_columns)))

        g_df = all_data[all_data["PN校正为阳性，H3-H6调VAF下限"] == ct_status]

        gene_rep = enum_report(g_df, ["基因"])
        all_genes = sorted(gene_rep["基因"], key=lambda x: x[1], reverse=True)
        all_genes = [item[0] for item in all_genes]
        all_gene_set = set(all_genes)

        all_groups = g_df.groupby(by=pn_columns)
        for g_type, g in all_groups:
            x = g[["姓名", "基因"]].drop_duplicates()
            zzSNV_cnts = enum_report(x, ["基因"])["基因"]
            zzSNV_cnts = {item[0]: item[1] for item in zzSNV_cnts if item[0] in all_gene_set}

            users = g[["姓名"]].drop_duplicates()
            all_user = len(users)
            print("{}-{}人".format(g_type, all_user))

            with open("g_data/zzSNV_gene_{}_{}(ff)_freq.txt".format(ct_status, g_type), "w") as f:
                for k in all_genes:
                    f.writelines("{}\t{}\t{}\n".format(k, zzSNV_cnts.get(k, 0), all_user))
            with open("g_data/zzSNV_gene_{}_{}(ff)_freq_ratio.txt".format(ct_status, g_type), "w") as f:
                for k in all_genes:
                    f.writelines("{}\t{}\t{}\n".format(k, zzSNV_cnts.get(k, 0) / all_user, all_user))


if __name__ == '__main__':
    main()

