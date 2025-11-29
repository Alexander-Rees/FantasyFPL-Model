
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

model_name = "Qwen/Qwen2.5-1.5B-Instruct"
print(f"Downloading {model_name}...")

print("Downloading tokenizer...")
tokenizer = AutoTokenizer.from_pretrained(model_name)
print("Tokenizer downloaded.")

print("Downloading model...")
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
    trust_remote_code=True
)
print("Model downloaded successfully.")
