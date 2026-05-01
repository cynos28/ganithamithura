'use client';

import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';
import { cn } from '@/lib/utils';
import { KPI } from '@/types';

interface KPICardProps {
  kpi: KPI;
  className?: string;
}

export function KPICard({ kpi, className }: KPICardProps) {
  const formatValue = (value: number, format?: string) => {
    switch (format) {
      case 'percentage':
        return `${value}%`;
      case 'time':
        return `${value}s`;
      default:
        return value.toLocaleString();
    }
  };

  const TrendIcon = kpi.trend === 'up' ? TrendingUp : kpi.trend === 'down' ? TrendingDown : Minus;
  const trendColor =
    kpi.trend === 'up'
      ? 'text-green-600'
      : kpi.trend === 'down'
      ? 'text-red-600'
      : 'text-neutral-500';

  return (
    <Card className={cn('transition-shadow hover:shadow-md', className)}>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium text-neutral-600 dark:text-neutral-400">
          {kpi.label}
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">{formatValue(kpi.value, kpi.format)}</div>
        {kpi.delta !== undefined && (
          <div className={cn('mt-2 flex items-center gap-1 text-xs', trendColor)}>
            <TrendIcon className="h-3 w-3" aria-hidden="true" />
            <span>
              {kpi.delta > 0 ? '+' : ''}
              {kpi.delta} from last week
            </span>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

interface KPIGridProps {
  kpis: KPI[];
  className?: string;
}

export function KPIGrid({ kpis, className }: KPIGridProps) {
  return (
    <div className={cn('grid gap-4 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6', className)}>
      {kpis.map((kpi, idx) => (
        <KPICard key={idx} kpi={kpi} />
      ))}
    </div>
  );
}
