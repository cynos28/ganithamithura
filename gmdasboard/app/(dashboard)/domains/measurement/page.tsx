'use client';

import { useState, useEffect } from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import DocumentUpload from '@/components/DocumentUpload';
import {
  FileText,
  Calendar,
  Download,
  Trash2,
  Eye,
  Loader2,
  BookOpen,
  Ruler,
  Square,
  Droplet,
  Weight as WeightIcon,
  HelpCircle,
  Sparkles
} from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';

interface Document {
  id: string;
  title: string;
  grade_levels: number[];
  topic: string;
  status: string;
  questions_count: number;
  created_at: string;
  file_path: string;
}

interface Question {
  id: string;
  question_text: string;
  options?: string[];
  correct_answer: string;
  explanation?: string;
  difficulty_level: number;
  grade_level: number;
}

export default function MeasurementPage() {
  const [activeTab, setActiveTab] = useState('length');
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedDocument, setSelectedDocument] = useState<Document | null>(null);
  const [questions, setQuestions] = useState<Question[]>([]);
  const [loadingQuestions, setLoadingQuestions] = useState(false);
  const [showQuestionsDialog, setShowQuestionsDialog] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [showGenerateDialog, setShowGenerateDialog] = useState(false);
  const [questionsPerGrade, setQuestionsPerGrade] = useState('5');

  const ragBase = process.env.NEXT_PUBLIC_RAG_API_URL || 'http://localhost:8002';

  const topics = [
    { id: 'length', name: 'Length', icon: Ruler, units: 'cm, m, km', color: 'blue' },
    { id: 'area', name: 'Area', icon: Square, units: 'cm², m²', color: 'green' },
    { id: 'capacity', name: 'Capacity', icon: Droplet, units: 'ml, l', color: 'cyan' },
    { id: 'weight', name: 'Weight', icon: WeightIcon, units: 'g, kg', color: 'purple' },
  ];

  useEffect(() => {
    fetchDocuments();
  }, [activeTab]);

  const fetchDocuments = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`${ragBase}/documents`);

      if (!response.ok) {
        throw new Error('Failed to fetch documents');
      }

      const data = await response.json();
      const allDocs = data.documents || [];

      const topicName = topics.find(t => t.id === activeTab)?.name || '';
      const filtered = allDocs.filter((doc: Document) =>
        doc.topic.toLowerCase() === topicName.toLowerCase()
      );

      setDocuments(filtered);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load documents');
      setDocuments([]);
    } finally {
      setLoading(false);
    }
  };

  const handleUploadSuccess = async (documentId?: string) => {
    // Immediately refresh to show the new document
    await fetchDocuments();

    // If documentId provided, poll for question generation completion
    if (documentId) {
      const maxAttempts = 40; // 40 * 3 seconds = 2 minutes
      let attempts = 0;

      const pollInterval = setInterval(async () => {
        attempts++;

        try {
          const response = await fetch(`${ragBase}/documents`);

          if (response.ok) {
            const data = await response.json();
            const allDocs = data.documents || [];
            const uploadedDoc = allDocs.find((doc: Document) => doc.id === documentId);

            // If questions have been generated (count > 0), refresh and stop polling
            if (uploadedDoc && uploadedDoc.questions_count > 0) {
              const topicName = topics.find(t => t.id === activeTab)?.name || '';
              const filtered = allDocs.filter((doc: Document) =>
                doc.topic.toLowerCase() === topicName.toLowerCase()
              );
              setDocuments(filtered);
              clearInterval(pollInterval);
              return;
            }
          }
        } catch (err) {
          console.error('Error polling for upload updates:', err);
        }

        // Stop after max attempts
        if (attempts >= maxAttempts) {
          clearInterval(pollInterval);
          await fetchDocuments(); // Final refresh
        }
      }, 3000);
    }
  };

  const handleDelete = async (docId: string) => {
    if (!confirm('Are you sure you want to delete this document?')) {
      return;
    }

    try {
      const response = await fetch(`${ragBase}/documents/${docId}`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        throw new Error('Failed to delete document');
      }

      fetchDocuments();
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to delete document');
    }
  };

  const handleViewQuestions = async (doc: Document) => {
    setSelectedDocument(doc);
    setShowQuestionsDialog(true);
    setLoadingQuestions(true);
    setQuestions([]);

    try {
      const response = await fetch(`${ragBase}/questions/document/${doc.id}`);

      if (!response.ok) {
        throw new Error('Failed to fetch questions');
      }

      const data = await response.json();
      setQuestions(data || []);
    } catch (err) {
      console.error('Failed to load questions:', err);
      setQuestions([]);
    } finally {
      setLoadingQuestions(false);
    }
  };

  const handleGenerateMore = (doc: Document) => {
    setSelectedDocument(doc);
    setShowGenerateDialog(true);
  };

  const handleGenerateQuestions = async () => {
    if (!selectedDocument) return;

    setGenerating(true);
    setShowGenerateDialog(false);

    try {
      const response = await fetch(`${ragBase}/api/v1/questions/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          document_id: selectedDocument.id,
          grade_levels: selectedDocument.grade_levels,
          questions_per_grade: parseInt(questionsPerGrade) || 5,
          question_types: ['mcq', 'short_answer']
        })
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to generate questions');
      }

      const expectedNewQuestions = parseInt(questionsPerGrade) * selectedDocument.grade_levels.length;
      alert(`✅ Generating ${expectedNewQuestions} questions in background. The question count will update automatically.`);

      // Poll for updates every 3 seconds for up to 2 minutes
      const maxAttempts = 40;
      let attempts = 0;
      const initialCount = selectedDocument.questions_count;
      const docId = selectedDocument.id;

      const pollInterval = setInterval(async () => {
        attempts++;

        try {
          const response = await fetch(`${ragBase}/documents`);

          if (response.ok) {
            const data = await response.json();
            const allDocs = data.documents || [];
            const updatedDoc = allDocs.find((doc: Document) => doc.id === docId);

            // Check if questions were added (count increased)
            if (updatedDoc && updatedDoc.questions_count > initialCount) {
              const topicName = topics.find(t => t.id === activeTab)?.name || '';
              const filtered = allDocs.filter((doc: Document) =>
                doc.topic.toLowerCase() === topicName.toLowerCase()
              );
              setDocuments(filtered);
              clearInterval(pollInterval);
              setGenerating(false);

              const addedQuestions = updatedDoc.questions_count - initialCount;
              console.log(`✅ ${addedQuestions} new questions generated successfully`);
              return;
            }
          }
        } catch (err) {
          console.error('Error polling for updates:', err);
        }

        // Stop after max attempts and reset state
        if (attempts >= maxAttempts) {
          clearInterval(pollInterval);
          setGenerating(false);
          await fetchDocuments();
          console.log('⏱️ Polling timeout reached');
        }
      }, 3000);

    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to generate questions');
      setGenerating(false);
    }
  };

  return (
    <div className="space-y-10 pb-10 px-4 sm:px-6 lg:px-8">
      {/* Header */}
      <div className="space-y-3 pt-2">
        <h1 className="text-3xl sm:text-4xl font-bold text-neutral-900">Measurement Domain</h1>
        <p className="text-neutral-600 text-base sm:text-lg max-w-3xl">
          Upload documents and generate adaptive questions for measurement topics
        </p>
      </div>

      {/* Topic Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full grid-cols-2 lg:grid-cols-4 h-auto p-1.5 gap-2">
          {topics.map((topic) => {
            const Icon = topic.icon;
            return (
              <TabsTrigger key={topic.id} value={topic.id} className="gap-2 py-3.5 text-sm sm:text-base">
                <Icon className="h-4 w-4 sm:h-5 sm:w-5" />
                <span className="hidden sm:inline">{topic.name}</span>
                <span className="sm:hidden">{topic.name.substring(0, 3)}</span>
              </TabsTrigger>
            );
          })}
        </TabsList>

        {topics.map((topic) => {
          const Icon = topic.icon;
          return (
            <TabsContent key={topic.id} value={topic.id} className="space-y-10 mt-10">
              {/* Topic Info Card */}
              <Card className={`border-l-4 border-${topic.color}-500 shadow-sm`}>
                <CardHeader className="pb-5 pt-6 px-6">
                  <CardTitle className="flex items-center gap-4 text-xl sm:text-2xl">
                    <div className={`p-3 rounded-xl bg-${topic.color}-50`}>
                      <Icon className={`h-6 w-6 sm:h-7 sm:w-7 text-${topic.color}-600`} />
                    </div>
                    {topic.name}
                  </CardTitle>
                  <CardDescription className="text-base sm:text-lg mt-3">
                    Units: <span className="font-medium">{topic.units}</span> • Grade levels: <span className="font-medium">1-4</span>
                  </CardDescription>
                </CardHeader>
              </Card>

              {/* Upload Section */}
              <div className="my-10">
                <DocumentUpload onUploadSuccess={handleUploadSuccess} />
              </div>

              {/* Documents List */}
              <Card className="shadow-sm">
                <CardHeader className="pb-5 pt-6 px-6">
                  <CardTitle className="flex items-center gap-3 text-xl sm:text-2xl">
                    <BookOpen className="h-6 w-6 text-neutral-700" />
                    Uploaded Documents ({documents.length})
                  </CardTitle>
                  <CardDescription className="text-base sm:text-lg mt-2">
                    Documents and generated questions for {topic.name}
                  </CardDescription>
                </CardHeader>
                <CardContent className="pt-4 px-6 pb-6">
                  {loading ? (
                    <div className="flex items-center justify-center py-16">
                      <Loader2 className="h-10 w-10 animate-spin text-neutral-400" />
                    </div>
                  ) : error ? (
                    <div className="rounded-lg border border-red-200 bg-red-50 p-6 text-red-700">
                      <p className="font-medium text-base">Error loading documents</p>
                      <p className="text-sm mt-2">{error}</p>
                      <Button variant="outline" size="sm" onClick={fetchDocuments} className="mt-4">
                        Retry
                      </Button>
                    </div>
                  ) : documents.length === 0 ? (
                    <div className="text-center py-20 text-neutral-500">
                      <FileText className="h-20 w-20 mx-auto mb-5 text-neutral-300" />
                      <p className="font-medium text-xl mb-2">No documents uploaded yet</p>
                      <p className="text-base text-neutral-400">Upload a document above to get started</p>
                    </div>
                  ) : (
                    <div className="space-y-5">
                      {documents.map((doc) => (
                        <div
                          key={doc.id}
                          className="flex flex-col lg:flex-row items-start gap-5 rounded-xl border border-neutral-200 p-6 hover:bg-neutral-50 hover:border-neutral-300 transition-all hover:shadow-md"
                        >
                          <div className="shrink-0">
                            <div className="h-14 w-14 rounded-xl bg-blue-100 flex items-center justify-center">
                              <FileText className="h-7 w-7 text-blue-600" />
                            </div>
                          </div>

                          <div className="flex-1 min-w-0 w-full space-y-3">
                            <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-3">
                              <h4 className="font-semibold text-neutral-900 text-lg">
                                {doc.title}
                              </h4>
                              <Badge variant={doc.status === 'completed' ? 'default' : 'outline'} className="self-start px-4 py-1.5 text-sm">
                                {doc.status}
                              </Badge>
                            </div>

                            <div className="flex flex-wrap gap-x-4 gap-y-2 text-sm sm:text-base text-neutral-600">
                              <span className="flex items-center gap-2">
                                <Calendar className="h-4 w-4" />
                                {formatDistanceToNow(new Date(doc.created_at), { addSuffix: true })}
                              </span>
                              <span className="hidden sm:inline text-neutral-300">•</span>
                              <span className="font-medium">{doc.questions_count} questions</span>
                              <span className="hidden sm:inline text-neutral-300">•</span>
                              <span>Grades: {doc.grade_levels.join(', ')}</span>
                            </div>
                          </div>

                          <div className="flex flex-wrap sm:flex-nowrap items-center gap-3 w-full lg:w-auto justify-start lg:justify-end">
                            <Button
                              variant="outline"
                              size="default"
                              className="gap-2 flex-1 sm:flex-initial"
                              onClick={() => handleViewQuestions(doc)}
                            >
                              <Eye className="h-4 w-4" />
                              <span>View</span>
                            </Button>
                            <Button
                              variant="default"
                              size="default"
                              className="flex-1 sm:flex-initial bg-purple-600 hover:bg-purple-700"
                              onClick={() => handleGenerateMore(doc)}
                              disabled={generating}
                            >
                              {generating ? (
                                <>
                                  <Loader2 className="h-4 w-4 animate-spin mr-2" />
                                  Generating...
                                </>
                              ) : (
                                'Generate More'
                              )}
                            </Button>
                            <Button
                              variant="outline"
                              size="default"
                              onClick={() => handleDelete(doc.id)}
                              className="gap-2 flex-1 sm:flex-initial border-red-200 text-red-600 hover:bg-red-50 hover:border-red-300"
                            >
                              <Trash2 className="h-4 w-4" />
                              <span>Delete</span>
                            </Button>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </CardContent>
              </Card>
            </TabsContent>
          );
        })}
      </Tabs>

      {/* Generate More Questions Dialog */}
      <Dialog open={showGenerateDialog} onOpenChange={setShowGenerateDialog}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle className="text-2xl flex items-center gap-3">
              <Sparkles className="h-6 w-6 text-purple-600" />
              Generate More Questions
            </DialogTitle>
            <DialogDescription className="text-base">
              {selectedDocument?.title}
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-6 py-4">
            <div className="space-y-2">
              <Label htmlFor="questions-count">Questions per grade level</Label>
              <Input
                id="questions-count"
                type="number"
                min="1"
                max="20"
                value={questionsPerGrade}
                onChange={(e) => setQuestionsPerGrade(e.target.value)}
                placeholder="5"
              />
              <p className="text-sm text-neutral-500">
                Total: {(parseInt(questionsPerGrade) || 5) * (selectedDocument?.grade_levels.length || 1)} questions
                ({selectedDocument?.grade_levels.length || 1} grade levels)
              </p>
            </div>

            <div className="flex gap-3">
              <Button variant="outline" onClick={() => setShowGenerateDialog(false)} className="flex-1">
                Cancel
              </Button>
              <Button
                onClick={handleGenerateQuestions}
                disabled={generating}
                className="flex-1 bg-purple-600 hover:bg-purple-700"
              >
                {generating ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Generating...
                  </>
                ) : (
                  'Generate'
                )}
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>

      {/* Questions Dialog */}
      <Dialog open={showQuestionsDialog} onOpenChange={setShowQuestionsDialog}>
        <DialogContent className="max-w-4xl max-h-[85vh]">
          <DialogHeader>
            <DialogTitle className="text-2xl flex items-center gap-3">
              <HelpCircle className="h-6 w-6 text-blue-600" />
              Generated Questions
            </DialogTitle>
            <DialogDescription className="text-base">
              {selectedDocument?.title} • {questions.length} questions
            </DialogDescription>
          </DialogHeader>

          <ScrollArea className="h-[60vh] pr-4">
            {loadingQuestions ? (
              <div className="flex items-center justify-center py-20">
                <Loader2 className="h-10 w-10 animate-spin text-neutral-400" />
              </div>
            ) : questions.length === 0 ? (
              <div className="text-center py-20 text-neutral-500">
                <HelpCircle className="h-16 w-16 mx-auto mb-4 text-neutral-300" />
                <p className="font-medium text-lg">No questions found</p>
                <p className="text-sm text-neutral-400 mt-2">Questions may still be generating</p>
              </div>
            ) : (
              <div className="space-y-6">
                {questions.map((question, index) => (
                  <Card key={question.id} className="shadow-sm">
                    <CardHeader className="pb-4">
                      <div className="flex items-start justify-between gap-4">
                        <CardTitle className="text-lg font-semibold flex-1">
                          <span className="text-blue-600 mr-2">Q{index + 1}.</span>
                          {question.question_text}
                        </CardTitle>
                        <div className="flex gap-2 shrink-0">
                          <Badge variant="outline">Grade {question.grade_level}</Badge>
                          <Badge variant="outline">Level {question.difficulty_level}</Badge>
                        </div>
                      </div>
                    </CardHeader>

                    {question.options && question.options.length > 0 && (
                      <CardContent className="space-y-3">
                        <div className="space-y-2">
                          <p className="text-sm font-medium text-neutral-700">Options:</p>
                          <div className="grid gap-2">
                            {question.options.map((option, optIndex) => (
                              <div
                                key={optIndex}
                                className={`p-3 rounded-lg border ${option === question.correct_answer
                                    ? 'bg-green-50 border-green-300 text-green-900'
                                    : 'bg-neutral-50 border-neutral-200'
                                  }`}
                              >
                                <span className="font-medium mr-2">{String.fromCharCode(65 + optIndex)}.</span>
                                {option}
                                {option === question.correct_answer && (
                                  <Badge variant="default" className="ml-2 bg-green-600">Correct</Badge>
                                )}
                              </div>
                            ))}
                          </div>
                        </div>

                        {question.explanation && (
                          <div className="mt-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                            <p className="text-sm font-medium text-blue-900 mb-1">Explanation:</p>
                            <p className="text-sm text-blue-800">{question.explanation}</p>
                          </div>
                        )}
                      </CardContent>
                    )}

                    {(!question.options || question.options.length === 0) && (
                      <CardContent>
                        <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
                          <p className="text-sm font-medium text-green-900 mb-1">Answer:</p>
                          <p className="text-sm text-green-800 font-medium">{question.correct_answer}</p>
                        </div>

                        {question.explanation && (
                          <div className="mt-3 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                            <p className="text-sm font-medium text-blue-900 mb-1">Explanation:</p>
                            <p className="text-sm text-blue-800">{question.explanation}</p>
                          </div>
                        )}
                      </CardContent>
                    )}
                  </Card>
                ))}
              </div>
            )}
          </ScrollArea>
        </DialogContent>
      </Dialog>
    </div>
  );
}