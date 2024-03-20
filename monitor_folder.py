"""
# -*- coding: utf-8 -*-
# @Project ：monitor_ortho
# @File    ：monitor_folder.py
# @Author  : longxu
# @Time    : 2023/12/20 16:35
# @Description: 监控文件夹 将新的卫星数据进行正射校正 输出到指定文件夹中

"""
import os
import time
from ortho import *


def process_file(file_path, file, target_dir_path, dem_name):
    # print(f"the new filename: {file_path}")
    # print(file)
    if not os.path.isdir(file_path):
        print("非文件夹文件")
        return

    satelite_type = file.split('_')[0].upper()

    if satelite_type is None:
        print('未知类型')
        return

    print(f'该卫星类型是: {satelite_type}')
    if satelite_type in ['ZY301A', 'ZY302A', 'ZY303A']:
        ortho_ZY3.ortho(file_path, target_dir_path, dem_name)
    elif satelite_type in ['DP01', 'DP03', 'DP04', 'DP05', 'DP06', 'DP07', 'DP08', 'DP09', 'DP10']:
        ortho_JL1DP.ortho(file_path, target_dir_path, dem_name)
    elif satelite_type in ['JL101A', 'JL103B', 'JL105B', 'JL106B', 'JL107B']:
        ortho_JL1.ortho(file_path, target_dir_path, dem_name)
    # elif satelite_type in ['JL1GF02A', 'JL1GF02B', 'JL1GF02D', 'JL1GF02F']:
    elif satelite_type.startswith('JL1GF'):
        ortho_JL1GF.ortho(file_path, target_dir_path, dem_name)
    elif satelite_type in ['JL1GP01', 'JL1GP02']:
        ortho_JL1GP.ortho(file_path, target_dir_path, dem_name)
    elif satelite_type in ['JL1KF01A', 'JL1KF01B', 'JL1KF01C']:
        ortho_JL1KF.ortho(file_path, target_dir_path, dem_name)
    elif satelite_type in ['GF1', 'GF1B', 'GF1C', 'GF1D']:
        ortho_GF1.ortho(file_path, target_dir_path, dem_name)
    elif satelite_type in ['GF2']:
        ortho_GF2.ortho(file_path, target_dir_path, dem_name)
    elif satelite_type in ['SV-2', 'SV1-04', 'SV2-01', 'SV2-02']:
        ortho_SV.ortho(file_path, target_dir_path, dem_name)
    else:
        # 还需完善
        print('未知卫星类型')
        pass


def monitor_folder(folder_path, target_dir_path, dem_name):
    processed_files = set()

    while True:
        files = set(os.listdir(folder_path))

        # 获取新增的文件
        new_files = files - processed_files

        for file in new_files:
            file_path = os.path.join(folder_path, file)
            process_file(file_path, file, target_dir_path, dem_name)
            processed_files.add(file)
            time.sleep(1)  # 间隔时间
            print('等待下一个文件夹\n\n')


if __name__ == "__main__":

    # folder_to_monitor = r"../imput"
    # target_dir_path = r'../output'
    folder_to_monitor = r'monitor_dir'
    target_dir_path = r'target_dir'
    dem_name = r'DEM\GMTED2010.jp2'
    monitor_folder(folder_to_monitor, target_dir_path, dem_name)
