import json
import os
from datetime import datetime
from tqdm import tqdm

# 读取标签文件
def read_labels(label_file):
    labels = {}
    with open(label_file, 'r', encoding='utf-8') as f:
        for line in f:
            # 按照 eid:xxxxx label:x 格式分割
            parts = line.strip().split('\t')
            event_id = parts[0].split(':')[1]
            label = parts[1].split(':')[1]
            # 将1转换为"fake"，0转换为"real"
            labels[event_id] = "fake" if label == "1" else "real"
    return labels

# 处理单个JSON文件
def process_json_file(file_path, event_id, label):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if data and len(data) > 0:
                first_post = data[0]
                content = first_post.get('original_text', '')
                
                # 检查文本长度是否大于100
                if len(content) < 100:
                    return None
                
                # 生成唯一的source_id (整数类型)
                source_id = abs(hash(content))
                
                # 将Unix时间戳转换为datetime格式
                timestamp = first_post.get('user_created_at', '')
                formatted_time = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S') if timestamp else ''
                
                return {
                    "content": content,
                    "label": label,
                    "time": formatted_time,
                    "source_id": source_id,
                    "td_rationale": "",
                    "td_pred": "",
                    "td_acc": "",
                    "cs_rationale": "",
                    "cs_pred": "",
                    "cs_acc": "",
                    "split": ""
                }
    except Exception as e:
        print(f"Error processing file {file_path}: {str(e)}")
    return None

def main():
    # 路径设置
    weibo_dir = r"C:\Users\wp\Downloads\rumdect\Weibo"
    label_file = r"C:\Users\wp\Downloads\rumdect\Weibo.txt"
    output_file = r"C:\Users\wp\Desktop\1\CHECKED-master\dataset\rundect\combined.json"
    
    # 创建输出目录
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # 读取标签
    labels = read_labels(label_file)
    
    # 处理所有JSON文件
    results = []
    for event_id in tqdm(labels, desc="Processing files"):
        json_file = os.path.join(weibo_dir, f"{event_id}.json")
        if os.path.exists(json_file):
            result = process_json_file(json_file, event_id, labels[event_id])
            if result is not None:  # 只添加非None的结果
                results.append(result)
    
    # 保存结果
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()