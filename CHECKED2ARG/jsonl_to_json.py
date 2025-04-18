import json

def jsonl_to_json(input_file, output_file):
    data = []
    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            data.append(json.loads(line.strip()))
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def json_to_jsonl(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    with open(output_file, 'w', encoding='utf-8') as f:
        for item in data:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')

if __name__ == '__main__':        
    # 转换文件
    base_path = 'c:/Users/wp/Desktop/1/CHECKED-master/dataset/processed'

    # 转换测试集
    jsonl_to_json(f'{base_path}/test.jsonl', f'{base_path}/test.json')

    # 转换训练集
    jsonl_to_json(f'{base_path}/train.jsonl', f'{base_path}/train.json')

    # 转换验证集
    jsonl_to_json(f'{base_path}/val.jsonl', f'{base_path}/val.json')

    print("转换完成！")