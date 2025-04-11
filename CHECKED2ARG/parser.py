from pydantic import BaseModel, Field
import os
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import PromptTemplate
from langchain_community.chat_models import ChatOpenAI  # 更新导入路径

class RumourVerification(BaseModel):
    cs_rationale: str = Field(
        description="基于特定视角提示（常识）的 LLM 推理过程",
        min_length=10,
        example="从常识角度看，这个说法与已知的科学事实相矛盾..."
    )
    cs_pred: str = Field(
        description="cs_rationale 的预测结果（real/fake）",
        pattern="^(real|fake)$",
        example="fake"
    )
    lg_rationale: str = Field(
        description="基于特定视角提示（逻辑）的 LLM 推理过程",
        min_length=10, 
        example="从逻辑角度看，这个说法存在时间线上的矛盾..."
    )
    lg_pred: str = Field(
        description="lg_rationale 的预测结果（real/fake）",
        pattern="^(real|fake)$",
        example="real"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "cs_rationale": "从常识角度看...",
                "cs_pred": "fake",
                "lg_rationale": "从逻辑角度看...",
                "lg_pred": "real"
            }
        }

class RumourVerifier:
    def __init__(self, model_config=None):
        if model_config is None:
            model_config = {
                'model': os.getenv('MODEL_NAME', 'TianQing-72B'),
                'base_url': os.getenv('BASE_URL'),
                'api_key': os.getenv('API_KEY'),
                'temperature': 0.0,
                'openai_api_key': os.getenv('OPENAI_API_KEY')  # 添加 OpenAI API key
            }
        self.model = ChatOpenAI(**model_config)
        self.parser = PydanticOutputParser(pydantic_object=RumourVerification)
    
    def get_prompt(self, content: str) -> str:
        template = """<Identity>
你是一个专业的谣言识别助手，擅长从多个维度分析和验证信息的真实性。
</Identity>

<Instructions>
分析以下内容是否为谣言:
{content}

请从以下两个维度进行分析：
1. 逻辑视角(logical)：分析信息的内在逻辑性和合理性
2. 常识视角(common-sense)：基于日常常识和基本认知进行判断
</Instructions>

<Reminder>
- 请确保每个维度的分析都详细且有理有据
- 分析结果需要清晰地指出是real还是fake
</Reminder>

<Example>
分析格式示例：
- 从逻辑角度：[详细的逻辑分析过程]，因此判断为[real/fake]
- 从常识角度：[详细的常识分析过程]，因此判断为[real/fake]
</Example>

{format_instructions}
"""
        
        prompt = PromptTemplate(
            template=template,
            input_variables=["content"],
            partial_variables={"format_instructions": self.parser.get_format_instructions()}
        )
        
        return prompt.format(content=content)
    
    def verify(self, content: str) -> RumourVerification:
        prompt = self.get_prompt(content)
        output = self.model.predict(prompt)
        return self.parser.parse(output)