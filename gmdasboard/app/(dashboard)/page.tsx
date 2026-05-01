'use client';

import { KPIGrid } from '@/components/dashboard/kpi-card';
import {
  ChartCard,
  ActivityLineChart,
  StackedBarChart,
  DonutChart,
} from '@/components/dashboard/charts';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Plus, Play, Users, ClipboardList } from 'lucide-react';
import {
  mockKPIs,
  mockActivityData,
  mockMasteryData,
  mockAttempts,
} from '@/data/mock-data';
import { formatDistanceToNow } from 'date-fns';

export default function OverviewPage() {
  // Prepare data for stacked bar chart (mastery by domain)
  const masteryByDomain = mockMasteryData.slice(0, 4).map((m) => ({
    name: m.strand,
    mastery: m.masteryPercentage,
  }));

  // Prepare hint usage data for donut chart
  const hintData = [
    { name: 'No Hints', value: 45 },
    { name: '1 Hint', value: 30 },
    { name: '2 Hints', value: 15 },
    { name: '3+ Hints', value: 10 },
  ];

  // Recent activity feed from latest attempts
  const recentActivity = mockAttempts
    .sort((a, b) => b.timestamp.getTime() - a.timestamp.getTime())
    .slice(0, 8);

  return (
    <div className="space-y-6 p-6">
      {/* Page Header */}
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Overview</h1>
        <p className="mt-2 text-neutral-600 dark:text-neutral-400">
          Welcome back! Here's what's happening with your students.
        </p>
      </div>

      {/* KPI Cards */}
      <KPIGrid kpis={mockKPIs} />

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle>Quick Actions</CardTitle>
          <CardDescription>Common tasks to get started</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-3">
            <Button className="gap-2">
              <ClipboardList className="h-4 w-4" />
              Create Assignment
            </Button>
            <Button variant="outline" className="gap-2">
              <Play className="h-4 w-4" />
              Start Live Session
            </Button>
            <Button variant="outline" className="gap-2">
              <Users className="h-4 w-4" />
              Import Students
            </Button>
            <Button variant="outline" className="gap-2">
              <Plus className="h-4 w-4" />
              New Class
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Charts Row */}
      <div className="grid gap-6 lg:grid-cols-2">
        <ChartCard
          title="Weekly Activity by Class"
          description="Student attempts per class over the last 7 days"
        >
          <ActivityLineChart data={mockActivityData} />
        </ChartCard>

        <ChartCard
          title="Skill Mastery by Domain"
          description="Current mastery levels across measurement strands"
        >
          <StackedBarChart data={masteryByDomain} keys={['mastery']} />
        </ChartCard>
      </div>

      {/* Second Charts Row */}
      <div className="grid gap-6 lg:grid-cols-3">
        <ChartCard
          title="Hint Usage Distribution"
          description="How students are using hints during practice"
        >
          <DonutChart data={hintData} />
        </ChartCard>

        {/* Recent Activity Feed */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Recent Activity</CardTitle>
            <CardDescription>Latest student attempts and scores</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {recentActivity.map((attempt) => (
                <div
                  key={attempt.id}
                  className="flex items-start justify-between rounded-lg border p-3 hover:bg-neutral-50 dark:hover:bg-neutral-900"
                >
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <p className="font-medium">{attempt.studentName}</p>
                      <Badge variant="outline" className="text-xs">
                        {attempt.domain}
                      </Badge>
                    </div>
                    <p className="mt-1 text-sm text-neutral-600 dark:text-neutral-400">
                      {attempt.strand} • {attempt.score}% • {attempt.hintCount} hints
                    </p>
                    <p className="mt-1 text-xs text-neutral-500">
                      {formatDistanceToNow(attempt.timestamp, { addSuffix: true })}
                    </p>
                  </div>
                  <Badge
                    variant={
                      attempt.score >= 80
                        ? 'default'
                        : attempt.score >= 60
                        ? 'secondary'
                        : 'destructive'
                    }
                  >
                    {attempt.score}%
                  </Badge>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
