#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2024/2/23 15:40
@Author  : junbao
@File    : pansharpen.py
@Description: 
"""
from osgeo import gdal
import numpy as np
from skimage.transform import resize

def read_image(image_path):
    dataset = gdal.Open(image_path)
    band = dataset.GetRasterBand(1)
    image_array = band.ReadAsArray()
    return image_array, dataset

def write_image(output_path, array, dataset_template):
    driver = gdal.GetDriverByName("GTiff")
    rows, cols = array.shape
    output_dataset = driver.Create(output_path, cols, rows, 1, gdal.GDT_Float32)
    output_band = output_dataset.GetRasterBand(1)
    output_band.WriteArray(array)
    output_dataset.SetProjection(dataset_template.GetProjection())
    output_dataset.SetGeoTransform(dataset_template.GetGeoTransform())
    output_dataset.FlushCache()

def pansharpen(pan_image_path, ms_image_path, output_path):
    # 读取全色图像和多光谱图像
    pan_image_array, pan_dataset = read_image(pan_image_path)
    ms_image_array, ms_dataset = read_image(ms_image_path)

    # 调整全色图像分辨率
    pan_image_array_resized = resize(pan_image_array, ms_image_array.shape, mode='constant', anti_aliasing=True)

    # 进行全色融合
    fused_image_array = np.copy(ms_image_array)
    fused_image_array[:, :] = pan_image_array_resized

    # 保存融合后的图像
    write_image(output_path, fused_image_array, ms_dataset)

    print("融合完成，结果保存在:", output_path)




if __name__ == "__main__":
    # 输入多光谱图像路径、全色图像路径和输出路径
    pan_path = r"data/JL1GF03B02_PMS_20220516095811_200084559_101_0008_001_L1/JL1GF03B02_PMS_20220516095811_200084559_101_0008_001_L1_PAN.tif"
    mss_path = r"data/JL1GF03B02_PMS_20220516095811_200084559_101_0008_001_L1/JL1GF03B02_PMS_20220516095811_200084559_101_0008_001_L1_MSS.tif"
    pansharpen_path = pan_path.replace("PAN.tif", "pansharpen1.tiff")

    # 执行全色与多光谱融合
    pansharpen(pan_path, mss_path, pansharpen_path)

# if __name__ == '__main__':
#     pan_path = r"data/DP09_PMS_20231120152824_200213459_101_0025_001_L1/DP09_PMS_20231120152824_200213459_101_0025_001_L1_PAN.tif"
#     mss_path = r"data/DP09_PMS_20231120152824_200213459_101_0025_001_L1/DP09_PMS_20231120152824_200213459_101_0025_001_L1_MSS.tif"
#     pansharpen_path = pan_path.replace("PAN.tiff", "pansharpen.tiff")
#     gdal_pansharpen(["pass", pan_path, mss_path, pansharpen_path])
