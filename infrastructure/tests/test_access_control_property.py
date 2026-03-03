"""
Property-Based Test for Access Control

**Validates: Requirements 7.4**

This test validates Property 14: Access Control
"For any data access request, the system should prevent unauthorized access 
to user data and forecasting results"

The test verifies:
1. Unauthorized requests (no token) are rejected
2. Invalid/expired tokens are rejected
3. Users can only access their own data
4. Cross-user data access is prevented
5. JWT token validation works correctly
"""

import json
import time
import jwt
from typing import Dict, Optional
from hypothesis import given, strategies as st, settings, assume
from hypothesis import HealthCheck
import boto3
from botocore.exceptions import ClientError
import pytest


# ===== Test Configuration =====

# JWT secret for testing (in production, this comes from Cognito)
TEST_JWT_SECRET = "test-secret-key-for-access-control-testing"
TEST_USER_POOL_ID = "us-east-1_TestPool"
TEST_CLIENT_ID = "test-client-id"


# ===== Strategies for Property-Based Testing =====

@st.composite
def user_id_strategy(draw):
    """Generate valid user IDs"""
    return f"user-{draw(st.integers(min_value=1, max_value=1000))}"


@st.composite
def jwt_token_strategy(draw, user_id: Optional[str] = None, expired: bool = False, invalid: bool = False):
    """Generate JWT tokens with various validity states"""
    if user_id is None:
        user_id = draw(user_id_strategy())
    
    # Token expiration time
    if expired:
        exp_time = int(time.time()) - 3600  # Expired 1 hour ago
    else:
        exp_time = int(time.time()) + 3600  # Valid for 1 hour
    
    payload = {
        "sub": user_id,
        "email": f"{user_id}@example.com",
        "cognito:username": user_id,
        "exp": exp_time,
        "iat": int(time.time()),
        "token_use": "access"
    }
    
    if invalid:
        # Create token with wrong secret
        token = jwt.encode(payload, "wrong-secret", algorithm="HS256")
    else:
        token = jwt.encode(payload, TEST_JWT_SECRET, algorithm="HS256")
    
    return token


@st.composite
def data_access_request_strategy(draw):
    """Generate data access requests"""
    user_id = draw(user_id_strategy())
    resource_type = draw(st.sampled_from(["user_profile", "forecast", "risk_assessment"]))
    resource_id = f"{user_id}#{draw(st.text(min_size=1, max_size=20, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'))))}"
    
    return {
        "user_id": user_id,
        "resource_type": resource_type,
        "resource_id": resource_id
    }


# ===== Mock AWS Services =====

class MockDynamoDBService:
    """Mock DynamoDB service for testing"""
    
    def __init__(self):
        self.tables = {
            "VyaparSaathi-UserProfiles": {},
            "VyaparSaathi-Forecasts": {},
        }
    
    def put_item(self, table_name: str, item: Dict):
        """Store item in mock table"""
        if table_name not in self.tables:
            raise ValueError(f"Table {table_name} does not exist")
        
        user_id = item.get("userId")
        if not user_id:
            raise ValueError("userId is required")
        
        self.tables[table_name][user_id] = item
    
    def get_item(self, table_name: str, user_id: str) -> Optional[Dict]:
        """Retrieve item from mock table"""
        if table_name not in self.tables:
            raise ValueError(f"Table {table_name} does not exist")
        
        return self.tables[table_name].get(user_id)


# ===== Access Control Implementation =====

class AccessControlValidator:
    """
    Access control validator that enforces authorization rules
    
    This simulates the access control logic that would be implemented
    in API Gateway authorizers and Lambda functions
    """
    
    def __init__(self, jwt_secret: str):
        self.jwt_secret = jwt_secret
        self.db_service = MockDynamoDBService()
    
    def validate_token(self, token: str) -> Optional[Dict]:
        """
        Validate JWT token and extract user information
        
        Returns user info if valid, None if invalid
        """
        try:
            # Decode and verify token
            payload = jwt.decode(
                token,
                self.jwt_secret,
                algorithms=["HS256"],
                options={"verify_exp": True}
            )
            
            return {
                "user_id": payload.get("sub"),
                "email": payload.get("email"),
                "username": payload.get("cognito:username")
            }
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
        except Exception:
            return None
    
    def check_resource_access(self, user_id: str, resource_type: str, resource_id: str) -> bool:
        """
        Check if user has access to the requested resource
        
        Returns True if access is allowed, False otherwise
        """
        # Extract owner user_id from resource_id
        # Resource IDs are formatted as "userId#resourceIdentifier"
        if "#" in resource_id:
            resource_owner = resource_id.split("#")[0]
        else:
            resource_owner = resource_id
        
        # User can only access their own resources
        return user_id == resource_owner
    
    def authorize_request(self, token: Optional[str], resource_type: str, resource_id: str) -> Dict:
        """
        Authorize a data access request
        
        Returns authorization result with status and reason
        """
        # No token provided
        if not token:
            return {
                "authorized": False,
                "reason": "No authentication token provided",
                "status_code": 401
            }
        
        # Validate token
        user_info = self.validate_token(token)
        if not user_info:
            return {
                "authorized": False,
                "reason": "Invalid or expired authentication token",
                "status_code": 401
            }
        
        user_id = user_info["user_id"]
        
        # Check resource access
        has_access = self.check_resource_access(user_id, resource_type, resource_id)
        if not has_access:
            return {
                "authorized": False,
                "reason": "Access denied: insufficient permissions",
                "status_code": 403
            }
        
        # Access granted
        return {
            "authorized": True,
            "user_id": user_id,
            "status_code": 200
        }


# ===== Property-Based Tests =====

@pytest.fixture
def access_control():
    """Fixture providing access control validator"""
    return AccessControlValidator(TEST_JWT_SECRET)


@given(user_id=user_id_strategy())
@settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_property_unauthorized_requests_rejected(user_id):
    """
    Property 14.1: Unauthorized requests without tokens are rejected
    
    **Validates: Requirements 7.4**
    
    For any data access request without an authentication token,
    the system should reject the request with 401 status
    """
    access_control = AccessControlValidator(TEST_JWT_SECRET)
    
    # Request without token
    result = access_control.authorize_request(
        token=None,
        resource_type="user_profile",
        resource_id=f"{user_id}#profile"
    )
    
    # Should be rejected
    assert result["authorized"] is False
    assert result["status_code"] == 401
    assert "authentication" in result["reason"].lower()


@given(user_id=user_id_strategy())
@settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_property_expired_tokens_rejected(user_id):
    """
    Property 14.2: Expired tokens are rejected
    
    **Validates: Requirements 7.4**
    
    For any data access request with an expired token,
    the system should reject the request with 401 status
    """
    access_control = AccessControlValidator(TEST_JWT_SECRET)
    
    # Create expired token
    expired_token = jwt.encode(
        {
            "sub": user_id,
            "exp": int(time.time()) - 3600,  # Expired 1 hour ago
            "iat": int(time.time()) - 7200,
            "token_use": "access"
        },
        TEST_JWT_SECRET,
        algorithm="HS256"
    )
    
    # Request with expired token
    result = access_control.authorize_request(
        token=expired_token,
        resource_type="user_profile",
        resource_id=f"{user_id}#profile"
    )
    
    # Should be rejected
    assert result["authorized"] is False
    assert result["status_code"] == 401


@given(user_id=user_id_strategy())
@settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_property_invalid_tokens_rejected(user_id):
    """
    Property 14.3: Invalid tokens are rejected
    
    **Validates: Requirements 7.4**
    
    For any data access request with an invalid token (wrong signature),
    the system should reject the request with 401 status
    """
    access_control = AccessControlValidator(TEST_JWT_SECRET)
    
    # Create token with wrong secret
    invalid_token = jwt.encode(
        {
            "sub": user_id,
            "exp": int(time.time()) + 3600,
            "iat": int(time.time()),
            "token_use": "access"
        },
        "wrong-secret-key",
        algorithm="HS256"
    )
    
    # Request with invalid token
    result = access_control.authorize_request(
        token=invalid_token,
        resource_type="user_profile",
        resource_id=f"{user_id}#profile"
    )
    
    # Should be rejected
    assert result["authorized"] is False
    assert result["status_code"] == 401


@given(
    owner_id=user_id_strategy(),
    requester_id=user_id_strategy()
)
@settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_property_users_access_own_data_only(owner_id, requester_id):
    """
    Property 14.4: Users can only access their own data
    
    **Validates: Requirements 7.4**
    
    For any data access request, users should only be able to access
    resources that belong to them. Cross-user access should be denied.
    """
    # Skip if same user (that's a valid access case)
    assume(owner_id != requester_id)
    
    access_control = AccessControlValidator(TEST_JWT_SECRET)
    
    # Create valid token for requester
    token = jwt.encode(
        {
            "sub": requester_id,
            "exp": int(time.time()) + 3600,
            "iat": int(time.time()),
            "token_use": "access"
        },
        TEST_JWT_SECRET,
        algorithm="HS256"
    )
    
    # Try to access another user's resource
    result = access_control.authorize_request(
        token=token,
        resource_type="forecast",
        resource_id=f"{owner_id}#forecast-123"
    )
    
    # Should be denied with 403 Forbidden
    assert result["authorized"] is False
    assert result["status_code"] == 403
    assert "access denied" in result["reason"].lower() or "permission" in result["reason"].lower()


@given(user_id=user_id_strategy())
@settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_property_valid_token_grants_own_resource_access(user_id):
    """
    Property 14.5: Valid tokens grant access to own resources
    
    **Validates: Requirements 7.4**
    
    For any data access request with a valid token accessing the user's
    own resources, the system should grant access
    """
    access_control = AccessControlValidator(TEST_JWT_SECRET)
    
    # Create valid token
    token = jwt.encode(
        {
            "sub": user_id,
            "exp": int(time.time()) + 3600,
            "iat": int(time.time()),
            "token_use": "access"
        },
        TEST_JWT_SECRET,
        algorithm="HS256"
    )
    
    # Access own resource
    result = access_control.authorize_request(
        token=token,
        resource_type="user_profile",
        resource_id=f"{user_id}#profile"
    )
    
    # Should be granted
    assert result["authorized"] is True
    assert result["status_code"] == 200
    assert result["user_id"] == user_id


@given(
    user_id=user_id_strategy(),
    resource_type=st.sampled_from(["user_profile", "forecast", "risk_assessment"])
)
@settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_property_access_control_consistent_across_resource_types(user_id, resource_type):
    """
    Property 14.6: Access control is consistent across all resource types
    
    **Validates: Requirements 7.4**
    
    For any resource type (user_profile, forecast, risk_assessment),
    the same access control rules should apply consistently
    """
    access_control = AccessControlValidator(TEST_JWT_SECRET)
    
    # Create valid token
    token = jwt.encode(
        {
            "sub": user_id,
            "exp": int(time.time()) + 3600,
            "iat": int(time.time()),
            "token_use": "access"
        },
        TEST_JWT_SECRET,
        algorithm="HS256"
    )
    
    # Access own resource of any type
    result = access_control.authorize_request(
        token=token,
        resource_type=resource_type,
        resource_id=f"{user_id}#resource-123"
    )
    
    # Should always be granted for own resources
    assert result["authorized"] is True
    assert result["status_code"] == 200


@given(
    user_id=user_id_strategy(),
    other_user_id=user_id_strategy(),
    resource_type=st.sampled_from(["user_profile", "forecast", "risk_assessment"])
)
@settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_property_cross_user_access_always_denied(user_id, other_user_id, resource_type):
    """
    Property 14.7: Cross-user data access is always denied
    
    **Validates: Requirements 7.4**
    
    For any combination of users and resource types, a user should never
    be able to access another user's data, regardless of resource type
    """
    # Skip if same user
    assume(user_id != other_user_id)
    
    access_control = AccessControlValidator(TEST_JWT_SECRET)
    
    # Create valid token for user
    token = jwt.encode(
        {
            "sub": user_id,
            "exp": int(time.time()) + 3600,
            "iat": int(time.time()),
            "token_use": "access"
        },
        TEST_JWT_SECRET,
        algorithm="HS256"
    )
    
    # Try to access other user's resource
    result = access_control.authorize_request(
        token=token,
        resource_type=resource_type,
        resource_id=f"{other_user_id}#resource-456"
    )
    
    # Should always be denied
    assert result["authorized"] is False
    assert result["status_code"] == 403


# ===== Integration Test Scenarios =====

def test_scenario_complete_access_control_flow():
    """
    Integration scenario: Complete access control flow
    
    Tests a realistic scenario with multiple users and resources
    """
    access_control = AccessControlValidator(TEST_JWT_SECRET)
    
    # User 1 creates a forecast
    user1_id = "user-1"
    user1_token = jwt.encode(
        {"sub": user1_id, "exp": int(time.time()) + 3600, "iat": int(time.time())},
        TEST_JWT_SECRET,
        algorithm="HS256"
    )
    
    # User 1 can access their own forecast
    result = access_control.authorize_request(
        token=user1_token,
        resource_type="forecast",
        resource_id=f"{user1_id}#forecast-abc"
    )
    assert result["authorized"] is True
    
    # User 2 tries to access User 1's forecast
    user2_id = "user-2"
    user2_token = jwt.encode(
        {"sub": user2_id, "exp": int(time.time()) + 3600, "iat": int(time.time())},
        TEST_JWT_SECRET,
        algorithm="HS256"
    )
    
    result = access_control.authorize_request(
        token=user2_token,
        resource_type="forecast",
        resource_id=f"{user1_id}#forecast-abc"
    )
    assert result["authorized"] is False
    assert result["status_code"] == 403
    
    # User 2 can access their own data
    result = access_control.authorize_request(
        token=user2_token,
        resource_type="user_profile",
        resource_id=f"{user2_id}#profile"
    )
    assert result["authorized"] is True


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])
