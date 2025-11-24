# RAG Service API Endpoints Reference

## Upload Endpoints

### Option 1: `/api/v1/upload/` (Primary)
```bash
curl -X POST "http://localhost:8000/api/v1/upload/" \
  -F "file=@document.pdf" \
  -F "grade_levels=5,6,7" \
  -F "topic=Length" \
  -F "title=Measurement Guide" \
  -F "uploaded_by=teacher123"
```

### Option 2: `/upload/document` (Alias - Same as above)
```bash
curl -X POST "http://localhost:8000/upload/document" \
  -F "file=@document.pdf" \
  -F "grade_levels=5,6,7" \
  -F "topic=Length"
```

**Required Fields:**
- `file` - PDF, DOCX, or TXT file
- `grade_levels` - Comma-separated grades (e.g., "5,6,7")
- `topic` - Topic name (Length, Area, Capacity, Weight)

**Optional Fields:**
- `title` - Document title (defaults to filename)
- `uploaded_by` - Teacher/uploader ID (defaults to "anonymous")

**Response:**
```json
{
  "id": "674321abc123def456789012",
  "title": "document.pdf",
  "grade_levels": [5, 6, 7],
  "topic": "Length",
  "uploaded_by": "teacher123",
  "uploaded_at": "2025-11-24T10:30:00.000Z",
  "status": "completed",
  "questions_count": 0
}
```

## Next.js/JavaScript Example

```javascript
async function uploadDocument(file, gradeLevels, topic, teacherId) {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('grade_levels', gradeLevels.join(','));
  formData.append('topic', topic);
  if (teacherId) {
    formData.append('uploaded_by', teacherId);
  }

  const response = await fetch('http://localhost:8000/api/v1/upload/', {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Upload failed');
  }

  return await response.json();
}

// Usage
try {
  const result = await uploadDocument(
    fileInput.files[0],
    [5, 6, 7],
    'Length',
    'teacher123'
  );
  console.log('Upload successful:', result);
} catch (error) {
  console.error('Upload failed:', error.message);
}
```

## Common Errors

### 404 Not Found
- **Problem:** Endpoint doesn't exist
- **Solution:** Use `/api/v1/upload/` or `/upload/document`

### 500 Internal Server Error
- **Cause 1:** Missing required fields (grade_levels, topic)
- **Solution:** Ensure all required fields are sent

- **Cause 2:** Invalid grade_levels format
- **Solution:** Use comma-separated string: "5,6,7" not array

- **Cause 3:** File processing error
- **Solution:** Check file is valid PDF/DOCX/TXT with readable text

### 400 Bad Request
- File type not allowed
- File too large (>10MB)
- Document content too short (<100 characters)

## Testing

### Test with curl
```bash
# Create test file
echo "Length measurement guide. 1 meter = 100 centimeters. 1 km = 1000 meters." > test.txt

# Upload
curl -X POST "http://localhost:8000/api/v1/upload/" \
  -F "file=@test.txt" \
  -F "grade_levels=5" \
  -F "topic=Length" \
  -v
```

### Check server logs
The server will show detailed errors:
```
ERROR: Document content too short
ERROR: Invalid grade_levels format
ERROR: File type not allowed
```

## All Available Endpoints

### Document Management
- `POST /api/v1/upload/` - Upload document
- `GET /api/v1/upload/` - List documents
- `GET /api/v1/upload/{id}` - Get document details
- `DELETE /api/v1/upload/{id}` - Delete document

### Question Generation
- `POST /questions/generate/{document_id}` - Generate questions
- `GET /questions/` - List questions
- `GET /questions/{id}` - Get question details

### Adaptive Learning
- `POST /adaptive/submit-answer` - Submit answer
- `GET /adaptive/next-question/{student_id}` - Get next question
- `GET /adaptive/analytics/{student_id}` - Get analytics

### System
- `GET /` - Health check
- `GET /health` - Detailed health
- `GET /docs` - Interactive API documentation
