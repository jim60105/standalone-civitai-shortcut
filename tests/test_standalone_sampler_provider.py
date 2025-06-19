"""
Unit tests for StandaloneSamplerProvider (scripts/civitai_manager_libs/compat/standalone_adapters/standalone_sampler_provider.py)
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))
import unittest
from civitai_manager_libs.compat.standalone_adapters.standalone_sampler_provider import (
    StandaloneSamplerProvider,
)


class TestStandaloneSamplerProvider(unittest.TestCase):
    def setUp(self):
        self.provider = StandaloneSamplerProvider()

    def test_get_samplers(self):
        samplers = self.provider.get_samplers()
        self.assertIsInstance(samplers, list)
        self.assertTrue(any(isinstance(s, str) for s in samplers))

    def test_get_samplers_for_img2img(self):
        samplers = self.provider.get_samplers_for_img2img()
        self.assertIsInstance(samplers, list)

    def test_get_upscale_modes(self):
        modes = self.provider.get_upscale_modes()
        self.assertIsInstance(modes, list)

    def test_get_sd_upscalers(self):
        upscalers = self.provider.get_sd_upscalers()
        self.assertIsInstance(upscalers, list)

    def test_get_all_upscalers(self):
        all_upscalers = self.provider.get_all_upscalers()
        self.assertIsInstance(all_upscalers, list)
        self.assertGreaterEqual(len(all_upscalers), len(self.provider.get_upscale_modes()))

    def test_is_sampler_available(self):
        samplers = self.provider.get_samplers()
        if samplers:
            self.assertTrue(self.provider.is_sampler_available(samplers[0]))
        self.assertFalse(self.provider.is_sampler_available('NonExistentSampler'))

    def test_get_default_sampler(self):
        default = self.provider.get_default_sampler()
        self.assertIsInstance(default, str)
        self.assertTrue(self.provider.is_sampler_available(default))

    def test_get_sampler_info_and_aliases(self):
        samplers = self.provider.get_samplers()
        if samplers:
            info = self.provider.get_sampler_info(samplers[0])
            self.assertIsInstance(info, dict)
            aliases = self.provider.get_sampler_aliases(samplers[0])
            self.assertIsInstance(aliases, list)

    def test_validate_sampler(self):
        samplers = self.provider.get_samplers()
        if samplers:
            self.assertTrue(self.provider.validate_sampler(samplers[0]))
        self.assertFalse(self.provider.validate_sampler('NonExistentSampler'))

    def test_normalize_sampler_name(self):
        samplers = self.provider.get_samplers()
        if samplers:
            norm = self.provider.normalize_sampler_name(samplers[0])
            self.assertIsInstance(norm, str)


if __name__ == '__main__':
    unittest.main()
