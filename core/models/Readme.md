# Hugging Face

``` json
{
  "resource_id": "res_hf_qwen2_5_7b_instruct",
  "resource_type": "huggingface_model",
  "name": "Qwen/Qwen2.5-7B-Instruct",
  "provider": "huggingface",
  "required": true,
  "install_strategy": ["huggingface_download"],
  "local_path": "runtime/models/huggingface/Qwen_Qwen2.5-7B-Instruct",
  "capabilities": ["intent", "workflow", "chat"],
  "metadata": {
    "format": "transformers",
    "recommended_tasks": ["intent", "workflow"]
  }
}
```