# models.py
from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

######################################################
# 以下是作为示例的JSON-Schema的model定义（仅供参考）
######################################################

class Person(BaseModel):
    _is_pydantic_model_ = True # 只有提供了该字段并配置为True才会被发现
    name: str
    age: int
    email: str | None = None

class Address(BaseModel):
    _is_pydantic_model_ = True
    street: str
    city: str
    zip_code: str

class Company(BaseModel):
    _is_pydantic_model_ = True
    name: str
    address: Address
    employees: list[Person] = []

class NonModelClass:
    pass

######################################################
# 多模态大模型标准算子输入输出JSON-Schema的model定义
######################################################

class GraphType(int, Enum):
    LLM = 1
    LMM = 2
    OPENMODEL = 3

# 类型别名
VecTokens = List[int]
BeamTokens = List[VecTokens]

class DataType(int, Enum):
    BOOL = 0
    UINT8 = 1
    INT8 = 2
    INT32 = 3
    INT64 = 4
    BF16 = 5
    FP8 = 6
    FP16 = 7
    FP32 = 8

class DataFormat(int, Enum):
    kBGR = 0                                          # BGR格式图片
    kRGB = 1                                          # RGB格式图片
    kGRAY = 2                                         # 灰度图
    kNV12 = 3                                         # NV12图片
    kI420 = 4                                         # I420图片
    kYV12 = 5                                         # YV12图片
    kNV21 = 6                                         # NV12图片
    kRAWDATA = 7                                      # 裸数据（直接计算使用，推理库不对数据格式意义做特殊处理）

class ProcMode(int, Enum):
    PIC_ONE_MODE = 1
    PIC_N_MODE = 2
    VID_MODE = 3
    TOK_ONLY_MODE = 4
    PIC_QWEN3VL_MODE = 5
    VID_QWEN3VL_MODE = 6


class MemoryType(int, Enum):
    HOST = 0
    DEVICE = 1

class Tensor(BaseModel):
    data: Optional[object] = None                          # 数据存储指针，使用object类型表示void*
    data_type: DataType                                    # 数据类型
    memory_type: MemoryType                                # memory类型
    device_id: int                                         # memory对应deviceID
    dims: List[int]                                        # 数据维度, [宽, 高, 帧数]
    format: DataFormat                                     # 数据格式

    class Config:
        arbitrary_types_allowed = True  # 允许任意类型，用于处理void*指针

# preprocess
class lme_preprocess_input(BaseModel):
    _is_pydantic_model_ = True

    request_id: int
    graph_type: GraphType
    input_prompt: str
    input_pics: List[Tensor]
    fps: Optional[float] = None
    frame_ids: List[int]
    config: str
    lora_id: str
    streaming: bool = Field(default=False, description="enable streaming or not")
    enable_thinking: int = Field(default=0, description="thiniking mode with 0-disable, 1-enable")

class lme_preprocess_output(BaseModel):
    _is_pydantic_model_ = True

# tokenizer
class lme_tokenizer_input(BaseModel):
    _is_pydantic_model_ = True

    graph_type: GraphType
    request_id: int

    input_prompt: str = Field(default=False, description="user prompt")
    system_prompt: Optional[str] = Field(default="", description="system prompt")

    enable_thinking: Optional[bool] = Field(default=False, description="enable thinking mode or not")
    input_pics: List[Tensor] | None = Field(default=None, description="image information for generating lmm chat template")

    @classmethod
    def dump_json(cls, indent: int = 4) -> str:
        instance = cls(
            graph_type=1,
            request_id=0,
            input_prompt="user prompt here",
            system_prompt="systemp prompt maybe none",
            enable_thinking=False,
            input_pics=None
        )

        return instance.model_dump_json(indent=indent)

class lme_tokenizer_output(BaseModel):
    _is_pydantic_model_ = True

    # 通用字段
    graph_type: GraphType
    status: int
    request_id: int

    # tokenizer输出字段
    tokens: VecTokens = Field(description="output input ids from tokenizer operator")
    proc_modes: List[ProcMode] = Field(description="tokenizer prrocess modes")

    @classmethod
    def dump_json(cls, indent: int = 4) -> str:
        instance = cls(
            graph_type=1,
            status=0,
            request_id=0,
            tokens={1,2,3,4,5},
            proc_modes={1}
        )

        return instance.model_dump_json(indent=indent)


# detokenizer
class lme_detokenizer_input(BaseModel):
    _is_pydantic_model_ = True

class lme_detokenizer_output(BaseModel):
    _is_pydantic_model_ = True

# vit
class lme_vit_input(BaseModel):
    _is_pydantic_model_ = True

class lme_vit_output(BaseModel):
    _is_pydantic_model_ = True

# llm
class lme_llm_input(BaseModel):
    _is_pydantic_model_ = True

class lme_llm_output(BaseModel):
    _is_pydantic_model_ = True
