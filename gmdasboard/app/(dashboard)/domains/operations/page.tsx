'use client';

import { DomainConfig } from '@/components/dashboard/domain-config';

export default function OperationsPage() {
  const strands = [
    {
      name: 'addition',
      units: [
        { label: 'Single Digit', enabled: true },
        { label: 'Two Digit', enabled: true },
        { label: 'With Regrouping', enabled: false },
      ],
      tolerance: 0,
      hintsVisible: true,
      difficulty: 'easy' as const,
    },
    {
      name: 'subtraction',
      units: [
        { label: 'Single Digit', enabled: true },
        { label: 'Two Digit', enabled: true },
        { label: 'With Borrowing', enabled: false },
      ],
      tolerance: 0,
      hintsVisible: true,
      difficulty: 'medium' as const,
    },
    {
      name: 'multiplication',
      units: [
        { label: '×2 Tables', enabled: true },
        { label: '×5 Tables', enabled: true },
        { label: '×10 Tables', enabled: true },
        { label: 'Others', enabled: false },
      ],
      tolerance: 0,
      hintsVisible: true,
      difficulty: 'medium' as const,
    },
    {
      name: 'division',
      units: [
        { label: 'Equal Groups', enabled: true },
        { label: 'Sharing', enabled: true },
        { label: 'Remainders', enabled: false },
      ],
      tolerance: 0,
      hintsVisible: true,
      difficulty: 'hard' as const,
    },
  ];

  return (
    <DomainConfig
      title="Operations"
      description="Configure arithmetic operations practice: addition, subtraction, multiplication, and division"
      strands={strands}
      accentColor="#F59E0B"
    />
  );
}
