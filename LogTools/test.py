import os
import re
from datetime import datetime
import LlmTools


class LogProcessor:
    def __init__(self, log_directory, output_directory, start_time, end_time, special_logs, slice_size_limit=32*1024, token_limit=4096):
        """
        初始化日志处理器
        :param log_directory: 日志文件所在的目录
        :param output_directory: 切片文件输出的目录
        :param start_time: 开始时间（格式："03-01 12:00:00.000"）
        :param end_time: 结束时间（格式："03-01 13:00:00.000"）
        :param special_logs: 特定日志的正则表达式列表
        :param slice_size_limit: 切片文件的大小限制（默认32KB）
        :param token_limit: 语言模型的token限制（默认4096）
        """
        self.log_directory = log_directory
        self.output_directory = output_directory
        self.start_time = datetime.strptime(start_time, "%m-%d %H:%M:%S.%f")
        self.end_time = datetime.strptime(end_time, "%m-%d %H:%M:%S.%f")
        self.special_logs = special_logs
        self.slice_size_limit = slice_size_limit
        self.token_limit = token_limit
        self.slice_file_count = 0
        self.slice_size = 0
        self.current_slice_file = os.path.join(self.output_directory, f"slice_{self.slice_file_count}.log")
        self.history_slice_file = []
        self.llm_client = LlmTools.LlmTools()
        self.tools = [
            # 工具1 获取当前时刻的时间
            {
                "type": "function",
                "function": {
                    "name": "get_current_time",
                    "description": "当你想知道现在的时间时非常有用。",
                    # 因为获取当前时间无需输入参数，因此parameters为空字典
                    "parameters": {}
                }
            },
            # 工具2 获取指定城市的天气
            {
                "type": "function",
                "function": {
                    "name": "get_current_weather",
                    "description": "当你想查询指定城市的天气时非常有用。",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            # 查询天气时需要提供位置，因此参数设置为location
                            "location": {
                                "type": "string",
                                "description": "城市或县区，比如北京市、杭州市、余杭区等。"
                            }
                        }
                    },
                    "required": [
                        "location"
                    ]
                }
            }
        ]

    def match_files(self):
        """匹配目录中所有名字含有system.log的文件"""
        pattern = re.compile(r".*system\.log.*")
        matched_files = []
        for root, _, files in os.walk(self.log_directory):
            for file in files:
                if pattern.match(file):
                    matched_files.append(os.path.join(root, file))
        return matched_files

    def parse_log_line(self, line):
        """
        解析安卓日志格式的日志行，提取时间戳、进程号、线程号、日志级别、标签和日志内容。
        安卓日志格式示例：
        03-01 12:12:46.399 12345 12345 I System.out: This is a log message.
        """
        log_pattern = re.compile(
            r"(\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3})\s+"  # 时间戳
            r"(\d+)\s+"  # 进程号 (PID)
            r"(\d+)\s+"  # 线程号 (TID)
            r"([DIWVE])\s+"  # 日志级别 (D, I, W, V, E)
            r"([\w\.]+):\s+"  # 标签 (Tag)
            r"(.*)"  # 日志内容
        )
        match = log_pattern.match(line)
        if match:
            timestamp_str, pid, tid, log_level, tag, log_content = match.groups()
            timestamp = datetime.strptime(timestamp_str, "%m-%d %H:%M:%S.%f")
            return {
                "timestamp": timestamp,
                "pid": int(pid),
                "tid": int(tid),
                "log_level": log_level,
                "tag": tag,
                "content": log_content,
                "text": line,
            }
        return None

    def is_log_valid(self, log_entry):
        """
        检查日志是否满足时间戳和特定日志的要求。
        :param log_entry: 解析后的日志条目（字典形式）
        """
        if not log_entry:
            return False
        timestamp = log_entry["timestamp"]
        log_content = log_entry["content"]
        if self.start_time <= timestamp <= self.end_time:
            for log_pattern in self.special_logs:
                if re.search(log_pattern, log_content):
                    return True
        return False

    def save_to_slice_file(self, log):
        """将日志保存到切片文件中，并返回新的切片文件大小"""
        with open(self.current_slice_file, "a") as f:
            f.write(log + "\n")
        self.slice_size += len(log.encode("utf-8"))
        self.history_slice_file.append(self.current_slice_file)
        if self.slice_size >= self.slice_size_limit:
            self.slice_file_count += 1
            self.slice_size = 0
            self.current_slice_file = os.path.join(self.output_directory, f"slice_{self.slice_file_count}.log")

    def ask_language_model(self, log_str):
        """向语言模型提问"""
        # 这里有一个语言模型的API可以调用
        result = self.llm_client.query_from_llm(log_str, self.tools, "qwen")
        print(result)
        return result

    def process_logs(self):
        """处理日志文件"""
        matched_files = self.match_files()
        result = ""
        message = "分析下面这段日志有无丢日志问题"
        for file in matched_files:
            with open(file, "r") as f:
                for line in f:
                    log_entry = self.parse_log_line(line)
                    if log_entry and self.is_log_valid(log_entry):
                        # 将日志内容保存到切片文件
                        self.save_to_slice_file(line.strip())
                        # 向语言模型提问
                        # response = self.ask_language_model(log_entry["content"])
                        # if response == "Token limit exceeded":
                        #     # 处理token过长的情况
                        #     # 这里可以将日志字符串切片后再提问
                        #     pass
        for file in self.history_slice_file:
            with open(file, "r") as f:
                for line in f:
                    message = message + line
                    if len(message) >= 16*1024:
                        response = self.ask_language_model(log_entry["content"])
                        result = result + response
                        message = "分析下面这段日志有无丢日志问题"
        if len(message) > len("分析下面这段日志有无丢日志问题"):
            print(message)
            response = self.ask_language_model(log_entry["content"])
            result = result + response
        return result

if __name__ == "__main__":
    # 配置参数
    log_directory = "D:\workspace\gitlab-tools\LogTools"  # 日志文件所在的目录
    output_directory = "D:\workspace\gitlab-tools\LogTools"  # 切片文件输出的目录
    start_time = "03-01 12:00:00.000"  # 开始时间
    end_time = "03-01 13:00:00.000"  # 结束时间
    #special_logs = [r"error", r"warning", r"critical"]  # 特定日志的正则表达式列表

    pattern_list = {
        'log_lost': {'special_logs': [r"error", r"warning", r"critical"]},
        'log_roll': {'special_logs': [r"error", r"warning", r"critical"]},
    }

    # 创建LogProcessor实例并处理日志
    log_processor = LogProcessor(log_directory, output_directory, start_time, end_time, pattern_list['log_lost']['special_logs'])
    log_processor.process_logs()