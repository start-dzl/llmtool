from pydantic import BaseModel, Field
import os
from typing import Optional
from langchain.output_parsers import PydanticOutputParser
from langchain_openai import ChatOpenAI
import base64
from PIL import Image
import io


class ContentCheckResult(BaseModel):
    """内容检查结果模型类"""
    result: str = Field(
        description="图片与文本内容相关性检查结果",
        example="real",
        pattern="^(real|fake)$"
    )
    explanation: str = Field(
        description="判断依据说明",
        min_length=10,
        example="图片内容与文本描述高度相符，展示了相同的场景和细节..."
    )

    class Config:
        """模型配置类"""
        json_schema_extra = {
            "example": {
                "result": "real",
                "explanation": "图片内容与文本描述完全吻合，展示了相同的场景和细节"
            }
        }


class ContentChecker:
    """内容检查器类"""
    def __init__(self, model_config: Optional[dict] = None) -> None:
        if model_config is None:
            model_config = {
                'model': os.getenv('LVM_MODEL_NAME'), # Qwen2-VL-7B QwenVL
                'base_url': os.getenv('BASE_URL'),
                'api_key': os.getenv('API_KEY'),
                'temperature': 0.0,
            }
        self.model = ChatOpenAI(**model_config)
        self.parser = PydanticOutputParser(pydantic_object=ContentCheckResult)
        self.format_instructions = self.parser.get_format_instructions()

    def _encode_image(self, image_path: str) -> str:
        with Image.open(image_path) as img:
            max_size = 800
            ratio = min(max_size/img.width, max_size/img.height)
            if ratio < 1:
                new_size = (int(img.width * ratio), int(img.height * ratio))
                img = img.resize(new_size, Image.Resampling.LANCZOS)
            
            buffer = io.BytesIO()
            img.save(buffer, format='JPEG', quality=85)
            return base64.b64encode(buffer.getvalue()).decode('utf-8')

    def check_content(self, image_path: str, text_content: str) -> tuple[str, str]:
        """
        检查图片与文本内容的相关性
        Args:
            image_path: 图片路径
            text_content: 文本内容
        Returns:
            tuple[str, str]: (检查结果('real'或'fake'), 解释说明)
        """
        try:
            base64_image = self._encode_image(image_path)
            image_data_uri = f"data:image/png;base64,{base64_image}"
            
            system_message = {
                "role": "system", 
                "content": f"""请分析图片与文本内容的相关性，判断是否匹配。请确保：
1. 仔细对比图片内容与文本描述的一致性
2. 关注关键细节的对应关系
3. 给出客观的判断依据
4. 返回"real"表示匹配，"fake"表示不匹配

{self.format_instructions}"""
            }
            
            user_message = {
                "role": "user",
                "content": [
                    {"type": "text", "text": f"请判断以下文本描述与图片是否相符：\n{text_content}"},
                    {"type": "image_url", "image_url": {"url": image_data_uri}}
                ]
            }
            
            messages = [system_message, user_message]
            output = self.model.invoke(messages)
            result = self.parser.parse(output.content)
            return result.result, result.explanation
            
        except Exception as e:
            print(f"内容检查过程出错: {str(e)}")
            return 'fake', f"检查过程发生错误: {str(e)}"


if __name__ == "__main__":
    checker = ContentChecker()
    result, explanation = checker.check_content(
        "C:\\Users\\wp\\Downloads\\weibo_dataset\\rumor_images\\a71ac854gw1dytin2zmk9j.jpg",
        "震惊，转发求证：【想都不敢想 ，在美国一桶金龙鱼食用油只要8元人民币】 一桶食用油相当于中国超市40多元(现在估计已经涨到五六十元了)的金龙鱼，在纽约沃尔玛感恩节时是1.6美元，圣诞节降至1.3美元。(折合人民币8.58元，而且油是绿色纯天然的，不是转基因的)，为什么中国一桶食用油要卖几十上百元？"
    )
    print(f"检查结果: {result}")
    print(f"解释说明: {explanation}")