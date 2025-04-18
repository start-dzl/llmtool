import json
import hashlib
import shutil
import os

def hash_to_int(text):
    """将文本转换为唯一的正整数"""
    hash_object = hashlib.md5(text.encode())
    # 取哈希值的前16位转为整数
    return abs(int(hash_object.hexdigest()[:16], 16))

def process_file(input_file):
    # 创建备份文件
    backup_file = input_file + '.backup'
    shutil.copy2(input_file, backup_file)
    
    # 创建临时文件
    temp_file = input_file + '.temp'
    
    try:
        # 处理文件
        with open(input_file, 'r', encoding='utf-8') as f_in, \
             open(temp_file, 'w', encoding='utf-8') as f_out:
            for line in f_in:
                data = json.loads(line)
                data['source_id'] = hash_to_int(data['source_id'])
                f_out.write(json.dumps(data, ensure_ascii=False) + '\n')
        
        # 用临时文件替换原文件
        os.replace(temp_file, input_file)
        
    except Exception as e:
        # 发生错误时恢复备份
        if os.path.exists(temp_file):
            os.remove(temp_file)
        shutil.copy2(backup_file, input_file)
        raise e
    finally:
        # 清理备份文件
        if os.path.exists(backup_file):
            os.remove(backup_file)

if __name__ == '__main__':
    # 输入文件路径
    input_file = r'c:\Users\wp\Desktop\1\CHECKED-master\dataset\processed\combined_processed.jsonl'
    process_file(input_file)