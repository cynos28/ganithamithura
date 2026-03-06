'use client';

import { useState, useCallback } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Upload, FileText, Loader2, CheckCircle2, XCircle } from 'lucide-react';
import { useDropzone } from 'react-dropzone';

interface DocumentUploadProps {
  onUploadSuccess?: (documentId?: string) => void;
}

export default function DocumentUpload({ onUploadSuccess }: DocumentUploadProps) {
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [title, setTitle] = useState('');
  const [topic, setTopic] = useState('Length');
  const [gradeLevel, setGradeLevel] = useState('1');
  const [status, setStatus] = useState<'idle' | 'success' | 'error'>('idle');
  const [message, setMessage] = useState('');

  const ragBase = process.env.NEXT_PUBLIC_RAG_API_URL || 'http://localhost:8000';

  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      const uploadedFile = acceptedFiles[0];
      setFile(uploadedFile);
      // Auto-fill title from filename if empty
      if (!title) {
        setTitle(uploadedFile.name.replace(/\.[^/.]+$/, ''));
      }
      setStatus('idle');
      setMessage('');
    }
  }, [title]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'text/plain': ['.txt'],
    },
    maxFiles: 1,
  });

  const handleUpload = async () => {
  if (!file) {
    setStatus('error');
    setMessage('Please select a file');
    return;
  }

  setUploading(true);
  setStatus('idle');
  setMessage('');

  const formData = new FormData();
  formData.append('file', file);
  formData.append('grade_levels', gradeLevel);
  formData.append('topic', topic);
  formData.append('title', title || file.name);

  try {
    const response = await fetch(`${ragBase}/api/v1/upload/`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Upload failed');
    }

    const result = await response.json();
    
    setStatus('success');
    setMessage(`Document "${result.title}" uploaded successfully! Questions are being generated...`);
    
    // Reset form
    setFile(null);
    setTitle('');
    
    // Pass document ID to parent for polling
    if (onUploadSuccess) {
      onUploadSuccess(result.id);
    }
  } catch (error) {
    setStatus('error');
    setMessage(error instanceof Error ? error.message : 'Upload failed');
  } finally {
    setUploading(false);
  }
};

  return (
    <Card className="shadow-sm">
      <CardHeader className="pb-5 pt-6 px-6">
        <CardTitle className="flex items-center gap-3 text-xl sm:text-2xl">
          <Upload className="h-6 w-6 text-neutral-700" />
          Upload & Generate Questions
        </CardTitle>
        <CardDescription className="text-base sm:text-lg mt-2">
          Upload learning materials to generate adaptive questions for students
        </CardDescription>
      </CardHeader>
      <CardContent className="pt-4 px-6 pb-6 space-y-6">
        {/* File Drop Zone */}
        <div
          {...getRootProps()}
          className={`border-2 border-dashed rounded-xl p-10 text-center cursor-pointer transition-all ${
            isDragActive
              ? 'border-blue-500 bg-blue-50'
              : file
              ? 'border-green-500 bg-green-50'
              : 'border-neutral-300 hover:border-neutral-400 hover:bg-neutral-50'
          }`}
        >
          <input {...getInputProps()} />
          {file ? (
            <div className="flex flex-col items-center gap-3">
              <FileText className="h-12 w-12 text-green-600" />
              <div>
                <p className="font-medium text-neutral-900">{file.name}</p>
                <p className="text-sm text-neutral-500 mt-1">
                  {(file.size / 1024 / 1024).toFixed(2)} MB
                </p>
              </div>
              <Button
                variant="outline"
                size="sm"
                onClick={(e) => {
                  e.stopPropagation();
                  setFile(null);
                }}
              >
                Change File
              </Button>
            </div>
          ) : (
            <div className="flex flex-col items-center gap-3">
              <Upload className="h-12 w-12 text-neutral-400" />
              <div>
                <p className="font-medium text-neutral-900">
                  {isDragActive ? 'Drop your file here' : 'Drop file or click to upload'}
                </p>
                <p className="text-sm text-neutral-500 mt-1">
                  Supports PDF, DOCX, TXT (Max 10MB)
                </p>
              </div>
            </div>
          )}
        </div>

        {/* Form Fields */}
        <div className="grid gap-6 sm:grid-cols-2">
          <div className="space-y-2">
            <Label htmlFor="title">Document Title</Label>
            <Input
              id="title"
              placeholder="e.g., Length Measurement Guide"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="topic">Measurement Domain</Label>
            <Select value={topic} onValueChange={setTopic}>
              <SelectTrigger id="topic">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="Length">📏 Length (cm, m, km)</SelectItem>
                <SelectItem value="Area">📐 Area (cm², m²)</SelectItem>
                <SelectItem value="Volume">🥛 Volume (mL, L)</SelectItem>
                <SelectItem value="Weight">⚖️ Weight (g, kg)</SelectItem>
              </SelectContent>
            </Select>
            <p className="text-xs text-neutral-500">
              Questions will be generated specifically for this measurement type
            </p>
          </div>

          <div className="space-y-2">
            <Label htmlFor="grade">Grade Levels</Label>
            <Select value={gradeLevel} onValueChange={setGradeLevel}>
              <SelectTrigger id="grade">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="1">Grade 1 (Simple - Ages 6-7)</SelectItem>
                <SelectItem value="2">Grade 2 (Basic - Ages 7-8)</SelectItem>
                <SelectItem value="3">Grade 3 (Intermediate - Ages 8-9)</SelectItem>
                <SelectItem value="4">Grade 4 (Advanced - Ages 9-10)</SelectItem>
                <SelectItem value="1,2">Grades 1-2</SelectItem>
                <SelectItem value="2,3">Grades 2-3</SelectItem>
                <SelectItem value="3,4">Grades 3-4</SelectItem>
                <SelectItem value="1,2,3,4">All Grades (1-4)</SelectItem>
              </SelectContent>
            </Select>
            <p className="text-xs text-neutral-500">
              {gradeLevel === '1' && 'Simple questions with basic counting and comparison (numbers 1-20)'}
              {gradeLevel === '2' && 'Basic calculations and comparisons (numbers 1-100)'}
              {gradeLevel === '3' && 'Multi-step problems with conversions (numbers 1-1000)'}
              {gradeLevel === '4' && 'Complex word problems with reasoning (decimals allowed)'}
              {gradeLevel.includes(',') && 'Questions adapted for each grade level'}
            </p>
          </div>
        </div>

        {/* Status Messages */}
        {status === 'success' && (
          <div className="rounded-lg border border-green-200 bg-green-50 p-4 flex items-start gap-3">
            <CheckCircle2 className="h-5 w-5 text-green-600 mt-0.5" />
            <div className="flex-1">
              <p className="font-medium text-green-900">Upload Successful</p>
              <p className="text-sm text-green-700 mt-1">{message}</p>
            </div>
          </div>
        )}

        {status === 'error' && (
          <div className="rounded-lg border border-red-200 bg-red-50 p-4 flex items-start gap-3">
            <XCircle className="h-5 w-5 text-red-600 mt-0.5" />
            <div className="flex-1">
              <p className="font-medium text-red-900">Upload Failed</p>
              <p className="text-sm text-red-700 mt-1">{message}</p>
            </div>
          </div>
        )}

        {/* Upload Button */}
        <Button
          onClick={handleUpload}
          disabled={!file || uploading}
          className="w-full h-12 text-base"
          size="lg"
        >
          {uploading ? (
            <>
              <Loader2 className="mr-2 h-5 w-5 animate-spin" />
              Uploading...
            </>
          ) : (
            <>
              <Upload className="mr-2 h-5 w-5" />
              Upload Document
            </>
          )}
        </Button>
      </CardContent>
    </Card>
  );
}