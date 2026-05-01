'use client';

import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Search, Download, FileText, Play } from 'lucide-react';
import { mockContentResources } from '@/data/mock-data';
import { format } from 'date-fns';

export default function ContentLibraryPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [typeFilter, setTypeFilter] = useState<string>('all');

  const filteredResources = mockContentResources.filter((resource) => {
    const matchesSearch = resource.title.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesType = typeFilter === 'all' || resource.type === typeFilter;
    return matchesSearch && matchesType;
  });

  return (
    <div className="space-y-6 p-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Content Library</h1>
        <p className="mt-2 text-neutral-600 dark:text-neutral-400">
          Worksheets, AR targets, how-to guides, and teaching resources
        </p>
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex gap-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-neutral-500" />
              <Input
                placeholder="Search resources..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-9"
              />
            </div>
            <Select value={typeFilter} onValueChange={setTypeFilter}>
              <SelectTrigger className="w-[200px]">
                <SelectValue placeholder="Filter by type" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Types</SelectItem>
                <SelectItem value="worksheet">Worksheets</SelectItem>
                <SelectItem value="ar-target">AR Targets</SelectItem>
                <SelectItem value="how-to-card">How-to Cards</SelectItem>
                <SelectItem value="video">Videos</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* Resources Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {filteredResources.map((resource) => (
          <Card key={resource.id} className="flex flex-col">
            <CardHeader>
              <div className="flex items-start justify-between gap-2">
                <CardTitle className="line-clamp-2 text-base">{resource.title}</CardTitle>
                {resource.type === 'video' ? (
                  <Play className="h-5 w-5 shrink-0 text-blue-500" />
                ) : (
                  <FileText className="h-5 w-5 shrink-0 text-neutral-500" />
                )}
              </div>
              <CardDescription>
                <Badge variant="outline" className="mr-2">
                  {resource.domain}
                </Badge>
                Grade {resource.grade}
              </CardDescription>
            </CardHeader>
            <CardContent className="flex flex-1 flex-col justify-between space-y-4">
              <div className="space-y-2 text-sm">
                <div className="flex items-center justify-between">
                  <span className="text-neutral-500">Type</span>
                  <span className="font-medium capitalize">
                    {resource.type.replace('-', ' ')}
                  </span>
                </div>
                {resource.fileSize && (
                  <div className="flex items-center justify-between">
                    <span className="text-neutral-500">Size</span>
                    <span className="font-medium">{resource.fileSize}</span>
                  </div>
                )}
                <div className="flex items-center justify-between">
                  <span className="text-neutral-500">Language</span>
                  <Badge variant="secondary">{resource.language.toUpperCase()}</Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-neutral-500">Added</span>
                  <span className="font-medium">
                    {format(resource.createdAt, 'MMM d, yyyy')}
                  </span>
                </div>
              </div>

              <div className="flex gap-2">
                <Button variant="outline" size="sm" className="flex-1">
                  Preview
                </Button>
                <Button size="sm" className="flex-1 gap-1">
                  <Download className="h-3 w-3" />
                  Download
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {filteredResources.length === 0 && (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-12">
            <FileText className="h-12 w-12 text-neutral-400" />
            <h3 className="mt-4 text-lg font-medium">No resources found</h3>
            <p className="mt-2 text-center text-sm text-neutral-600 dark:text-neutral-400">
              Try adjusting your search or filters
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
