class LlmTools:
    def __init__(self):
        """
        向语言模型请求
        :param messages: 请求的消息
        :param tools: 工具调用
        :param type: 语言模型类型
        """
        self.init_tag = False
        self.client = None

    def init_llm(self, type):
        if self.init_tag == True:
            return True
        # self.client = OpenAI(
        #     api_key=os.getenv("DASHSCOPE_API_KEY"),
        #     base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        # )

    def query_from_llm(self, messages, tools, type):
        return "SUCCESS"
        if self.init_llm(type) is False:
            return None
        if type == "qwen":
            completion = self.client.chat.completions.create(model="qwen-plus", messages=messages, tools=tools)
            return completion.model_dump()