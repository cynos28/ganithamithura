// Core domain types for Ganitha Mithura Dashboard

export type MathDomain = 'numbers' | 'measurement' | 'shapes' | 'operations';

export type MeasurementStrand = 'length' | 'area' | 'capacity' | 'weight';

export type NumbersStrand = 'place-value' | 'number-facts' | 'simple-equations';

export type ShapesStrand = '2d-properties' | '3d-properties';

export type OperationsStrand = 'addition' | 'subtraction' | 'multiplication' | 'division';

export interface Teacher {
  id: string;
  name: string;
  email: string;
  avatar?: string;
  role: 'teacher' | 'admin' | 'coordinator';
}

export interface Class {
  id: string;
  name: string;
  grade: number;
  teacherId: string;
  teacherName: string;
  studentCount: number;
  status: 'active' | 'archived';
  notes?: string;
  createdAt: Date;
  updatedAt: Date;
}

export interface Student {
  id: string;
  name: string;
  classId: string;
  className: string;
  grade: number;
  avatar?: string;
  lastLogin?: Date;
  totalAttempts: number;
  averageScore: number;
  needsHelp: boolean;
  strengths: string[];
  weaknesses: string[];
}

export interface Attempt {
  id: string;
  studentId: string;
  studentName: string;
  domain: MathDomain;
  strand: string;
  subskill?: string;
  unit?: string;
  score: number;
  timeOnTask: number; // in seconds
  hintCount: number;
  timestamp: Date;
  mistakes: string[];
  deviceType: 'phone' | 'tablet';
  isOffline: boolean;
}

export interface Assignment {
  id: string;
  title: string;
  domain: MathDomain;
  strand: string;
  difficulty: 'easy' | 'medium' | 'hard';
  assignedClassIds: string[];
  dueDate: Date;
  timeLimit?: number; // in minutes
  status: 'draft' | 'active' | 'completed';
  averageScore?: number;
  completionRate?: number;
  createdAt: Date;
}

export interface Assessment {
  id: string;
  title: string;
  type: 'quick-probe' | 'unit-test';
  domain: MathDomain;
  itemsPerSubskill: number;
  hintsLocked: boolean;
  tolerance: number;
  assignedClassIds: string[];
  dueDate: Date;
  results?: AssessmentResult[];
}

export interface AssessmentResult {
  assessmentId: string;
  studentId: string;
  score: number;
  itemAnalysis: {
    item: string;
    correct: boolean;
    mostMissedUnit?: string;
  }[];
  completedAt: Date;
}

export interface MasteryData {
  domain: MathDomain;
  strand: string;
  subskill?: string;
  masteryPercentage: number;
  studentCount: number;
  averageAccuracy: number;
  averageTimeOnTask: number;
}

export interface LessonProfile {
  id: string;
  name: string;
  domain: MathDomain;
  strand: string;
  unitsEnabled: string[];
  tolerance: number;
  hintsVisible: boolean;
  difficulty: 'easy' | 'medium' | 'hard';
  scaffoldLevel: 'low' | 'medium' | 'high';
}

export interface KPI {
  label: string;
  value: number;
  delta?: number; // week-over-week change
  trend?: 'up' | 'down' | 'stable';
  format?: 'number' | 'percentage' | 'time';
}

export interface ActivityData {
  date: string;
  className: string;
  attempts: number;
  averageScore: number;
}

export interface ContentResource {
  id: string;
  title: string;
  type: 'worksheet' | 'ar-target' | 'how-to-card' | 'video';
  domain: MathDomain;
  grade: number;
  fileSize?: string;
  language: 'en' | 'si' | 'ta';
  previewUrl?: string;
  downloadUrl: string;
  createdAt: Date;
}

export interface LiveSession {
  id: string;
  classId: string;
  className: string;
  domain: MathDomain;
  strand: string;
  activeStudents: number;
  totalStudents: number;
  status: 'active' | 'paused' | 'ended';
  startedAt: Date;
  currentUnit?: string;
  topErrors: string[];
  raiseHandQueue: string[]; // student IDs
}

export interface Notification {
  id: string;
  type: 'info' | 'warning' | 'success' | 'error';
  title: string;
  message: string;
  read: boolean;
  timestamp: Date;
  actionUrl?: string;
}

export interface Organization {
  id: string;
  name: string;
  timezone: string;
  language: 'en' | 'si' | 'ta';
  themeColor: string;
}

export interface Report {
  id: string;
  title: string;
  type: 'class' | 'student' | 'skill' | 'retention';
  generatedAt: Date;
  format: 'csv' | 'pdf';
  downloadUrl: string;
}
