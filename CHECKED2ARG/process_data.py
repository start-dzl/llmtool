import json
from parser import RumourVerifier
import os
from tqdm import tqdm
from dotenv import load_dotenv

def process_combined_data():
    load_dotenv()
    verifier = RumourVerifier()
    
    output_file = 'c:/Users/wp/Desktop/1/CHECKED-master/dataset/processed/combined_processed.jsonl'
    
    # 读取数据
    with open('c:/Users/wp/Desktop/1/CHECKED-master/dataset/processed/combined.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 处理每条数据并实时保存
    with open(output_file, 'w', encoding='utf-8') as f_out:
        for item in tqdm(data, desc='处理数据进度'):
            if not item['cs_rationale'] and not item['td_rationale']:
                try:
                    result = verifier.verify(item['content'])
                    
                    # 更新数据
                    item['td_rationale'] = result.cs_rationale
                    item['td_pred'] = result.cs_pred
                    item['cs_rationale'] = result.lg_rationale
                    item['cs_pred'] = result.lg_pred
                    
                except Exception as e:
                    print(f"处理内容时出错: {e}")
            
            # 每处理完一条数据就写入文件
            f_out.write(json.dumps(item, ensure_ascii=False) + '\n')
            f_out.flush()  # 确保立即写入磁盘

if __name__ == "__main__":
    process_combined_data()