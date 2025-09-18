import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

from app.db.migrations import Migration, MigrationManager, run_migrations, rollback_migrations


class TestMigration:
    """Test migration class"""
    
    def test_migration_creation(self):
        """Test migration creation"""
        up_func = lambda db: None
        down_func = lambda db: None
        
        migration = Migration(
            version="001",
            description="Test migration",
            up_func=up_func,
            down_func=down_func
        )
        
        assert migration.version == "001"
        assert migration.description == "Test migration"
        assert migration.up_func == up_func
        assert migration.down_func == down_func
        assert isinstance(migration.created_at, datetime)


class TestMigrationManager:
    """Test migration manager"""
    
    @pytest.fixture
    def migration_manager(self):
        """Create migration manager instance"""
        return MigrationManager()
    
    @patch('app.db.migrations.get_database')
    async def test_get_current_version_none(self, mock_get_db, migration_manager):
        """Test getting current version when no migrations exist"""
        mock_db = AsyncMock()
        mock_get_db.return_value = mock_db
        mock_db.migrations.find_one.return_value = None
        
        version = await migration_manager._get_current_version(mock_db)
        
        assert version is None
        mock_db.migrations.find_one.assert_called_once()
    
    @patch('app.db.migrations.get_database')
    async def test_get_current_version_exists(self, mock_get_db, migration_manager):
        """Test getting current version when migrations exist"""
        mock_db = AsyncMock()
        mock_get_db.return_value = mock_db
        mock_db.migrations.find_one.return_value = {"version": "002"}
        
        version = await migration_manager._get_current_version(mock_db)
        
        assert version == "002"
    
    @patch('app.db.migrations.get_database')
    async def test_record_migration(self, mock_get_db, migration_manager):
        """Test recording a migration"""
        mock_db = AsyncMock()
        mock_get_db.return_value = mock_db
        
        migration = Migration(
            version="001",
            description="Test migration",
            up_func=lambda db: None
        )
        
        await migration_manager._record_migration(mock_db, migration)
        
        mock_db.migrations.insert_one.assert_called_once()
        call_args = mock_db.migrations.insert_one.call_args[0][0]
        assert call_args["version"] == "001"
        assert call_args["description"] == "Test migration"
        assert "applied_at" in call_args
    
    @patch('app.db.migrations.get_database')
    async def test_remove_migration_record(self, mock_get_db, migration_manager):
        """Test removing a migration record"""
        mock_db = AsyncMock()
        mock_get_db.return_value = mock_db
        
        await migration_manager._remove_migration_record(mock_db, "001")
        
        mock_db.migrations.delete_one.assert_called_once_with({"version": "001"})
    
    @patch('app.db.migrations.get_database')
    async def test_run_migrations_no_current_version(self, mock_get_db, migration_manager):
        """Test running migrations when no current version exists"""
        mock_db = AsyncMock()
        mock_get_db.return_value = mock_db
        mock_db.migrations.find_one.return_value = None
        
        # Mock migration functions
        migration_001_up = AsyncMock()
        migration_002_up = AsyncMock()
        
        # Replace the migration functions
        migration_manager._migration_001_up = migration_001_up
        migration_manager._migration_002_up = migration_002_up
        
        await migration_manager.run_migrations()
        
        # Should run both migrations
        migration_001_up.assert_called_once_with(mock_db)
        migration_002_up.assert_called_once_with(mock_db)
        
        # Should record both migrations
        assert mock_db.migrations.insert_one.call_count == 2
    
    @patch('app.db.migrations.get_database')
    async def test_run_migrations_with_current_version(self, mock_get_db, migration_manager):
        """Test running migrations when current version exists"""
        mock_db = AsyncMock()
        mock_get_db.return_value = mock_db
        mock_db.migrations.find_one.return_value = {"version": "001"}
        
        # Mock migration functions
        migration_001_up = AsyncMock()
        migration_002_up = AsyncMock()
        
        # Replace the migration functions
        migration_manager._migration_001_up = migration_001_up
        migration_manager._migration_002_up = migration_002_up
        
        await migration_manager.run_migrations()
        
        # Should only run migration 002
        migration_001_up.assert_not_called()
        migration_002_up.assert_called_once_with(mock_db)
        
        # Should record only migration 002
        assert mock_db.migrations.insert_one.call_count == 1
    
    @patch('app.db.migrations.get_database')
    async def test_run_migrations_with_target_version(self, mock_get_db, migration_manager):
        """Test running migrations up to target version"""
        mock_db = AsyncMock()
        mock_get_db.return_value = mock_db
        mock_db.migrations.find_one.return_value = None
        
        # Mock migration functions
        migration_001_up = AsyncMock()
        migration_002_up = AsyncMock()
        
        # Replace the migration functions
        migration_manager._migration_001_up = migration_001_up
        migration_manager._migration_002_up = migration_002_up
        
        await migration_manager.run_migrations(target_version="001")
        
        # Should only run migration 001
        migration_001_up.assert_called_once_with(mock_db)
        migration_002_up.assert_not_called()
        
        # Should record only migration 001
        assert mock_db.migrations.insert_one.call_count == 1
    
    @patch('app.db.migrations.get_database')
    async def test_run_migrations_no_migrations_needed(self, mock_get_db, migration_manager):
        """Test running migrations when no migrations are needed"""
        mock_db = AsyncMock()
        mock_get_db.return_value = mock_db
        mock_db.migrations.find_one.return_value = {"version": "002"}
        
        # Mock migration functions
        migration_001_up = AsyncMock()
        migration_002_up = AsyncMock()
        
        # Replace the migration functions
        migration_manager._migration_001_up = migration_001_up
        migration_manager._migration_002_up = migration_002_up
        
        await migration_manager.run_migrations()
        
        # Should not run any migrations
        migration_001_up.assert_not_called()
        migration_002_up.assert_not_called()
        
        # Should not record any migrations
        mock_db.migrations.insert_one.assert_not_called()
    
    @patch('app.db.migrations.get_database')
    async def test_rollback_migration(self, mock_get_db, migration_manager):
        """Test rolling back migrations"""
        mock_db = AsyncMock()
        mock_get_db.return_value = mock_db
        mock_db.migrations.find_one.return_value = {"version": "002"}
        
        # Mock migration functions
        migration_001_down = AsyncMock()
        migration_002_down = AsyncMock()
        
        # Replace the migration functions
        migration_manager._migration_001_down = migration_001_down
        migration_manager._migration_002_down = migration_002_down
        
        await migration_manager.rollback_migration("001")
        
        # Should rollback migration 002 only
        migration_001_down.assert_not_called()
        migration_002_down.assert_called_once_with(mock_db)
        
        # Should remove migration record
        mock_db.migrations.delete_one.assert_called_once_with({"version": "002"})
    
    @patch('app.db.migrations.get_database')
    async def test_rollback_migration_no_rollback_needed(self, mock_get_db, migration_manager):
        """Test rollback when no rollback is needed"""
        mock_db = AsyncMock()
        mock_get_db.return_value = mock_db
        mock_db.migrations.find_one.return_value = {"version": "001"}
        
        # Mock migration functions
        migration_001_down = AsyncMock()
        migration_002_down = AsyncMock()
        
        # Replace the migration functions
        migration_manager._migration_001_down = migration_001_down
        migration_manager._migration_002_down = migration_002_down
        
        await migration_manager.rollback_migration("002")
        
        # Should not rollback any migrations
        migration_001_down.assert_not_called()
        migration_002_down.assert_not_called()
        
        # Should not remove any migration records
        mock_db.migrations.delete_one.assert_not_called()
    
    @patch('app.db.migrations.get_database')
    async def test_migration_001_up(self, mock_get_db, migration_manager):
        """Test migration 001 up function"""
        mock_db = AsyncMock()
        mock_get_db.return_value = mock_db
        mock_db.list_collection_names.return_value = []
        mock_db.create_collection = AsyncMock()
        
        await migration_manager._migration_001_up(mock_db)
        
        # Should create all required collections
        expected_collections = ["workflows", "agents", "debate_threads", "resources", "users", "migrations"]
        assert mock_db.create_collection.call_count == len(expected_collections)
    
    @patch('app.db.migrations.get_database')
    async def test_migration_001_down(self, mock_get_db, migration_manager):
        """Test migration 001 down function"""
        mock_db = AsyncMock()
        mock_get_db.return_value = mock_db
        mock_db.drop_collection = AsyncMock()
        
        await migration_manager._migration_001_down(mock_db)
        
        # Should drop all collections except migrations
        expected_collections = ["workflows", "agents", "debate_threads", "resources", "users"]
        assert mock_db.drop_collection.call_count == len(expected_collections)
    
    @patch('app.db.migrations.get_database')
    async def test_migration_002_up(self, mock_get_db, migration_manager):
        """Test migration 002 up function"""
        mock_db = AsyncMock()
        mock_get_db.return_value = mock_db
        mock_db.agents.update_many = AsyncMock()
        
        await migration_manager._migration_002_up(mock_db)
        
        # Should update agents collection
        mock_db.agents.update_many.assert_called_once()
        call_args = mock_db.agents.update_many.call_args
        assert call_args[0][0] == {"performance_metrics": {"$exists": False}}
        assert call_args[0][1] == {"$set": {"performance_metrics": {}}}
    
    @patch('app.db.migrations.get_database')
    async def test_migration_002_down(self, mock_get_db, migration_manager):
        """Test migration 002 down function"""
        mock_db = AsyncMock()
        mock_get_db.return_value = mock_db
        mock_db.agents.update_many = AsyncMock()
        
        await migration_manager._migration_002_down(mock_db)
        
        # Should remove performance_metrics field
        mock_db.agents.update_many.assert_called_once()
        call_args = mock_db.agents.update_many.call_args
        assert call_args[0][0] == {}
        assert call_args[0][1] == {"$unset": {"performance_metrics": ""}}


@patch('app.db.migrations.migration_manager')
async def test_run_migrations_function(mock_migration_manager):
    """Test run_migrations function"""
    mock_migration_manager.run_migrations = AsyncMock()
    
    await run_migrations("001")
    
    mock_migration_manager.run_migrations.assert_called_once_with("001")


@patch('app.db.migrations.migration_manager')
async def test_rollback_migrations_function(mock_migration_manager):
    """Test rollback_migrations function"""
    mock_migration_manager.rollback_migration = AsyncMock()
    
    await rollback_migrations("001")
    
    mock_migration_manager.rollback_migration.assert_called_once_with("001")