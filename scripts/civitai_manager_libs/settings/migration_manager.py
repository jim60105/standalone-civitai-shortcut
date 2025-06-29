"""
Migration Manager Module

Handles configuration and data migration between different versions
of the application.
"""

import json
import os
from typing import Any, Dict, List, Optional
from ..logging_config import get_logger
from ..error_handler import with_error_handling
from .defaults import Defaults

logger = get_logger(__name__)


class MigrationManager:
    """Manages data and configuration migrations."""

    def __init__(self, data_dir: str = None):
        """
        Initialize migration manager.

        Args:
            data_dir: Path to data directory
        """
        self.data_dir = data_dir or Defaults.DATA_DIR
        self.migration_log_path = os.path.join(self.data_dir, 'migrations.log')
        self._migrations = self._get_available_migrations()

    @with_error_handling("Failed to run migrations")
    def run_migrations(self, target_version: str = None) -> bool:
        """
        Run all pending migrations.

        Args:
            target_version: Target version to migrate to

        Returns:
            bool: True if successful, False otherwise
        """
        current_version = self._get_current_version()
        applied_migrations = self._get_applied_migrations()

        logger.info(f"Current version: {current_version}")
        logger.info(f"Target version: {target_version or 'latest'}")

        migrations_to_run = self._get_migrations_to_run(
            current_version, target_version, applied_migrations
        )

        if not migrations_to_run:
            logger.info("No migrations to run")
            return True

        logger.info(f"Running {len(migrations_to_run)} migrations")

        for migration in migrations_to_run:
            try:
                result = self._run_migration(migration)
                if not result:
                    logger.error(f"Migration {migration['version']} failed")
                    return False
                self._log_migration(migration)
            except Exception as e:
                logger.error(f"Migration {migration['version']} failed with error: {e}")
                return False

        logger.info("All migrations completed successfully")
        return True

    def _get_current_version(self) -> str:
        """
        Get current application version.

        Returns:
            str: Current version
        """
        try:
            version_file = os.path.join(self.data_dir, 'version.txt')
            if os.path.exists(version_file):
                with open(version_file, 'r') as file:
                    return file.read().strip()
        except Exception:
            pass
        return '0.0.0'

    def _get_applied_migrations(self) -> List[str]:
        """
        Get list of applied migrations.

        Returns:
            List[str]: List of applied migration versions
        """
        applied = []
        try:
            if os.path.exists(self.migration_log_path):
                with open(self.migration_log_path, 'r') as file:
                    for line in file:
                        if line.strip():
                            parts = line.strip().split('\t')
                            if len(parts) >= 2:
                                applied.append(parts[1])
        except Exception as e:
            logger.warning(f"Could not read migration log: {e}")
        return applied

    def _log_migration(self, migration: Dict[str, Any]) -> None:
        """
        Log completed migration.

        Args:
            migration: Migration details
        """
        try:
            os.makedirs(os.path.dirname(self.migration_log_path), exist_ok=True)
            with open(self.migration_log_path, 'a') as file:
                import datetime

                timestamp = datetime.datetime.now().isoformat()
                file.write(f"{timestamp}\t{migration['version']}\t{migration['name']}\n")
        except Exception as e:
            logger.warning(f"Could not log migration: {e}")

    def _get_migrations_to_run(
        self, current_version: str, target_version: Optional[str], applied_migrations: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Get list of migrations to run.

        Args:
            current_version: Current version
            target_version: Target version
            applied_migrations: Already applied migrations

        Returns:
            List[Dict[str, Any]]: Migrations to run
        """
        migrations = []
        for migration in self._migrations:
            # Skip already applied migrations
            if migration['version'] in applied_migrations:
                continue

            # Check if migration should be applied
            if self._should_apply_migration(migration, current_version, target_version):
                migrations.append(migration)

        # Sort by version
        migrations.sort(key=lambda x: self._version_to_tuple(x['version']))
        return migrations

    def _should_apply_migration(
        self, migration: Dict[str, Any], current_version: str, target_version: Optional[str]
    ) -> bool:
        """
        Check if migration should be applied.

        Args:
            migration: Migration details
            current_version: Current version
            target_version: Target version

        Returns:
            bool: True if should apply, False otherwise
        """
        migration_version = migration['version']

        # Migration version should be greater than current
        if self._version_to_tuple(migration_version) <= self._version_to_tuple(current_version):
            return False

        # If target version specified, migration should be less than or equal to target
        if target_version:
            if self._version_to_tuple(migration_version) > self._version_to_tuple(target_version):
                return False

        return True

    def _version_to_tuple(self, version: str) -> tuple:
        """
        Convert version string to tuple for comparison.

        Args:
            version: Version string

        Returns:
            tuple: Version tuple
        """
        try:
            return tuple(map(int, version.split('.')))
        except Exception:
            return (0, 0, 0)

    def _run_migration(self, migration: Dict[str, Any]) -> bool:
        """
        Run a single migration.

        Args:
            migration: Migration details

        Returns:
            bool: True if successful, False otherwise
        """
        migration_func = migration.get('function')
        if not migration_func:
            logger.error(f"No migration function for {migration['version']}")
            return False

        try:
            logger.info(f"Running migration {migration['version']}: {migration['name']}")
            result = migration_func()
            if result:
                logger.info(f"Migration {migration['version']} completed")
            return result
        except Exception as e:
            logger.error(f"Migration {migration['version']} failed: {e}")
            return False

    def _get_available_migrations(self) -> List[Dict[str, Any]]:
        """
        Get list of available migrations.

        Returns:
            List[Dict[str, Any]]: Available migrations
        """
        return [
            {
                'version': '1.0.0',
                'name': 'Initial data structure setup',
                'function': self._migrate_1_0_0,
            },
            {
                'version': '1.1.0',
                'name': 'Add new configuration options',
                'function': self._migrate_1_1_0,
            },
            {
                'version': '1.2.0',
                'name': 'Update model data format',
                'function': self._migrate_1_2_0,
            },
            {
                'version': '2.0.0',
                'name': 'Major structure refactoring',
                'function': self._migrate_2_0_0,
            },
        ]

    def _migrate_1_0_0(self) -> bool:
        """
        Migration to version 1.0.0 - Initial setup.

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Create necessary directories
            directories = [
                self.data_dir,
                os.path.join(self.data_dir, 'models'),
                os.path.join(self.data_dir, 'cache'),
                os.path.join(self.data_dir, 'thumbnails'),
            ]

            for directory in directories:
                os.makedirs(directory, exist_ok=True)

            # Create initial configuration files
            config_files = {
                'settings.json': self._get_default_settings(),
                'models.json': [],
                'classifications.json': {},
            }

            for filename, content in config_files.items():
                filepath = os.path.join(self.data_dir, filename)
                if not os.path.exists(filepath):
                    with open(filepath, 'w') as file:
                        json.dump(content, file, indent=2)

            return True
        except Exception as e:
            logger.error(f"Migration 1.0.0 failed: {e}")
            return False

    def _migrate_1_1_0(self) -> bool:
        """
        Migration to version 1.1.0 - Add new configuration options.

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            settings_file = os.path.join(self.data_dir, 'settings.json')
            if os.path.exists(settings_file):
                with open(settings_file, 'r') as file:
                    settings = json.load(file)

                # Add new configuration options
                new_options = {
                    'ui': {'auto_refresh': True, 'show_nsfw': False},
                    'cache': {'enable': True, 'max_age_days': 30},
                }

                settings.update(new_options)

                with open(settings_file, 'w') as file:
                    json.dump(settings, file, indent=2)

            return True
        except Exception as e:
            logger.error(f"Migration 1.1.0 failed: {e}")
            return False

    def _migrate_1_2_0(self) -> bool:
        """
        Migration to version 1.2.0 - Update model data format.

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            models_file = os.path.join(self.data_dir, 'models.json')
            if os.path.exists(models_file):
                with open(models_file, 'r') as file:
                    models = json.load(file)

                # Update model data format
                updated_models = []
                for model in models:
                    if isinstance(model, dict):
                        # Add new fields if missing
                        if 'metadata' not in model:
                            model['metadata'] = {}
                        if 'tags' not in model:
                            model['tags'] = []
                        if 'stats' not in model:
                            model['stats'] = {
                                'downloadCount': 0,
                                'favoriteCount': 0,
                                'commentCount': 0,
                                'ratingCount': 0,
                                'rating': 0,
                            }
                        updated_models.append(model)

                with open(models_file, 'w') as file:
                    json.dump(updated_models, file, indent=2)

            return True
        except Exception as e:
            logger.error(f"Migration 1.2.0 failed: {e}")
            return False

    def _migrate_2_0_0(self) -> bool:
        """
        Migration to version 2.0.0 - Major structure refactoring.

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # This would handle major structural changes
            # For now, just ensure all necessary directories exist
            new_directories = [
                os.path.join(self.data_dir, 'recipes'),
                os.path.join(self.data_dir, 'galleries'),
                os.path.join(self.data_dir, 'shortcuts'),
            ]

            for directory in new_directories:
                os.makedirs(directory, exist_ok=True)

            return True
        except Exception as e:
            logger.error(f"Migration 2.0.0 failed: {e}")
            return False

    def _get_default_settings(self) -> Dict[str, Any]:
        """
        Get default settings for initial setup.

        Returns:
            Dict[str, Any]: Default settings
        """
        return {
            'civitai': {'api_key': '', 'base_url': 'https://civitai.com/api/v1'},
            'paths': {'models_dir': 'models', 'cache_dir': 'cache', 'data_dir': 'data'},
            'ui': {'theme': 'default', 'max_results': 50},
        }

    def create_backup(self, backup_path: Optional[str] = None) -> bool:
        """
        Create backup of data directory.

        Args:
            backup_path: Path for backup

        Returns:
            bool: True if successful, False otherwise
        """
        if backup_path is None:
            import datetime

            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = f"{self.data_dir}_backup_{timestamp}"

        try:
            import shutil

            shutil.copytree(self.data_dir, backup_path)
            logger.info(f"Backup created at {backup_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to create backup: {e}")
            return False

    def restore_backup(self, backup_path: str) -> bool:
        """
        Restore from backup.

        Args:
            backup_path: Path to backup

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            import shutil

            if os.path.exists(self.data_dir):
                shutil.rmtree(self.data_dir)
            shutil.copytree(backup_path, self.data_dir)
            logger.info(f"Restored from backup {backup_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to restore backup: {e}")
            return False
