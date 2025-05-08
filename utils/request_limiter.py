import logging
import time
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Dict, Tuple, List

logger = logging.getLogger(__name__)

# Store usage limits: IP+User Agent -> [(timestamp, count), ...]
# Using in-memory storage for simplicity; in production, use Redis or database
usage_tracker = defaultdict(list)

# Maximum allowed requests per user
MAX_REQUESTS = 10

# Time window for tracking (24 hours)
TIME_WINDOW = 24 * 60 * 60  # seconds

class RequestLimiter:
    @staticmethod
    def get_client_identifier(request) -> str:
        """Create a unique identifier based on IP and user agent"""
        ip = request.remote_addr
        user_agent = request.headers.get('User-Agent', 'Unknown')
        # Create a simple hash for the client
        return f"{ip}_{hash(user_agent)}"

    @staticmethod
    def can_make_request(request) -> Tuple[bool, int]:
        """
        Check if the client can make a request based on their usage.
        Returns (allowed, requests_remaining)
        """
        client_id = RequestLimiter.get_client_identifier(request)
        now = time.time()
        
        # Remove old entries beyond the time window
        current_usage = usage_tracker[client_id]
        current_usage = [entry for entry in current_usage if now - entry[0] < TIME_WINDOW]
        usage_tracker[client_id] = current_usage
        
        # Count requests in the time window
        request_count = len(current_usage)
        
        # Check if user has hit the limit
        if request_count >= MAX_REQUESTS:
            logger.warning(f"Request limit reached for client {client_id}")
            return False, 0
        
        # Update usage tracker with the current request
        usage_tracker[client_id].append((now, request_count + 1))
        
        # Return allowed status and remaining requests
        return True, MAX_REQUESTS - (request_count + 1)

    @staticmethod
    def get_usage_data() -> Dict[str, List[Tuple[datetime, int]]]:
        """Get all usage data for debugging"""
        return {k: [(datetime.fromtimestamp(ts), count) for ts, count in v] 
                for k, v in usage_tracker.items()}
                
    @staticmethod
    def reset_for_client(request) -> None:
        """Reset usage for a specific client - for testing only"""
        client_id = RequestLimiter.get_client_identifier(request)
        if client_id in usage_tracker:
            del usage_tracker[client_id]
            
    @staticmethod
    def get_remaining_requests(request) -> int:
        """Get remaining requests for a client"""
        client_id = RequestLimiter.get_client_identifier(request)
        now = time.time()
        
        # Remove old entries beyond the time window
        current_usage = usage_tracker.get(client_id, [])
        current_usage = [entry for entry in current_usage if now - entry[0] < TIME_WINDOW]
        
        if not current_usage:
            return MAX_REQUESTS
            
        # Count requests in the time window
        request_count = len(current_usage)
        return max(0, MAX_REQUESTS - request_count)