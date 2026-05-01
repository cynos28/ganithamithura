'use client';

import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { Plus, Clock, Users, TrendingUp, AlertCircle } from 'lucide-react';
import { ChartCard, DonutChart } from '@/components/dashboard/charts';

export default function AssessmentsPage() {
  const [isCreating, setIsCreating] = useState(false);
  const [assessmentType, setAssessmentType] = useState<'quick-probe' | 'unit-test'>('quick-probe');

  const assessments = [
    {
      id: 'a1',
      title: 'Length Quick Probe',
      type: 'quick-probe',
      domain: 'measurement',
      completed: 23,
      total: 28,
      avgScore: 78,
      status: 'active',
    },
    {
      id: 'a2',
      title: 'Numbers Unit Test',
      type: 'unit-test',
      domain: 'numbers',
      completed: 28,
      total: 28,
      avgScore: 82,
      status: 'completed',
    },
  ];

  const distributionData = [
    { name: 'Excellent (90-100%)', value: 8 },
    { name: 'Good (80-89%)', value: 12 },
    { name: 'Fair (70-79%)', value: 6 },
    { name: 'Needs Help (<70%)', value: 2 },
  ];

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Assessments</h1>
          <p className="mt-2 text-neutral-600 dark:text-neutral-400">
            Create and manage quick probes and unit tests for your students
          </p>
        </div>
        <Dialog open={isCreating} onOpenChange={setIsCreating}>
          <DialogTrigger asChild>
            <Button className="gap-2">
              <Plus className="h-4 w-4" />
              New Assessment
            </Button>
          </DialogTrigger>
          <DialogContent className="sm:max-w-2xl">
            <DialogHeader>
              <DialogTitle>Create New Assessment</DialogTitle>
              <DialogDescription>
                Build a customized assessment for your students
              </DialogDescription>
            </DialogHeader>

            <Tabs value={assessmentType} onValueChange={(v) => setAssessmentType(v as any)}>
              <TabsList className="grid w-full grid-cols-2">
                <TabsTrigger value="quick-probe">Quick Probe (2 min)</TabsTrigger>
                <TabsTrigger value="unit-test">Unit Test</TabsTrigger>
              </TabsList>

              <TabsContent value="quick-probe" className="space-y-4 pt-4">
                <div className="grid gap-4">
                  <div className="grid gap-2">
                    <Label htmlFor="probe-title">Title</Label>
                    <Input id="probe-title" placeholder="e.g., Length Quick Check" />
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div className="grid gap-2">
                      <Label htmlFor="probe-domain">Domain</Label>
                      <Select>
                        <SelectTrigger id="probe-domain">
                          <SelectValue placeholder="Select domain" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="numbers">Numbers</SelectItem>
                          <SelectItem value="measurement">Measurement</SelectItem>
                          <SelectItem value="shapes">Shapes</SelectItem>
                          <SelectItem value="operations">Operations</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>

                    <div className="grid gap-2">
                      <Label htmlFor="probe-items">Items</Label>
                      <Input id="probe-items" type="number" defaultValue="5" />
                    </div>
                  </div>

                  <div className="grid gap-2">
                    <Label>Options</Label>
                    <div className="space-y-2">
                      <div className="flex items-center justify-between rounded-lg border p-3">
                        <span className="text-sm">Lock hints</span>
                        <Badge variant="outline">Recommended</Badge>
                      </div>
                      <div className="flex items-center justify-between rounded-lg border p-3">
                        <span className="text-sm">Fixed tolerance (5%)</span>
                        <Badge variant="outline">Default</Badge>
                      </div>
                    </div>
                  </div>
                </div>
              </TabsContent>

              <TabsContent value="unit-test" className="space-y-4 pt-4">
                <div className="grid gap-4">
                  <div className="grid gap-2">
                    <Label htmlFor="test-title">Title</Label>
                    <Input id="test-title" placeholder="e.g., Measurement Unit 1 Test" />
                  </div>

                  <div className="grid gap-2">
                    <Label htmlFor="test-domain">Domain</Label>
                    <Select>
                      <SelectTrigger id="test-domain">
                        <SelectValue placeholder="Select domain" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="numbers">Numbers</SelectItem>
                        <SelectItem value="measurement">Measurement</SelectItem>
                        <SelectItem value="shapes">Shapes</SelectItem>
                        <SelectItem value="operations">Operations</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="grid gap-2">
                    <Label htmlFor="items-per-skill">Items per Subskill</Label>
                    <Input id="items-per-skill" type="number" defaultValue="3" />
                    <p className="text-xs text-neutral-500">
                      Total items will vary based on selected domain
                    </p>
                  </div>
                </div>
              </TabsContent>
            </Tabs>

            <div className="flex justify-end gap-2 pt-4">
              <Button variant="outline" onClick={() => setIsCreating(false)}>
                Cancel
              </Button>
              <Button onClick={() => setIsCreating(false)}>Create Assessment</Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      {/* Active Assessments */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {assessments.map((assessment) => (
          <Card key={assessment.id}>
            <CardHeader>
              <div className="flex items-start justify-between">
                <div>
                  <CardTitle className="text-base">{assessment.title}</CardTitle>
                  <CardDescription className="mt-1">
                    <Badge variant="outline" className="mr-2">
                      {assessment.domain}
                    </Badge>
                    {assessment.type === 'quick-probe' ? 'Quick Probe' : 'Unit Test'}
                  </CardDescription>
                </div>
                <Badge variant={assessment.status === 'active' ? 'default' : 'secondary'}>
                  {assessment.status}
                </Badge>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-3">
                <div className="flex items-center gap-2 text-sm">
                  <Users className="h-4 w-4 text-neutral-500" />
                  <span>{assessment.completed}/{assessment.total}</span>
                </div>
                <div className="flex items-center gap-2 text-sm">
                  <TrendingUp className="h-4 w-4 text-neutral-500" />
                  <span>{assessment.avgScore}% avg</span>
                </div>
              </div>

              <div>
                <div className="mb-1 flex items-center justify-between text-sm">
                  <span className="text-neutral-600">Progress</span>
                  <span className="font-medium">
                    {Math.round((assessment.completed / assessment.total) * 100)}%
                  </span>
                </div>
                <div className="h-2 overflow-hidden rounded-full bg-neutral-200">
                  <div
                    className="h-full rounded-full bg-blue-500"
                    style={{ width: `${(assessment.completed / assessment.total) * 100}%` }}
                  />
                </div>
              </div>

              <div className="flex gap-2">
                <Button variant="outline" size="sm" className="flex-1">
                  View Results
                </Button>
                <Button size="sm" className="flex-1">
                  Item Analysis
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Results Overview */}
      <div className="grid gap-6 lg:grid-cols-2">
        <ChartCard
          title="Score Distribution"
          description="How students performed on recent assessments"
        >
          <DonutChart data={distributionData} />
        </ChartCard>

        <Card>
          <CardHeader>
            <CardTitle>Most Missed Items</CardTitle>
            <CardDescription>Common challenges across assessments</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {[
                { skill: 'Converting cm to m', misses: 12, domain: 'measurement' },
                { skill: 'Area of rectangles', misses: 8, domain: 'measurement' },
                { skill: 'Place value (hundreds)', misses: 7, domain: 'numbers' },
                { skill: 'Multiplication by 5', misses: 5, domain: 'operations' },
              ].map((item, idx) => (
                <div
                  key={idx}
                  className="flex items-center justify-between rounded-lg border p-3"
                >
                  <div>
                    <p className="text-sm font-medium">{item.skill}</p>
                    <p className="text-xs text-neutral-500">{item.domain}</p>
                  </div>
                  <div className="flex items-center gap-2">
                    <AlertCircle className="h-4 w-4 text-red-500" />
                    <Badge variant="destructive">{item.misses} students</Badge>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Assessment Tips */}
      <Card>
        <CardHeader>
          <CardTitle>Assessment Best Practices</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-3 md:grid-cols-2">
            <div className="flex gap-3 rounded-lg border p-4">
              <Clock className="h-5 w-5 shrink-0 text-blue-500" />
              <div>
                <p className="font-medium">Quick Probes</p>
                <p className="text-sm text-neutral-600">
                  Use 2-minute probes to check daily understanding
                </p>
              </div>
            </div>
            <div className="flex gap-3 rounded-lg border p-4">
              <TrendingUp className="h-5 w-5 shrink-0 text-green-500" />
              <div>
                <p className="font-medium">Item Analysis</p>
                <p className="text-sm text-neutral-600">
                  Review which questions students struggled with
                </p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
