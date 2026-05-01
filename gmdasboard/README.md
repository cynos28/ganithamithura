# Ganitha Mithura Teacher Dashboard

A comprehensive teacher dashboard for the Ganitha Mithura Grade 3 math learning application, featuring AI-powered question generation through RAG (Retrieval-Augmented Generation) integration.

## Features

### Dashboard Pages
- **Overview**: KPI cards, activity charts, quick actions, recent activity
- **Classes**: Class management with TanStack Table, filters, sorting
- **Students**: Student roster with profiles, progress tracking, strengths/weaknesses
- **Domains**:
  - **Measurement** (RAG-integrated): Upload documents, generate adaptive questions for Length, Area, Capacity, Weight
  - **Numbers**: Number concepts configuration
  - **Operations**: Addition, subtraction, multiplication, division
  - **Shapes**: 2D and 3D shapes configuration
- **Assignments**: Create and manage assignments
- **Assessments**: Assessment configuration and results
- **Analytics**: Data visualization and reports
- **Live Session**: Real-time classroom monitoring
- **Content Library**: Educational resource management
- **Settings**: User preferences and system configuration

### RAG Service Integration
The Measurement domain features full integration with a RAG service for:
- Document upload (PDF, DOCX, TXT)
- Topic-based organization (Length, Area, Capacity, Weight)
- Grade level selection (3-7)
- Automatic question generation from uploaded documents
- Document management (view, download, delete)

## Tech Stack

- **Framework**: Next.js 16 with App Router & Turbopack
- **Language**: TypeScript (strict mode)
- **Styling**: Tailwind CSS v4
- **UI Components**: shadcn/ui (18+ components)
- **Tables**: TanStack Table v8
- **Charts**: Recharts
- **Icons**: Lucide React
- **Forms**: React Hook Form + Zod
- **Date Utilities**: date-fns

## Getting Started

### Prerequisites
- Node.js 18+ installed
- RAG service running at `http://localhost:8000` (optional, for Measurement domain features)

### Installation

1. Install dependencies:
```bash
npm install
```

2. Configure environment variables:
Create a `.env.local` file in the root directory:
```env
NEXT_PUBLIC_RAG_API_URL=http://localhost:8000
```

3. Run the development server:
```bash
npm run dev
```

4. Open [http://localhost:3000](http://localhost:3000) in your browser

### Running with RAG Service

To use the document upload and question generation features in the Measurement domain:

1. Start the RAG service on port 8000 (see RAG service documentation)

2. Ensure the `NEXT_PUBLIC_RAG_API_URL` environment variable is set correctly

3. Navigate to **Domains > Measurement** in the dashboard

4. Select a topic tab (Length, Area, Capacity, or Weight)

5. Upload documents using the upload form:
   - Choose a PDF, DOCX, or TXT file
   - Select the topic
   - Choose grade levels (3-7)
   - Click "Upload & Generate Questions"

6. View uploaded documents and generated questions in the list below

## Project Structure

```
gmdasboard/
├── app/
│   ├── layout.tsx              # Root layout with Sidebar + TopBar
│   ├── page.tsx               # Redirects to dashboard
│   ├── globals.css            # Global styles
│   └── (dashboard)/           # Dashboard route group
│       ├── page.tsx           # Overview dashboard
│       ├── classes/           # Class management
│       ├── students/          # Student management
│       ├── domains/           # Domain configurations
│       │   ├── measurement/   # RAG-integrated measurement domain
│       │   ├── numbers/
│       │   ├── operations/
│       │   └── shapes/
│       ├── assignments/
│       ├── assessments/
│       ├── analytics/
│       ├── live/
│       ├── content/
│       └── settings/
├── components/
│   ├── DocumentUpload.tsx     # RAG document upload component
│   ├── dashboard/             # Dashboard-specific components
│   │   ├── charts.tsx
│   │   ├── domain-config.tsx
│   │   └── kpi-card.tsx
│   ├── layout/                # Layout components
│   │   ├── sidebar.tsx
│   │   └── topbar.tsx
│   └── ui/                    # shadcn/ui components
├── data/
│   └── mock-data.ts           # Sample data for development
├── types/
│   └── index.ts               # TypeScript type definitions
└── lib/
    └── utils.ts               # Utility functions
```

## Key Components

### Sidebar Navigation
- Collapsible sidebar with ARIA menubar pattern
- Keyboard navigation support
- Mobile-responsive hamburger menu
- Skip-to-content link for accessibility

### TopBar
- Global search
- Notifications dropdown
- User menu with profile and settings

### DocumentUpload Component
Located at `/components/DocumentUpload.tsx`, handles:
- File selection (PDF, DOCX, TXT)
- Topic dropdown (Length, Area, Capacity, Weight)
- Grade level multi-select (3-7)
- Form validation and error handling
- Success/error state display
- Automatic question generation after upload

### Measurement Dashboard
Located at `/app/(dashboard)/domains/measurement/page.tsx`, features:
- Topic tabs (Length, Area, Capacity, Weight)
- Document upload section per topic
- Uploaded documents list with:
  - Document metadata (title, grades, topic, status)
  - Question count
  - Timestamp (relative format)
  - Actions (view, download, delete)
- Empty states and loading indicators
- Error handling and retry logic

## API Endpoints Used

### Document Upload
```
POST /upload/document
Content-Type: multipart/form-data

FormData:
- file: File (PDF, DOCX, TXT)
- grade_levels: string (comma-separated, e.g., "3,4,5")
- topic: string (Length, Area, Capacity, Weight)
- uploaded_by: string (teacher ID)

Response:
{
  "id": "uuid",
  "title": "Document Title",
  "grade_levels": [3, 4, 5],
  "topic": "Length",
  "status": "processing",
  "questions_count": 0
}
```

### Question Generation
```
POST /questions/generate/{document_id}
Content-Type: application/json

Body:
{
  "num_questions": 10,
  "grade_level": 3,
  "difficulty_levels": [1, 2, 3, 4, 5]
}

Response:
{
  "questions_generated": 10,
  "document_id": "uuid"
}
```

### List Documents
```
GET /documents

Response:
{
  "documents": [
    {
      "id": "uuid",
      "title": "Document Title",
      "grade_levels": [3, 4, 5],
      "topic": "Length",
      "status": "processed",
      "questions_count": 10,
      "created_at": "2024-01-15T10:30:00Z",
      "file_path": "/path/to/file"
    }
  ]
}
```

### Delete Document
```
DELETE /documents/{document_id}

Response:
{
  "message": "Document deleted successfully"
}
```

## Accessibility Features

- ARIA roles and labels throughout
- Keyboard navigation support
- Skip-to-content link
- Focus management
- Semantic HTML structure
- Color contrast compliance

## Development Commands

```bash
npm run dev      # Start development server
npm run build    # Build for production
npm start        # Start production server
npm run lint     # Run ESLint
```

## Mock Data

The application includes comprehensive mock data in `/data/mock-data.ts`:
- 110+ students with Sri Lankan names
- 4 classes (Grade 3A-3D)
- Student performance data
- Assignment and assessment records
- Attempt history
- Mastery tracking

## Future Enhancements

- Authentication and authorization
- Real-time updates with WebSockets
- Enhanced analytics and reporting
- Export functionality for reports
- Integration with other domains (Numbers, Operations, Shapes)
- Student-facing interface
- Parent portal

## License

Private - Ganitha Mithura Project

## Support

For questions or issues, please contact the development team.
