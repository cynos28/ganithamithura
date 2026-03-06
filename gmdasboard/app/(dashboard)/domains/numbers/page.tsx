'use client';

import { DomainConfig } from '@/components/dashboard/domain-config';

export default function NumbersPage() {
  const strands = [
    {
      name: 'place-value',
      units: [
        { label: 'Ones', enabled: true },
        { label: 'Tens', enabled: true },
        { label: 'Hundreds', enabled: true },
        { label: 'Thousands', enabled: false },
      ],
      tolerance: 0,
      hintsVisible: true,
      difficulty: 'easy' as const,
    },
    {
      name: 'number-facts',
      units: [
        { label: 'To 10', enabled: true },
        { label: 'To 20', enabled: true },
        { label: 'To 50', enabled: false },
        { label: 'To 100', enabled: false },
      ],
      tolerance: 0,
      hintsVisible: true,
      difficulty: 'medium' as const,
    },
    {
      name: 'simple-equations',
      units: [
        { label: 'Find Missing', enabled: true },
        { label: 'Balance', enabled: true },
        { label: 'Word Problems', enabled: false },
      ],
      tolerance: 0,
      hintsVisible: true,
      difficulty: 'hard' as const,
    },
  ];

  return (
    <DomainConfig
      title="Numbers"
      description="Configure place value, number facts, and simple equations practice"
      strands={strands}
      accentColor="#8B5CF6"
    />
  );
}
