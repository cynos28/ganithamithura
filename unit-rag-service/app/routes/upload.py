from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import List
import uuid
from app.models.database import DocumentModel
from app.models.schemas import DocumentResponse
from app.utils.document_processor import document_processor
from app.services.embeddings_service import embeddings_service
from app.config import settings

router = APIRouter(prefix="/api/v1/upload", tags=["upload"])


@router.post("/", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    title: str = Form(...),
    grade_levels: str = Form(...),  # Comma-separated: "1,2,3,4"
    topic: str = Form(...),
    uploaded_by: str = Form(...)
):
    """
    Upload and process a document
    
    - Accepts PDF, DOCX, or TXT files
    - Extracts text content
    - Creates embeddings and stores in vector database
    - Returns document metadata
    """
    
    # Validate file extension
    file_ext = file.filename.split('.')[-1].lower()
    if file_ext not in settings.allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Allowed: {', '.join(settings.allowed_extensions)}"
        )
    
    # Validate file size
    file_content = await file.read()
    if len(file_content) > settings.max_upload_size:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Max size: {settings.max_upload_size / 1024 / 1024}MB"
        )
    
    try:
        # Extract text from document
        text_content = document_processor.extract_text(file_content, file.filename)
        
        # Clean text
        text_content = document_processor.clean_text(text_content)
        
        if not text_content or len(text_content) < 100:
            raise HTTPException(
                status_code=400,
                detail="Document content is too short or could not be extracted"
            )
        
        # Parse grade levels
        grade_list = [int(g.strip()) for g in grade_levels.split(',')]
        
        # Create document record in MongoDB
        document = DocumentModel(
            title=title,
            content=text_content,
            grade_levels=grade_list,
            topic=topic,
            uploaded_by=uploaded_by,
            status="processing"
        )
        await document.insert()
        
        # Generate unique document ID for vector store
        vector_doc_id = f"doc_{str(document.id)}_{uuid.uuid4().hex[:8]}"
        
        # Chunk the text
        chunks = document_processor.chunk_text(
            text_content,
            chunk_size=settings.chunk_size,
            overlap=settings.chunk_overlap
        )
        
        # Add to vector database
        metadata = {
            "document_id": str(document.id),
            "title": title,
            "topic": topic,
            "grade_levels": grade_list
        }
        
        await embeddings_service.add_document_chunks(
            document_id=vector_doc_id,
            chunks=chunks,
            metadata=metadata
        )
        
        # Update document status
        document.vector_db_id = vector_doc_id
        document.status = "completed"
        await document.save()
        
        return DocumentResponse(
            id=str(document.id),
            title=document.title,
            grade_levels=document.grade_levels,
            topic=document.topic,
            uploaded_by=document.uploaded_by,
            uploaded_at=document.uploaded_at,
            status=document.status,
            questions_count=document.questions_count
        )
        
    except Exception as e:
        # If document was created, update status to failed
        if 'document' in locals():
            document.status = "failed"
            await document.save()
        
        raise HTTPException(
            status_code=500,
            detail=f"Error processing document: {str(e)}"
        )


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(document_id: str):
    """Get document by ID"""
    document = await DocumentModel.get(document_id)
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return DocumentResponse(
        id=str(document.id),
        title=document.title,
        grade_levels=document.grade_levels,
        topic=document.topic,
        uploaded_by=document.uploaded_by,
        uploaded_at=document.uploaded_at,
        status=document.status,
        questions_count=document.questions_count
    )


@router.get("/", response_model=List[DocumentResponse])
async def list_documents(
    topic: str = None,
    grade_level: int = None,
    status: str = None,
    skip: int = 0,
    limit: int = 20
):
    """List all documents with optional filters"""
    query = {}
    
    if topic:
        query["topic"] = topic
    if status:
        query["status"] = status
    if grade_level:
        query["grade_levels"] = grade_level
    
    documents = await DocumentModel.find(query).skip(skip).limit(limit).to_list()
    
    return [
        DocumentResponse(
            id=str(doc.id),
            title=doc.title,
            grade_levels=doc.grade_levels,
            topic=doc.topic,
            uploaded_by=doc.uploaded_by,
            uploaded_at=doc.uploaded_at,
            status=doc.status,
            questions_count=doc.questions_count
        )
        for doc in documents
    ]


@router.delete("/{document_id}")
async def delete_document(document_id: str):
    """Delete a document and its vector embeddings"""
    document = await DocumentModel.get(document_id)
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Delete from vector database
    if document.vector_db_id:
        try:
            await embeddings_service.delete_document(document.vector_db_id)
        except Exception as e:
            print(f"Warning: Could not delete from vector DB: {e}")
    
    # Delete from MongoDB
    await document.delete()
    
    return {"message": "Document deleted successfully"}
