# models.py
from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

######################################################
# 以下是作为示例的JSON-Schema的model定义（仅供参考）
######################################################

class Person(BaseModel):
    # _is_pydantic_model_ = True
    name: str
    age: int
    email: str | None = None

class Address(BaseModel):
    # _is_pydantic_model_ = True
    street: str
    city: str
    zip_code: str

class Company(BaseModel):
    # _is_pydantic_model_ = True
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
BeamStrings = List[str]

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

# 算子输入通用元数据
class lme_input_meta(BaseModel):
    graph_type: GraphType
    request_id: int
    operation: int = Field(default=1, description="Process selection field, with values as powers of 2(2^n): pre = 1, tok = 2, vit = 4, llm = 8, dtk = 16.")


# 算子输出通用元数据
class lme_output_meta(BaseModel):
    graph_type: GraphType
    status_msg: str
    status_code: int
    request_id: int

# preprocess
class lme_preprocess_input(BaseModel):
    _is_pydantic_model_ = True

    meta_data: lme_input_meta

    input_pics: List[Tensor]
    fps: float = Field(description="fps=0 表示图片模式，>0 表示视频模式")
    frame_ids: Optional[List[int]] = Field(default=None, description="视频模式，表示帧号")

    @classmethod
    def dump_json(cls, indent: int = 4) -> str:
        # 创建 Tensor 示例 (模拟输入图片数据)
        tensor = Tensor(
            data=None,
            data_type=DataType.UINT8,
            memory_type=MemoryType.HOST,
            device_id=0,
            dims=[1920, 1080, 3],  # 假设的图片维度
            format=DataFormat.kRGB
        )
        
        meta_data = lme_input_meta(
            graph_type=GraphType.LMM,
            request_id=1001,
            operation=31
        )

        instance = cls(
            meta_data=meta_data,
            input_pics=[tensor],
            fps=0.0,  # 图片模式
            frame_ids=None
        )

        return instance.model_dump_json(indent=indent)


class lme_preprocess_data(BaseModel):
    pic: Tensor
    patch_num_width: int
    patch_num: int

    class Config:
        arbitrary_types_allowed = True  # 允许任意类型，用于处理void*指针

class lme_preprocess_output(BaseModel):
    _is_pydantic_model_ = True

    meta_data: lme_output_meta

    # Preprocessing output data and proc mode
    output_data: List[lme_preprocess_data] = Field(description="The processed image.")
    proc_mode: ProcMode = Field(description="The processing mode (e.g., text-only, image-only, interleaved).")

    @classmethod
    def dump_json(cls, indent: int = 4) -> str:
        # 创建嵌套的 Tensor 和 lme_preprocess_data 示例
        tensor = Tensor(
            data=None,
            data_type=DataType.BF16,
            memory_type=MemoryType.DEVICE,
            device_id=0,
            dims=[3, 224, 224],
            format=DataFormat.kNV12
        )
        preprocess_data = lme_preprocess_data(
            pic=tensor,
            patch_num_width=14,
            patch_num=196
        )
        
        meta_data = lme_output_meta(
            graph_type=GraphType.LMM,
            status_msg="Preprocessing completed",
            status_code=0,
            request_id=1001
        )

        instance = cls(
            meta_data=meta_data,
            output_data=[preprocess_data],
            proc_mode=ProcMode.PIC_ONE_MODE
        )

        return instance.model_dump_json(indent=indent)

# tokenizer
class lme_tokenizer_input(BaseModel):
    _is_pydantic_model_ = True

    meta_data: lme_input_meta

    input_prompt: str = Field(default=False, description="user prompt")
    system_prompt: Optional[str] = Field(default="", description="system prompt")

    enable_thinking: Optional[bool] = Field(default=False, description="enable thinking mode or not")
    input_pics: List[Tensor] | None = Field(default=None, description="image information for generating lmm chat template")

    @classmethod
    def dump_json(cls, indent: int = 4) -> str:
        meta_data = lme_input_meta(
            graph_type=1,
            request_id=0,
            operation=31
        )

        instance = cls(
            meta_data=meta_data,
            input_prompt="user prompt here",
            system_prompt="system prompt maybe none",
            enable_thinking=False,
            input_pics=None
        )

        return instance.model_dump_json(indent=indent)

class lme_tokenizer_output(BaseModel):
    _is_pydantic_model_ = True

    meta_data: lme_output_meta

    # Tokenizer outputs
    tokens: VecTokens = Field(description="The input token IDs generated by the tokenizer for the model.")
    proc_modes: List[ProcMode] = Field(description="The processing modes applied during tokenization.")

    @classmethod
    def dump_json(cls, indent: int = 4) -> str:
        meta_data = lme_output_meta(
            graph_type=1,
            status_msg="success",
            status_code=0,
            request_id=0
        )

        instance = cls(
            meta_data=meta_data,
            tokens={1,2,3,4,5},
            proc_modes={1}
        )

        return instance.model_dump_json(indent=indent)

# vit
class lme_vit_input(BaseModel):
    _is_pydantic_model_ = True

    meta_data: lme_input_meta

    preprocess_data: lme_preprocess_output

    @classmethod
    def dump_json(cls, indent: int = 4) -> str:
        # 复用上面生成的 preprocess_output 示例
        preprocess_output_json = lme_preprocess_output.dump_json(indent=0)
        preprocess_data = lme_preprocess_output.model_validate_json(preprocess_output_json)
        
        meta_data = lme_input_meta(
            graph_type=GraphType.LMM,
            request_id=1002,
            operation=31
        )

        instance = cls(
            meta_data=meta_data,
            preprocess_data=preprocess_data
        )

        return instance.model_dump_json(indent=indent)

class lme_vit_output(BaseModel):
    _is_pydantic_model_ = True

    meta_data: lme_output_meta

    # Vision Transformer Outputs
    pic_tokens: List[Tensor] = Field(description="The visual feature embeddings (tokens) extracted by the Vision Transformer (ViT) from input images.")

    @classmethod
    def dump_json(cls, indent: int = 4) -> str:
        tensor = Tensor(
            data=None,
            data_type=DataType.FP16,
            memory_type=MemoryType.DEVICE,
            device_id=0,
            dims=[1, 576, 1024],  # 假设的特征维度 [Batch, SeqLen, HiddenSize]
            format=DataFormat.kRAWDATA
        )
        
        meta_data = lme_output_meta(
            graph_type=GraphType.LMM,
            status_msg="ViT inference success",
            status_code=0,
            request_id=1002
        )

        instance = cls(
            meta_data=meta_data,
            pic_tokens=[tensor]
        )

        return instance.model_dump_json(indent=indent)


# llm
class lme_llm_input(BaseModel):
    """
    Input data model for the LLM (Language Model) component.
    Aggregates tokenized text and visual features.
    """
    _is_pydantic_model_ = True

    meta_data: lme_input_meta

    # llm private field
    config: str = Field(description="Configuration data in JSON format. See ProCfg.json for schema details.")
    streaming: bool = Field(
        default=False, 
        description="Whether to enable streaming mode for incremental output."
    )
    lora_id: str = Field(description="Identifier for the LoRA (Low-Rank Adaptation) weights to load.")

    # Input data from the tokenizer
    tokenizer_data: lme_tokenizer_output = Field(description="Tokenized text data required by the LLM.")
    
    # Optional visual features extracted by the ViT
    vit_data: Optional[lme_vit_output] = Field(default=None, description="Optional visual features extracted by the Vision Transformer (ViT).")

    @classmethod
    def dump_json(cls, indent: int = 4) -> str:
        # 获取 tokenizer_data 示例
        tokenizer_output_json = lme_tokenizer_output.dump_json(indent=0)
        tokenizer_data = lme_tokenizer_output.model_validate_json(tokenizer_output_json)
        
        # 获取 vit_data 示例 (可选)
        vit_output_json = lme_vit_output.dump_json(indent=0)
        vit_data = lme_vit_output.model_validate_json(vit_output_json)
        
        meta_data = lme_input_meta(
            graph_type=GraphType.LLM,
            request_id=1003,
            operation=31
        )

        instance = cls(
            meta_data=meta_data,
            config='{"max_length": 2048, "temperature": 0.7}',
            streaming=False,
            lora_id="default",
            tokenizer_data=tokenizer_data,
            vit_data=vit_data
        )

        return instance.model_dump_json(indent=indent)

class lme_llm_output(BaseModel):
    _is_pydantic_model_ = True

    meta_data: lme_output_meta

    # LLM outputs
    is_final: bool = Field(description="Indicates whether the decoder generation has finished.")
    beam_tokens: BeamTokens = Field(description="The generated token sequences (output IDs) from each beam.")
    advance_output: dict[str, Tensor] = Field(description="Intermediate output tensors for advanced processing (e.g., logits, KV-cache).")
    dictionary_index: int = Field(description="The index corresponding to the selected token in the model's vocabulary.")
    search_tokens: VecTokens = Field(description="The token sequences resulting from the search algorithm (e.g., beam search).")

    input_tokens_num: int = Field(description="The total count of input tokens processed by the model.")

    @classmethod
    def dump_json(cls, indent: int = 4) -> str:

        tensor = Tensor(
            data=None,                   # 模拟 void* 空指针
            data_type=DataType.UINT8,    # 指定数据类型
            memory_type=MemoryType.HOST, # 指定内存类型
            device_id=0,                 # GPU 设备 ID
            dims=[1, 3, 224, 224],       # NCHW 维度
            format=DataFormat.kNV12      # 数据格式
        )

        meta_data = lme_output_meta(
            graph_type=1,
            status_msg="success",
            status_code=0,
            request_id=0
        )

        instance = cls(
            meta_data=meta_data,
            is_final=True,
            beam_tokens=[[1,2,3]],
            advance_output={
                "generation_logits": tensor,
            },
            dictionary_index=1,
            search_tokens={1,2,3},
            input_tokens_num=1086
        )

        return instance.model_dump_json(indent=indent)

# detokenizer
class lme_detokenizer_input(BaseModel):
    _is_pydantic_model_ = True

    meta_data: lme_input_meta

    llm_data: lme_llm_output = Field(description="The LLM's output is fed into the detokenizer.")

    @classmethod
    def dump_json(cls, indent: int = 4) -> str:
        # 获取 llm_data 示例
        llm_output_json = lme_llm_output.dump_json(indent=0)
        llm_data = lme_llm_output.model_validate_json(llm_output_json)
        
        meta_data = lme_input_meta(
            graph_type=GraphType.LLM,
            request_id=1004,
            operation=31
            
        )

        instance = cls(
            meta_data=meta_data,
            llm_data=llm_data
        )

        return instance.model_dump_json(indent=indent)


class lme_detokenizer_output(BaseModel):
    _is_pydantic_model_ = True

    meta_data: lme_output_meta

    # Detokenizer outputs
    is_final: bool = Field(description="Indicates whether the decoder generation has finished.")
    beam_strings: BeamStrings = Field(description="The generated text sequences (output strings) from each beam.")
    beam_tokens_nums: List[int] = Field(description="The number of tokens in each beam.")
    logits: dict[int, float] = Field(description="The raw logits output mapped by token ID.")

    input_tokens_num: int = Field(description="The count of input tokens processed.")
    feature: str = Field(default="", description="The MMR embedding feature std::vector[char].")

    @classmethod
    def dump_json(cls, indent: int = 4) -> str:
        meta_data = lme_output_meta(
            graph_type=GraphType.LLM,
            status_msg="Detokenization complete",
            status_code=0,
            request_id=1004
        )

        instance = cls(
            meta_data=meta_data,
            is_final=True,
            beam_strings=["Hello, this is a generated response."],
            beam_tokens_nums=[5],
            logits={1: 0.99, 2: 0.01},
            input_tokens_num=10,
            feature=""
        )

        return instance.model_dump_json(indent=indent)