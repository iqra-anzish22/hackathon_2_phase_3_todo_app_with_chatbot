'use client';

/**
 * TaskItem component - displays a single task in the list.
 * Includes delete functionality, completion toggle, and link to detail view.
 */
import { Task } from '@/types/task';
import { ApiError } from '@/types/errors';
import { apiRequest } from '@/lib/api';
import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import { Trash2, CheckCircle2, Circle, AlertCircle, Calendar } from 'lucide-react';

interface TaskItemProps {
  task: Task;
  onDeleted: (taskId: number) => void;
  onUpdated: (task: Task) => void;
}

export default function TaskItem({ task, onDeleted, onUpdated }: TaskItemProps) {
  const router = useRouter();
  const [deleting, setDeleting] = useState(false);
  const [toggling, setToggling] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleDelete = async (e: React.MouseEvent) => {
    e.stopPropagation();

    if (!confirm('Are you sure you want to delete this task?')) return;

    try {
      setDeleting(true);
      setError(null);
      await apiRequest(`/api/tasks/${task.id}`, {
        method: 'DELETE',
      });
      onDeleted(task.id);
    } catch (err) {
      if (err && typeof err === 'object' && 'error_code' in err) {
        const apiError = err as ApiError;
        setError(apiError.message);
      } else {
        setError('Failed to delete task');
      }
      setDeleting(false);
    }
  };

  const handleToggleComplete = async (e: React.MouseEvent) => {
    e.stopPropagation();

    try {
      setToggling(true);
      setError(null);
      const updatedTask = await apiRequest<Task>(`/api/tasks/${task.id}/complete`, {
        method: 'PATCH',
      });
      onUpdated(updatedTask);
    } catch (err) {
      if (err && typeof err === 'object' && 'error_code' in err) {
        const apiError = err as ApiError;
        setError(apiError.message);
      } else {
        setError('Failed to toggle task completion');
      }
    } finally {
      setToggling(false);
    }
  };

  const handleClick = () => {
    router.push(`/tasks/${task.id}`);
  };

  return (
    <motion.div
      whileHover={{ scale: 1.01, y: -2 }}
      whileTap={{ scale: 0.99 }}
      onClick={handleClick}
      className={`card cursor-pointer transition-all duration-300 ${
        task.completed
          ? 'bg-gradient-to-br from-gray-50 to-gray-100 opacity-90 border border-gray-200'
          : 'bg-white hover:shadow-xl hover:border-primary-200 border border-transparent'
      }`}
    >
      {/* Error Message */}
      {error && (
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: 'auto' }}
          className="bg-red-50 border border-red-200 rounded-lg p-3 mb-4 flex items-start gap-2"
        >
          <AlertCircle className="w-4 h-4 text-red-600 mt-0.5 flex-shrink-0" />
          <p className="text-sm text-red-700">{error}</p>
        </motion.div>
      )}

      <div className="flex items-start justify-between gap-4">
        {/* Left Section: Checkbox + Content */}
        <div className="flex items-start gap-3 flex-1 min-w-0">
          {/* Completion Toggle Button */}
          <motion.button
            whileHover={{ scale: 1.15 }}
            whileTap={{ scale: 0.85 }}
            onClick={handleToggleComplete}
            disabled={toggling}
            className={`flex-shrink-0 mt-1 transition-all duration-200 ${
              toggling ? 'cursor-not-allowed opacity-50' : 'cursor-pointer'
            }`}
          >
            {task.completed ? (
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ type: "spring", stiffness: 500, damping: 15 }}
              >
                <CheckCircle2 className="w-6 h-6 text-green-600" />
              </motion.div>
            ) : (
              <Circle className="w-6 h-6 text-gray-400 hover:text-primary-600 transition-colors" />
            )}
          </motion.button>

          {/* Task Content */}
          <div className="flex-1 min-w-0">
            <h3
              className={`text-lg font-semibold mb-1 ${
                task.completed
                  ? 'text-gray-500 line-through'
                  : 'text-gray-900'
              }`}
            >
              {task.title}
            </h3>

            {task.description && (
              <p
                className={`text-sm mb-2 truncate ${
                  task.completed
                    ? 'text-gray-400 line-through'
                    : 'text-gray-600'
                }`}
              >
                {task.description}
              </p>
            )}

            {/* Metadata */}
            <div className="flex items-center gap-3 text-xs text-gray-500">
              <span className={`flex items-center gap-1 ${
                task.completed ? 'text-green-600' : 'text-gray-500'
              }`}>
                {task.completed ? (
                  <>
                    <CheckCircle2 className="w-3 h-3" />
                    Completed
                  </>
                ) : (
                  <>
                    <Circle className="w-3 h-3" />
                    Incomplete
                  </>
                )}
              </span>
              <span className="flex items-center gap-1">
                <Calendar className="w-3 h-3" />
                {new Date(task.created_at).toLocaleDateString()}
              </span>
            </div>
          </div>
        </div>

        {/* Right Section: Delete Button */}
        <motion.button
          whileHover={{ scale: 1.08, rotate: 2 }}
          whileTap={{ scale: 0.92 }}
          onClick={handleDelete}
          disabled={deleting}
          className="flex-shrink-0 px-4 py-2 bg-gradient-to-r from-red-500 to-red-600 hover:from-red-600 hover:to-red-700 text-white rounded-lg transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 text-sm font-medium shadow-md hover:shadow-lg"
        >
          <Trash2 className="w-4 h-4" />
          {deleting ? 'Deleting...' : 'Delete'}
        </motion.button>
      </div>
    </motion.div>
  );
}
