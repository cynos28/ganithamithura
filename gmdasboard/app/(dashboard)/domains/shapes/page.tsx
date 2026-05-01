'use client';

import { DomainConfig } from '@/components/dashboard/domain-config';

export default function ShapesPage() {
  const strands = [
    {
      name: '2d-properties',
      units: [
        { label: 'Triangles', enabled: true },
        { label: 'Squares', enabled: true },
        { label: 'Rectangles', enabled: true },
        { label: 'Circles', enabled: true },
        { label: 'Polygons', enabled: false },
      ],
      tolerance: 5,
      hintsVisible: true,
      difficulty: 'easy' as const,
    },
    {
      name: '3d-properties',
      units: [
        { label: 'Cubes', enabled: true },
        { label: 'Spheres', enabled: true },
        { label: 'Cylinders', enabled: true },
        { label: 'Cones', enabled: false },
        { label: 'Pyramids', enabled: false },
      ],
      tolerance: 5,
      hintsVisible: true,
      difficulty: 'medium' as const,
    },
  ];

  return (
    <DomainConfig
      title="Shapes"
      description="Configure 2D and 3D shape recognition and properties practice with AR visualization"
      strands={strands}
      accentColor="#10B981"
    />
  );
}
