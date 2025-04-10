from deepface import DeepFace
import cv2
import os, re
detect_image = './compare2.jpg'
stored_image = './labeled_image.jpg'
dfs = DeepFace.find(
    img_path=detect_image, db_path='./facedb', model_name='Facenet512'
)

if len(dfs) < 1:
    print("non-recognize-face-pretrained")
    exit(0)
else:
    img = cv2.imread(detect_image)
    for idfiy in dfs:
        if idfiy.empty:
            continue
        x = int(idfiy.source_x.iloc[0])
        y = int(idfiy.source_y.iloc[0])
        w = int(idfiy.source_w.iloc[0])
        h = int(idfiy.source_h.iloc[0])
        cv2.rectangle(img , (x, y), 
                      (x + w, 
                       y + h), (0,255,0), 2)
        label = re.match(r"([a-zA-Z]+)", os.path.basename(idfiy.identity.iloc[0])).group(1)
        fix_label = f"[detect_named: {label}]"
        cv2.putText(img, fix_label, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)     
    cv2.imwrite(stored_image, img)

print('label ok')

from IPython.display import Image, display, clear_output
clear_output(wait=True)
display(Image(url=stored_image))

from transformers import Qwen2_5_VLForConditionalGeneration, AutoTokenizer, AutoProcessor
from qwen_vl_utils import process_vision_info

model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
    "devJy/space-voice-label-detect-beta",  torch_dtype="auto", device_map="auto"
)


processor = AutoProcessor.from_pretrained("devJy/space-voice-label-detect-beta", )

messages = [
    {
        "role": "user",
        "content": [
            {
                "type": "image",
                "image": stored_image,
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

generated_ids = model.generate(**inputs, max_new_tokens=256)
generated_ids_trimmed = [
    out_ids[len(in_ids) :] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
]
output_text = processor.batch_decode(
    generated_ids_trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False
)
print(output_text[0])
