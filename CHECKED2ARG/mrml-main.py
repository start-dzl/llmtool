import process_dataset_mrml
import process_images
import accuracy_calculator
import jsonl_to_json
import json
import split_jsonl_dataset

def convert_time_format(input_file):
    """
    转换jsonl文件中time字段的格式
    :param input_file: 输入jsonl文件路径
    :param output_file: 输出jsonl文件路径
    """
    from datetime import datetime
    
    converted_data = []
    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            data = json.loads(line)
            if 'time' in data:
                time_str = data['time']
                try:
                    # 如果是时间戳格式
                    dt = datetime.fromtimestamp(int(time_str) / 1000)
                except ValueError:
                    # 如果已经是日期时间格式，则解析它
                    try:
                        dt = datetime.strptime(time_str, '%Y-%m-%d %H:%M')
                    except ValueError:
                        # 如果格式不匹配，保持原样
                        dt = None
                
                if dt:
                    # 转换为指定格式的字符串
                    data['time'] = dt.strftime('%Y-%m-%d %H:%M:%S')
            converted_data.append(data)
    
    # 写入新文件
    with open(input_file, 'w', encoding='utf-8') as f:
        for data in converted_data:
            f.write(json.dumps(data, ensure_ascii=False) + '\n')

if __name__ == '__main__':
    # 配置文件路径和参数
    base_path = r"C:\Users\wp\Desktop\1\CHECKED-master\dataset\MRML"
    original_dataset_dir = r"C:\Users\wp\Downloads\weibo_dataset\tweets"
    # 数据集划分比例配置
    train_ratio = 0.5
    val_ratio = 0.25

    # 处理数据集
    process_dataset_mrml.process_weibo_mrml_dataset(original_dataset_dir=original_dataset_dir, output_file=base_path + r"\combined.json")

    # 多模态处理图片数据 大语言模型生成逻辑判断和尝试判断
    process_images_config = process_images.Config()
    process_images.process_dataset(base_path + r"\combined_processed.json", process_images_config)
    # 将json转换为jsonl
    jsonl_to_json.json_to_jsonl(base_path + r"\combined_processed.json", base_path + r"\combined_processed.jsonl")

    # 计算逻辑判断和常识预测是否正确
    accuracy_calculator.process_file(base_path + r"\combined_processed.jsonl")

    # time_id 从时间戳转换为日期时间格式
    convert_time_format(base_path + r"\combined_processed.jsonl")

    # 拆分数据集
    split_jsonl_dataset.split_jsonl_dataset(base_path + r"\combined_processed.jsonl", base_path, train_ratio, val_ratio)

    # 将jsonl转换为json
    jsonl_to_json.jsonl_to_json(base_path + r"\train.jsonl", base_path + r"\train.json")
    jsonl_to_json.jsonl_to_json(base_path + r"\val.jsonl", base_path + r"\val.json")
    jsonl_to_json.jsonl_to_json(base_path + r"\test.jsonl", base_path + r"\test.json")
    


    



    