
# Pydantic Model to JSON Schema Generator

一个简单的命令行工具，用于从 `model.py` 文件中定义的 Pydantic 模型自动生成 JSON Schema。

## 功能介绍

*   **自动发现**: 自动扫描 `model.py` 文件中继承自 `BaseModel` 并带有 `_is_pydantic_model_ = True` 标记的类。
*   **交互式选择**: 列出所有发现的模型，允许用户通过输入编号选择单个或多个模型，或输入 `all` 选择全部。
*   **双路输出**: 将生成的 JSON Schema 同时打印到控制台并保存到指定的 JSON 文件中（默认为 `generated_schemas.json`）。
*   **易于扩展**: 用户只需在 `model.py` 中添加新的 Pydantic 模型，并标记它们，即可在下次运行时选择生成。
*   **配置化**: 支持通过 `src/pyproject.toml` 文件自定义提示信息和默认输出文件名。

## 快速开始

### 1. 前提条件

*   安装了 [Python](https://www.python.org/) (版本 >= 3.13)。
*   安装了 [uv](https://github.com/astral-sh/uv) 包管理器。

### 2. 安装

1.  将此仓库克隆或下载到本地。
2.  确保你的项目目录结构为 `src-layout`：
    ```
    your-project-name/
    ├── src/
    │   ├── pydantic_sample/
    │   │   ├── __init__.py
    │   │   ├── main.py
    │   │   └── model.py
    │   └── pyproject.toml
    └── (其他文件，如 run.sh, README.md 等)
    ```
3.  在项目根目录 (`your-project-name/`) 下打开终端。
4.  运行以下命令进行开发模式安装：
    ```bash
    uv pip install -e .
    ```

### 3. 运行

在项目根目录下，运行命令：
```bash
uv run gen
```
程序将启动，自动加载 `src/pydantic_sample/model.py` 中的模型，并引导你进行选择。

---

## 如何扩展

### 1. 添加新的 Pydantic 模型

最核心的扩展方式是在 `src/pydantic_sample/model.py` 文件中添加新的模型类。

1.  **编辑 `src/pydantic_sample/model.py`**。
2.  **导入 `BaseModel`**：
    ```python
    from pydantic import BaseModel
    ```
3.  **定义你的新模型**，并**必须**添加 `_is_pydantic_model_ = True` 属性，以便工具能够识别它：
    ```python
    class YourNewModel(BaseModel):
        _is_pydantic_model_ = True  # 必需的标记
        field_name: str
        optional_field: int | None = None
        # ... 其他字段定义 ...
    ```
    **示例**:
    ```python
    # src/pydantic_sample/model.py
    from pydantic import BaseModel

    class Person(BaseModel):
        _is_pydantic_model_ = True
        name: str
        age: int
        email: str | None = None

    class Address(BaseModel):
        _is_pydantic_model_ = True
        street: str
        city: str
        zip_code: str

    # --- 新增模型 ---
    class Pet(BaseModel):
        _is_pydantic_model_ = True
        name: str
        species: str
        owner: Person # 可以引用其他模型
    ```
4.  **保存文件**。
5.  **重新运行** `uv run gen`，你的新模型 `Pet` 就会被发现并可供选择。
