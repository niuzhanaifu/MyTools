import html2text

def html_to_markdown(html_file_path, markdown_file_path):
    try:
        with open(html_file_path, 'r', encoding='utf-8') as file:
            html_content = file.read()
        h = html2text.HTML2Text()
        # 可以根据需要调整配置
        h.ignore_links = False
        h.ignore_images = False
        markdown_content = h.handle(html_content)
        with open(markdown_file_path, 'w', encoding='utf-8') as file:
            file.write(markdown_content)
        print(f"成功将 {html_file_path} 转换为 {markdown_file_path}")
    except FileNotFoundError:
        print("错误: HTML 文件未找到!")
    except Exception as e:
        print(f"错误: 发生了一个未知错误: {e}")

if __name__ == "__main__":
    html_file = 'D:\项目资料\工作时学习资料\日志解析\RAG_mk_test.html'
    markdown_file = 'D:\项目资料\工作时学习资料\日志解析\output1.md'
    html_to_markdown(html_file, markdown_file)