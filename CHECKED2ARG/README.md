# 配置说明文档

## 环境配置文件 (.env)

### 基础配置
| 配置项 | 说明 | 示例值 |
|--------|------|--------|
| `BASE_URL` | 服务器基础URL地址 | `http://localhost:8080` |
| `API_KEY` | API访问密钥 | `sk-xxxxxxxxxxxxx` |

### 模型配置
| 配置项 | 说明 | 示例值 |
|--------|------|--------|
| `LLM_MODEL_NAME` | 大语言模型名称 | `gpt-3.5-turbo` |
| `LVM_MODEL_NAME` | 视觉语言模型名称 | `clip-vit-base` |

> **注意**：请在项目根目录创建 `.env` 文件并填写以上配置项

## 主程序配置 (mrml-main.py)

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `base_path` | 项目输出目录路径 | `./output` |
| `original_dataset_dir` | 原始数据集目录路径 | `./dataset` |
| `train_ratio` | 训练集比例 | `0.5` |
| `val_ratio` | 验证集比例 | `0.25` |

