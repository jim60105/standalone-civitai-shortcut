import json
import re


# def parse_data(data):
#     parsed_data = {}

#     # Split the data into lines
#     lines = data.split('\n')

#     # Parse the positive prompt
#     if not lines[0].startswith('Negative prompt:') and not lines[0].startswith('Steps:'):
#         parsed_data['prompt'] = lines[0]

#     # Check if negative prompt is present
#     if len(lines) > 1 and lines[1].startswith('Negative prompt:'):
#         negative_prompt_match = re.search(r'Negative prompt:\s*(.+)', lines[1])
#         if negative_prompt_match:
#             parsed_data['negativePrompt'] = negative_prompt_match.group(1)

#     # Parse the other data using the parse_steps_data function
#     steps_data = lines[-1]
#     parsed_steps_data = parse_option_data(steps_data)
#     if parsed_steps_data:
#         parsed_data['options'] = parsed_steps_data
#     return parsed_data

# def parse_data(data):
#     parsed_data = {}

#     # Split the data into lines
#     lines = data.split('\n')

#     # Parse the positive prompt
#     count = 0
#     for line in lines:
#         if not line.startswith('Negative prompt:') and not line.startswith('Steps:'):
#             if 'prompt' in parsed_data:
#                 parsed_data['prompt'] = parsed_data['prompt']  + line
#             else:
#                 parsed_data['prompt'] = line
#             count = count + 1
#         else:
#             break

#     if len(lines) >= count:
#         lines = lines[count:]

#     # Check if negative prompt is present
#     if len(lines) > 0 and lines[0].startswith('Negative prompt:'):
#         negative_prompt_match = re.search(r'Negative prompt:\s*(.+)', lines[0])
#         if negative_prompt_match:
#             parsed_data['negativePrompt'] = negative_prompt_match.group(1)

#     # Parse the other data using the parse_steps_data function
#     steps_data = lines[-1]
#     if steps_data and steps_data.startswith('Steps:'):
#         parsed_steps_data = parse_option_data(steps_data)
#         if parsed_steps_data:
#             parsed_data['options'] = parsed_steps_data

#     return parsed_data


def parse_data(data):
    from scripts.civitai_manager_libs import util
    
    parsed_data = {}
    
    util.printD(f"[PROMPT] parse_data called with data: {repr(data)}")

    # Split the data into lines
    lines = data.split('\n')
    util.printD(f"[PROMPT] Split into {len(lines)} lines: {lines}")

    # Parse the positive prompt
    count = 0
    for line in lines:
        util.printD(f"[PROMPT] Processing line {count}: {repr(line)}")
        if not line.startswith('Negative prompt:') and not line.startswith('Steps:'):
            # Handle "Prompt: " prefix on the first line
            if count == 0 and line.startswith('Prompt:'):
                util.printD("[PROMPT] Found 'Prompt:' prefix on first line")
                prompt_match = re.search(r'Prompt:\s*(.+)', line)
                if prompt_match:
                    extracted_prompt = prompt_match.group(1)
                    parsed_data['prompt'] = extracted_prompt
                    util.printD(f"[PROMPT] Extracted prompt from prefix: {repr(extracted_prompt)}")
                else:
                    parsed_data['prompt'] = line
                    util.printD(f"[PROMPT] No regex match, using full line: {repr(line)}")
            else:
                if 'prompt' in parsed_data:
                    parsed_data['prompt'] = parsed_data['prompt'] + line
                    util.printD(
                        f"[PROMPT] Appended to existing prompt: {repr(parsed_data['prompt'])}"
                    )
                else:
                    parsed_data['prompt'] = line
                    util.printD(f"[PROMPT] Set initial prompt: {repr(line)}")
            count = count + 1
        else:
            util.printD(f"[PROMPT] Breaking at line {count} (negative/steps found)")
            break

    if len(lines) >= count:
        lines = lines[count:]
        util.printD(f"[PROMPT] Remaining lines after prompt parsing: {lines}")
    
    util.printD(f"[PROMPT] Current parsed_data after prompt: {parsed_data}")

    # Check if negative prompt is present
    for i, line in enumerate(lines):
        util.printD(f"[PROMPT] Processing remaining line {i}: {repr(line)}")
        if not line.startswith('Steps:'):
            if line.startswith('Negative prompt:'):
                util.printD("[PROMPT] Found negative prompt line")
                negative_prompt_match = re.search(r'Negative prompt:\s*(.+)', line)
                if negative_prompt_match:
                    extracted_negative = negative_prompt_match.group(1)
                    parsed_data['negativePrompt'] = extracted_negative
                    util.printD(f"[PROMPT] Extracted negative prompt: {repr(extracted_negative)}")
                else:
                    util.printD("[PROMPT] No regex match for negative prompt")
            else:
                if 'negativePrompt' in parsed_data:
                    parsed_data['negativePrompt'] = parsed_data['negativePrompt'] + line
                    util.printD(
                        f"[PROMPT] Appended to negative: {repr(parsed_data['negativePrompt'])}"
                    )
                else:
                    parsed_data['negativePrompt'] = line
                    util.printD(f"[PROMPT] Set initial negative: {repr(line)}")
        else:
            util.printD(f"[PROMPT] Breaking at Steps line: {repr(line)}")
            break

    # Parse the other data using the parse_steps_data function
    if lines:
        steps_data = lines[-1]
        util.printD(f"[PROMPT] Processing steps data: {repr(steps_data)}")
        if steps_data and steps_data.startswith('Steps:'):
            parsed_steps_data = parse_option_data(steps_data)
            util.printD(f"[PROMPT] Parsed steps data: {parsed_steps_data}")
            if parsed_steps_data:
                parsed_data['options'] = parsed_steps_data
        else:
            util.printD("[PROMPT] No valid steps data found")
    else:
        util.printD("[PROMPT] No remaining lines for steps data")
    
    util.printD(f"[PROMPT] Final parsed_data: {parsed_data}")
    return parsed_data


def parse_option_data(option_data):
    parsed_data = {}

    if option_data:
        # Split the data by comma and colon
        entries = re.split(r',\s*|\s*:\s*', option_data)

        # Extract key-value pairs
        for i in range(0, len(entries), 2):
            key = entries[i].strip()
            if i + 1 < len(entries):
                value = entries[i + 1].strip()
                parsed_data[key] = value

    return parsed_data


def parse_detail_prompt(prompt_data):
    details = re.split(r',\s*|\s*,\s*', prompt_data)
    details = [detail.strip() for detail in details if detail.strip()]
    return details


# # Example usage
# data = '''Best quality, masterpiece, ultra high res, (photorealistic:1.4),girl, beautiful_face, detailed skin,upper body, <lora:caise2-000022:0.6>
# Negative prompt: ng_deepnegative_v1_75t, badhandv4 (worst quality:2), (low quality:2), (normal quality:2), lowres, bad anatomy, bad hands, normal quality, ((monochrome)), ((grayscale)), ng_deepnegative_v1_75t, badhandv4 (worst quality:2), (low quality:2), (normal quality:2), lowres, bad anatomy, bad hands, normal quality, ((monochrome)), ((grayscale)),
# Steps: 28, Sampler: DPM++ 2M Karras, CFG scale: 11, Seed: 2508416159, Size: 640x384, Model hash: 7af26c6c98, Model: 真人_xsmix_V04很好看, Denoising strength: 0.53, Hires upscale: 2, Hires steps: 20, Hires upscaler: 4x-UltraSharp, Dynamic thresholding enabled: True, Mimic scale: 7, Threshold percentile: 100'''

# data = '''Best quality, masterpiece, ultra high res, (photorealistic:1.4), beautiful_face, detailed skin,upper body,,1boy,
# <lora:caise2-000022:0.6>
# Negative prompt: ng_deepnegative_v1_75t, badhandv4 (worst quality:2), (low quality:2), (normal quality:2), lowres, bad anatomy, bad hands, normal quality, ((monochrome)), ((grayscale)), ng_deepnegative_v1_75t, badhandv4 (worst quality:2), (low quality:2), (normal quality:2), lowres, bad anatomy, bad hands, normal quality, ((monochrome)), ((grayscale)),
# Steps: 28, Sampler: DPM++ 2M Karras, CFG scale: 11, Seed: 2899275, Size: 640x384, Model hash: 69bc54fc2c, Model: 2.8D_majicmixRealistic_v3, Denoising strength: 0.53, Hires upscale: 2, Hires steps: 20, Hires upscaler: 4x-UltraSharp, Dynamic thresholding enabled: True, Mimic scale: 7, Threshold percentile: 100'''

# data = '''Best quality, masterpiece, ultra high res, (photorealistic:1.4), beautiful_face, detailed skin,upper body,,1boy, <lora:caise2-000022:0.6>
# Steps: 28, Sampler: DPM++ 2M Karras, CFG scale: 11, Seed: 2899275, Size: 640x384, Model hash: 69bc54fc2c, Model: 2.8D_majicmixRealistic_v3, Denoising strength: 0.53, Hires upscale: 2, Hires steps: 20, Hires upscaler: 4x-UltraSharp, Dynamic thresholding enabled: True, Mimic scale: 7, Threshold percentile: 100'''

# data = '''Best quality, masterpiece, ultra high res, (photorealistic:1.4), beautiful_face, detailed skin,upper body,,1boy, <lora:caise2-000022:0.6>
# Negative prompt: ng_deepnegative_v1_75t, badhandv4 (worst quality:2), (low quality:2), (normal quality:2), lowres, bad anatomy, bad hands, normal quality, ((monochrome)), ((grayscale)), ng_deepnegative_v1_75t, badhandv4 (worst quality:2), (low quality:2), (normal quality:2), lowres, bad anatomy, bad hands, normal quality, ((monochrome)), ((grayscale)),'''


# data = '''<lora:betterCuteAsian03:0.3>, woman, (wearing kimono_clothes:1.3), holding umbrella,
# good hand,4k, high-res, masterpiece, best quality, head:1.3,((Hasselblad photography)), finely detailed skin, sharp focus, (cinematic lighting), night, soft lighting, dynamic angle, [:(detailed face:1.2):0.2], medium breasts, outside,   <lora:realistic_kimono_clothes:0.5>
# Negative prompt: NG_DeepNagetive_V1_75T,(greyscale:1.2),
# paintings, sketches, (worst quality:2), (low quality:2), (normal quality:2), lowres, normal quality, ((monochrome)), ((grayscale)), skin spots, acnes, skin blemishes, age spot, glans
# Steps: 30, Sampler: DPM++ 2M Karras, CFG scale: 7, Seed: 2181989112, Face restoration: CodeFormer, Size: 512x768, Model hash: 3e9211917c, Model: CheckpointYesmix_v16Original'''

# parsed_data = parse_data(data)
# print(parsed_data)

# output_file = 'parsed_prompt.json'
# with open(output_file, 'w') as f:
#     json.dump(parsed_data, f, indent=4)
