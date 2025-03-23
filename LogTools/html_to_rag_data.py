import json
from bs4 import BeautifulSoup
import pandas as pd
import requests
import os
import re


def html_to_rag_data(html_file_path):
    try:
        # 读取 HTML 文件
        with open(html_file_path, 'r', encoding='utf-8') as file:
            html_content = file.read()

        # 解析 HTML 内容
        soup = BeautifulSoup(html_content, 'html.parser')

        # 创建保存图片的文件夹
        if not os.path.exists('images'):
            os.makedirs('images')

        # 提取文本并分段
        data = []
        current_section = {'prompt': None, 'content': []}
        for element in soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'img']):
            if element.name.startswith('h'):
                if current_section['prompt'] is not None:
                    data.append(current_section)
                    current_section = {'prompt': None, 'content': []}
                current_section['prompt'] = element.get_text().strip()
            elif element.name == 'p':
                current_section['content'].append(element.get_text().strip())
            elif element.name == 'img':
                img_src = element.get('src')
                if img_src:
                    # 处理相对路径
                    if not img_src.startswith('http'):
                        base_url = os.path.dirname(os.path.abspath(html_file_path))
                        img_src = os.path.join(base_url, img_src)
                    img_name = os.path.basename(img_src)
                    save_path = os.path.join('images', img_name)
                    download_image(img_src, save_path)
                    current_section['content'].append(f"[图片: {img_name}]")
        if current_section['prompt'] is not None:
            data.append(current_section)

        return data

    except FileNotFoundError:
        print("错误: HTML 文件未找到!")
    except Exception as e:
        print(f"错误: 发生了一个未知错误: {e}")
    return []


def download_image(img_url, save_path):
    try:
        response = requests.get(img_url)
        if response.status_code == 200:
            with open(save_path, 'wb') as file:
                file.write(response.content)
            print(f"图片下载成功: {save_path}")
        else:
            print(f"图片下载失败: {img_url}，状态码: {response.status_code}")
    except Exception as e:
        print(f"下载图片时出错: {e}")


def clean_filename(filename):
    # 移除非法字符
    return re.sub(r'[\\/*?:"<>|]', '', filename)


def save_rag_data_to_excel(rag_data, output_file_path):
    try:
        # 清理文件名
        output_file_path = os.path.join(os.path.dirname(output_file_path), clean_filename(os.path.basename(output_file_path)))
        df = pd.DataFrame(rag_data)
        df['content'] = df['content'].apply(lambda x: '\n'.join(x))
        df.to_excel(output_file_path, index=False)
        print(f"成功将 RAG 数据保存到 {output_file_path}")
    except Exception as e:
        print(f"保存文件时出错: {e}")


if __name__ == "__main__":
    html_file = 'D:RAG_mk_test.html'
    output_file = 'D:\ag_data.xlsx'
    rag_data = html_to_rag_data(html_file)
    if rag_data:
        save_rag_data_to_excel(rag_data, output_file)
