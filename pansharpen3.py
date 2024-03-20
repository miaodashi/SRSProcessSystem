#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2024/2/26 21:24
@Author  : junbao
@File    : pansharpen3.py
@Description: 
"""
from osgeo import gdal

def pan_sharpen(pan_path, multispectral_path, output_path):
    # 打开全色图像和多光谱图像
    pan_dataset = gdal.Open(pan_path, gdal.GA_ReadOnly)
    multispectral_dataset = gdal.Open(multispectral_path, gdal.GA_ReadOnly)

    # 获取全色图像和多光谱图像的信息
    pan_info = pan_dataset.GetGeoTransform()
    multispectral_info = multispectral_dataset.GetGeoTransform()

    # 获取全色图像和多光谱图像的投影
    pan_proj = pan_dataset.GetProjection()
    multispectral_proj = multispectral_dataset.GetProjection()

    # 获取全色图像和多光谱图像的波段
    pan_band = pan_dataset.GetRasterBand(1)
    multispectral_bands = [multispectral_dataset.GetRasterBand(i) for i in range(1, multispectral_dataset.RasterCount + 1)]

    # 创建输出图像
    driver = gdal.GetDriverByName("GTiff")
    output_dataset = driver.Create(output_path, multispectral_dataset.RasterXSize, multispectral_dataset.RasterYSize, multispectral_dataset.RasterCount + 1, gdal.GDT_Byte)

    # 将全色图像的像素值缩放到与多光谱图像相匹配
    pan_scaled = pan_band.ReadAsArray().astype(float) / 255.0
    pan_scaled = pan_scaled * (multispectral_bands[0].ReadAsArray().max() - multispectral_bands[0].ReadAsArray().min())
    pan_scaled = pan_scaled + multispectral_bands[0].ReadAsArray().min()

    # 将全色图像写入输出图像的第一个波段
    output_dataset.GetRasterBand(1).WriteArray(pan_scaled)

    # 将多光谱图像的波段写入输出图像
    for i, band in enumerate(multispectral_bands):
        output_dataset.GetRasterBand(i + 2).WriteArray(band.ReadAsArray())

    # 设置输出图像的信息和投影
    output_dataset.SetGeoTransform(multispectral_info)
    output_dataset.SetProjection(multispectral_proj)

    # 关闭数据集
    pan_dataset = None
    multispectral_dataset = None
    output_dataset = None


if __name__ == '__main__':
    # 输入多光谱图像路径、全色图像路径和输出路径
    pan_path = r"data/JL1GF03B02_PMS_20220516095811_200084559_101_0008_001_L1/JL1GF03B02_PMS_20220516095811_200084559_101_0008_001_L1_PAN.tif"
    mss_path = r"data/JL1GF03B02_PMS_20220516095811_200084559_101_0008_001_L1/JL1GF03B02_PMS_20220516095811_200084559_101_0008_001_L1_MSS.tif"
    pansharpen_path = pan_path.replace("PAN.tif", "pansharpen3.tiff")

    pan_dataset = gdal.Open(pan_path, gdal.GA_ReadOnly)
    multispectral_dataset = gdal.Open(mss_path, gdal.GA_ReadOnly)

    pan_size = (pan_dataset.RasterXSize, pan_dataset.RasterYSize)
    multispectral_size = (multispectral_dataset.RasterXSize, multispectral_dataset.RasterYSize)

    print("Pan Size:", pan_size)
    print("Multispectral Size:", multispectral_size)

    pan_sharpen(pan_path, mss_path, pansharpen_path)
