import json

def process_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    processed_lines = []
    for line in lines:
        data = json.loads(line)
        
        # 判断td_acc
        if data['td_pred'] not in ['real', 'fake']:
            data['td_acc'] = 2
        elif (data['label'] == 'real' and data['td_pred'] == 'real') or \
             (data['label'] == 'fake' and data['td_pred'] == 'fake'):
            data['td_acc'] = 1
        else:
            data['td_acc'] = 0
            
        # 判断cs_acc
        if data['cs_pred'] not in ['real', 'fake']:
            data['cs_acc'] = 2
        elif (data['label'] == 'real' and data['cs_pred'] == 'real') or \
             (data['label'] == 'fake' and data['cs_pred'] == 'fake'):
            data['cs_acc'] = 1
        else:
            data['cs_acc'] = 0
            
        processed_lines.append(json.dumps(data, ensure_ascii=False) + '\n')
    
    # 写回文件
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(processed_lines)

if __name__ == '__main__':
    # 处理文件
    file_path = r'c:\Users\wp\Desktop\1\CHECKED-master\dataset\processed\combined_processed.jsonl'
    process_file(file_path)