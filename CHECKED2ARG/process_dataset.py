import os
import json
from datetime import datetime

def process_dataset(input_dir, output_file, label):
    outputs = []
    total_files = len([f for f in os.listdir(input_dir) if f.endswith('.json')])
    processed = 0
    
    for filename in os.listdir(input_dir):
        if filename.endswith('.json'):
            filepath = os.path.join(input_dir, filename)
            max_retries = 3
            retry_count = 0
            
            while retry_count < max_retries:
                try:
                    with open(filepath, 'r', encoding='utf-8') as f_in:
                        data = json.load(f_in)
                        
                        # 转换时间格式为YYYY-MM-DD HH:MM:SS
                        try:
                            time_obj = datetime.strptime(data['date'], "%Y-%m-%d %H:%M")
                            formatted_time = time_obj.strftime("%Y-%m-%d %H:%M:%S")
                        except:
                            formatted_time = data['date']
                        
                        output = {
                            "content": data['text'],
                            "label": label,
                            "time": formatted_time,
                            "source_id": data['id'],
                            "td_rationale": "",
                            "td_pred": "",
                            "td_acc": "",
                            "cs_rationale": "",
                            "cs_pred": "",
                            "cs_acc": "",
                            "split": ""
                        }
                        outputs.append(output)
                        processed += 1
                        print(f"\r处理进度: {processed}/{total_files} ({(processed/total_files*100):.1f}%)", end="")
                        break
                        
                except (json.JSONDecodeError, IOError) as e:
                    retry_count += 1
                    if retry_count == max_retries:
                        print(f"\n处理文件 {filename} 失败: {str(e)}")
                    else:
                        print(f"\n重试处理文件 {filename} (第 {retry_count} 次)")
                        import time
                        time.sleep(1)  # 重试前等待1秒
    
    print("\n所有文件处理完成")
    # 将结果写入json文件
    with open(output_file.replace('.jsonl', '.json'), 'w', encoding='utf-8') as f_out:
        json.dump(outputs, f_out, ensure_ascii=False, indent=4)

def main():
    base_dir = r"c:\Users\wp\Desktop\1\CHECKED-master\dataset"
    output_dir = os.path.join(base_dir, "processed")
    
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    
    # 处理真实新闻
    real_news_dir = os.path.join(base_dir, "real_news")
    real_output = os.path.join(output_dir, "real_news.json")
    process_dataset(real_news_dir, real_output, "real")
    
    # 处理假新闻
    fake_news_dir = os.path.join(base_dir, "fake_news")
    fake_output = os.path.join(output_dir, "fake_news.json")
    process_dataset(fake_news_dir, fake_output, "fake")
    
    # 合并数据集
    combined_output = os.path.join(output_dir, "combined.json")
    combined_data = []
    for f in [real_output, fake_output]:
        with open(f, 'r', encoding='utf-8') as f_in:
            combined_data.extend(json.load(f_in))
    
    # 写入合并后的数据
    with open(combined_output, 'w', encoding='utf-8') as f_out:
        json.dump(combined_data, f_out, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()