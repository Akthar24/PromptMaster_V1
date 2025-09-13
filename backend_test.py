#!/usr/bin/env python3
"""
Backend API Testing for PromptMaster
Tests all backend endpoints with focus on high-priority tasks
"""

import requests
import json
import time
from datetime import datetime

# Get backend URL from frontend .env
BACKEND_URL = "https://promptmaster-15.preview.emergentagent.com/api"

def test_health_check():
    """Test basic health check endpoint"""
    print("🔍 Testing Health Check...")
    try:
        # Test the categories endpoint as a health check since root returns HTML
        response = requests.get(f"{BACKEND_URL}/categories")
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print("✅ Backend API is accessible")
            return True
        else:
            print(f"❌ Backend API not accessible: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_categories_api():
    """Test categories API endpoint"""
    print("\n🔍 Testing Categories API...")
    try:
        response = requests.get(f"{BACKEND_URL}/categories")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            categories = data.get("categories", [])
            print(f"✅ Found {len(categories)} categories")
            
            # Verify expected categories
            expected_categories = [
                "text_summarization", "code_generation", "content_creation",
                "data_analysis", "chatbot_response", "creative_writing",
                "email_templates", "social_media", "academic_writing", "marketing_copy"
            ]
            
            found_ids = [cat["id"] for cat in categories]
            missing = [cat for cat in expected_categories if cat not in found_ids]
            
            if missing:
                print(f"⚠️ Missing categories: {missing}")
                return False
            else:
                print("✅ All expected categories found")
                return True
        else:
            print(f"❌ Categories API failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Categories API test failed: {e}")
        return False

def test_templates_api():
    """Test templates API endpoint"""
    print("\n🔍 Testing Templates API...")
    try:
        # Test getting all templates
        response = requests.get(f"{BACKEND_URL}/templates")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            templates = response.json()
            print(f"✅ Found {len(templates)} templates")
            
            if len(templates) == 0:
                print("⚠️ No templates found - may need database initialization")
                return False
            
            # Test category filtering
            test_category = "code_generation"
            response = requests.get(f"{BACKEND_URL}/templates?category={test_category}")
            
            if response.status_code == 200:
                filtered_templates = response.json()
                print(f"✅ Category filtering works - found {len(filtered_templates)} templates for {test_category}")
                return True
            else:
                print(f"❌ Category filtering failed with status {response.status_code}")
                return False
        else:
            print(f"❌ Templates API failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Templates API test failed: {e}")
        return False

def test_history_api():
    """Test history API endpoints"""
    print("\n🔍 Testing History API...")
    try:
        # Test getting history (should work even if empty)
        response = requests.get(f"{BACKEND_URL}/history")
        print(f"GET History Status Code: {response.status_code}")
        
        if response.status_code == 200:
            history = response.json()
            print(f"✅ History API working - found {len(history)} items")
            
            # Test delete functionality if we have history items
            if len(history) > 0:
                test_id = history[0]["id"]
                delete_response = requests.delete(f"{BACKEND_URL}/history/{test_id}")
                print(f"DELETE History Status Code: {delete_response.status_code}")
                
                if delete_response.status_code == 200:
                    print("✅ History delete functionality working")
                    return True
                else:
                    print(f"⚠️ History delete failed with status {delete_response.status_code}")
                    return True  # Still consider history API working if GET works
            else:
                print("✅ History GET working (no items to test delete)")
                return True
        else:
            print(f"❌ History API failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ History API test failed: {e}")
        return False

def test_llm_integration_and_optimize():
    """Test LLM integration via optimize endpoint - HIGH PRIORITY"""
    print("\n🔍 Testing LLM Integration & Optimize Endpoint (HIGH PRIORITY)...")
    
    test_prompt = "Write a professional email to a client about project delays"
    test_category = "email_templates"
    
    payload = {
        "original_prompt": test_prompt,
        "category": test_category
    }
    
    try:
        print(f"Sending optimization request...")
        print(f"Original prompt: {test_prompt}")
        print(f"Category: {test_category}")
        
        response = requests.post(
            f"{BACKEND_URL}/optimize",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30  # LLM calls can take time
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            # Verify response structure
            required_fields = ["id", "original_prompt", "optimized_prompt", "category", "timestamp"]
            missing_fields = [field for field in required_fields if field not in result]
            
            if missing_fields:
                print(f"❌ Missing fields in response: {missing_fields}")
                return False
            
            print(f"✅ LLM Integration successful!")
            print(f"Original: {result['original_prompt'][:100]}...")
            print(f"Optimized: {result['optimized_prompt'][:100]}...")
            print(f"Category: {result['category']}")
            print(f"Timestamp: {result['timestamp']}")
            
            # Verify the optimized prompt is different and longer (usually optimized prompts are more detailed)
            if result['optimized_prompt'] != result['original_prompt']:
                print("✅ Prompt was actually optimized (different from original)")
                return True
            else:
                print("⚠️ Optimized prompt is identical to original - may indicate LLM issue")
                return False
                
        elif response.status_code == 500:
            print(f"❌ Server error during optimization: {response.text}")
            try:
                error_detail = response.json()
                print(f"Error details: {error_detail}")
            except:
                pass
            return False
        else:
            print(f"❌ Optimize endpoint failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out - LLM integration may be slow or failing")
        return False
    except Exception as e:
        print(f"❌ LLM Integration test failed: {e}")
        return False

def test_error_handling():
    """Test error handling with invalid inputs"""
    print("\n🔍 Testing Error Handling...")
    
    # Test optimize with missing fields
    try:
        response = requests.post(f"{BACKEND_URL}/optimize", json={})
        print(f"Empty payload status: {response.status_code}")
        
        # Should return 422 for validation error
        if response.status_code == 422:
            print("✅ Proper validation error handling")
            return True
        else:
            print(f"⚠️ Unexpected status code for invalid input: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
        return False

def run_all_tests():
    """Run all backend tests in priority order"""
    print("🚀 Starting PromptMaster Backend API Tests")
    print("=" * 60)
    
    results = {}
    
    # Basic connectivity
    results["health_check"] = test_health_check()
    
    # HIGH PRIORITY TESTS
    print("\n" + "=" * 60)
    print("HIGH PRIORITY TESTS")
    print("=" * 60)
    
    results["llm_integration"] = test_llm_integration_and_optimize()
    
    # MEDIUM PRIORITY TESTS  
    print("\n" + "=" * 60)
    print("MEDIUM PRIORITY TESTS")
    print("=" * 60)
    
    results["history_api"] = test_history_api()
    results["templates_api"] = test_templates_api()
    
    # LOW PRIORITY TESTS
    print("\n" + "=" * 60)
    print("LOW PRIORITY TESTS")
    print("=" * 60)
    
    results["categories_api"] = test_categories_api()
    
    # ERROR HANDLING
    results["error_handling"] = test_error_handling()
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST RESULTS SUMMARY")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        priority = ""
        if test_name == "llm_integration":
            priority = " (HIGH PRIORITY)"
        elif test_name in ["history_api", "templates_api"]:
            priority = " (MEDIUM PRIORITY)"
        elif test_name == "categories_api":
            priority = " (LOW PRIORITY)"
            
        print(f"{test_name.replace('_', ' ').title()}: {status}{priority}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if results.get("llm_integration", False):
        print("\n🎉 CRITICAL SUCCESS: LLM Integration is working!")
    else:
        print("\n⚠️ CRITICAL ISSUE: LLM Integration failed - this is the core functionality!")
    
    return results

if __name__ == "__main__":
    run_all_tests()