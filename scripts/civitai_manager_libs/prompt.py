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

    # Find the prompt line and extract everything after "Prompt:"
    prompt_found = False
    negative_found = False
    steps_found = False

    for i, line in enumerate(lines):
        line = line.strip()
        util.printD(f"[PROMPT] Processing line {i}: {repr(line)}")

        # Handle Prompt line
        if line.startswith('Prompt:') and not prompt_found:
            util.printD("[PROMPT] Found 'Prompt:' line")
            prompt_match = re.search(r'Prompt:\s*(.+)', line)
            if prompt_match:
                extracted_prompt = prompt_match.group(1).strip()
                parsed_data['prompt'] = extracted_prompt
                util.printD(f"[PROMPT] Extracted prompt: {repr(extracted_prompt)}")
                prompt_found = True
            continue

        # Handle Negative prompt line
        elif line.startswith('Negative prompt:') and not negative_found:
            util.printD("[PROMPT] Found 'Negative prompt:' line")
            negative_prompt_match = re.search(r'Negative prompt:\s*(.+)', line)
            if negative_prompt_match:
                extracted_negative = negative_prompt_match.group(1).strip().rstrip(',')
                parsed_data['negativePrompt'] = extracted_negative
                util.printD(f"[PROMPT] Extracted negative prompt: {repr(extracted_negative)}")
                negative_found = True
            continue

        # Handle parameter lines (Steps, Sampler, CFG scale, etc.)
        elif not steps_found and (
            line.startswith('Steps:')
            or line.startswith('Sampler:')
            or line.startswith('CFG scale:')
            or line.startswith('Seed:')
            or line.startswith('Size:')
            or line.startswith('Model')
            or line.startswith('Denoising')
            or line.startswith('Hires')
            or line.startswith('Dynamic')
            or line.startswith('Mimic')
            or line.startswith('Threshold')
            or line.startswith('Face restoration')
        ):
            util.printD("[PROMPT] Found parameter line, collecting all parameters")
            # Collect all parameter lines starting from this line
            param_lines = []
            for j in range(i, len(lines)):
                param_line = lines[j].strip()
                if param_line and (
                    param_line.startswith('Steps:')
                    or param_line.startswith('Sampler:')
                    or param_line.startswith('CFG scale:')
                    or param_line.startswith('Seed:')
                    or param_line.startswith('Size:')
                    or param_line.startswith('Model')
                    or param_line.startswith('Denoising')
                    or param_line.startswith('Hires')
                    or param_line.startswith('Dynamic')
                    or param_line.startswith('Mimic')
                    or param_line.startswith('Threshold')
                    or param_line.startswith('Face restoration')
                ):
                    param_lines.append(param_line)
                    util.printD(f"[PROMPT] Added parameter line: {repr(param_line)}")

            if param_lines:
                # Join all parameter lines with commas
                steps_data = ', '.join(param_lines)
                util.printD(f"[PROMPT] Combined steps data: {repr(steps_data)}")
                parsed_steps_data = parse_option_data(steps_data)
                util.printD(f"[PROMPT] Parsed steps data: {parsed_steps_data}")
                if parsed_steps_data:
                    parsed_data['options'] = parsed_steps_data
                steps_found = True
            break

        # Skip lines that are not prompt, negative prompt, or parameters
        elif line == '' or line.startswith('Generated using'):
            util.printD(f"[PROMPT] Skipping line: {repr(line)}")
            continue

        # Handle the first line as prompt if it doesn't start with known prefixes (standard format)
        elif (
            i == 0
            and not prompt_found
            and not line.startswith('Negative prompt:')
            and not line.startswith('Steps:')
            and line
        ):
            util.printD("[PROMPT] Using first line as prompt (standard format)")
            parsed_data['prompt'] = line
            util.printD(f"[PROMPT] Set prompt from first line: {repr(line)}")
            prompt_found = True

        # If we haven't found prompt yet, and this line doesn't start with known prefixes,
        # it might be a continuation of a previous prompt (but we'll be more careful)
        elif (
            prompt_found
            and not negative_found
            and not line.startswith('Negative prompt:')
            and not line.startswith('Steps:')
        ):
            # This could be a continuation of the prompt
            if 'prompt' in parsed_data:
                parsed_data['prompt'] = parsed_data['prompt'] + ' ' + line
                util.printD(f"[PROMPT] Appended to prompt: {repr(parsed_data['prompt'])}")

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
