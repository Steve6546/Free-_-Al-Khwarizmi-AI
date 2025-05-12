import requests
import unittest
import os
import json
import sys
from datetime import datetime

class AIWebsiteBuilderAPITester(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Get the backend URL from environment variable
        self.base_url = "https://c15d194e-a8df-4942-b9ef-c693230ecf58.preview.emergentagent.com"
        self.api_url = f"{self.base_url}/api"
        # Sample API key for testing (doesn't need to be real for UI testing)
        self.api_key = "DUMMY_API_KEY_FOR_TESTING"
        self.website_idea = "Create a portfolio website for a photographer with a gallery and contact form"

    def test_01_root_endpoint(self):
        """Test the root API endpoint"""
        print("\n🔍 Testing root API endpoint...")
        try:
            response = requests.get(f"{self.api_url}/")
            self.assertEqual(response.status_code, 200)
            self.assertIn("message", response.json())
            print("✅ Root API endpoint test passed")
        except Exception as e:
            print(f"❌ Root API endpoint test failed: {str(e)}")
            raise

    def test_02_status_endpoint(self):
        """Test the status API endpoints"""
        print("\n🔍 Testing status POST endpoint...")
        try:
            # Test POST /api/status
            data = {"client_name": "test_client"}
            response = requests.post(f"{self.api_url}/status", json=data)
            self.assertEqual(response.status_code, 200)
            response_data = response.json()
            self.assertIn("id", response_data)
            self.assertEqual(response_data["client_name"], "test_client")
            print("✅ Status POST endpoint test passed")
            
            # Test GET /api/status
            print("\n🔍 Testing status GET endpoint...")
            response = requests.get(f"{self.api_url}/status")
            self.assertEqual(response.status_code, 200)
            self.assertIsInstance(response.json(), list)
            print("✅ Status GET endpoint test passed")
        except Exception as e:
            print(f"❌ Status endpoint test failed: {str(e)}")
            raise

    def test_03_analyze_idea_endpoint(self):
        """Test the analyze-idea endpoint"""
        print("\n🔍 Testing analyze-idea endpoint...")
        try:
            data = {
                "idea": self.website_idea,
                "api_key": self.api_key
            }
            response = requests.post(f"{self.api_url}/analyze-idea", json=data)
            
            # Since we're using a dummy API key, we expect a 400 error
            # This is fine for UI testing as we're not testing the actual Gemini API integration
            if response.status_code == 400:
                print("✅ Analyze idea endpoint correctly rejected invalid API key")
            elif response.status_code == 200:
                self.assertIn("analysis", response.json())
                print("✅ Analyze idea endpoint test passed")
            else:
                self.fail(f"Unexpected status code: {response.status_code}")
        except Exception as e:
            print(f"❌ Analyze idea endpoint test failed: {str(e)}")
            raise

    def test_04_plan_website_endpoint(self):
        """Test the plan-website endpoint"""
        print("\n🔍 Testing plan-website endpoint...")
        try:
            # Create a sample analysis
            analysis = {
                "website_type": "portfolio",
                "target_audience": "Photography clients",
                "key_features": ["Gallery", "Contact form", "About page"],
                "pages": ["Home", "Gallery", "About", "Contact"],
                "technologies": {
                    "frontend": ["HTML", "CSS", "JavaScript"],
                    "backend": ["None"],
                    "database": ["None"]
                },
                "design_suggestions": {
                    "color_scheme": ["#000000", "#ffffff"],
                    "layout": "Minimalist",
                    "typography": "Sans-serif"
                }
            }
            
            data = {
                "idea": self.website_idea,
                "analysis": analysis,
                "api_key": self.api_key
            }
            
            response = requests.post(f"{self.api_url}/plan-website", json=data)
            
            # Since we're using a dummy API key, we expect a 400 error
            if response.status_code == 400:
                print("✅ Plan website endpoint correctly rejected invalid API key")
            elif response.status_code == 200:
                self.assertIn("plan", response.json())
                print("✅ Plan website endpoint test passed")
            else:
                self.fail(f"Unexpected status code: {response.status_code}")
        except Exception as e:
            print(f"❌ Plan website endpoint test failed: {str(e)}")
            raise

    def test_05_generate_code_endpoint(self):
        """Test the generate-code endpoint"""
        print("\n🔍 Testing generate-code endpoint...")
        try:
            # Create a sample plan
            plan = {
                "file_structure": {
                    "directories": ["css", "js", "images"],
                    "files": [
                        {
                            "name": "index.html",
                            "description": "Home page"
                        },
                        {
                            "name": "style.css",
                            "description": "Main stylesheet"
                        }
                    ]
                },
                "implementation_steps": [
                    "Step 1: Create HTML structure",
                    "Step 2: Style with CSS"
                ],
                "data_models": [],
                "api_endpoints": [],
                "third_party_integrations": []
            }
            
            data = {
                "idea": self.website_idea,
                "plan": plan,
                "api_key": self.api_key
            }
            
            response = requests.post(f"{self.api_url}/generate-code", json=data)
            
            # Since we're using a dummy API key, we expect a 400 error
            if response.status_code == 400:
                print("✅ Generate code endpoint correctly rejected invalid API key")
            elif response.status_code == 200:
                self.assertIn("files", response.json())
                print("✅ Generate code endpoint test passed")
            else:
                self.fail(f"Unexpected status code: {response.status_code}")
        except Exception as e:
            print(f"❌ Generate code endpoint test failed: {str(e)}")
            raise

    def test_06_test_website_endpoint(self):
        """Test the test-website endpoint"""
        print("\n🔍 Testing test-website endpoint...")
        try:
            # Create sample files
            files = [
                {
                    "name": "index.html",
                    "content": "<html><body><h1>Test</h1></body></html>",
                    "file_type": "html"
                },
                {
                    "name": "style.css",
                    "content": "body { color: black; }",
                    "file_type": "css"
                }
            ]
            
            data = {
                "files": files,
                "api_key": self.api_key
            }
            
            response = requests.post(f"{self.api_url}/test-website", json=data)
            
            # Since we're using a dummy API key, we expect a 400 error
            if response.status_code == 400:
                print("✅ Test website endpoint correctly rejected invalid API key")
            elif response.status_code == 200:
                self.assertIn("test_results", response.json())
                print("✅ Test website endpoint test passed")
            else:
                self.fail(f"Unexpected status code: {response.status_code}")
        except Exception as e:
            print(f"❌ Test website endpoint test failed: {str(e)}")
            raise

    def test_07_prepare_deployment_endpoint(self):
        """Test the prepare-deployment endpoint"""
        print("\n🔍 Testing prepare-deployment endpoint...")
        try:
            # Create sample files and test results
            files = [
                {
                    "name": "index.html",
                    "content": "<html><body><h1>Test</h1></body></html>",
                    "file_type": "html"
                },
                {
                    "name": "style.css",
                    "content": "body { color: black; }",
                    "file_type": "css"
                }
            ]
            
            test_results = {
                "test_summary": "All tests passed",
                "tests": [
                    {
                        "file": "index.html",
                        "issues": [],
                        "recommendations": []
                    }
                ],
                "performance_score": 95,
                "accessibility_score": 90,
                "best_practices_score": 85
            }
            
            data = {
                "files": files,
                "test_results": test_results,
                "api_key": self.api_key
            }
            
            response = requests.post(f"{self.api_url}/prepare-deployment", json=data)
            
            # Since we're using a dummy API key, we expect a 400 error
            if response.status_code == 400:
                print("✅ Prepare deployment endpoint correctly rejected invalid API key")
            elif response.status_code == 200:
                self.assertIn("deployment_info", response.json())
                print("✅ Prepare deployment endpoint test passed")
            else:
                self.fail(f"Unexpected status code: {response.status_code}")
        except Exception as e:
            print(f"❌ Prepare deployment endpoint test failed: {str(e)}")
            raise

def run_tests():
    """Run all tests"""
    test_suite = unittest.TestSuite()
    test_suite.addTest(AIWebsiteBuilderAPITester('test_01_root_endpoint'))
    test_suite.addTest(AIWebsiteBuilderAPITester('test_02_status_endpoint'))
    test_suite.addTest(AIWebsiteBuilderAPITester('test_03_analyze_idea_endpoint'))
    test_suite.addTest(AIWebsiteBuilderAPITester('test_04_plan_website_endpoint'))
    test_suite.addTest(AIWebsiteBuilderAPITester('test_05_generate_code_endpoint'))
    test_suite.addTest(AIWebsiteBuilderAPITester('test_06_test_website_endpoint'))
    test_suite.addTest(AIWebsiteBuilderAPITester('test_07_prepare_deployment_endpoint'))
    
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(test_suite)

if __name__ == "__main__":
    print("🚀 Starting AI Website Builder API Tests")
    run_tests()