import {
  Teacher,
  Class,
  Student,
  Attempt,
  Assignment,
  KPI,
  ActivityData,
  MasteryData,
  ContentResource,
  Notification,
  MathDomain,
} from '@/types';

// Teachers
export const mockTeachers: Teacher[] = [
  { id: 't1', name: 'Ms. Perera', email: 'perera@school.lk', role: 'teacher' },
  { id: 't2', name: 'Mr. Silva', email: 'silva@school.lk', role: 'teacher' },
  { id: 't3', name: 'Mrs. Fernando', email: 'fernando@school.lk', role: 'coordinator' },
];

// Classes
export const mockClasses: Class[] = [
  {
    id: 'c1',
    name: '3A',
    grade: 3,
    teacherId: 't1',
    teacherName: 'Ms. Perera',
    studentCount: 28,
    status: 'active',
    notes: 'Strong in numbers, needs measurement practice',
    createdAt: new Date('2024-01-15'),
    updatedAt: new Date('2024-11-20'),
  },
  {
    id: 'c2',
    name: '3B',
    grade: 3,
    teacherId: 't1',
    teacherName: 'Ms. Perera',
    studentCount: 25,
    status: 'active',
    createdAt: new Date('2024-01-15'),
    updatedAt: new Date('2024-11-22'),
  },
  {
    id: 'c3',
    name: '3C',
    grade: 3,
    teacherId: 't2',
    teacherName: 'Mr. Silva',
    studentCount: 30,
    status: 'active',
    createdAt: new Date('2024-01-15'),
    updatedAt: new Date('2024-11-23'),
  },
  {
    id: 'c4',
    name: '3D',
    grade: 3,
    teacherId: 't2',
    teacherName: 'Mr. Silva',
    studentCount: 27,
    status: 'active',
    createdAt: new Date('2024-01-15'),
    updatedAt: new Date('2024-11-21'),
  },
];

// Students
const firstNames = ['Saman', 'Nimal', 'Kasun', 'Dilani', 'Amaya', 'Sanduni', 'Tharindu', 'Nethmi', 'Kamal', 'Ishara', 'Chamodi', 'Nuwan', 'Hashini', 'Ravindu', 'Malsha'];
const lastNames = ['Perera', 'Silva', 'Fernando', 'Gunawardena', 'Jayawardena', 'Wickramasinghe', 'Dias', 'De Silva', 'Rodrigo', 'Mendis'];

export const mockStudents: Student[] = [];
let studentIdCounter = 1;

mockClasses.forEach((cls) => {
  for (let i = 0; i < cls.studentCount; i++) {
    const firstName = firstNames[Math.floor(Math.random() * firstNames.length)];
    const lastName = lastNames[Math.floor(Math.random() * lastNames.length)];
    const totalAttempts = Math.floor(Math.random() * 100) + 20;
    const avgScore = Math.floor(Math.random() * 40) + 60;
    
    mockStudents.push({
      id: `s${studentIdCounter++}`,
      name: `${firstName} ${lastName}`,
      classId: cls.id,
      className: cls.name,
      grade: cls.grade,
      lastLogin: new Date(Date.now() - Math.random() * 7 * 24 * 60 * 60 * 1000),
      totalAttempts,
      averageScore: avgScore,
      needsHelp: avgScore < 70,
      strengths: avgScore > 80 ? ['numbers', 'operations'] : avgScore > 70 ? ['shapes'] : [],
      weaknesses: avgScore < 70 ? ['measurement', 'operations'] : avgScore < 80 ? ['measurement'] : [],
    });
  }
});

// Attempts
export const mockAttempts: Attempt[] = [];
const domains: MathDomain[] = ['numbers', 'measurement', 'shapes', 'operations'];
const strands: Record<MathDomain, string[]> = {
  numbers: ['place-value', 'number-facts', 'simple-equations'],
  measurement: ['length', 'area', 'capacity', 'weight'],
  shapes: ['2d-properties', '3d-properties'],
  operations: ['addition', 'subtraction', 'multiplication', 'division'],
};

mockStudents.slice(0, 30).forEach((student) => {
  const attemptCount = Math.floor(Math.random() * 10) + 5;
  for (let i = 0; i < attemptCount; i++) {
    const domain = domains[Math.floor(Math.random() * domains.length)];
    const strand = strands[domain][Math.floor(Math.random() * strands[domain].length)];
    mockAttempts.push({
      id: `a${mockAttempts.length + 1}`,
      studentId: student.id,
      studentName: student.name,
      domain,
      strand,
      score: Math.floor(Math.random() * 40) + 60,
      timeOnTask: Math.floor(Math.random() * 300) + 60,
      hintCount: Math.floor(Math.random() * 5),
      timestamp: new Date(Date.now() - Math.random() * 14 * 24 * 60 * 60 * 1000),
      mistakes: [],
      deviceType: Math.random() > 0.7 ? 'tablet' : 'phone',
      isOffline: Math.random() > 0.8,
    });
  }
});

// Assignments
export const mockAssignments: Assignment[] = [
  {
    id: 'as1',
    title: 'Length Practice - cm & m',
    domain: 'measurement',
    strand: 'length',
    difficulty: 'medium',
    assignedClassIds: ['c1', 'c2'],
    dueDate: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000),
    timeLimit: 20,
    status: 'active',
    averageScore: 78,
    completionRate: 65,
    createdAt: new Date('2024-11-20'),
  },
  {
    id: 'as2',
    title: 'Addition Facts to 20',
    domain: 'operations',
    strand: 'addition',
    difficulty: 'easy',
    assignedClassIds: ['c1', 'c2', 'c3'],
    dueDate: new Date(Date.now() + 3 * 24 * 60 * 60 * 1000),
    timeLimit: 15,
    status: 'active',
    averageScore: 82,
    completionRate: 88,
    createdAt: new Date('2024-11-18'),
  },
  {
    id: 'as3',
    title: '2D Shape Properties',
    domain: 'shapes',
    strand: '2d-properties',
    difficulty: 'medium',
    assignedClassIds: ['c3', 'c4'],
    dueDate: new Date(Date.now() + 10 * 24 * 60 * 60 * 1000),
    status: 'active',
    averageScore: 71,
    completionRate: 45,
    createdAt: new Date('2024-11-22'),
  },
];

// KPIs
export const mockKPIs: KPI[] = [
  { label: 'Active Classes', value: 4, delta: 0, trend: 'stable', format: 'number' },
  { label: 'Total Students', value: 110, delta: 5, trend: 'up', format: 'number' },
  { label: 'Tasks Completed This Week', value: 287, delta: 34, trend: 'up', format: 'number' },
  { label: 'Average Accuracy', value: 76, delta: 3, trend: 'up', format: 'percentage' },
  { label: 'Avg Time on Task', value: 156, delta: -12, trend: 'down', format: 'time' },
  { label: 'Students Needing Help', value: 18, delta: -3, trend: 'down', format: 'number' },
];

// Activity Data (for charts)
export const mockActivityData: ActivityData[] = [];
const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
mockClasses.slice(0, 3).forEach((cls) => {
  days.forEach((day, idx) => {
    mockActivityData.push({
      date: day,
      className: cls.name,
      attempts: Math.floor(Math.random() * 50) + 20,
      averageScore: Math.floor(Math.random() * 20) + 70,
    });
  });
});

// Mastery Data
export const mockMasteryData: MasteryData[] = [
  {
    domain: 'measurement',
    strand: 'length',
    masteryPercentage: 78,
    studentCount: 110,
    averageAccuracy: 76,
    averageTimeOnTask: 145,
  },
  {
    domain: 'measurement',
    strand: 'area',
    masteryPercentage: 65,
    studentCount: 110,
    averageAccuracy: 68,
    averageTimeOnTask: 189,
  },
  {
    domain: 'measurement',
    strand: 'capacity',
    masteryPercentage: 71,
    studentCount: 110,
    averageAccuracy: 73,
    averageTimeOnTask: 156,
  },
  {
    domain: 'measurement',
    strand: 'weight',
    masteryPercentage: 69,
    studentCount: 110,
    averageAccuracy: 71,
    averageTimeOnTask: 162,
  },
  {
    domain: 'numbers',
    strand: 'place-value',
    masteryPercentage: 82,
    studentCount: 110,
    averageAccuracy: 81,
    averageTimeOnTask: 134,
  },
  {
    domain: 'numbers',
    strand: 'number-facts',
    masteryPercentage: 88,
    studentCount: 110,
    averageAccuracy: 86,
    averageTimeOnTask: 112,
  },
  {
    domain: 'shapes',
    strand: '2d-properties',
    masteryPercentage: 74,
    studentCount: 110,
    averageAccuracy: 75,
    averageTimeOnTask: 167,
  },
  {
    domain: 'operations',
    strand: 'addition',
    masteryPercentage: 85,
    studentCount: 110,
    averageAccuracy: 84,
    averageTimeOnTask: 121,
  },
];

// Content Resources
export const mockContentResources: ContentResource[] = [
  {
    id: 'cr1',
    title: 'Length Measurement Worksheet',
    type: 'worksheet',
    domain: 'measurement',
    grade: 3,
    fileSize: '2.3 MB',
    language: 'en',
    downloadUrl: '/resources/length-worksheet.pdf',
    createdAt: new Date('2024-10-15'),
  },
  {
    id: 'cr2',
    title: 'AR Ruler Practice Targets',
    type: 'ar-target',
    domain: 'measurement',
    grade: 3,
    fileSize: '1.8 MB',
    language: 'en',
    downloadUrl: '/resources/ar-rulers.zip',
    createdAt: new Date('2024-10-20'),
  },
  {
    id: 'cr3',
    title: 'How to Use AR Capacity Tools',
    type: 'how-to-card',
    domain: 'measurement',
    grade: 3,
    fileSize: '850 KB',
    language: 'en',
    downloadUrl: '/resources/capacity-guide.pdf',
    createdAt: new Date('2024-10-12'),
  },
  {
    id: 'cr4',
    title: '2D Shapes Introduction Video',
    type: 'video',
    domain: 'shapes',
    grade: 3,
    language: 'si',
    downloadUrl: '/resources/shapes-video.mp4',
    createdAt: new Date('2024-09-28'),
  },
];

// Notifications
export const mockNotifications: Notification[] = [
  {
    id: 'n1',
    type: 'warning',
    title: 'Students Need Help',
    message: '5 students in class 3A scoring below 60% this week',
    read: false,
    timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000),
    actionUrl: '/students?filter=needsHelp',
  },
  {
    id: 'n2',
    type: 'success',
    title: 'Assignment Completed',
    message: 'Length Practice assignment has 88% completion rate',
    read: false,
    timestamp: new Date(Date.now() - 5 * 60 * 60 * 1000),
  },
  {
    id: 'n3',
    type: 'info',
    title: 'New Resources Available',
    message: '3 new AR targets uploaded to Content Library',
    read: true,
    timestamp: new Date(Date.now() - 24 * 60 * 60 * 1000),
    actionUrl: '/content',
  },
];
