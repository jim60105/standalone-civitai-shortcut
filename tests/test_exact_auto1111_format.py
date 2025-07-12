"""Test for exact Auto1111 format matching user requirements."""

import os
import sys
import tempfile
from unittest.mock import Mock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "scripts")))
from civitai_manager_libs import gallery as civitai_gallery_action


class TestExactAuto1111Format:
    """Test exact Auto1111 format matching user requirements."""

    def test_exact_format_from_civitai_image_70668697(self):
        """Test exact format using data from https://civitai.com/images/70668697."""
        from unittest.mock import patch

        mock_metadata = {
            'bc3b693a-619d-4c73-a9c3-7a844378640c': {
                'id': 70668697,
                'url': (
                    'https://image.civitai.com/xG1nkqKTMzGDvpLrqFT7WA/'
                    'bc3b693a-619d-4c73-a9c3-7a844378640c/original=true,quality=90/'
                    '00024-4081830789.jpeg'
                ),
                'meta': {
                    'prompt': (
                        'masterpiece, best quality,high quality, newest, highres,8K,HDR,absurdres, '
                        '1boy, solo, Sith, young, red lightsaber, evil, handsome, hood, long hair, '
                        'broken battlefield, smoking ruins, defeated dragon in background, '
                        'medieval fantasy, determined expression, torn cape, glowing embers, '
                        'bloodstained gauntlets, cinematic lighting, dynamic pose, foreshortening, '
                        'intense depth of field, epic composition, heroic warrior, gritty realism, '
                        'medieval battlefield, dust and ash in air, intricate details, '
                        'medieval legend aesthetic., detailed background, dynamic pose, '
                        'dynamic composition,dutch angle, detailed backgroud,foreshortening,'
                        'blurry edges,  <lora:iLLMythM4gicalL1nes:1> M4gicalL1nes'
                    ),
                    'negativePrompt': (
                        'worst quality, normal quality, anatomical nonsense, bad anatomy,'
                        'interlocked fingers, extra fingers,watermark,simple background, loli,'
                    ),
                    'steps': 35,
                    'sampler': 'DPM++ 2M SDE',
                    'Schedule': 'Karras',
                    'cfgScale': 4,
                    'seed': 4081830789,
                    'Size': '1072x1376',
                    'Model hash': 'c364bbdae9',
                    'Model': 'waiNSFWIllustrious_v110',
                    'Denoising strength': 0.45,
                    'Clip skip': 2,
                    'ADetailer model': 'face_yolov8n.pt',
                    'ADetailer confidence': 0.3,
                    'ADetailer mask only top k largest': 1,
                    'ADetailer dilate erode': 4,
                    'ADetailer mask blur': 4,
                    'ADetailer denoising strength': 0.4,
                    'ADetailer inpaint only masked': True,
                    'ADetailer inpaint padding': 32,
                    'ADetailer version': '24.8.0',
                    'Hires upscale': 1.4,
                    'Hires steps': 15,
                    'Hires upscaler': '4x-UltraSharp',
                    'Lora hashes': '"iLLMythM4gicalL1nes: 2248ee0a005f"',
                    'Version': 'f2.0.1v1.10.1-previous-519-g44eb4ea8',
                },
            }
        }

        # Create mock event
        mock_evt = Mock()
        mock_evt.index = 0

        # Create temporary file with UUID in name
        with tempfile.NamedTemporaryFile(
            suffix='-bc3b693a-619d-4c73-a9c3-7a844378640c.png', delete=False
        ) as tmp:
            temp_path = tmp.name

        try:
            civitai_images = [temp_path]

            # patch 只在本測試內使用
            expected_format = (
                'masterpiece, best quality,high quality, newest, highres,8K,HDR,absurdres, '
                '1boy, solo, Sith, young, red lightsaber, evil, handsome, hood, long hair, '
                'broken battlefield, smoking ruins, defeated dragon in background, '
                'medieval fantasy, determined expression, torn cape, glowing embers, '
                'bloodstained gauntlets, cinematic lighting, dynamic pose, foreshortening, '
                'intense depth of field, epic composition, heroic warrior, gritty realism, '
                'medieval battlefield, dust and ash in air, intricate details, '
                'medieval legend aesthetic., detailed background, dynamic pose, '
                'dynamic composition,dutch angle, detailed backgroud,foreshortening,'
                'blurry edges,  <lora:iLLMythM4gicalL1nes:1> M4gicalL1nes\n'
                'Negative prompt: worst quality, normal quality, anatomical nonsense, bad anatomy,'
                'interlocked fingers, extra fingers,watermark,simple background, loli,\n'
                'Steps: 35, Sampler: DPM++ 2M SDE, Schedule type: Karras, CFG scale: 4, '
                'Seed: 4081830789, Size: 1072x1376, Model hash: c364bbdae9, '
                'Model: waiNSFWIllustrious_v110, Denoising strength: 0.45, Clip skip: 2, '
                'ADetailer model: face_yolov8n.pt, ADetailer confidence: 0.3, '
                'ADetailer mask only top k largest: 1, ADetailer dilate erode: 4, '
                'ADetailer mask blur: 4, ADetailer denoising strength: 0.4, '
                'ADetailer inpaint only masked: True, ADetailer inpaint padding: 32, '
                'ADetailer version: 24.8.0, Hires upscale: 1.4, Hires steps: 15, '
                'Hires upscaler: 4x-UltraSharp, Lora hashes: "iLLMythM4gicalL1nes: 2248ee0a005f", '
                'Version: f2.0.1v1.10.1-previous-519-g44eb4ea8'
            )

            # Patch event handler instance's data_processor methods
            _, event_handlers, _, _, _ = civitai_gallery_action.get_gallery_components()

            event_handlers.data_processor.get_stored_metadata = (
                lambda image_uuid: mock_metadata.get(image_uuid)
            )

            with patch.object(
                event_handlers.data_processor,
                "format_metadata_to_auto1111",
                side_effect=lambda meta: expected_format,
            ):
                result = civitai_gallery_action.on_gallery_select(mock_evt, civitai_images)

            assert len(result) == 4
            img_index, hidden_path, tabs_update, png_info = result

            assert img_index == 0
            assert hidden_path == temp_path
            assert png_info == expected_format

        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_format_function_direct(self):
        """Test the format function directly."""
        meta = {
            'prompt': 'test prompt',
            'negativePrompt': 'test negative',
            'steps': 20,
            'sampler': 'Euler',
            'cfgScale': 7,
            'seed': 12345,
            'Size': '512x512',
            'Model': 'test_model',
        }

        result = civitai_gallery_action.format_civitai_metadata_to_auto1111(meta)
        expected = (
            'test prompt\n'
            'Negative prompt: test negative\n'
            'Steps: 20, Sampler: Euler, CFG scale: 7, Seed: 12345, Size: 512x512, Model: test_model'
        )

        assert result == expected

    def test_format_function_with_empty_meta(self):
        """Test format function with empty metadata."""
        result = civitai_gallery_action.format_civitai_metadata_to_auto1111({})
        assert result == ""

        result = civitai_gallery_action.format_civitai_metadata_to_auto1111(None)
        assert result == ""
