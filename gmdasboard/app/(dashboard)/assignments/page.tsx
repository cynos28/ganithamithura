'use client';

import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Plus, Calendar, BarChart3, Users, Clock } from 'lucide-react';
import { mockAssignments, mockClasses } from '@/data/mock-data';
import { format } from 'date-fns';

export default function AssignmentsPage() {
  const [isCreating, setIsCreating] = useState(false);

  return (
    <div className="space-y-6 p-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Assignments</h1>
          <p className="mt-2 text-neutral-600 dark:text-neutral-400">
            Create and manage practice assignments for your classes
          </p>
        </div>
        <Dialog open={isCreating} onOpenChange={setIsCreating}>
          <DialogTrigger asChild>
            <Button className="gap-2">
              <Plus className="h-4 w-4" />
              New Assignment
            </Button>
          </DialogTrigger>
          <DialogContent className="sm:max-w-2xl">
            <DialogHeader>
              <DialogTitle>Create New Assignment</DialogTitle>
              <DialogDescription>
                Set up a new practice assignment for your students
              </DialogDescription>
            </DialogHeader>

            <div className="grid gap-4 py-4">
              <div className="grid gap-2">
                <Label htmlFor="title">Assignment Title</Label>
                <Input
                  id="title"
                  placeholder="e.g., Length Practice - Week 3"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="grid gap-2">
                  <Label htmlFor="domain">Math Domain</Label>
                  <Select>
                    <SelectTrigger id="domain">
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
                  <Label htmlFor="strand">Strand/Skill</Label>
                  <Select>
                    <SelectTrigger id="strand">
                      <SelectValue placeholder="Select skill" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="length">Length</SelectItem>
                      <SelectItem value="area">Area</SelectItem>
                      <SelectItem value="capacity">Capacity</SelectItem>
                      <SelectItem value="weight">Weight</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="grid gap-2">
                  <Label htmlFor="difficulty">Difficulty</Label>
                  <Select>
                    <SelectTrigger id="difficulty">
                      <SelectValue placeholder="Select difficulty" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="easy">Easy</SelectItem>
                      <SelectItem value="medium">Medium</SelectItem>
                      <SelectItem value="hard">Hard</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="grid gap-2">
                  <Label htmlFor="timeLimit">Time Limit (minutes)</Label>
                  <Input
                    id="timeLimit"
                    type="number"
                    placeholder="20"
                  />
                </div>
              </div>

              <div className="grid gap-2">
                <Label htmlFor="classes">Assign to Classes</Label>
                <Select>
                  <SelectTrigger id="classes">
                    <SelectValue placeholder="Select classes" />
                  </SelectTrigger>
                  <SelectContent>
                    {mockClasses.map((cls) => (
                      <SelectItem key={cls.id} value={cls.id}>
                        {cls.name} ({cls.studentCount} students)
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="grid gap-2">
                <Label htmlFor="dueDate">Due Date</Label>
                <Input
                  id="dueDate"
                  type="date"
                />
              </div>

              <div className="grid gap-2">
                <Label htmlFor="instructions">Instructions (optional)</Label>
                <Textarea
                  id="instructions"
                  placeholder="Add any special instructions for students..."
                  rows={3}
                />
              </div>
            </div>

            <div className="flex justify-end gap-2">
              <Button variant="outline" onClick={() => setIsCreating(false)}>
                Cancel
              </Button>
              <Button onClick={() => setIsCreating(false)}>
                Create Assignment
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      {/* Active Assignments */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {mockAssignments.map((assignment) => (
          <Card key={assignment.id} className="flex flex-col">
            <CardHeader>
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <CardTitle className="line-clamp-2">{assignment.title}</CardTitle>
                  <CardDescription className="mt-1">
                    <Badge variant="outline" className="mr-2">
                      {assignment.domain}
                    </Badge>
                    {assignment.strand}
                  </CardDescription>
                </div>
                <Badge
                  variant={
                    assignment.status === 'active'
                      ? 'default'
                      : assignment.status === 'draft'
                      ? 'secondary'
                      : 'outline'
                  }
                >
                  {assignment.status}
                </Badge>
              </div>
            </CardHeader>
            <CardContent className="flex-1 space-y-4">
              {/* Stats */}
              <div className="grid grid-cols-2 gap-3">
                <div className="flex items-center gap-2 text-sm">
                  <Users className="h-4 w-4 text-neutral-500" />
                  <span>{assignment.assignedClassIds.length} classes</span>
                </div>
                <div className="flex items-center gap-2 text-sm">
                  <Calendar className="h-4 w-4 text-neutral-500" />
                  <span>{format(assignment.dueDate, 'MMM d')}</span>
                </div>
                {assignment.timeLimit && (
                  <div className="flex items-center gap-2 text-sm">
                    <Clock className="h-4 w-4 text-neutral-500" />
                    <span>{assignment.timeLimit} min</span>
                  </div>
                )}
                {assignment.averageScore && (
                  <div className="flex items-center gap-2 text-sm">
                    <BarChart3 className="h-4 w-4 text-neutral-500" />
                    <span>{assignment.averageScore}% avg</span>
                  </div>
                )}
              </div>

              {/* Progress */}
              {assignment.completionRate !== undefined && (
                <div>
                  <div className="mb-1 flex items-center justify-between text-sm">
                    <span className="text-neutral-600">Completion</span>
                    <span className="font-medium">{assignment.completionRate}%</span>
                  </div>
                  <div className="h-2 overflow-hidden rounded-full bg-neutral-200">
                    <div
                      className="h-full rounded-full bg-blue-500 transition-all"
                      style={{ width: `${assignment.completionRate}%` }}
                    />
                  </div>
                </div>
              )}

              {/* Actions */}
              <div className="flex gap-2 pt-2">
                <Button variant="outline" size="sm" className="flex-1">
                  View Results
                </Button>
                <Button variant="outline" size="sm" className="flex-1">
                  Edit
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Empty State */}
      {mockAssignments.length === 0 && (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-12">
            <div className="rounded-full bg-neutral-100 p-3 dark:bg-neutral-800">
              <Plus className="h-6 w-6 text-neutral-500" />
            </div>
            <h3 className="mt-4 text-lg font-medium">No assignments yet</h3>
            <p className="mt-2 text-center text-sm text-neutral-600 dark:text-neutral-400">
              Create your first assignment to get started
            </p>
            <Button className="mt-4" onClick={() => setIsCreating(true)}>
              Create Assignment
            </Button>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
