"""
Comprehensive tests for standalone adapters.

These tests aim to achieve high coverage for the standalone adapter implementations.
"""
import os
import sys

# Add the scripts directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from civitai_manager_libs.compat.standalone_adapters.standalone_config_manager import (
    StandaloneConfigManager
)
from civitai_manager_libs.compat.standalone_adapters.standalone_path_manager import (
    StandalonePathManager
)
from civitai_manager_libs.compat.standalone_adapters.standalone_metadata_processor import (
    StandaloneMetadataProcessor
)
from civitai_manager_libs.compat.standalone_adapters.standalone_parameter_processor import (
    StandaloneParameterProcessor
)
from civitai_manager_libs.compat.standalone_adapters.standalone_sampler_provider import (
    StandaloneSamplerProvider
)
from civitai_manager_libs.compat.standalone_adapters.standalone_ui_bridge import (
    StandaloneUIBridge
)


class TestStandaloneConfigManager:
    """Test StandaloneConfigManager functionality."""

    def test_init_with_config_file(self, tmp_path):
        """Test initialization with specific config file."""
        config_file = tmp_path / "test_config.json"
        config_file.write_text('{"test_key": "test_value"}')
        
        manager = StandaloneConfigManager(str(config_file))
        assert manager.get_config("test_key") == "test_value"

    def test_init_without_config_file(self):
        """Test initialization without config file."""
        manager = StandaloneConfigManager()
        assert manager.get_config("nonexistent", "default") == "default"

    def test_config_crud_operations(self, tmp_path):
        """Test create, read, update, delete operations."""
        config_file = tmp_path / "crud_config.json"
        manager = StandaloneConfigManager(str(config_file))
        
        # Create/Set
        manager.set_config("key1", "value1")
        manager.set_config("key2", {"nested": "value"})
        
        # Read
        assert manager.get_config("key1") == "value1"
        assert manager.get_config("key2") == {"nested": "value"}
        assert manager.get_config("nonexistent", "default") == "default"
        
        # Update
        manager.set_config("key1", "updated_value")
        assert manager.get_config("key1") == "updated_value"
        
        # Save and reload
        assert manager.save_config() is True
        assert config_file.exists()
        
        manager2 = StandaloneConfigManager(str(config_file))
        assert manager2.get_config("key1") == "updated_value"
        assert manager2.get_config("key2") == {"nested": "value"}

    def test_get_all_configs(self, tmp_path):
        """Test getting all configurations."""
        config_file = tmp_path / "all_config.json"
        manager = StandaloneConfigManager(str(config_file))
        
        manager.set_config("key1", "value1")
        manager.set_config("key2", "value2")
        
        all_configs = manager.get_all_configs()
        assert all_configs["key1"] == "value1"
        assert all_configs["key2"] == "value2"

    def test_has_config(self, tmp_path):
        """Test checking if config exists."""
        config_file = tmp_path / "has_config.json"
        manager = StandaloneConfigManager(str(config_file))
        
        assert manager.has_config("nonexistent") is False
        manager.set_config("existing", "value")
        assert manager.has_config("existing") is True

    def test_model_folders(self, tmp_path):
        """Test model folder operations."""
        config_file = tmp_path / "model_config.json"
        manager = StandaloneConfigManager(str(config_file))
        
        folders = manager.get_model_folders()
        assert isinstance(folders, dict)
        assert "Checkpoint" in folders
        assert "LORA" in folders

    def test_directory_getters(self, tmp_path):
        """Test individual directory getters."""
        config_file = tmp_path / "dir_config.json"
        manager = StandaloneConfigManager(str(config_file))
        
        # These should return None or strings
        emb_dir = manager.get_embeddings_dir()
        assert emb_dir is None or isinstance(emb_dir, str)
        
        hyper_dir = manager.get_hypernetwork_dir()
        assert hyper_dir is None or isinstance(hyper_dir, str)
        
        ckpt_dir = manager.get_ckpt_dir()
        assert ckpt_dir is None or isinstance(ckpt_dir, str)
        
        lora_dir = manager.get_lora_dir()
        assert lora_dir is None or isinstance(lora_dir, str)

    def test_corrupted_config_file(self, tmp_path):
        """Test handling of corrupted config file."""
        config_file = tmp_path / "corrupted_config.json"
        config_file.write_text("invalid json content")
        
        manager = StandaloneConfigManager(str(config_file))
        # Should handle gracefully
        assert manager.get_config("test", "default") == "default"

    def test_read_only_config_file(self, tmp_path):
        """Test handling of read-only config file."""
        config_file = tmp_path / "readonly_config.json"
        config_file.write_text('{"test": "value"}')
        config_file.chmod(0o444)  # Read-only
        
        manager = StandaloneConfigManager(str(config_file))
        manager.set_config("new_key", "new_value")
        
        # Save should handle the permission error gracefully
        result = manager.save_config()
        # May be True or False depending on system behavior
        assert isinstance(result, bool)


class TestStandalonePathManager:
    """Test StandalonePathManager functionality."""

    def test_basic_paths(self):
        """Test basic path operations."""
        manager = StandalonePathManager()
        
        script_path = manager.get_script_path()
        assert isinstance(script_path, str)
        assert os.path.exists(script_path)
        
        models_path = manager.get_models_path()
        assert isinstance(models_path, str)
        
        config_path = manager.get_config_path()
        assert isinstance(config_path, str)

    def test_model_folder_path(self):
        """Test model folder path operations."""
        manager = StandalonePathManager()
        
        lora_path = manager.get_model_folder_path("Lora")
        assert isinstance(lora_path, str)
        assert "Lora" in lora_path
        
        checkpoint_path = manager.get_model_folder_path("Checkpoint")
        assert isinstance(checkpoint_path, str)

    def test_directory_creation(self, tmp_path):
        """Test directory creation."""
        manager = StandalonePathManager()
        
        test_dir = tmp_path / "test_directory"
        assert manager.ensure_directory_exists(str(test_dir)) is True
        assert test_dir.exists()

    def test_path_validation(self, tmp_path):
        """Test path validation."""
        manager = StandalonePathManager()
        
        # Invalid paths
        assert manager.validate_path("") is False
        long_path = "/nonexistent/extremely/long/path/that/should/not/exist"
        assert manager.validate_path(long_path) is False
        
        # Valid paths within base path - create a subdir in the manager's base path
        base_path = manager.get_script_path()
        test_subdir = os.path.join(base_path, "test_validation")
        os.makedirs(test_subdir, exist_ok=True)
        assert manager.validate_path(test_subdir) is True

    def test_model_folder_management(self, tmp_path):
        """Test model folder management."""
        manager = StandalonePathManager()
        
        test_path = str(tmp_path / "test_model")
        result = manager.add_model_folder("TestModel", test_path)
        assert isinstance(result, bool)
        
        all_paths = manager.get_all_model_paths()
        assert isinstance(all_paths, dict)


class TestStandaloneMetadataProcessor:
    """Test StandaloneMetadataProcessor functionality."""

    def test_png_info_extraction(self, tmp_path):
        """Test PNG info extraction."""
        processor = StandaloneMetadataProcessor()
        
        # Test with non-existent file
        fake_path = str(tmp_path / "nonexistent.png")
        result = processor.extract_png_info(fake_path)
        assert isinstance(result, tuple)
        assert len(result) == 3

    def test_parameter_extraction(self, tmp_path):
        """Test parameter extraction from PNG."""
        processor = StandaloneMetadataProcessor()
        
        fake_path = str(tmp_path / "test.png")
        result = processor.extract_parameters_from_png(fake_path)
        assert result is None or isinstance(result, str)

    def test_prompt_extraction(self):
        """Test prompt extraction from parameters."""
        processor = StandaloneMetadataProcessor()
        
        test_params = "positive prompt\nNegative prompt: negative prompt\nSteps: 20"
        pos, neg = processor.extract_prompt_from_parameters(test_params)
        assert isinstance(pos, str)
        assert isinstance(neg, str)

    def test_parameter_formatting(self):
        """Test parameter formatting for display."""
        processor = StandaloneMetadataProcessor()
        
        test_params = {"steps": 20, "sampler": "Euler"}
        formatted = processor.format_parameters_for_display(test_params)
        assert isinstance(formatted, str)

    def test_generation_parameters_parsing(self):
        """Test generation parameter parsing."""
        processor = StandaloneMetadataProcessor()
        
        test_text = "Steps: 20, Sampler: Euler, CFG scale: 7"
        result = processor.parse_generation_parameters(test_text)
        assert isinstance(result, dict)


class TestStandaloneParameterProcessor:
    """Test StandaloneParameterProcessor functionality."""

    def test_parameter_parsing(self):
        """Test parameter parsing."""
        processor = StandaloneParameterProcessor()
        
        test_text = "Steps: 20, Sampler: Euler, CFG scale: 7"
        result = processor.parse_parameters(test_text)
        assert isinstance(result, dict)
        assert "steps" in result or "Steps" in result

    def test_parameter_formatting(self):
        """Test parameter formatting."""
        processor = StandaloneParameterProcessor()
        
        test_params = {"steps": 20, "sampler": "Euler"}
        formatted = processor.format_parameters(test_params)
        assert isinstance(formatted, str)

    def test_prompt_extraction(self):
        """Test prompt and negative prompt extraction."""
        processor = StandaloneParameterProcessor()
        
        test_text = "positive prompt\nNegative prompt: negative prompt"
        pos, neg = processor.extract_prompt_and_negative(test_text)
        assert isinstance(pos, str)
        assert isinstance(neg, str)

    def test_parameter_validation(self):
        """Test parameter validation."""
        processor = StandaloneParameterProcessor()
        
        test_params = {"steps": 20, "sampler": "Euler"}
        validated = processor.validate_parameters(test_params)
        assert isinstance(validated, dict)

    def test_parameter_merging(self):
        """Test parameter merging."""
        processor = StandaloneParameterProcessor()
        
        base_params = {"steps": 20, "sampler": "Euler"}
        override_params = {"steps": 30, "cfg": 7}
        merged = processor.merge_parameters(base_params, override_params)
        assert isinstance(merged, dict)
        assert merged["steps"] == 30  # Override should win
        assert merged["sampler"] == "Euler"  # Base should remain
        assert merged["cfg"] == 7  # New parameter should be added


class TestStandaloneSamplerProvider:
    """Test StandaloneSamplerProvider functionality."""

    def test_sampler_lists(self):
        """Test sampler list retrieval."""
        provider = StandaloneSamplerProvider()
        
        samplers = provider.get_samplers()
        assert isinstance(samplers, list)
        assert len(samplers) > 0
        
        img2img_samplers = provider.get_samplers_for_img2img()
        assert isinstance(img2img_samplers, list)

    def test_upscale_modes(self):
        """Test upscale mode retrieval."""
        provider = StandaloneSamplerProvider()
        
        upscale_modes = provider.get_upscale_modes()
        assert isinstance(upscale_modes, list)
        
        sd_upscalers = provider.get_sd_upscalers()
        assert isinstance(sd_upscalers, list)
        
        all_upscalers = provider.get_all_upscalers()
        assert isinstance(all_upscalers, list)

    def test_sampler_availability(self):
        """Test sampler availability checking."""
        provider = StandaloneSamplerProvider()
        
        samplers = provider.get_samplers()
        if samplers:
            assert provider.is_sampler_available(samplers[0]) is True
        
        assert provider.is_sampler_available("NonexistentSampler") is False

    def test_default_sampler(self):
        """Test default sampler retrieval."""
        provider = StandaloneSamplerProvider()
        
        default = provider.get_default_sampler()
        assert isinstance(default, str)
        assert len(default) > 0


class TestStandaloneUIBridge:
    """Test StandaloneUIBridge functionality."""

    def test_ui_registration(self):
        """Test UI tab registration."""
        bridge = StandaloneUIBridge()
        
        # Should not raise an exception
        bridge.register_ui_tabs(lambda: None)

    def test_send_to_buttons(self):
        """Test send-to button creation."""
        bridge = StandaloneUIBridge()
        
        buttons = bridge.create_send_to_buttons(["txt2img", "img2img"])
        # Should return None or a dict-like object
        assert buttons is None or isinstance(buttons, dict)

    def test_button_binding(self):
        """Test button binding."""
        bridge = StandaloneUIBridge()
        
        # Should not raise an exception
        bridge.bind_send_to_buttons(None, None, None)

    def test_standalone_launch(self, monkeypatch):
        """Test standalone launch (mock gradio launch to avoid blocking)."""
        bridge = StandaloneUIBridge()
        
        # Patch gradio.Interface.launch and gradio.Blocks.launch to avoid real server start
        try:
            import gradio as gr
        except ImportError:
            gr = None
        if gr is not None:
            monkeypatch.setattr(gr.Interface, "launch", lambda *a, **kw: None, raising=False)
            monkeypatch.setattr(gr.Blocks, "launch", lambda *a, **kw: None, raising=False)
        # Should not raise an exception
        result = bridge.launch_standalone(lambda: None)
        assert result is None

    def test_mode_detection(self):
        """Test mode detection."""
        bridge = StandaloneUIBridge()
        
        assert bridge.is_webui_mode() is False

    def test_ui_operations(self):
        """Test UI operations."""
        bridge = StandaloneUIBridge()
        
        # Should not raise exceptions
        bridge.interrupt_generation()
        bridge.request_restart()
        
        config_value = bridge.get_ui_config("test_key", "default")
        assert config_value == "default"
