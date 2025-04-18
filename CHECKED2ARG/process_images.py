from dataclasses import dataclass
import json
import logging
from pathlib import Path
from tqdm import tqdm
from image_parser import ImageAnalyzer
import os
from typing import Dict, Any, Optional
from parser import RumourVerifier
from content_checker import ContentChecker
import concurrent.futures
from typing import Tuple

@dataclass
class Config:
    # 处理配置
    SAVE_INTERVAL: int = 10
    MAX_WORKERS: int = 3
    BATCH_SIZE: int = 100
    
    # 日志配置
    LOG_FILE: str = 'image_processing.log'
    LOG_FORMAT: str = '%(asctime)s - %(levelname)s - %(message)s'
    LOG_LEVEL: int = logging.INFO
    
    # 结果文件配置
    RESULT_SUFFIX: str = '_processed'
    ERROR_LOG_FILE: str = 'processing_errors.log'

def setup_logging(config: Config) -> None:
    logging.basicConfig(
        level=config.LOG_LEVEL,
        format=config.LOG_FORMAT,
        handlers=[
            logging.FileHandler(config.LOG_FILE),
            logging.StreamHandler()
        ]
    )

@dataclass
class ProcessingResult:
    image_description: str
    relevance_result: bool
    relevance_explanation: str
    cs_rationale: str
    cs_pred: bool
    td_rationale: str
    td_pred: bool

# 在文件顶部添加 logger 导入
import logging

# 配置 logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def process_single_item(args: Tuple[str, str, ImageAnalyzer, RumourVerifier, ContentChecker], 
                       config: Config) -> Optional[ProcessingResult]:
    image_path, content, analyzer, verifier, checker = args
    
    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=config.MAX_WORKERS) as executor:
            image_future = executor.submit(analyzer.analyze, image_path)
            verify_future = executor.submit(verifier.verify, content)
            relevance_future = executor.submit(checker.check_content, image_path, content)
            
            image_result = image_future.result()
            verify_result = verify_future.result()
            # 确保 verify_result 是单个对象而不是列表
            if isinstance(verify_result, list) and len(verify_result) > 0:
                verify_result = verify_result[0]
            relevance_result, explanation = relevance_future.result()
        
        return ProcessingResult(
            image_description=image_result,
            relevance_result=relevance_result,
            relevance_explanation=explanation,
            cs_rationale=verify_result.cs_rationale,
            cs_pred=verify_result.cs_pred,
            td_rationale=verify_result.td_rationale,
            td_pred=verify_result.td_pred
        )
    except Exception as e:
        logger.error(f"处理项目失败 {image_path}: {str(e)}", exc_info=True)
        return None

def process_dataset(json_path: str, config: Config = Config()) -> None:
    setup_logging(config)
    logger = logging.getLogger(__name__)
    error_logger = logging.getLogger('errors')
    error_logger.addHandler(logging.FileHandler(config.ERROR_LOG_FILE))
    
    try:
        save_path = str(Path(json_path).with_stem(Path(json_path).stem + config.RESULT_SUFFIX))
        processed_count = 0
        error_count = 0
        skipped_count = 0
        
        # 首先尝试读取已有的处理结果文件
        existing_data = {}
        if os.path.exists(save_path):
            with open(save_path, 'r', encoding='utf-8') as f:
                existing_results = json.load(f)
                for item in existing_results:
                    if 'image_path' in item and 'image_description' in item:
                        if item['image_description'] != "No image description available":
                            existing_data[item['image_path']] = item

        # 读取原始数据
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        analyzer = ImageAnalyzer()
        verifier = RumourVerifier()
        checker = ContentChecker()
        base_path = Path(json_path).parent
        
        for idx, item in enumerate(tqdm(data, desc="处理进度")):
            image_path = os.path.join(base_path, item['image_path']) if not os.path.isabs(item['image_path']) else item['image_path']
            
            # 检查是否已在处理结果中
            if item['image_path'] in existing_data:
                item.update(existing_data[item['image_path']])
                skipped_count += 1
                continue
                
            try:
                if not os.path.exists(image_path):
                    error_logger.warning(f"图片不存在: {image_path}")
                    error_count += 1
                    continue
                
                result = process_single_item((image_path, item['content'], analyzer, verifier, checker), config)
                
                if result:
                    item.update({
                        'image_description': result.image_description,
                        'image_text_relevance': result.relevance_result,
                        'relevance_explanation': result.relevance_explanation,
                        'cs_rationale': result.cs_rationale,
                        'cs_pred': result.cs_pred,
                        'td_rationale': result.td_rationale,
                        'td_pred': result.td_pred
                    })
                    processed_count += 1
                else:
                    error_count += 1
                
                if (idx + 1) % config.SAVE_INTERVAL == 0:
                    save_json(save_path, data)
                    logger.info(f"进度: {idx + 1}/{len(data)} ({processed_count} 成功, {error_count} 失败)")
                
            except Exception as e:
                error_logger.error(f"处理失败 {image_path}: {str(e)}", exc_info=True)
                error_count += 1
                continue
        
        save_json(save_path, data)
        logger.info(f"处理完成: 总计 {len(data)}, 成功 {processed_count}, 失败 {error_count}, 跳过 {skipped_count}")
        logger.info(f"结果已保存到 {save_path}")
        
    except Exception as e:
        logger.error(f"处理数据集失败: {str(e)}", exc_info=True)

def save_json(file_path: str, data: list[Dict[str, Any]]) -> None:
    """
    保存 JSON 文件
    Args:
        file_path: 文件路径
        data: 要保存的数据
    """
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"保存文件时出错: {str(e)}")

if __name__ == "__main__":
    config = Config()
    json_path = r"C:\Users\wp\Desktop\1\CHECKED-master\dataset\MRML\combined.json"
    process_dataset(json_path, config)