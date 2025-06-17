"""
Integration tests for the compatibility layer adapters.

Tests the actual functionality of standalone and WebUI adapters.
"""

import unittest
import os
import sys
import tempfile
import json
from unittest.mock import patch, MagicMock

# Add the scripts directory to the path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from civitai_manager_libs.compat import get_compatibility_layer, reset_compatibility_layer
from civitai_manager_libs.compat.standalone_adapters.standalone_path_manager import StandalonePathManager
from civitai_manager_libs.compat.standalone_adapters.standalone_config_manager import StandaloneConfigManager
from civitai_manager_libs.compat.standalone_adapters.standalone_sampler_provider import StandaloneSamplerProvider
from civitai_manager_libs.compat.standalone_adapters.standalone_parameter_processor import StandaloneParameterProcessor


class TestStandaloneAdapters(unittest.TestCase):
    """Test standalone adapter implementations."""
    
    def setUp(self):
        """Set up test fixtures."""
        reset_compatibility_layer()
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up after tests."""
        reset_compatibility_layer()
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_standalone_path_manager(self):
        """Test standalone path manager functionality."""
        path_manager = StandalonePathManager()
        
        # Test basic path operations
        base_path = path_manager.get_base_path()
        self.assertIsInstance(base_path, str)
        self.assertTrue(os.path.isabs(base_path))
        
        extension_path = path_manager.get_extension_path()
        self.assertIsInstance(extension_path, str)
        
        models_path = path_manager.get_models_path()
        self.assertIsInstance(models_path, str)
        self.assertTrue('models' in models_path)
        
        # Test model-specific paths
        checkpoint_path = path_manager.get_model_folder_path('Checkpoint')
        self.assertIsInstance(checkpoint_path, str)
        self.assertTrue('Stable-diffusion' in checkpoint_path)
        
        lora_path = path_manager.get_model_folder_path('LORA')
        self.assertIsInstance(lora_path, str)
        self.assertTrue('Lora' in lora_path)
        
        # Test directory creation
        test_dir = os.path.join(self.temp_dir, 'test_dir')
        self.assertTrue(path_manager.ensure_directory_exists(test_dir))
        self.assertTrue(os.path.exists(test_dir))
    
    def test_standalone_config_manager(self):
        """Test standalone configuration manager functionality."""
        # Create a temporary config file
        config_file = os.path.join(self.temp_dir, 'test_config.json')
        
        with patch.object(StandaloneConfigManager, '_get_config_file_path', return_value=config_file):
            config_manager = StandaloneConfigManager()
            
            # Test setting and getting configuration
            config_manager.set_config('test_key', 'test_value')
            self.assertEqual(config_manager.get_config('test_key'), 'test_value')
            
            # Test default values
            self.assertEqual(config_manager.get_config('nonexistent_key', 'default'), 'default')
            
            # Test saving and loading
            self.assertTrue(config_manager.save_config())
            self.assertTrue(os.path.exists(config_file))
            
            # Create new instance and load
            config_manager2 = StandaloneConfigManager()
            with patch.object(config_manager2, '_get_config_file_path', return_value=config_file):
                self.assertTrue(config_manager2.load_config())
                self.assertEqual(config_manager2.get_config('test_key'), 'test_value')
            
            # Test model folders
            model_folders = config_manager.get_model_folders()
            self.assertIsInstance(model_folders, dict)
            self.assertIn('Checkpoint', model_folders)
            self.assertIn('LORA', model_folders)
    
    def test_standalone_sampler_provider(self):
        """Test standalone sampler provider functionality."""
        sampler_provider = StandaloneSamplerProvider()
        
        # Test sampler lists
        samplers = sampler_provider.get_samplers()
        self.assertIsInstance(samplers, list)
        self.assertGreater(len(samplers), 0)
        self.assertIn('Euler', samplers)
        self.assertIn('Euler a', samplers)
        
        img2img_samplers = sampler_provider.get_samplers_for_img2img()
        self.assertIsInstance(img2img_samplers, list)
        self.assertEqual(samplers, img2img_samplers)  # Should be the same in standalone
        
        # Test upscaler lists
        upscale_modes = sampler_provider.get_upscale_modes()
        self.assertIsInstance(upscale_modes, list)
        self.assertIn('Linear', upscale_modes)
        
        sd_upscalers = sampler_provider.get_sd_upscalers()
        self.assertIsInstance(sd_upscalers, list)
        self.assertIn('None', sd_upscalers)
        
        all_upscalers = sampler_provider.get_all_upscalers()
        self.assertEqual(len(all_upscalers), len(upscale_modes) + len(sd_upscalers))
        
        # Test sampler availability
        self.assertTrue(sampler_provider.is_sampler_available('Euler'))
        self.assertFalse(sampler_provider.is_sampler_available('NonexistentSampler'))
        
        # Test default sampler
        default_sampler = sampler_provider.get_default_sampler()
        self.assertIsInstance(default_sampler, str)
        self.assertTrue(sampler_provider.is_sampler_available(default_sampler))
    
    def test_standalone_parameter_processor(self):
        """Test standalone parameter processor functionality."""
        param_processor = StandaloneParameterProcessor()
        
        # Test parameter parsing
        parameters_text = """beautiful landscape, detailed
Negative prompt: blurry, low quality
Steps: 20, Sampler: Euler a, CFG scale: 7.5, Seed: 123456789, Size: 512x768"""
        
        parsed_params = param_processor.parse_parameters(parameters_text)
        self.assertIsInstance(parsed_params, dict)
        self.assertIn('prompt', parsed_params)
        self.assertIn('negative_prompt', parsed_params)
        self.assertEqual(parsed_params['steps'], 20)
        self.assertEqual(parsed_params['cfg_scale'], 7.5)
        self.assertEqual(parsed_params['sampler_name'], 'Euler a')
        
        # Test prompt extraction
        positive, negative = param_processor.extract_prompt_and_negative(parameters_text)
        self.assertEqual(positive, 'beautiful landscape, detailed')
        self.assertEqual(negative, 'blurry, low quality')
        
        # Test parameter formatting
        test_params = {
            'prompt': 'test prompt',
            'negative_prompt': 'test negative',
            'steps': 25,
            'cfg_scale': 8.0
        }
        formatted = param_processor.format_parameters(test_params)
        self.assertIn('test prompt', formatted)
        self.assertIn('Negative prompt: test negative', formatted)
        self.assertIn('Steps: 25', formatted)
        
        # Test parameter validation
        invalid_params = {
            'steps': 200,  # Too high
            'cfg_scale': 50,  # Too high
            'width': 32,  # Too low
        }
        validated = param_processor.validate_parameters(invalid_params)
        self.assertLessEqual(validated['steps'], 150)
        self.assertLessEqual(validated['cfg_scale'], 30)
        self.assertGreaterEqual(validated['width'], 64)
        
        # Test parameter merging
        base_params = {'steps': 20, 'cfg_scale': 7.5}
        override_params = {'steps': 30, 'sampler_name': 'DPM++ 2M'}
        merged = param_processor.merge_parameters(base_params, override_params)
        self.assertEqual(merged['steps'], 30)  # Override takes precedence
        self.assertEqual(merged['cfg_scale'], 7.5)  # Base value preserved
        self.assertEqual(merged['sampler_name'], 'DPM++ 2M')  # New value added


class TestCompatibilityLayerIntegration(unittest.TestCase):
    """Test compatibility layer integration with standalone mode."""
    
    def setUp(self):
        """Set up test fixtures."""
        reset_compatibility_layer()
    
    def tearDown(self):
        """Clean up after tests."""
        reset_compatibility_layer()
    
    def test_compatibility_layer_standalone_integration(self):
        """Test full integration in standalone mode."""
        # Force standalone mode
        compat = get_compatibility_layer(mode='standalone')
        
        # Test all components are accessible
        self.assertIsNotNone(compat.path_manager)
        self.assertIsNotNone(compat.config_manager)
        self.assertIsNotNone(compat.metadata_processor)
        self.assertIsNotNone(compat.ui_bridge)
        self.assertIsNotNone(compat.sampler_provider)
        self.assertIsNotNone(compat.parameter_processor)
        
        # Test basic functionality
        base_path = compat.path_manager.get_base_path()
        self.assertIsInstance(base_path, str)
        
        samplers = compat.sampler_provider.get_samplers()
        self.assertGreater(len(samplers), 0)
        
        # Test configuration
        compat.config_manager.set_config('test_integration', True)
        self.assertTrue(compat.config_manager.get_config('test_integration'))
        
        # Test parameter processing
        test_params = {'prompt': 'test', 'steps': 20}
        formatted = compat.parameter_processor.format_parameters(test_params)
        self.assertIn('test', formatted)
        self.assertIn('Steps: 20', formatted)
    
    def test_compatibility_layer_mode_consistency(self):
        """Test that mode is consistent across components."""
        compat = get_compatibility_layer(mode='standalone')
        
        self.assertEqual(compat.mode, 'standalone')
        self.assertTrue(compat.is_standalone_mode())
        self.assertFalse(compat.is_webui_mode())
        
        # UI bridge should reflect standalone mode
        ui_bridge = compat.ui_bridge
        self.assertFalse(ui_bridge.is_webui_mode())


if __name__ == '__main__':
    unittest.main()
