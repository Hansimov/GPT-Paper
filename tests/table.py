from huggingface_hub import hf_hub_download
from transformers import AutoImageProcessor, TableTransformerForObjectDetection
import torch
from pathlib import Path
from PIL import Image, ImageDraw
from utils.envs import init_os_envs

init_os_envs(set_proxy=True, cuda_device=3)

# file_path = hf_hub_download(
#     repo_id="nielsr/example-pdf", repo_type="dataset", filename="example_pdf.png"
# )

file_path = Path(__file__).parent / "example_pdf_2.png"
image = Image.open(file_path).convert("RGB")

image_processor = AutoImageProcessor.from_pretrained(
    "microsoft/table-transformer-detection"
)
model = TableTransformerForObjectDetection.from_pretrained(
    "microsoft/table-transformer-detection"
)

inputs = image_processor(images=image, return_tensors="pt")
outputs = model(**inputs)

# convert outputs (bounding boxes and class logits) to COCO API
target_sizes = torch.tensor([image.size[::-1]])
results = image_processor.post_process_object_detection(
    outputs, threshold=0.9, target_sizes=target_sizes
)[0]


rects = []
for score, label, box in zip(results["scores"], results["labels"], results["boxes"]):
    box = [int(i) for i in box.tolist()]
    print(
        f"Detected {model.config.id2label[label.item()]} with confidence "
        f"{round(score.item(), 3)} at location {box}"
    )
    rects.append([(box[0], box[1]), (box[2], box[3])])

image_draw = ImageDraw.Draw(image)
for rect in rects:
    image_draw.rectangle(rect, fill=None, outline="red")

output_image_path = Path(__file__).parent / "example_pdf_output.png"
with open(output_image_path, "wb") as wf:
    image.save(output_image_path)
