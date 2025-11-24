#!/usr/bin/env python3
"""
Test script to verify RAG service endpoints
Run this after starting the server to test all APIs
"""

import requests
import json
from pathlib import Path

BASE_URL = "http://localhost:8000"

def test_health():
    """Test if server is running"""
    print("🔍 Testing server health...")
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"✅ Server is running: {response.json()}")
        return True
    except Exception as e:
        print(f"❌ Server not responding: {e}")
        return False

def test_upload_document():
    """Test document upload"""
    print("\n📤 Testing document upload...")
    
    # Create a simple test file
    test_file_path = Path("test_measurement.txt")
    test_file_path.write_text("""
    Measurement - Length
    
    In the metric system, we measure length using:
    - Millimeters (mm)
    - Centimeters (cm) 
    - Meters (m)
    - Kilometers (km)
    
    Conversions:
    1 cm = 10 mm
    1 m = 100 cm
    1 km = 1000 m
    
    Example: A pencil is about 15 cm long.
    A classroom is about 8 meters wide.
    The distance between two cities might be 50 kilometers.
    """)
    
    try:
        with open(test_file_path, 'rb') as f:
            files = {'file': f}
            data = {
                'grade_levels': '5,6',
                'topic': 'Length',
                'uploaded_by': 'test_teacher'
            }
            response = requests.post(
                f"{BASE_URL}/upload/document",
                files=files,
                data=data
            )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Document uploaded successfully!")
            print(f"   Document ID: {result['id']}")
            print(f"   Title: {result['title']}")
            print(f"   Status: {result['status']}")
            test_file_path.unlink()  # Clean up
            return result['id']
        else:
            print(f"❌ Upload failed: {response.text}")
            test_file_path.unlink()
            return None
    except Exception as e:
        print(f"❌ Upload error: {e}")
        if test_file_path.exists():
            test_file_path.unlink()
        return None

def test_generate_questions(document_id):
    """Test question generation"""
    print(f"\n📝 Testing question generation for document {document_id}...")
    
    try:
        payload = {
            "num_questions": 5,
            "grade_level": 5,
            "difficulty_levels": [1, 2, 3]
        }
        response = requests.post(
            f"{BASE_URL}/questions/generate/{document_id}",
            json=payload,
            timeout=60  # Question generation can take time
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Generated {result.get('questions_generated', 0)} questions")
            if 'questions' in result and len(result['questions']) > 0:
                first_q = result['questions'][0]
                print(f"\n   Sample Question:")
                print(f"   Q: {first_q['question_text']}")
                print(f"   Type: {first_q['question_type']}")
                print(f"   Difficulty: {first_q['difficulty_level']}/5")
                if first_q.get('options'):
                    print(f"   Options: {first_q['options']}")
                print(f"   Answer: {first_q['correct_answer']}")
                return result['questions']
            return []
        else:
            print(f"❌ Generation failed: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Generation error: {e}")
        return None

def test_get_questions(document_id=None):
    """Test fetching questions"""
    print(f"\n📋 Testing question retrieval...")
    
    try:
        url = f"{BASE_URL}/questions/"
        params = {}
        if document_id:
            params['document_id'] = document_id
        params['limit'] = 10
        
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            questions = response.json()
            print(f"✅ Retrieved {len(questions)} questions")
            return questions
        else:
            print(f"❌ Retrieval failed: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Retrieval error: {e}")
        return None

def test_adaptive_flow(question_id):
    """Test adaptive learning flow"""
    print(f"\n🎯 Testing adaptive learning...")
    
    student_id = "test_student_123"
    
    # Submit an answer
    try:
        payload = {
            "student_id": student_id,
            "question_id": question_id,
            "answer": "100 cm",  # Example answer
            "time_taken": 15
        }
        response = requests.post(
            f"{BASE_URL}/adaptive/submit-answer",
            json=payload
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Answer submitted")
            print(f"   Correct: {result.get('is_correct', False)}")
            print(f"   Ability Score: {result.get('ability_score', 0):.2f}")
            print(f"   Recommended Difficulty: {result.get('recommended_difficulty', 1)}")
        else:
            print(f"⚠️  Answer submission: {response.text}")
    except Exception as e:
        print(f"⚠️  Adaptive answer error: {e}")
    
    # Get next adaptive question
    try:
        response = requests.get(
            f"{BASE_URL}/adaptive/next-question/{student_id}",
            params={"unit_id": 1}
        )
        
        if response.status_code == 200:
            question = response.json()
            print(f"✅ Next adaptive question retrieved")
            print(f"   Difficulty: {question.get('difficulty_level', 1)}/5")
        else:
            print(f"⚠️  No adaptive question available")
    except Exception as e:
        print(f"⚠️  Adaptive question error: {e}")

def test_get_documents():
    """Test document listing"""
    print(f"\n📚 Testing document listing...")
    
    try:
        response = requests.get(f"{BASE_URL}/upload/documents")
        
        if response.status_code == 200:
            documents = response.json()
            print(f"✅ Retrieved {len(documents)} documents")
            for doc in documents[:3]:  # Show first 3
                print(f"   - {doc['title']} (Grade {doc.get('grade_levels', [])})")
            return documents
        else:
            print(f"❌ Document listing failed: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Document listing error: {e}")
        return None

def main():
    print("=" * 60)
    print("RAG SERVICE INTEGRATION TEST")
    print("=" * 60)
    
    # 1. Check if server is running
    if not test_health():
        print("\n❌ Server not running. Start it with: python -m app.main")
        return
    
    # 2. Test document upload
    document_id = test_upload_document()
    if not document_id:
        print("\n⚠️  Skipping question generation (upload failed)")
        # Try to get existing documents instead
        documents = test_get_documents()
        if documents and len(documents) > 0:
            document_id = documents[0]['id']
            print(f"\n📌 Using existing document: {document_id}")
    
    # 3. Test question generation
    if document_id:
        questions = test_generate_questions(document_id)
        
        # 4. Test question retrieval
        all_questions = test_get_questions(document_id)
        
        # 5. Test adaptive flow
        if all_questions and len(all_questions) > 0:
            question_id = all_questions[0]['id']
            test_adaptive_flow(question_id)
    
    # 6. Test document listing
    test_get_documents()
    
    print("\n" + "=" * 60)
    print("✅ INTEGRATION TEST COMPLETE")
    print("=" * 60)
    print("\n💡 Next steps:")
    print("   1. Check API docs: http://localhost:8000/docs")
    print("   2. Test with Postman or your frontend")
    print("   3. Upload real documents for your curriculum")

if __name__ == "__main__":
    main()
