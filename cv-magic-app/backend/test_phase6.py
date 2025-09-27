#!/usr/bin/env python3
"""
Test script for Phase 6: Production Deployment & Monitoring
"""
import requests
import json
import sys
import time
import os
from datetime import datetime
from pathlib import Path

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

def test_health_check():
    """Test health check endpoint"""
    print_test_header("Health Check Endpoint")
    
    try:
        response = requests.get(f"{BASE_URL}/monitoring/health", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print_result(True, f"Health check passed: {data.get('status', 'unknown')}")
            return True
        else:
            print_result(False, f"Health check failed: {response.status_code} - {response.text}")
            return False
        
    except Exception as e:
        print_result(False, f"Health check error: {e}")
        return False

def test_monitoring_endpoints(admin_token):
    """Test monitoring endpoints"""
    print_test_header("Monitoring Endpoints")
    
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    endpoints = [
        ("/monitoring/health/detailed", "Detailed Health Check"),
        ("/monitoring/metrics", "Current Metrics"),
        ("/monitoring/status", "Application Status"),
        ("/monitoring/alerts", "Current Alerts")
    ]
    
    results = []
    
    for endpoint, name in endpoints:
        try:
            response = requests.get(f"{API_BASE}{endpoint}", headers=headers, timeout=10)
            
            if response.status_code == 200:
                print_result(True, f"{name} accessible")
                results.append(True)
            else:
                print_result(False, f"{name} failed: {response.status_code}")
                results.append(False)
                
        except Exception as e:
            print_result(False, f"{name} error: {e}")
            results.append(False)
    
    return all(results)

def test_metrics_collection(admin_token):
    """Test metrics collection"""
    print_test_header("Metrics Collection")
    
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    try:
        # Test manual metrics collection
        response = requests.post(f"{API_BASE}/monitoring/metrics/collect", headers=headers, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            print_result(True, "Metrics collection successful")
            return True
        else:
            print_result(False, f"Metrics collection failed: {response.status_code} - {response.text}")
            return False
        
    except Exception as e:
        print_result(False, f"Metrics collection error: {e}")
        return False

def test_logging_system():
    """Test logging system"""
    print_test_header("Logging System")
    
    try:
        # Check if log files exist
        log_files = [
            "/app/logs/app.log",
            "/app/logs/error.log", 
            "/app/logs/security.log"
        ]
        
        existing_logs = []
        for log_file in log_files:
            if os.path.exists(log_file):
                existing_logs.append(log_file)
        
        if existing_logs:
            print_result(True, f"Log files found: {len(existing_logs)}")
            return True
        else:
            print_result(False, "No log files found")
            return False
        
    except Exception as e:
        print_result(False, f"Logging system test error: {e}")
        return False

def test_production_config():
    """Test production configuration"""
    print_test_header("Production Configuration")
    
    try:
        # Check if production config exists
        config_files = [
            "deployment_config.json",
            "Dockerfile",
            "docker-compose.prod.yml"
        ]
        
        existing_configs = []
        for config_file in config_files:
            if os.path.exists(config_file):
                existing_configs.append(config_file)
        
        if existing_configs:
            print_result(True, f"Production configs found: {len(existing_configs)}")
            return True
        else:
            print_result(False, "Production configs not found")
            return False
        
    except Exception as e:
        print_result(False, f"Production config test error: {e}")
        return False

def test_deployment_scripts():
    """Test deployment scripts"""
    print_test_header("Deployment Scripts")
    
    try:
        # Check if deployment scripts exist
        script_files = [
            "scripts/deploy.py",
            "scripts/maintenance.py"
        ]
        
        existing_scripts = []
        for script_file in script_files:
            if os.path.exists(script_file):
                existing_scripts.append(script_file)
        
        if existing_scripts:
            print_result(True, f"Deployment scripts found: {len(existing_scripts)}")
            return True
        else:
            print_result(False, "Deployment scripts not found")
            return False
        
    except Exception as e:
        print_result(False, f"Deployment scripts test error: {e}")
        return False

def test_monitoring_integration():
    """Test monitoring integration"""
    print_test_header("Monitoring Integration")
    
    try:
        # Test if monitoring service is working
        response = requests.get(f"{API_BASE}/monitoring/status", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if 'application' in data and 'system' in data:
                print_result(True, "Monitoring integration working")
                return True
            else:
                print_result(False, "Monitoring data incomplete")
                return False
        else:
            print_result(False, f"Monitoring integration failed: {response.status_code}")
            return False
        
    except Exception as e:
        print_result(False, f"Monitoring integration error: {e}")
        return False

def test_security_monitoring(admin_token):
    """Test security monitoring"""
    print_test_header("Security Monitoring")
    
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    try:
        # Test security endpoints
        response = requests.get(f"{API_BASE}/security/security-stats", headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            stats = data.get('stats', {})
            print_result(True, f"Security monitoring working: {stats.get('total_active_sessions', 0)} sessions")
            return True
        else:
            print_result(False, f"Security monitoring failed: {response.status_code}")
            return False
        
    except Exception as e:
        print_result(False, f"Security monitoring error: {e}")
        return False

def test_performance_monitoring():
    """Test performance monitoring"""
    print_test_header("Performance Monitoring")
    
    try:
        # Test multiple requests to measure performance
        start_time = time.time()
        
        for i in range(10):
            response = requests.get(f"{BASE_URL}/", timeout=5)
            if response.status_code != 200:
                print_result(False, f"Request {i+1} failed: {response.status_code}")
                return False
        
        end_time = time.time()
        avg_response_time = (end_time - start_time) / 10
        
        if avg_response_time < 2.0:  # Less than 2 seconds average
            print_result(True, f"Performance monitoring: {avg_response_time:.3f}s average")
            return True
        else:
            print_result(False, f"Performance too slow: {avg_response_time:.3f}s average")
            return False
        
    except Exception as e:
        print_result(False, f"Performance monitoring error: {e}")
        return False

def test_docker_configuration():
    """Test Docker configuration"""
    print_test_header("Docker Configuration")
    
    try:
        # Check if Docker files exist
        docker_files = [
            "Dockerfile",
            "docker-compose.prod.yml"
        ]
        
        existing_docker = []
        for docker_file in docker_files:
            if os.path.exists(docker_file):
                existing_docker.append(docker_file)
        
        if existing_docker:
            print_result(True, f"Docker configs found: {len(existing_docker)}")
            return True
        else:
            print_result(False, "Docker configs not found")
            return False
        
    except Exception as e:
        print_result(False, f"Docker configuration test error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 PHASE 6 TESTING: Production Deployment & Monitoring")
    print(f"Testing at: {BASE_URL}")
    print(f"Timestamp: {datetime.now()}")
    
    # Test results
    results = []
    
    # 1. Test server connection
    if not test_server_connection():
        print("\n❌ Server is not running. Please start the server first.")
        sys.exit(1)
    
    # 2. Test health check
    health_check_result = test_health_check()
    results.append(("Health Check", health_check_result))
    
    # 3. Test production configuration
    production_config_result = test_production_config()
    results.append(("Production Configuration", production_config_result))
    
    # 4. Test deployment scripts
    deployment_scripts_result = test_deployment_scripts()
    results.append(("Deployment Scripts", deployment_scripts_result))
    
    # 5. Test Docker configuration
    docker_config_result = test_docker_configuration()
    results.append(("Docker Configuration", docker_config_result))
    
    # 6. Test logging system
    logging_system_result = test_logging_system()
    results.append(("Logging System", logging_system_result))
    
    # 7. Test monitoring integration
    monitoring_integration_result = test_monitoring_integration()
    results.append(("Monitoring Integration", monitoring_integration_result))
    
    # 8. Test performance monitoring
    performance_monitoring_result = test_performance_monitoring()
    results.append(("Performance Monitoring", performance_monitoring_result))
    
    # 9. Get admin token for protected endpoints
    admin_token = get_admin_token()
    
    if admin_token:
        # 10. Test monitoring endpoints
        monitoring_endpoints_result = test_monitoring_endpoints(admin_token)
        results.append(("Monitoring Endpoints", monitoring_endpoints_result))
        
        # 11. Test metrics collection
        metrics_collection_result = test_metrics_collection(admin_token)
        results.append(("Metrics Collection", metrics_collection_result))
        
        # 12. Test security monitoring
        security_monitoring_result = test_security_monitoring(admin_token)
        results.append(("Security Monitoring", security_monitoring_result))
    else:
        results.append(("Monitoring Endpoints", False))
        results.append(("Metrics Collection", False))
        results.append(("Security Monitoring", False))
    
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
        print("🎉 ALL TESTS PASSED! Phase 6 implementation is working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the implementation.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
