# Postman Testing Guide for JD Analysis API

## 🚀 Server Setup

First, make sure your Flask server is running:
```bash
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Base URL:** `http://localhost:8000`

## 📋 Postman Collection Setup

### 1. Create New Collection
- Open Postman
- Click "New" → "Collection"
- Name: "JD Analysis API Tests"
- Description: "Test collection for Job Description Analysis endpoints"

### 2. Set Collection Variables
Go to Collection → Variables tab and add:
```
base_url: http://localhost:8000
auth_token: your_bearer_token_here
company_name: Australia_for_UNHCR
```

## 🔐 Authentication Setup

**Note:** You'll need a valid Bearer token. If you don't have one, you can:
1. Use the auth endpoints to get a token first
2. Or temporarily modify the routes to skip auth for testing

### Option 1: Get Auth Token First
```http
POST {{base_url}}/api/auth/login
Content-Type: application/json

{
  "username": "your_username",
  "password": "your_password"
}
```

### Option 2: Skip Auth for Testing (Temporary)
Comment out the auth verification in the routes for testing.

---

## 📝 API Endpoint Tests

### 1. **Analyze Job Description** 
```http
POST {{base_url}}/api/analyze-jd/{{company_name}}
```

**Headers:**
```
Authorization: Bearer {{auth_token}}
Content-Type: application/json
```

**Body (JSON):**
```json
{
  "force_refresh": false,
  "temperature": 0.3
}
```

**Expected Response:**
```json
{
  "success": true,
  "message": "Job description analysis completed for Australia_for_UNHCR",
  "data": {
    "company_name": "Australia_for_UNHCR",
    "required_keywords": ["SQL", "Power BI", "Excel", ...],
    "preferred_keywords": ["Tableau", "Python", ...],
    "all_keywords": [...],
    "experience_years": 2,
    "analysis_timestamp": "2025-09-10T11:56:10.590499",
    "ai_model_used": "openai/gpt-4o",
    "processing_status": "completed",
    "from_cache": false
  },
  "metadata": {
    "analysis_duration": "N/A",
    "ai_service_status": {...},
    "saved_path": "/path/to/jd_analysis.json"
  }
}
```

---

### 2. **Get Saved Analysis**
```http
GET {{base_url}}/api/jd-analysis/{{company_name}}
```

**Headers:**
```
Authorization: Bearer {{auth_token}}
```

**Expected Response:**
```json
{
  "success": true,
  "message": "Analysis results retrieved for Australia_for_UNHCR",
  "data": {
    "company_name": "Australia_for_UNHCR",
    "required_keywords": ["SQL", "Power BI", "Excel"],
    "preferred_keywords": ["Tableau", "Python"],
    "all_keywords": ["SQL", "Power BI", "Excel", "Tableau", "Python"],
    "experience_years": 2,
    "analysis_timestamp": "2025-09-10T11:56:10.590499",
    "ai_model_used": "openai/gpt-4o",
    "processing_status": "completed"
  },
  "metadata": {
    "from_cache": true,
    "analysis_age": "N/A"
  }
}
```

---

### 3. **Get Keywords Only (All)**
```http
GET {{base_url}}/api/jd-analysis/{{company_name}}/keywords?keyword_type=all
```

**Headers:**
```
Authorization: Bearer {{auth_token}}
```

**Expected Response:**
```json
{
  "success": true,
  "message": "Retrieved all keywords for Australia_for_UNHCR",
  "data": {
    "company_name": "Australia_for_UNHCR",
    "keyword_type": "all",
    "keywords": ["SQL", "Power BI", "Excel", "Tableau", "Python"],
    "count": 5
  },
  "metadata": {
    "analysis_timestamp": "2025-09-10T11:56:10.590499",
    "ai_model_used": "openai/gpt-4o"
  }
}
```

---

### 4. **Get Required Keywords Only**
```http
GET {{base_url}}/api/jd-analysis/{{company_name}}/keywords?keyword_type=required
```

**Headers:**
```
Authorization: Bearer {{auth_token}}
```

**Expected Response:**
```json
{
  "success": true,
  "message": "Retrieved required keywords for Australia_for_UNHCR",
  "data": {
    "company_name": "Australia_for_UNHCR",
    "keyword_type": "required",
    "keywords": ["SQL", "Power BI", "Excel"],
    "count": 3
  },
  "metadata": {
    "analysis_timestamp": "2025-09-10T11:56:10.590499",
    "ai_model_used": "openai/gpt-4o"
  }
}
```

---

### 5. **Get Preferred Keywords Only**
```http
GET {{base_url}}/api/jd-analysis/{{company_name}}/keywords?keyword_type=preferred
```

**Headers:**
```
Authorization: Bearer {{auth_token}}
```

**Expected Response:**
```json
{
  "success": true,
  "message": "Retrieved preferred keywords for Australia_for_UNHCR",
  "data": {
    "company_name": "Australia_for_UNHCR",
    "keyword_type": "preferred",
    "keywords": ["Tableau", "Python"],
    "count": 2
  },
  "metadata": {
    "analysis_timestamp": "2025-09-10T11:56:10.590499",
    "ai_model_used": "openai/gpt-4o"
  }
}
```

---

### 6. **Check Analysis Status**
```http
GET {{base_url}}/api/jd-analysis/{{company_name}}/status
```

**Headers:**
```
Authorization: Bearer {{auth_token}}
```

**Expected Response:**
```json
{
  "success": true,
  "message": "Status retrieved for Australia_for_UNHCR",
  "data": {
    "company_name": "Australia_for_UNHCR",
    "analysis_exists": true,
    "jd_file_exists": true,
    "can_analyze": true,
    "needs_analysis": false,
    "analysis_timestamp": "2025-09-10T11:56:10.590499",
    "ai_model_used": "openai/gpt-4o",
    "keyword_counts": {
      "required": 16,
      "preferred": 3,
      "total": 19
    }
  }
}
```

---

### 7. **Delete Analysis**
```http
DELETE {{base_url}}/api/jd-analysis/{{company_name}}
```

**Headers:**
```
Authorization: Bearer {{auth_token}}
```

**Expected Response:**
```json
{
  "success": true,
  "message": "Analysis deleted for Australia_for_UNHCR",
  "data": {
    "company_name": "Australia_for_UNHCR",
    "deleted_file": "/path/to/jd_analysis.json"
  }
}
```

---

## 🧪 Test Scenarios

### **Scenario 1: Fresh Analysis**
1. Delete existing analysis (if any)
2. Run analysis endpoint
3. Verify new analysis is created
4. Check that `from_cache: false`

### **Scenario 2: Cached Analysis**
1. Run analysis endpoint again
2. Verify cached results are returned
3. Check that `from_cache: true`

### **Scenario 3: Force Refresh**
1. Run analysis with `force_refresh: true`
2. Verify fresh analysis is performed
3. Check that `from_cache: false`

### **Scenario 4: Error Handling**
1. Test with non-existent company
2. Test with invalid authentication
3. Test with malformed requests

---

## 🔧 Postman Environment Setup

Create a Postman Environment with these variables:

```
base_url: http://localhost:8000
auth_token: your_bearer_token_here
company_name: Australia_for_UNHCR
test_company: Test_Company
```

---

## 📊 Test Scripts (Postman Tests)

Add these test scripts to your Postman requests:

### **For Analysis Endpoint:**
```javascript
pm.test("Status code is 200", function () {
    pm.response.to.have.status(200);
});

pm.test("Response has success field", function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData).to.have.property('success');
    pm.expect(jsonData.success).to.be.true;
});

pm.test("Response has required keywords", function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData.data).to.have.property('required_keywords');
    pm.expect(jsonData.data.required_keywords).to.be.an('array');
});

pm.test("Response has preferred keywords", function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData.data).to.have.property('preferred_keywords');
    pm.expect(jsonData.data.preferred_keywords).to.be.an('array');
});

pm.test("Response has AI model info", function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData.data).to.have.property('ai_model_used');
    pm.expect(jsonData.data.ai_model_used).to.be.a('string');
});
```

### **For Status Endpoint:**
```javascript
pm.test("Status code is 200", function () {
    pm.response.to.have.status(200);
});

pm.test("Response has analysis status", function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData.data).to.have.property('analysis_exists');
    pm.expect(jsonData.data).to.have.property('jd_file_exists');
    pm.expect(jsonData.data).to.have.property('can_analyze');
});
```

---

## 🚨 Common Issues & Solutions

### **Issue 1: 401 Unauthorized**
**Solution:** Make sure you have a valid Bearer token in the Authorization header.

### **Issue 2: 404 Not Found**
**Solution:** Check that the company name exists and has a `jd_original.txt` file.

### **Issue 3: 500 Internal Server Error**
**Solution:** Check server logs for AI service issues or file permission problems.

### **Issue 4: Connection Refused**
**Solution:** Make sure the Flask server is running on the correct port.

---

## 📱 Flutter Integration Testing

Use these same endpoints in your Flutter app:

```dart
// Example Flutter HTTP call
final response = await http.post(
  Uri.parse('http://localhost:8000/api/analyze-jd/Australia_for_UNHCR'),
  headers: {
    'Authorization': 'Bearer $token',
    'Content-Type': 'application/json',
  },
  body: jsonEncode({
    'force_refresh': false,
    'temperature': 0.3,
  }),
);
```

---

## 🎯 Quick Test Checklist

- [ ] Server is running on port 8000
- [ ] Authentication token is valid
- [ ] Company directory exists with `jd_original.txt`
- [ ] All endpoints return 200 status
- [ ] Response format matches expected structure
- [ ] Caching works (second request returns cached data)
- [ ] Force refresh works (bypasses cache)
- [ ] Error handling works (404 for missing company)

---

## 📈 Performance Testing

For performance testing, you can:

1. **Load Testing:** Use Postman's Collection Runner with multiple iterations
2. **Response Time:** Check response times in Postman's response tab
3. **AI Model Switching:** Test with different AI models by changing the active provider

---

## 🔍 Debugging Tips

1. **Check Server Logs:** Look at the Flask server console for detailed error messages
2. **Verify File Paths:** Ensure the `cv-analysis` directory structure is correct
3. **Test AI Service:** Use the test script to verify AI service is working
4. **Check Permissions:** Ensure the server has read/write permissions to the analysis directory

---

## 🆕 **NEW: Categorized Endpoints**

### 6. Get Technical Skills
```http
GET /api/jd-analysis/{company_name}/technical?required_only=false
```

**Parameters:**
- `required_only`: Boolean (optional, default: false)

**Response:**
```json
{
  "success": true,
  "message": "Retrieved technical skills for Australia_for_UNHCR",
  "data": {
    "company_name": "Australia_for_UNHCR",
    "skill_type": "technical",
    "required_only": false,
    "skills": ["SQL", "Power BI", "Excel", "VBA", "Tableau"],
    "count": 5
  },
  "metadata": {
    "analysis_timestamp": "2025-09-10T12:13:44.912265",
    "ai_model_used": "openai/gpt-4o"
  }
}
```

### 7. Get Soft Skills
```http
GET /api/jd-analysis/{company_name}/soft-skills?required_only=true
```

**Response:**
```json
{
  "success": true,
  "message": "Retrieved soft skills for Australia_for_UNHCR",
  "data": {
    "company_name": "Australia_for_UNHCR",
    "skill_type": "soft_skills",
    "required_only": true,
    "skills": ["communication", "project management", "stakeholder management", "customer service"],
    "count": 4
  }
}
```

### 8. Get Experience Requirements
```http
GET /api/jd-analysis/{company_name}/experience?required_only=false
```

**Response:**
```json
{
  "success": true,
  "message": "Retrieved experience requirements for Australia_for_UNHCR",
  "data": {
    "company_name": "Australia_for_UNHCR",
    "skill_type": "experience",
    "required_only": false,
    "requirements": ["2 years experience"],
    "count": 1,
    "experience_years": 2
  }
}
```

### 9. Get Domain Knowledge
```http
GET /api/jd-analysis/{company_name}/domain-knowledge?required_only=false
```

**Response:**
```json
{
  "success": true,
  "message": "Retrieved domain knowledge for Australia_for_UNHCR",
  "data": {
    "company_name": "Australia_for_UNHCR",
    "skill_type": "domain_knowledge",
    "required_only": false,
    "knowledge": ["data warehouse", "marketing campaigns", "advanced understanding of data", "appreciation of data issues"],
    "count": 4
  }
}
```

### 10. Get All Categorized Skills
```http
GET /api/jd-analysis/{company_name}/categorized
```

**Response:**
```json
{
  "success": true,
  "message": "Retrieved categorized skills for Australia_for_UNHCR",
  "data": {
    "company_name": "Australia_for_UNHCR",
    "categorized_skills": {
      "required": {
        "technical": ["SQL", "Excel", "VBA", "Power BI"],
        "soft_skills": ["project management", "stakeholder management", "communication", "customer service"],
        "experience": ["2 years experience"],
        "domain_knowledge": ["data warehouse", "marketing campaigns"]
      },
      "preferred": {
        "technical": ["Tableau"],
        "soft_skills": [],
        "experience": [],
        "domain_knowledge": ["advanced understanding of data", "appreciation of data issues"]
      }
    },
    "skill_summary": {
      "total_required": 11,
      "total_preferred": 3,
      "required_technical": 4,
      "required_soft_skills": 4,
      "required_experience": 1,
      "required_domain_knowledge": 2,
      "preferred_technical": 1,
      "preferred_soft_skills": 0,
      "preferred_experience": 0,
      "preferred_domain_knowledge": 2
    },
    "experience_years": 2
  }
}
```

---

## 🎯 **Enhanced Response Format**

The main analysis endpoint now returns both backward-compatible flat lists AND the new categorized structure:

```json
{
  "success": true,
  "data": {
    "company_name": "Australia_for_UNHCR",
    // Backward compatibility - flat keyword lists
    "required_keywords": ["SQL", "Power BI", "Excel", ...],
    "preferred_keywords": ["Tableau", "Python", ...],
    "all_keywords": [...],
    "experience_years": 2,
    // Enhanced categorized structure
    "required_skills": {
      "technical": ["SQL", "Power BI", "VBA"],
      "soft_skills": ["communication", "project management"],
      "experience": ["2+ years experience"],
      "domain_knowledge": ["data warehouse", "marketing campaigns"]
    },
    "preferred_skills": {
      "technical": ["Tableau", "Python"],
      "soft_skills": ["leadership"],
      "experience": ["5+ years preferred"],
      "domain_knowledge": ["machine learning"]
    },
    // Skill summary for quick overview
    "skill_summary": {
      "total_required": 11,
      "total_preferred": 3,
      "required_technical": 4,
      "required_soft_skills": 4,
      "required_experience": 1,
      "required_domain_knowledge": 2
    }
  }
}
```

Happy testing! 🚀
