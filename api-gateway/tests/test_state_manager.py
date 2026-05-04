import pytest
import sys
import os
import json

# Mock redis before importing state_manager
sys.modules['redis'] = MockRedis()

from unittest.mock import Mock, AsyncMock, patch


class MockRedis:
    """Mock async redis client."""
    def __init__(self):
        self.data = {}
        
    def from_url(self, url):
        return MockAsyncRedis()


class MockAsyncRedis:
    """Mock async redis for testing."""
    def __init__(self):
        self.data = {}
        
    async def get(self, key):
        return self.data.get(key)
        
    async def set(self, key, value):
        self.data[key] = value
        
    async def delete(self, key):
        if key in self.data:
            del self.data[key]


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))


class TestStateManager:
    """Tests for StateManager class."""
    
    @pytest.fixture
    def state_manager(self):
        # Import without connecting to real redis
        with patch('redis.asyncio.from_url') as mock_redis:
            mock_redis.return_value = MockAsyncRedis()
            from src.state_manager import StateManager
            return StateManager()
    
    def test_state_manager_initialization(self, state_manager):
        """Test state manager initializes."""
        assert state_manager is not None
    
    @pytest.mark.asyncio
    async def test_get_system_state_default(self, state_manager):
        """Test get_system_state returns default structure."""
        # Mock redis to return nothing
        with patch.object(state_manager.redis, 'get', return_value=None):
            state = await state_manager.get_system_state()
            
            assert 'tracks' in state
            assert 'threats' in state
            assert 'assignments' in state
            assert 'systemHealth' in state
            assert 'metrics' in state
    
    @pytest.mark.asyncio
    async def test_get_system_state_with_data(self, state_manager):
        """Test get_system_state returns stored data."""
        test_data = {
            "tracks": {"TRK-001": {"track_id": "TRK-001", "pos_x": 100}},
            "threats": [],
            "assignments": [],
            "systemHealth": {},
            "metrics": {}
        }
        
        with patch.object(state_manager.redis, 'get', return_value=json.dumps(test_data)):
            state = await state_manager.get_system_state()
            
            assert 'TRK-001' in state['tracks']
            assert state['tracks']['TRK-001']['pos_x'] == 100
    
    @pytest.mark.asyncio
    async def test_update_module_health(self, state_manager):
        """Test update_module_health updates state."""
        with patch.object(state_manager.redis, 'get', return_value=None), \
             patch.object(state_manager.redis, 'set', return_value=None):
            
            await state_manager.update_module_health('sim-engine', 'online')
            
            # Should have been called
            
    @pytest.mark.asyncio
    async def test_default_tracks_is_dict(self, state_manager):
        """Test default tracks is a dictionary."""
        with patch.object(state_manager.redis, 'get', return_value=None):
            state = await state_manager.get_system_state()
            
            assert isinstance(state['tracks'], dict)
    
    @pytest.mark.asyncio
    async def test_default_threats_is_list(self, state_manager):
        """Test default threats is a list."""
        with patch.object(state_manager.redis, 'get', return_value=None):
            state = await state_manager.get_system_state()
            
            assert isinstance(state['threats'], list)
    
    @pytest.mark.asyncio
    async def test_default_assignments_is_list(self, state_manager):
        """Test default assignments is a list."""
        with patch.object(state_manager.redis, 'get', return_value=None):
            state = await state_manager.get_system_state()
            
            assert isinstance(state['assignments'], list)


class TestRedisConnection:
    """Tests for Redis connection string."""
    
    def test_default_redis_url(self):
        """Test default Redis URL."""
        # The URL should be configurable via environment
        import os
        
        # Clear any existing var
        if 'REDIS_URL' in os.environ:
            del os.environ['REDIS_URL']
        
        # Default should be localhost
        from src.state_manager import REDIS_URL
        
        assert 'redis://localhost:6379' in REDIS_URL or REDIS_URL == 'redis://localhost:6379'