import os
import json
from datetime import datetime

def process_weibo_file(file_path, is_rumor=True):
    results = []
    seen_ids = set()
    
    image_base_path = r"C:\Users\wp\Downloads\weibo_dataset\rumor_images" if is_rumor else r"C:\Users\wp\Downloads\weibo_dataset\nonrumor_images"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
        for i in range(0, len(lines), 3):
            if i + 2 >= len(lines):
                break
                
            meta_line = lines[i].strip()
            image_line = lines[i + 1].strip()  # 图片URL行
            content = lines[i + 2].strip()
            
            # 从图片URL中提取图片名称，并去除最后的"|null"
            image_urls = image_line.split('|')
            image_urls = [url for url in image_urls if url != 'null']  # 移除'null'
            
            # 尝试找到第一张存在的图片
            image_path = ""
            for url in image_urls:
                image_name = url.split('/')[-1]
                temp_image_path = os.path.join(image_base_path, image_name)
                if os.path.exists(temp_image_path):
                    image_path = temp_image_path
                    break
            
            # 如果所有图片都不存在，跳过这条数据
            if not image_path:
                print(f"警告：所有图片都不存在，跳过数据: {image_line[:100]}...")
                continue
            
            # 解析元数据行
            meta_info = meta_line.split('|')
            if len(meta_info) < 5:
                print(f"警告：元数据格式不正确: {meta_line[:100]}...")
                continue
                
            try:
                source_id = int(meta_info[0])
                post_time = meta_info[4]
                
                if source_id in seen_ids:
                    print(f"警告：发现重复的source_id: {source_id} 在文件 {file_path}")
                else:
                    seen_ids.add(source_id)
                    if len(content) >= 50:
                        result = {
                            "content": content,
                            "label": "fake" if is_rumor else "real",
                            "time": post_time,
                            "source_id": source_id,
                            "image_path": image_path,  # 添加图片路径
                            "image_description": "No image description available",  # 将来可以替换为实际的图片描述
                            "image_text_relevance": "none",
                            "td_rationale": "",
                            "td_pred": "",
                            "td_acc": "",
                            "cs_rationale": "",
                            "cs_pred": "",
                            "cs_acc": "",
                            "split": ""
                        }
                        results.append(result)
                        
            except ValueError:
                print(f"警告：无法解析source_id，跳过数据: {meta_line[:100]}...")
    
    return results

def process_weibo_mrml_dataset(original_dataset_dir, output_file):
    all_results = []
    global_seen_ids = set()  # 用于全局检查source_id唯一性

    # 处理所有文件
    all_files = [('train_rumor.txt', True), ('test_rumor.txt', True),
                 ('train_nonrumor.txt', False), ('test_nonrumor.txt', False)]
    
    all_results = []
    global_seen_ids = set()  # 用于全局检查source_id唯一性
    
    # 处理所有文件
    all_files = [('train_rumor.txt', True), ('test_rumor.txt', True),
                 ('train_nonrumor.txt', False), ('test_nonrumor.txt', False)]
    
    for file_name, is_rumor in all_files:
        file_path = os.path.join(original_dataset_dir, file_name)
        if os.path.exists(file_path):
            results = process_weibo_file(file_path, is_rumor)
            
            # 检查全局唯一性
            for result in results:
                if result['source_id'] in global_seen_ids:
                    print(f"警告：在不同文件间发现重复的source_id: {result['source_id']}")
                else:
                    global_seen_ids.add(result['source_id'])
                    all_results.append(result)
    
    print(f"总共处理了 {len(all_results)} 条数据")
    print(f"唯一source_id数量: {len(global_seen_ids)}")
    
    # 保存结果
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
        # 原始数据集目录，可根据实际情况修改 需要修改 todo
    original_dataset_dir = r"C:\Users\wp\Downloads\weibo_dataset\tweets"
    output_file = r"C:\Users\wp\Desktop\1\CHECKED-master\dataset\MRML\combined.json"
    process_weibo_mrml_dataset(original_dataset_dir, output_file)