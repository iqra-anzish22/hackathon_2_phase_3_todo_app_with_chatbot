'use client';

/**
 * TaskList component - displays a list of tasks with stagger animations.
 */
import { motion, AnimatePresence } from 'framer-motion';
import { Task } from '@/types/task';
import TaskItem from './TaskItem';

interface TaskListProps {
  tasks: Task[];
  onTaskDeleted: (taskId: number) => void;
  onTaskUpdated: (task: Task) => void;
}

export default function TaskList({ tasks, onTaskDeleted, onTaskUpdated }: TaskListProps) {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="space-y-4"
    >
      <AnimatePresence mode="popLayout">
        {tasks.map((task, index) => (
          <motion.div
            key={task.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, x: -100 }}
            transition={{
              duration: 0.3,
              delay: index * 0.05,
            }}
          >
            <TaskItem
              task={task}
              onDeleted={onTaskDeleted}
              onUpdated={onTaskUpdated}
            />
          </motion.div>
        ))}
      </AnimatePresence>
    </motion.div>
  );
}
