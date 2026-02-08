'use client';

/**
 * TaskForm component - form for creating new tasks with validation feedback.
 */
import { useState } from 'react';
import { motion } from 'framer-motion';
import { AlertCircle, Plus } from 'lucide-react';
import { Task, TaskCreate } from '@/types/task';
import { ApiError } from '@/types/errors';
import { apiRequest } from '@/lib/api';

interface TaskFormProps {
  onTaskCreated: (task: Task) => void;
}

export default function TaskForm({ onTaskCreated }: TaskFormProps) {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [error, setError] = useState<ApiError | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [titleError, setTitleError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setTitleError(null);

    // Client-side validation
    if (!title.trim()) {
      setTitleError('Title is required');
      return;
    }

    if (title.trim().length > 200) {
      setTitleError('Title must be 200 characters or less');
      return;
    }

    try {
      setSubmitting(true);

      const taskData: TaskCreate = {
        title: title.trim(),
        description: description.trim() || undefined,
      };

      const newTask = await apiRequest<Task>('/api/tasks', {
        method: 'POST',
        body: JSON.stringify(taskData),
      });

      onTaskCreated(newTask);

      // Reset form
      setTitle('');
      setDescription('');
    } catch (err) {
      if (err && typeof err === 'object' && 'error_code' in err) {
        const apiError = err as ApiError;
        setError(apiError);

        // Map field-level errors to form fields
        if (apiError.details) {
          apiError.details.forEach(detail => {
            if (detail.field === 'title') {
              setTitleError(detail.message);
            }
          });
        }
      } else {
        setError({
          error_code: 'UNKNOWN_ERROR',
          message: 'Failed to create task',
        });
      }
    } finally {
      setSubmitting(false);
    }
  };

  const getCharCountColor = () => {
    const percentage = (description.length / 2000) * 100;
    if (percentage >= 90) return 'text-red-600';
    if (percentage >= 75) return 'text-orange-600';
    return 'text-gray-500';
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className="card bg-gradient-to-br from-white via-primary-50/30 to-white border border-primary-100 shadow-lg"
    >
      <div className="flex items-center gap-3 mb-6">
        <div className="w-10 h-10 bg-gradient-to-br from-primary-500 to-primary-700 rounded-lg flex items-center justify-center shadow-md">
          <Plus className="w-6 h-6 text-white" />
        </div>
        <h3 className="text-2xl font-bold text-gray-900">Create New Task</h3>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* General Error Message */}
        {error && !error.details && (
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-start gap-2"
          >
            <AlertCircle className="w-5 h-5 text-red-600 mt-0.5 flex-shrink-0" />
            <p className="text-sm text-red-700">{error.message}</p>
          </motion.div>
        )}

        {/* Title Field */}
        <div>
          <label htmlFor="title" className="block text-sm font-medium text-gray-700 mb-2">
            Title <span className="text-red-500">*</span>
          </label>
          <input
            id="title"
            type="text"
            value={title}
            onChange={(e) => {
              setTitle(e.target.value);
              setTitleError(null);
            }}
            required
            maxLength={200}
            className={`input-field ${
              titleError ? 'border-red-500 focus:ring-red-500 focus:border-red-500' : ''
            }`}
            placeholder="Enter task title"
          />
          {titleError && (
            <motion.p
              initial={{ opacity: 0, y: -5 }}
              animate={{ opacity: 1, y: 0 }}
              className="text-sm text-red-600 mt-2 flex items-center gap-1"
            >
              <AlertCircle className="w-4 h-4" />
              {titleError}
            </motion.p>
          )}
          <p className="text-xs text-gray-500 mt-2">
            {title.length}/200 characters
          </p>
        </div>

        {/* Description Field */}
        <div>
          <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-2">
            Description <span className="text-gray-400">(optional)</span>
          </label>
          <textarea
            id="description"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            rows={4}
            maxLength={2000}
            className="input-field resize-none"
            placeholder="Add more details about your task..."
          />
          <p className={`text-xs mt-2 font-medium ${getCharCountColor()}`}>
            {description.length}/2000 characters
          </p>
        </div>

        {/* Submit Button */}
        <motion.button
          whileHover={{ scale: submitting ? 1 : 1.02 }}
          whileTap={{ scale: submitting ? 1 : 0.98 }}
          type="submit"
          disabled={submitting}
          className="btn-primary w-full disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 text-lg py-3 shadow-lg hover:shadow-xl"
        >
          <Plus className="w-5 h-5" />
          {submitting ? (
            <>
              <motion.div
                animate={{ rotate: 360 }}
                transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                className="w-5 h-5 border-2 border-white border-t-transparent rounded-full"
              />
              Creating...
            </>
          ) : (
            'Create Task'
          )}
        </motion.button>
      </form>
    </motion.div>
  );
}
