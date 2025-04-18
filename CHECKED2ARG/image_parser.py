from pydantic import BaseModel, Field
import os
import base64
from typing import Optional
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from PIL import Image
import io


class ImageDescription(BaseModel):
    """图片描述模型类"""
    image_description: str = Field(
        description="图片中可见的具体内容描述",
        min_length=10,
        example="图片展示了一只橘色的猫咪正在窗台上晒太阳..."
    )

    class Config:
        """模型配置类"""
        json_schema_extra = {
            "example": {
                "image_description": "图片展示了一只橘色的猫咪正在窗台上晒太阳",
            }
        }


class ImageAnalyzer:
    """图片分析器类"""
    def __init__(self, model_config: Optional[dict] = None) -> None:
        """
        初始化图片分析器
        Args:
            model_config: 模型配置字典
        """
        if model_config is None:
            model_config = {
                'model': os.getenv('LVM_MODEL_NAME'),  # QwenVL 
                'base_url': os.getenv('BASE_URL'),
                'api_key': os.getenv('API_KEY'),
                'temperature': 0.0,
            }
        self.model = ChatOpenAI(**model_config)
        self.parser = PydanticOutputParser(pydantic_object=ImageDescription)
        # 获取格式说明并存储为实例变量
        self.format_instructions = self.parser.get_format_instructions()

    def _encode_image(self, image_path: str) -> str:
        with Image.open(image_path) as img:
            # 确保图片是 RGB 模式
            if img.mode not in ('RGB', 'L'):
                img = img.convert('RGB')
            
            # 设置最大尺寸
            max_size = 800
            ratio = min(max_size/img.width, max_size/img.height)
            if ratio < 1:
                new_size = (int(img.width * ratio), int(img.height * ratio))
                img = img.resize(new_size, Image.Resampling.LANCZOS)
            
            # 转换为bytes
            buffer = io.BytesIO()
            # 强制使用 JPEG 格式保存 RGB 图片
            img = img.convert('RGB')  # 确保在保存前转换为 RGB
            img.save(buffer, format='JPEG', quality=85)
            return base64.b64encode(buffer.getvalue()).decode('utf-8')

    def _verify_image_data(self, image_base64: str) -> bool:
        """
        验证base64编码的图片数据
        Args:
            image_base64: base64编码的图片数据
        Returns:
            验证是否成功
        """
        try:
            base64.b64decode(image_base64)
            return True
        except Exception as e:
            print(f"Base64 编码验证失败: {e}")
            return False
    
    def analyze(self, image_path: str, text: str = None) -> str:
        base64_image = self._encode_image(image_path)
        image_data_uri = f"data:image/png;base64,{base64_image}"
        
        system_message = {
            "role": "system", 
            "content": f"""请根据用户提供的图片和问题进行分析和回答。请确保：
1. 回答要客观准确，避免主观臆测
2. 使用专业且清晰的语言
3. 按照重要性顺序组织内容
4. 确保描述完整且连贯

{self.format_instructions}"""
        }
        user_message = {
            "role": "user",
            "content": [
                {"type": "text", "text": text if text else "请描述这张图片"},
                {"type": "image_url", "image_url": {"url": image_data_uri}}
            ]
        }
        
        messages = [system_message, user_message]
        output = self.model.invoke(messages)
        try:
            return self.parser.parse(output.content).image_description
        except Exception as e:
            print(f"解析失败: {e}")
            return output.content

if __name__ == "__main__":
    analyzer = ImageAnalyzer()
    result = analyzer.analyze(
        "C:\\Users\\wp\\Downloads\\weibo_dataset\\rumor_images\\a71ac854gw1dytin2zmk9j.jpg",
        "请描述这张图片"
    )
    print(result)