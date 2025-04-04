from transformers import Qwen2_5_VLForConditionalGeneration, AutoTokenizer, AutoProcessor
from qwen_vl_utils import process_vision_info
from IPython.display import Image, display

model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
    "./space-voice-vl-poc", trust_remote_code=True, torch_dtype="auto", device_map="auto"
)

processor = AutoProcessor.from_pretrained("./space-voice-vl-poc", trust_remote_code=True)

display(Image(url="https://img.freepik.com/free-photo/beautiful-tropical-beach-sea-ocean-with-white-cloud-blue-sky-copyspace_74190-8663.jpg"))

messages = [
    {
        "role": "user",
        "content": [
            {
                "type": "image",
                "image": "https://img.freepik.com/free-photo/beautiful-tropical-beach-sea-ocean-with-white-cloud-blue-sky-copyspace_74190-8663.jpg",
            },
            {"type": "text", "text": "Write a description for the image"},
        ],
    }
]


text = processor.apply_chat_template(
    messages, tokenize=False, add_generation_prompt=True
)
image_inputs, video_inputs = process_vision_info(messages)
inputs = processor(
    text=[text],
    images=image_inputs,
    videos=video_inputs,
    padding=True,
    return_tensors="pt",
)
inputs = inputs.to("cuda")

generated_ids = model.generate(**inputs, max_new_tokens=128)
generated_ids_trimmed = [
    out_ids[len(in_ids) :] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
]
output_text = processor.batch_decode(
    generated_ids_trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False
)
print(output_text)
