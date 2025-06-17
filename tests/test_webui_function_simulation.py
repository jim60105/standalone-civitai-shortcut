"""
Tests for enhanced standalone adapters in Backlog 003.

Tests PNG metadata processing, parameter parsing, sampler management,
path management, and configuration management.
"""

import unittest
import os
import sys
import tempfile
import json
import shutil
from unittest.mock import patch, MagicMock

# Add the scripts directory to the path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from civitai_manager_libs.compat.standalone_adapters.standalone_metadata_processor import StandaloneMetadataProcessor
from civitai_manager_libs.compat.standalone_adapters.standalone_sampler_provider import StandaloneSamplerProvider
from civitai_manager_libs.compat.standalone_adapters.standalone_path_manager import StandalonePathManager
from civitai_manager_libs.compat.standalone_adapters.standalone_config_manager import StandaloneConfigManager
from civitai_manager_libs.compat.standalone_adapters.parameter_parser import ParameterParser, ParameterFormatter


class TestStandaloneMetadataProcessor(unittest.TestCase):
    """Test enhanced PNG metadata processing functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.processor = StandaloneMetadataProcessor()
        self.processor.set_debug_mode(True)
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up after tests."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_parameter_parsing(self):
        """Test parameter parsing functionality."""
        test_parameters = """masterpiece, best quality, 1girl, solo, long hair, looking at viewer
Negative prompt: bad quality, worst quality, lowres
Steps: 20, Sampler: DPM++ 2M Karras, CFG scale: 7, Seed: 123456789, Size: 512x768, Model hash: abcd1234, Model: v1-5-pruned-emaonly"""
        
        result = self.processor.parse_generation_parameters(test_parameters)
        
        # Check basic parameters
        self.assertIn('prompt', result)
        self.assertIn('negative_prompt', result)
        self.assertIn('steps', result)
        self.assertIn('sampler_name', result)
        self.assertIn('cfg_scale', result)
        self.assertIn('seed', result)
        
        # Check types
        self.assertIsInstance(result['steps'], int)
        self.assertEqual(result['steps'], 20)
        self.assertIsInstance(result['cfg_scale'], float)
        self.assertEqual(result['cfg_scale'], 7.0)
        self.assertIsInstance(result['seed'], int)
        
        # Check size parsing
        self.assertIn('size', result)
        size_data = result['size']
        self.assertIsInstance(size_data, dict)
        self.assertEqual(size_data['width'], 512)
        self.assertEqual(size_data['height'], 768)
    
    def test_prompt_extraction(self):
        """Test prompt extraction from parameters."""
        test_text = """beautiful landscape, mountains, sunset
Negative prompt: ugly, blurry, low quality
Steps: 25, Sampler: Euler a"""
        
        positive, negative = self.processor.extract_prompt_from_parameters(test_text)
        
        self.assertEqual(positive, "beautiful landscape, mountains, sunset")
        self.assertEqual(negative, "ugly, blurry, low quality")
    
    def test_advanced_parameter_extraction(self):
        """Test extraction of advanced parameters like LoRA and embeddings."""
        test_text = """beautiful girl <lora:test_lora:0.8> <embedding_name> __wildcard__
Negative prompt: bad quality
Steps: 20, Sampler: DPM++ 2M"""
        
        result = self.processor.parse_generation_parameters(test_text)
        
        # Should contain LoRA information
        self.assertIn('lora', result)
        self.assertIsInstance(result['lora'], list)
        self.assertEqual(len(result['lora']), 1)
        self.assertEqual(result['lora'][0]['name'], 'test_lora')
        self.assertEqual(result['lora'][0]['strength'], 0.8)
        
        # Should contain embeddings
        self.assertIn('embeddings', result)
        self.assertIn('embedding_name', result['embeddings'])
        
        # Should contain wildcards
        self.assertIn('wildcards', result)
        self.assertIn('wildcard', result['wildcards'])
    
    def test_parameter_validation(self):
        """Test parameter validation functionality."""
        test_params = {
            'steps': 20,
            'cfg_scale': 7.5,
            'seed': 123456789,
            'size': {'width': 512, 'height': 768},
            'invalid_steps': 999,  # Should be limited
            'invalid_cfg': 50.0,   # Should be limited
        }
        
        validated = self.processor.validate_parameters(test_params)
        
        # Valid parameters should pass through
        self.assertEqual(validated['steps'], 20)
        self.assertEqual(validated['cfg_scale'], 7.5)
        
        # Size should be preserved if valid
        self.assertIn('size', validated)


class TestParameterParser(unittest.TestCase):
    """Test the standalone parameter parser."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.parser = ParameterParser()
        self.formatter = ParameterFormatter()
        self.parser.set_debug_mode(True)
    
    def test_basic_parsing(self):
        """Test basic parameter parsing."""
        test_text = """beautiful artwork
Negative prompt: bad quality
Steps: 25, Sampler: Euler, CFG scale: 7.5, Seed: 987654321"""
        
        result = self.parser.parse(test_text)
        
        self.assertEqual(result['prompt'], "beautiful artwork")
        self.assertEqual(result['negative_prompt'], "bad quality")
        self.assertEqual(result['steps'], 25)
        self.assertEqual(result['sampler'], "Euler")
        self.assertEqual(result['cfg_scale'], 7.5)
        self.assertEqual(result['seed'], 987654321)
    
    def test_complex_parsing(self):
        """Test parsing with complex parameters."""
        test_text = """masterpiece <lora:style:0.7> <lyco:char:0.5>
Negative prompt: worst quality, <bad_embed>
Steps: 30, Sampler: DPM++ 2M Karras, CFG scale: 8.0, Seed: 123456, Size: 1024x768, Clip skip: 2"""
        
        result = self.parser.parse(test_text)
        
        # Check LoRA and LyCORIS extraction
        self.assertIn('lora', result)
        self.assertIn('lycoris', result)
        self.assertEqual(len(result['lora']), 1)
        self.assertEqual(len(result['lycoris']), 1)
        
        # Check size parsing
        size = result['size']
        self.assertEqual(size['width'], 1024)
        self.assertEqual(size['height'], 768)
    
    def test_formatting(self):
        """Test parameter formatting."""
        params = {
            'prompt': 'beautiful landscape',
            'negative_prompt': 'ugly, blurry',
            'steps': 20,
            'sampler': 'Euler a',
            'cfg_scale': 7.0,
            'seed': 123456,
            'size': {'width': 512, 'height': 768, 'size_string': '512x768'}
        }
        
        formatted = self.formatter.format(params)
        
        self.assertIn('beautiful landscape', formatted)
        self.assertIn('Negative prompt: ugly, blurry', formatted)
        self.assertIn('Steps: 20', formatted)
        self.assertIn('CFG scale: 7.0', formatted)


class TestStandaloneSamplerProvider(unittest.TestCase):
    """Test enhanced sampler provider."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.provider = StandaloneSamplerProvider()
        self.provider.set_debug_mode(True)
    
    def test_sampler_list(self):
        """Test getting sampler list."""
        samplers = self.provider.get_samplers()
        
        self.assertIsInstance(samplers, list)
        self.assertGreater(len(samplers), 0)
        self.assertIn("Euler", samplers)
        self.assertIn("DPM++ 2M Karras", samplers)
    
    def test_sampler_validation(self):
        """Test sampler validation."""
        self.assertTrue(self.provider.is_sampler_available("Euler"))
        self.assertTrue(self.provider.is_sampler_available("DPM++ 2M Karras"))
        self.assertFalse(self.provider.is_sampler_available("NonexistentSampler"))
    
    def test_sampler_info(self):
        """Test getting detailed sampler information."""
        info = self.provider.get_sampler_info("Euler")
        
        self.assertIsInstance(info, dict)
        self.assertEqual(info['name'], "Euler")
        self.assertIn('aliases', info)
        self.assertIn('categories', info)
    
    def test_sampler_aliases(self):
        """Test sampler alias resolution."""
        # Test alias recognition
        self.assertTrue(self.provider.is_sampler_available("euler"))
        self.assertTrue(self.provider.is_sampler_available("dpmpp_2m_karras"))
        
        # Test normalization
        normalized = self.provider.normalize_sampler_name("euler")
        self.assertEqual(normalized, "Euler")
    
    def test_upscaler_lists(self):
        """Test upscaler list functionality."""
        upscale_modes = self.provider.get_upscale_modes()
        sd_upscalers = self.provider.get_sd_upscalers()
        all_upscalers = self.provider.get_all_upscalers()
        
        self.assertIsInstance(upscale_modes, list)
        self.assertIsInstance(sd_upscalers, list)
        self.assertIsInstance(all_upscalers, list)
        
        self.assertIn("Lanczos", upscale_modes)
        self.assertIn("RealESRGAN_x4plus", sd_upscalers)
        
        # All upscalers should be combination of both
        self.assertEqual(len(all_upscalers), len(upscale_modes) + len(sd_upscalers))


class TestStandalonePathManager(unittest.TestCase):
    """Test enhanced path manager."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.path_manager = StandalonePathManager(base_path=self.temp_dir)
        self.path_manager.set_debug_mode(True)
    
    def tearDown(self):
        """Clean up after tests."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_base_path(self):
        """Test base path functionality."""
        base_path = self.path_manager.get_base_path()
        self.assertEqual(base_path, self.temp_dir)
    
    def test_model_paths(self):
        """Test model path functionality."""
        models_path = self.path_manager.get_models_path()
        self.assertTrue(os.path.exists(models_path))
        
        # Test specific model folder
        checkpoint_path = self.path_manager.get_model_folder_path("Checkpoint")
        self.assertTrue(os.path.exists(checkpoint_path))
        self.assertIn("Stable-diffusion", checkpoint_path)
    
    def test_directory_creation(self):
        """Test directory creation."""
        test_path = os.path.join(self.temp_dir, 'test', 'nested', 'directory')
        result = self.path_manager.ensure_directory_exists(test_path)
        
        self.assertTrue(result)
        self.assertTrue(os.path.exists(test_path))
    
    def test_path_validation(self):
        """Test path validation."""
        valid_path = os.path.join(self.temp_dir, 'valid')
        os.makedirs(valid_path)
        
        self.assertTrue(self.path_manager.validate_path(valid_path))
        self.assertFalse(self.path_manager.validate_path('/nonexistent/path'))
    
    def test_model_folder_management(self):
        """Test adding and managing model folders."""
        result = self.path_manager.add_model_folder("TestType", "models/TestType", save_config=False)
        self.assertTrue(result)
        
        # Check if folder was created
        test_path = self.path_manager.get_model_folder_path("TestType")
        self.assertTrue(os.path.exists(test_path))
        
        # Check if it's in the all paths list
        all_paths = self.path_manager.get_all_model_paths()
        self.assertIn("TestType", all_paths)


class TestStandaloneConfigManager(unittest.TestCase):
    """Test enhanced configuration manager."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        config_path = os.path.join(self.temp_dir, 'test_config.json')
        self.config_manager = StandaloneConfigManager(config_path)
        self.config_manager.set_debug_mode(True)
    
    def tearDown(self):
        """Clean up after tests."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_basic_config_operations(self):
        """Test basic configuration operations."""
        # Test setting and getting
        self.config_manager.set_config('test_key', 'test_value')
        result = self.config_manager.get_config('test_key')
        self.assertEqual(result, 'test_value')
        
        # Test default value
        result = self.config_manager.get_config('nonexistent_key', 'default')
        self.assertEqual(result, 'default')
    
    def test_nested_config_keys(self):
        """Test dot notation for nested configuration."""
        self.config_manager.set_config('section.subsection.key', 'nested_value')
        result = self.config_manager.get_config('section.subsection.key')
        self.assertEqual(result, 'nested_value')
        
        # Test partial path
        section = self.config_manager.get_config('section')
        self.assertIsInstance(section, dict)
        self.assertIn('subsection', section)
    
    def test_config_persistence(self):
        """Test configuration saving and loading."""
        # Set some values
        self.config_manager.set_config('persistent_key', 'persistent_value')
        self.config_manager.set_config('server.port', 8080)
        
        # Save configuration
        save_result = self.config_manager.save_config()
        self.assertTrue(save_result)
        
        # Create new manager instance to test loading
        new_manager = StandaloneConfigManager(self.config_manager._config_file_path)
        
        # Check if values were loaded
        self.assertEqual(new_manager.get_config('persistent_key'), 'persistent_value')
        self.assertEqual(new_manager.get_config('server.port'), 8080)
    
    def test_config_validation(self):
        """Test configuration value validation."""
        # Test port validation (should clamp to valid range)
        self.config_manager.set_config('server.port', 999999)  # Too high
        port = self.config_manager.get_config('server.port')
        self.assertLessEqual(port, 65535)
        
        # Test cache size validation
        self.config_manager.set_config('civitai.cache_size_mb', 50)  # Too low
        cache_size = self.config_manager.get_config('civitai.cache_size_mb')
        self.assertGreaterEqual(cache_size, 100)
    
    def test_model_folder_management(self):
        """Test model folder configuration management."""
        folders = self.config_manager.get_model_folders()
        self.assertIsInstance(folders, dict)
        self.assertIn('Checkpoint', folders)
        
        # Test updating model folder
        result = self.config_manager.update_model_folder('TestModel', 'custom/path')
        self.assertTrue(result)
        
        updated_folders = self.config_manager.get_model_folders()
        self.assertEqual(updated_folders['TestModel'], 'custom/path')
    
    def test_config_export_import(self):
        """Test configuration export and import."""
        # Set some test values
        self.config_manager.set_config('export_test', 'export_value')
        
        # Export configuration
        export_path = os.path.join(self.temp_dir, 'exported_config.json')
        export_result = self.config_manager.export_config(export_path)
        self.assertTrue(export_result)
        self.assertTrue(os.path.exists(export_path))
        
        # Modify current config
        self.config_manager.set_config('export_test', 'modified_value')
        
        # Import configuration
        import_result = self.config_manager.import_config(export_path, merge=False)
        self.assertTrue(import_result)
        
        # Check if original value was restored
        result = self.config_manager.get_config('export_test')
        self.assertEqual(result, 'export_value')


if __name__ == '__main__':
    unittest.main()
