import os
import json
import random

def split_jsonl_dataset(input_file, output_dir, train_ratio=0.5, val_ratio=0.25):
    # 读取jsonl文件
    data = []
    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            data.append(json.loads(line))
    
    # 按标签分组
    real_data = [item for item in data if item['label'] == 'real']
    fake_data = [item for item in data if item['label'] == 'fake']
    
    # 分别打乱两组数据
    random.shuffle(real_data)
    random.shuffle(fake_data)
    
    # 计算分割点
    real_total = len(real_data)
    fake_total = len(fake_data)
    
    real_train_end = int(real_total * train_ratio)
    real_val_end = real_train_end + int(real_total * val_ratio)
    
    fake_train_end = int(fake_total * train_ratio)
    fake_val_end = fake_train_end + int(fake_total * val_ratio)
    
    # 合并数据集
    train_data = real_data[:real_train_end] + fake_data[:fake_train_end]
    val_data = real_data[real_train_end:real_val_end] + fake_data[fake_train_end:fake_val_end]
    test_data = real_data[real_val_end:] + fake_data[fake_val_end:]
    
    # 打乱最终数据集
    random.shuffle(train_data)
    random.shuffle(val_data)
    random.shuffle(test_data)
    
    # 写入数据集
    for split_name, split_data in [
        ('train', train_data),
        ('val', val_data),
        ('test', test_data)
    ]:
        output_file = os.path.join(output_dir, f'{split_name}.jsonl')
        with open(output_file, 'w', encoding='utf-8') as f:
            for item in split_data:
                f.write(json.dumps(item, ensure_ascii=False) + '\n')

def main():
    input_file = r'C:\Users\wp\Desktop\1\CHECKED-master\dataset\processed\combined_processed.jsonl'
    output_dir = os.path.dirname(input_file)
    
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    # 执行数据集划分
    split_jsonl_dataset(input_file, output_dir)

if __name__ == "__main__":
    main()