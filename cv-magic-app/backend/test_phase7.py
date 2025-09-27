#!/usr/bin/env python3
"""
Test script for Phase 7: Advanced Features & API Optimization
"""
import requests
import json
import sys
import time
from datetime import datetime
from typing import Dict, Any

# Configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api"

def print_test_header(test_name):
    """Print test header"""
    print(f"\n{'='*60}")
    print(f"🧪 TESTING: {test_name}")
    print(f"{'='*60}")

def print_result(success, message):
    """Print test result"""
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status}: {message}")

def get_auth_token():
    """Get authentication token"""
    login_data = {
        "email": "test@example.com",
        "password": "testpassword123"
    }
    
    try:
        response = requests.post(
            f"{API_BASE}/auth/login",
            json=login_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            return data['access_token']
        else:
            print(f"Login failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Login error: {e}")
        return None

def get_admin_token():
    """Get admin authentication token"""
    login_data = {
        "email": "admin@cvapp.com",
        "password": "admin123"
    }
    
    try:
        response = requests.post(
            f"{API_BASE}/auth/admin/login",
            json=login_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            return data['access_token']
        else:
            print(f"Admin login failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Admin login error: {e}")
        return None

def test_server_connection():
    """Test if server is running"""
    print_test_header("Server Connection")
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        if response.status_code == 200:
            print_result(True, "Server is running")
            return True
        else:
            print_result(False, f"Server returned status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print_result(False, f"Server connection failed: {e}")
        return False

def test_advanced_features_endpoints(token):
    """Test advanced features endpoints"""
    print_test_header("Advanced Features Endpoints")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    endpoints = [
        ("/advanced/statistics", "GET", "User Statistics"),
        ("/advanced/search", "POST", "Search Files"),
        ("/advanced/bulk-upload", "POST", "Bulk Upload"),
        ("/advanced/bulk-delete", "POST", "Bulk Delete"),
        ("/advanced/bulk-export", "POST", "Bulk Export")
    ]
    
    results = []
    
    for endpoint, method, name in endpoints:
        try:
            if method == "GET":
                response = requests.get(f"{API_BASE}{endpoint}", headers=headers, timeout=10)
            elif method == "POST":
                # Use appropriate test data for each endpoint
                test_data = get_test_data_for_endpoint(endpoint)
                response = requests.post(f"{API_BASE}{endpoint}", json=test_data, headers=headers, timeout=10)
            
            if response.status_code in [200, 201]:
                print_result(True, f"{name} accessible")
                results.append(True)
            else:
                print_result(False, f"{name} failed: {response.status_code}")
                results.append(False)
                
        except Exception as e:
            print_result(False, f"{name} error: {e}")
            results.append(False)
    
    return all(results)

def get_test_data_for_endpoint(endpoint):
    """Get test data for specific endpoints"""
    if endpoint == "/advanced/search":
        return {
            "query": "test",
            "file_types": ["pdf", "docx"],
            "date_range": {
                "start_date": "2024-01-01",
                "end_date": "2024-12-31"
            }
        }
    elif endpoint == "/advanced/bulk-upload":
        return {
            "files": [
                {"filename": "test1.pdf", "size": 1024, "type": "pdf"},
                {"filename": "test2.docx", "size": 2048, "type": "docx"}
            ]
        }
    elif endpoint == "/advanced/bulk-delete":
        return {
            "file_ids": ["file1", "file2"]
        }
    elif endpoint == "/advanced/bulk-export":
        return {
            "data_types": ["profile", "files", "activity"]
        }
    else:
        return {}

def test_optimized_api_endpoints(token):
    """Test optimized API endpoints"""
    print_test_header("Optimized API Endpoints")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    endpoints = [
        ("/optimized/user/files", "GET", "Optimized User Files"),
        ("/optimized/user/analytics", "GET", "Optimized User Analytics"),
        ("/optimized/search/global", "GET", "Global Search")
    ]
    
    results = []
    
    for endpoint, method, name in endpoints:
        try:
            if method == "GET":
                response = requests.get(f"{API_BASE}{endpoint}", headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                source = data.get('source', 'unknown')
                print_result(True, f"{name} accessible (source: {source})")
                results.append(True)
            else:
                print_result(False, f"{name} failed: {response.status_code}")
                results.append(False)
                
        except Exception as e:
            print_result(False, f"{name} error: {e}")
            results.append(False)
    
    return all(results)

def test_cache_functionality(admin_token):
    """Test cache functionality"""
    print_test_header("Cache Functionality")
    
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    try:
        # Test cache statistics
        response = requests.get(f"{API_BASE}/advanced/cache/stats", headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            cache_stats = data.get('cache_stats', {})
            print_result(True, f"Cache stats accessible: {cache_stats.get('connected', False)}")
        else:
            print_result(False, f"Cache stats failed: {response.status_code}")
            return False
        
        # Test cache clear
        response = requests.post(f"{API_BASE}/advanced/cache/clear", headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            cleared_count = data.get('cleared_count', 0)
            print_result(True, f"Cache clear successful: {cleared_count} entries cleared")
        else:
            print_result(False, f"Cache clear failed: {response.status_code}")
            return False
        
        return True
        
    except Exception as e:
        print_result(False, f"Cache functionality error: {e}")
        return False

def test_performance_monitoring(admin_token):
    """Test performance monitoring"""
    print_test_header("Performance Monitoring")
    
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    try:
        # Test performance metrics
        response = requests.get(f"{API_BASE}/advanced/performance/metrics", headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            metrics = data.get('performance_metrics', {})
            print_result(True, f"Performance metrics accessible: {len(metrics)} operations tracked")
        else:
            print_result(False, f"Performance metrics failed: {response.status_code}")
            return False
        
        # Test optimization recommendations
        response = requests.get(f"{API_BASE}/advanced/performance/recommendations", headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            recommendations = data.get('recommendations', [])
            print_result(True, f"Optimization recommendations: {len(recommendations)} recommendations")
        else:
            print_result(False, f"Optimization recommendations failed: {response.status_code}")
            return False
        
        return True
        
    except Exception as e:
        print_result(False, f"Performance monitoring error: {e}")
        return False

def test_optimized_api_performance(token):
    """Test optimized API performance"""
    print_test_header("Optimized API Performance")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        # Test multiple requests to measure performance
        start_time = time.time()
        
        for i in range(5):
            response = requests.get(f"{API_BASE}/optimized/user/files", headers=headers, timeout=10)
            if response.status_code != 200:
                print_result(False, f"Request {i+1} failed: {response.status_code}")
                return False
        
        end_time = time.time()
        avg_response_time = (end_time - start_time) / 5
        
        if avg_response_time < 1.0:  # Less than 1 second average
            print_result(True, f"Optimized API performance: {avg_response_time:.3f}s average")
            return True
        else:
            print_result(False, f"Optimized API too slow: {avg_response_time:.3f}s average")
            return False
        
    except Exception as e:
        print_result(False, f"Optimized API performance error: {e}")
        return False

def test_system_analytics(admin_token):
    """Test system analytics"""
    print_test_header("System Analytics")
    
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    try:
        # Test system analytics
        response = requests.get(f"{API_BASE}/advanced/analytics", headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            analytics = data.get('analytics', {})
            print_result(True, f"System analytics accessible: {analytics.get('users', {}).get('total_users', 0)} users")
            return True
        else:
            print_result(False, f"System analytics failed: {response.status_code}")
            return False
        
    except Exception as e:
        print_result(False, f"System analytics error: {e}")
        return False

def test_optimization_status(admin_token):
    """Test optimization status"""
    print_test_header("Optimization Status")
    
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    try:
        # Test optimization status
        response = requests.get(f"{API_BASE}/optimized/optimization/status", headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            optimization_score = data.get('optimization_score', 0)
            print_result(True, f"Optimization status: {optimization_score}% score")
            return True
        else:
            print_result(False, f"Optimization status failed: {response.status_code}")
            return False
        
    except Exception as e:
        print_result(False, f"Optimization status error: {e}")
        return False

def test_performance_health(admin_token):
    """Test performance health"""
    print_test_header("Performance Health")
    
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    try:
        # Test performance health
        response = requests.get(f"{API_BASE}/optimized/performance/health", headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            health_score = data.get('health_score', 0)
            health_status = data.get('health_status', 'unknown')
            print_result(True, f"Performance health: {health_score}% ({health_status})")
            return True
        else:
            print_result(False, f"Performance health failed: {response.status_code}")
            return False
        
    except Exception as e:
        print_result(False, f"Performance health error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 PHASE 7 TESTING: Advanced Features & API Optimization")
    print(f"Testing at: {BASE_URL}")
    print(f"Timestamp: {datetime.now()}")
    
    # Test results
    results = []
    
    # 1. Test server connection
    if not test_server_connection():
        print("\n❌ Server is not running. Please start the server first.")
        sys.exit(1)
    
    # 2. Get authentication tokens
    token = get_auth_token()
    admin_token = get_admin_token()
    
    if not token:
        print("\n❌ Authentication failed. Please ensure test user exists.")
        sys.exit(1)
    
    # 3. Test advanced features endpoints
    advanced_features_result = test_advanced_features_endpoints(token)
    results.append(("Advanced Features Endpoints", advanced_features_result))
    
    # 4. Test optimized API endpoints
    optimized_api_result = test_optimized_api_endpoints(token)
    results.append(("Optimized API Endpoints", optimized_api_result))
    
    # 5. Test optimized API performance
    optimized_performance_result = test_optimized_api_performance(token)
    results.append(("Optimized API Performance", optimized_performance_result))
    
    # 6. Test system analytics
    if admin_token:
        system_analytics_result = test_system_analytics(admin_token)
        results.append(("System Analytics", system_analytics_result))
    else:
        results.append(("System Analytics", False))
    
    # 7. Test cache functionality
    if admin_token:
        cache_functionality_result = test_cache_functionality(admin_token)
        results.append(("Cache Functionality", cache_functionality_result))
    else:
        results.append(("Cache Functionality", False))
    
    # 8. Test performance monitoring
    if admin_token:
        performance_monitoring_result = test_performance_monitoring(admin_token)
        results.append(("Performance Monitoring", performance_monitoring_result))
    else:
        results.append(("Performance Monitoring", False))
    
    # 9. Test optimization status
    if admin_token:
        optimization_status_result = test_optimization_status(admin_token)
        results.append(("Optimization Status", optimization_status_result))
    else:
        results.append(("Optimization Status", False))
    
    # 10. Test performance health
    if admin_token:
        performance_health_result = test_performance_health(admin_token)
        results.append(("Performance Health", performance_health_result))
    else:
        results.append(("Performance Health", False))
    
    # Print summary
    print_test_header("TEST SUMMARY")
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
        if result:
            passed += 1
    
    print(f"\n📊 RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Phase 7 implementation is working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the implementation.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
