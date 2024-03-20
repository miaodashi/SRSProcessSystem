#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2023/12/27 20:21
@Author  : junbao
@File    : ortho_GF1.py
@Description: 
"""

import os

from PIL import Image
from osgeo import gdal, osr
import time


# 设置像素限制为较大的值
Image.MAX_IMAGE_PIXELS = None


# 重新定义投影
def reproject_tif(input_tif, output_tif, target_srs='EPSG:4326'):
    # 打开输入tif文件
    input_dataset = gdal.Open(input_tif)

    # 获取输入tif的宽度和高度
    input_width = input_dataset.RasterXSize
    input_height = input_dataset.RasterYSize

    # 执行坐标系转换
    gdal.Warp(output_tif, input_dataset, dstSRS=target_srs, width=input_width, height=input_height)

    # 关闭输入tif文件
    input_dataset = None


# 读入rpc文件
def read_rpc(file_path):
    rpc_dict = {}

    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()
            if line:
                key, value = line.split(':')
                if key.split('_')[-1].isdigit():
                    coeff_prefix = key[:key.rindex('_')]
                    # print(coeff_prefix)
                    if coeff_prefix not in rpc_dict:
                        rpc_dict[coeff_prefix.strip()] = value.strip()
                    else:
                        rpc_dict[coeff_prefix.strip()] += ' ' + value.strip()
                else:
                    rpc_dict[key.strip()] = value.strip()

    return rpc_dict


# 正射校正
def RPCrect(input, output, dem_name, rpc_path):
    """
    使用
    :param input:输入原始影像
    :param output:输出正射影像
    """

    dataset = gdal.Open(input, gdal.GA_ReadOnly)  # 读入影像
    # print(type(dataset))

    rpc = dataset.GetMetadata("RPC")  # 读入影像，rpc
    # print(rpc)

    if rpc == {}:
        if not os.path.exists(rpc_path):
            print('该文件rpc.txt不存在')
            return
        rpc = read_rpc(rpc_path)
    # print(rpc)

    reput = input.replace('.tif', '(1).tif')
    # print(reput)
    reproject_tif(input, reput)
    # print('reproject finish')
    # print(output)

    output_dataset = gdal.Open(reput)

    # 获取输入图像的x和y方向分辨率
    x_res = output_dataset.GetGeoTransform()[1]
    y_res = output_dataset.GetGeoTransform()[5]
    # print(output_dataset.GetGeoTransform())
    y_res = abs(y_res)

    # print(x_res, y_res)

    # 删除重新定义投影的文件
    output_dataset = None
    os.remove(reput)

    # 3.8933185e-05
    dst_ds = gdal.Warp(output, dataset, dstSRS='EPSG:4326',
                       xRes=x_res,  # x方向正射影像分辨率
                       yRes=y_res,  # y方向正射影像分辨率
                       resampleAlg=gdal.GRIORA_Bilinear,  # 插值方式，默认为最最邻近，我们一般使用双线性
                       rpc=True,  # 使用RPC模型进行校正
                       transformerOptions=[r'RPC_DEM=' + dem_name]  # 参考DEM
                       )

    # 关闭tif文件
    dataset = None


def ortho(file_path, target_dir_path, dem_name):
    list = [i for i in os.listdir(file_path) if i.endswith('.tif') or i.endswith('.tiff')]
    # print(list)
    # print(file_path)
    num = len(list)
    print(f'该文件夹下共{num}个tif文件')
    # 获取tif文件
    for i, file_name in enumerate(list):
        print(f'开始第{i + 1}张图片的正射校正')
        input = os.path.join(file_path, file_name)
        print(input)
        start = time.time()  # 统计运行时间

        output = file_name.replace('.tif', '_ortho.tif')
        output = os.path.join(target_dir_path, output)

        rpc_path = input.replace('.tif', '_rpc.txt')

        RPCrect(input, output, dem_name, rpc_path)

        if not os.path.exists(output):
            print('该文件正射校正失败，请检查文件夹\n')
            return

        end = time.time()
        print(f'第{i + 1}张图片的正射校正完成')
        print("正射校正运行时间:%.2f秒\n" % (end - start))
