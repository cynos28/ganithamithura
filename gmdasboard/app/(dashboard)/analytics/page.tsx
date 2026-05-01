'use client';

import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import { ChartCard, MasteryBarChart, ProgressChart, DonutChart } from '@/components/dashboard/charts';
import { Download, FileText, Mail } from 'lucide-react';
import { mockMasteryData, mockAttempts } from '@/data/mock-data';

export default function AnalyticsPage() {
  const deviceData = [
    { name: 'Phone', value: 75 },
    { name: 'Tablet', value: 25 },
  ];

  const progressData = mockAttempts.slice(0, 10).map((a, idx) => ({
    date: `Day ${idx + 1}`,
    score: a.score,
  }));

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Analytics & Reports</h1>
          <p className="mt-2 text-neutral-600 dark:text-neutral-400">
            Comprehensive insights into student performance and engagement
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" className="gap-2">
            <Mail className="h-4 w-4" />
            Schedule Email
          </Button>
          <Button className="gap-2">
            <Download className="h-4 w-4" />
            Export Report
          </Button>
        </div>
      </div>

      <Tabs defaultValue="class" className="space-y-6">
        <TabsList>
          <TabsTrigger value="class">By Class</TabsTrigger>
          <TabsTrigger value="student">By Student</TabsTrigger>
          <TabsTrigger value="skill">By Skill</TabsTrigger>
          <TabsTrigger value="retention">Retention</TabsTrigger>
        </TabsList>

        <TabsContent value="class" className="space-y-6">
          <div className="grid gap-6 lg:grid-cols-2">
            <ChartCard title="Skill Mastery by Domain" description="Average mastery across all strands">
              <MasteryBarChart data={mockMasteryData.slice(0, 8)} />
            </ChartCard>

            <ChartCard title="Device Usage" description="Student device preferences">
              <DonutChart data={deviceData} />
            </ChartCard>
          </div>

          <Card>
            <CardHeader>
              <CardTitle>Class Performance Summary</CardTitle>
              <CardDescription>Overall metrics for all active classes</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4 md:grid-cols-4">
                <div className="rounded-lg border p-4">
                  <p className="text-2xl font-bold">287</p>
                  <p className="text-sm text-neutral-500">Total Attempts</p>
                </div>
                <div className="rounded-lg border p-4">
                  <p className="text-2xl font-bold">76%</p>
                  <p className="text-sm text-neutral-500">Average Score</p>
                </div>
                <div className="rounded-lg border p-4">
                  <p className="text-2xl font-bold">156s</p>
                  <p className="text-sm text-neutral-500">Avg Time on Task</p>
                </div>
                <div className="rounded-lg border p-4">
                  <p className="text-2xl font-bold">2.1</p>
                  <p className="text-sm text-neutral-500">Avg Hints Used</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="student" className="space-y-6">
          <ChartCard title="Student Progress Over Time" description="Average scores across all students">
            <ProgressChart data={progressData} />
          </ChartCard>

          <Card>
            <CardHeader>
              <CardTitle>Top Performers</CardTitle>
              <CardDescription>Students with highest average scores</CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-neutral-500">Student performance data would be displayed here</p>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="skill" className="space-y-6">
          <ChartCard title="Skill Mastery Breakdown" description="Performance by math strand">
            <MasteryBarChart data={mockMasteryData} />
          </ChartCard>
        </TabsContent>

        <TabsContent value="retention" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Retention Metrics</CardTitle>
              <CardDescription>Long-term learning and recall patterns</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4 md:grid-cols-3">
                <div className="rounded-lg border p-4">
                  <p className="text-2xl font-bold">82%</p>
                  <p className="text-sm text-neutral-500">7-Day Retention</p>
                </div>
                <div className="rounded-lg border p-4">
                  <p className="text-2xl font-bold">74%</p>
                  <p className="text-sm text-neutral-500">14-Day Retention</p>
                </div>
                <div className="rounded-lg border p-4">
                  <p className="text-2xl font-bold">68%</p>
                  <p className="text-sm text-neutral-500">30-Day Retention</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      <Card>
        <CardHeader>
          <CardTitle>Export Options</CardTitle>
          <CardDescription>Download reports in various formats</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex gap-3">
            <Button variant="outline" className="gap-2">
              <FileText className="h-4 w-4" />
              Export as PDF
            </Button>
            <Button variant="outline" className="gap-2">
              <Download className="h-4 w-4" />
              Export as CSV
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
