'use client';

import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Play, Pause, Users, AlertCircle, MessageSquare, Clock, TrendingUp } from 'lucide-react';
import { mockClasses, mockStudents } from '@/data/mock-data';

export default function LiveSessionPage() {
  const [isActive, setIsActive] = useState(false);
  const [selectedClass, setSelectedClass] = useState<string | null>(null);

  const activeStudents = 23;
  const totalStudents = 28;

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Live Session</h1>
          <p className="mt-2 text-neutral-600 dark:text-neutral-400">
            Monitor real-time student activity and provide instant support
          </p>
        </div>
        {isActive ? (
          <Button variant="destructive" className="gap-2" onClick={() => setIsActive(false)}>
            <Pause className="h-4 w-4" />
            End Session
          </Button>
        ) : (
          <Button className="gap-2" onClick={() => setIsActive(true)}>
            <Play className="h-4 w-4" />
            Start Session
          </Button>
        )}
      </div>

      {!isActive ? (
        <Card>
          <CardHeader>
            <CardTitle>Select a Class</CardTitle>
            <CardDescription>Choose which class to monitor</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-3">
              {mockClasses.map((cls) => (
                <button
                  key={cls.id}
                  onClick={() => {
                    setSelectedClass(cls.id);
                    setIsActive(true);
                  }}
                  className="flex items-center justify-between rounded-lg border p-4 text-left transition-colors hover:bg-neutral-50 dark:hover:bg-neutral-900"
                >
                  <div>
                    <p className="font-medium">{cls.name}</p>
                    <p className="text-sm text-neutral-500">{cls.studentCount} students</p>
                  </div>
                  <Users className="h-5 w-5 text-neutral-400" />
                </button>
              ))}
            </div>
          </CardContent>
        </Card>
      ) : (
        <>
          {/* Live Session Controls */}
          <div className="grid gap-4 md:grid-cols-4">
            <Card>
              <CardContent className="pt-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-2xl font-bold">{activeStudents}/{totalStudents}</p>
                    <p className="text-sm text-neutral-500">Active Students</p>
                  </div>
                  <Users className="h-8 w-8 text-blue-500" />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="pt-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-2xl font-bold">18</p>
                    <p className="text-sm text-neutral-500">Attempts</p>
                  </div>
                  <TrendingUp className="h-8 w-8 text-green-500" />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="pt-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-2xl font-bold">74%</p>
                    <p className="text-sm text-neutral-500">Avg Accuracy</p>
                  </div>
                  <TrendingUp className="h-8 w-8 text-amber-500" />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="pt-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-2xl font-bold">3</p>
                    <p className="text-sm text-neutral-500">Raised Hands</p>
                  </div>
                  <AlertCircle className="h-8 w-8 text-red-500" />
                </div>
              </CardContent>
            </Card>
          </div>

          <div className="grid gap-6 lg:grid-cols-3">
            {/* Real-time Activity */}
            <Card className="lg:col-span-2">
              <CardHeader>
                <CardTitle>Student Activity Stream</CardTitle>
                <CardDescription>Live updates as students work</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {mockStudents.slice(0, 8).map((student, idx) => (
                    <div
                      key={student.id}
                      className="flex items-center justify-between rounded-lg border p-3"
                    >
                      <div className="flex items-center gap-3">
                        <div className="flex h-8 w-8 items-center justify-center rounded-full bg-blue-100 text-sm font-medium text-blue-600">
                          {student.name.split(' ').map(n => n[0]).join('')}
                        </div>
                        <div>
                          <p className="text-sm font-medium">{student.name}</p>
                          <p className="text-xs text-neutral-500">
                            Working on length • {Math.floor(Math.random() * 5) + 1}m ago
                          </p>
                        </div>
                      </div>
                      <Badge variant={idx % 3 === 0 ? 'destructive' : idx % 2 === 0 ? 'secondary' : 'default'}>
                        {idx % 3 === 0 ? 'Needs Help' : idx % 2 === 0 ? 'In Progress' : 'Completed'}
                      </Badge>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Controls & Chat */}
            <div className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle>Session Controls</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <Button className="w-full" variant="outline">
                    <Pause className="mr-2 h-4 w-4" />
                    Pause All Students
                  </Button>
                  <Button className="w-full" variant="outline">
                    <MessageSquare className="mr-2 h-4 w-4" />
                    Broadcast Tip
                  </Button>
                  <Button className="w-full" variant="outline">
                    <Clock className="mr-2 h-4 w-4" />
                    Extend Time
                  </Button>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Raise Hand Queue</CardTitle>
                  <CardDescription>3 students need help</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    {mockStudents.slice(0, 3).map((student) => (
                      <div
                        key={student.id}
                        className="flex items-center justify-between rounded-lg border p-2"
                      >
                        <p className="text-sm">{student.name}</p>
                        <Button size="sm">Help</Button>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Top Errors</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    <div className="flex items-center justify-between text-sm">
                      <span>Converting cm to m</span>
                      <Badge variant="destructive">8</Badge>
                    </div>
                    <div className="flex items-center justify-between text-sm">
                      <span>Reading ruler marks</span>
                      <Badge variant="destructive">5</Badge>
                    </div>
                    <div className="flex items-center justify-between text-sm">
                      <span>Decimal placement</span>
                      <Badge variant="secondary">3</Badge>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
