# src/pydantic_sample/main.py
import importlib.util
import inspect
import json
import os
from pathlib import Path
from pydantic import BaseModel

def get_default_prompts():
    """返回默认提示信息"""
    return {
        "welcome": "--- Pydantic Model to JSON Schema Generator ---",
        "loading_msg": "正在从 'model.py' 加载模型...",
        "no_models_warning": "警告: 在 'model.py' 中未找到任何带有 '_is_pydantic_model_' 标记的 Pydantic 模型。",
        "found_models_msg": "已找到 {count} 个模型: {list}",
        "select_prompt": "请选择要生成 Schema 的模型 (输入编号，逗号分隔)，输入 'all' 选择全部: ",
        "no_selection_msg": "没有选择任何模型，退出。",
        "generating_msg": "正在生成 {name} 的 Schema...",
        "output_file_msg": "Schema 将同时输出到控制台和文件 '{filename}'",
        "console_header": "--- JSON Schemas (Console Output) ---",
        "console_model_header": "\n--- Schema for '{name}' ---",
        "default_output_file": "generated_schemas.json",
        "default_output_file_json_data": "generated_data.json",
        "input_cancel_msg": "操作被取消。",
        "file_not_found_error": "错误: 找不到模型文件 'model.py'",
        "invalid_input_format": "输入格式错误，请输入数字，用逗号分隔，或输入 'all'。",
        "invalid_number_format": "输入格式错误，请输入数字或 'all'。",
    }


def load_models_from_file():
    """
    从同级目录下的 model.py 文件中加载所有带有 _is_pydantic_model_ 标记的 Pydantic 模型。
    """
    model_file_path = Path(__file__).parent / "model.py" # 指向同目录下的 model.py
    if not model_file_path.exists():
        raise FileNotFoundError(f"模型文件不存在: {model_file_path}")

    spec = importlib.util.spec_from_file_location("model", model_file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    models = {}
    for name, obj in inspect.getmembers(module):
        if (inspect.isclass(obj) and 
            issubclass(obj, BaseModel) and 
            obj is not BaseModel and
            hasattr(obj, '_is_pydantic_model_') and
            obj._is_pydantic_model_):
            models[name] = obj
    return models

def get_user_selection(choices_dict: dict, prompt: str, prompts: dict):
    """
    让用户选择模型，支持 'all' 输入。
    """
    print(prompt)
    for i, (key, value) in enumerate(choices_dict.items(), 1):
        print(f"{i}. {key} ({value.__name__})")

    selected_keys = []
    while True:
        try:
            choice_input = input("\n请输入选择项的编号 (用逗号分隔，或输入 'all' 选择全部): ").strip().lower()
            
            if choice_input == 'all':
                selected_keys = list(choices_dict.keys())
                break
            elif not choice_input:
                print(prompts["no_selection_msg"])
                return []
            else:
                indices = [int(x.strip()) for x in choice_input.split(',')]
                for idx in indices:
                    if 1 <= idx <= len(choices_dict):
                        key = list(choices_dict.keys())[idx - 1]
                        if key not in selected_keys:
                            selected_keys.append(key)
                    else:
                        print(f"无效的选择: {idx}")
                
                if selected_keys: # 如果至少有一个有效选择
                    break
                else:
                     print("没有有效的选择。")
        except ValueError:
            print(prompts["invalid_input_format"])
        except KeyboardInterrupt:
            print(f"\n{prompts['input_cancel_msg']}")
            return []
    
    return [choices_dict[k] for k in selected_keys]

def output_schemas(schemas: list, output_file: str, prompts: dict):
    """
    将 schemas 同时输出到控制台和指定文件。
    """
    print(f"\n{prompts['console_header']}")
    
    # 控制台输出
    for name, schema in schemas:
        print(prompts['console_model_header'].format(name=name))
        print(json.dumps(schema, indent=2))

    # 文件输出
    print(f"\n{prompts['output_file_msg'].format(filename=output_file)}")
    if len(schemas) > 1:
        combined_schema = {name: schema for name, schema in schemas}
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(combined_schema, f, indent=2, ensure_ascii=False)
    else:
        _, single_schema = schemas[0]
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(single_schema, f, indent=2, ensure_ascii=False)
    
    print(f"Schema 已保存到 {output_file}")

def output_json_data(data_list: list, output_file: str, prompts: dict):
    """
    将生成的 JSON 示例数据列表写入文件。
    
    Args:
        data_list: 包含 (模型名, JSON字符串) 元组的列表。
        output_file: 输出文件路径。
        prompts: 提示词字典。
    """
    # 控制台输出
    print(f"\n--- JSON 示例数据 (Console Output) ---")
    for name, json_str in data_list:
        print(f"\n--- 示例数据 for '{name}' ---")
        # json_str 通常是已经格式化好的字符串，直接打印
        print(json_str)

    # 文件输出
    print(f"\n{prompts['output_file_msg'].format(filename=output_file)}")
    
    # 准备写入文件的数据结构
    # 如果只有一个模型，直接写入该 JSON 对象
    # 如果有多个模型，写入一个 {模型名: JSON对象} 的字典
    if len(data_list) == 1:
        # 只有一个时，直接写入内容（注意：json_str 是字符串，需要先 loads 成对象）
        _, json_str = data_list[0]
        file_data = json.loads(json_str) 
    else:
        combined_data = {}
        for name, json_str in data_list:
            combined_data[name] = json.loads(json_str)
        file_data = combined_data

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(file_data, f, indent=2, ensure_ascii=False)
    
    print(f"JSON 示例数据已保存到 {output_file}")

def main():
    prompts = get_default_prompts()

    print(prompts["welcome"])
    
    model_file = "model.py" # 用于错误提示
    try:
        print(prompts["loading_msg"])
        models = load_models_from_file()
    except FileNotFoundError:
        print(prompts["file_not_found_error"])
        return
    
    if not models:
        print(prompts["no_models_warning"])
        return
    
    print(prompts["found_models_msg"].format(count=len(models), list=', '.join(models.keys())))
    
    selected_model_classes = get_user_selection(
        models,
        prompts["select_prompt"],
        prompts
    )
    
    if not selected_model_classes:
        # get_user_selection 内部已处理 "no_selection_msg"
        return

    schemas_to_output = []
    json_data_to_output = []
    for cls in selected_model_classes:
        print(prompts["generating_msg"].format(name=cls.__name__))
        schema = cls.model_json_schema()
        schemas_to_output.append((cls.__name__, schema))

        # 对定义了dump_json的类，输出json示例
        if hasattr(cls, 'dump_json'):
            method_dump_json = getattr(cls, 'dump_json')
            json_data = method_dump_json()
            json_data_to_output.append((cls.__name__, json_data))
            print(f'{cls.__name__} json_data like:\n{json_data}')
        else:
            print(f"class {cls.__name__} does not define @classmehtod dump_json")

    # 使用配置文件中的默认输出文件名
    output_file = prompts["default_output_file"]
    output_schemas(schemas_to_output, output_file, prompts)

    if json_data_to_output:
        output_file_data = prompts["default_output_file_json_data"]
        output_json_data(json_data_to_output, output_file_data, prompts)

if __name__ == "__main__":
    main()