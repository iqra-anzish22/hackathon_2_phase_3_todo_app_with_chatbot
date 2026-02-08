'use client';

/**
 * Task detail page - displays and allows editing of a single task.
 */
import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { Task, TaskUpdate } from '@/types/task';
import { ApiError } from '@/types/errors';
import { apiRequest } from '@/lib/api';
import ErrorMessage from '@/components/ErrorMessage';

export default function TaskDetailPage() {
  const params = useParams();
  const router = useRouter();
  const taskId = params.id as string;

  const [task, setTask] = useState<Task | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<ApiError | null>(null);
  const [editing, setEditing] = useState(false);
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    fetchTask();
  }, [taskId]);

  const fetchTask = async () => {
    try {
      setLoading(true);
      setError(null);

      const data = await apiRequest<Task>(`/api/tasks/${taskId}`);

      setTask(data);
      setTitle(data.title);
      setDescription(data.description || '');
    } catch (err) {
      if (err && typeof err === 'object' && 'error_code' in err) {
        setError(err as ApiError);
      } else {
        setError({
          error_code: 'UNKNOWN_ERROR',
          message: 'Failed to load task',
        });
      }
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    if (!task) return;

    try {
      setSaving(true);
      setError(null);

      const updateData: TaskUpdate = {
        title: title !== task.title ? title : undefined,
        description: description !== (task.description || '') ? description : undefined,
      };

      const updatedTask = await apiRequest<Task>(`/api/tasks/${taskId}`, {
        method: 'PUT',
        body: JSON.stringify(updateData),
      });

      setTask(updatedTask);
      setEditing(false);
    } catch (err) {
      if (err && typeof err === 'object' && 'error_code' in err) {
        setError(err as ApiError);
      } else {
        setError({
          error_code: 'UNKNOWN_ERROR',
          message: 'Failed to update task',
        });
      }
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async () => {
    if (!confirm('Are you sure you want to delete this task?')) return;

    try {
      await apiRequest(`/api/tasks/${taskId}`, {
        method: 'DELETE',
      });

      router.push('/tasks');
    } catch (err) {
      if (err && typeof err === 'object' && 'error_code' in err) {
        setError(err as ApiError);
      } else {
        setError({
          error_code: 'UNKNOWN_ERROR',
          message: 'Failed to delete task',
        });
      }
    }
  };

  if (loading) {
    return (
      <div style={{ maxWidth: '800px', margin: '0 auto', padding: '20px' }}>
        <div style={{ textAlign: 'center', padding: '40px', color: '#666' }}>
          <div style={{ fontSize: '18px' }}>Loading task...</div>
        </div>
      </div>
    );
  }

  // Handle 404 or 403 errors when task couldn't be loaded
  if (error && !task) {
    return (
      <div style={{ maxWidth: '800px', margin: '0 auto', padding: '20px' }}>
        <ErrorMessage error={error} />
        <button
          onClick={() => router.push('/tasks')}
          style={{
            padding: '10px 20px',
            backgroundColor: '#0070f3',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer',
            marginTop: '10px',
          }}
        >
          Back to Tasks
        </button>
      </div>
    );
  }

  if (!task) {
    return (
      <div style={{ maxWidth: '800px', margin: '0 auto', padding: '20px' }}>
        <div style={{ padding: '20px', textAlign: 'center' }}>Task not found</div>
        <button
          onClick={() => router.push('/tasks')}
          style={{
            padding: '10px 20px',
            backgroundColor: '#0070f3',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer',
          }}
        >
          Back to Tasks
        </button>
      </div>
    );
  }

  return (
    <div style={{ maxWidth: '800px', margin: '0 auto', padding: '20px' }}>
      <div style={{ marginBottom: '20px' }}>
        <button
          onClick={() => router.push('/tasks')}
          style={{
            padding: '8px 16px',
            backgroundColor: '#f0f0f0',
            border: '1px solid #ccc',
            borderRadius: '4px',
            cursor: 'pointer',
          }}
        >
          ← Back to Tasks
        </button>
      </div>

      {error && (
        <ErrorMessage error={error} />
      )}

      {editing ? (
        <div>
          <h1>Edit Task</h1>
          <div style={{ marginBottom: '15px' }}>
            <label style={{ display: 'block', marginBottom: '5px' }}>Title</label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              style={{
                width: '100%',
                padding: '8px',
                fontSize: '16px',
                border: '1px solid #ccc',
                borderRadius: '4px',
              }}
            />
          </div>
          <div style={{ marginBottom: '15px' }}>
            <label style={{ display: 'block', marginBottom: '5px' }}>Description</label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              rows={5}
              style={{
                width: '100%',
                padding: '8px',
                fontSize: '16px',
                border: '1px solid #ccc',
                borderRadius: '4px',
              }}
            />
          </div>
          <div style={{ display: 'flex', gap: '10px' }}>
            <button
              onClick={handleSave}
              disabled={saving}
              style={{
                padding: '10px 20px',
                backgroundColor: '#0070f3',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: saving ? 'not-allowed' : 'pointer',
              }}
            >
              {saving ? 'Saving...' : 'Save'}
            </button>
            <button
              onClick={() => {
                setEditing(false);
                setTitle(task.title);
                setDescription(task.description || '');
                setError(null);
              }}
              style={{
                padding: '10px 20px',
                backgroundColor: '#f0f0f0',
                border: '1px solid #ccc',
                borderRadius: '4px',
                cursor: 'pointer',
              }}
            >
              Cancel
            </button>
          </div>
        </div>
      ) : (
        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '20px' }}>
            <h1>{task.title}</h1>
            <div style={{ display: 'flex', gap: '10px' }}>
              <button
                onClick={() => setEditing(true)}
                style={{
                  padding: '8px 16px',
                  backgroundColor: '#0070f3',
                  color: 'white',
                  border: 'none',
                  borderRadius: '4px',
                  cursor: 'pointer',
                }}
              >
                Edit
              </button>
              <button
                onClick={handleDelete}
                style={{
                  padding: '8px 16px',
                  backgroundColor: '#dc3545',
                  color: 'white',
                  border: 'none',
                  borderRadius: '4px',
                  cursor: 'pointer',
                }}
              >
                Delete
              </button>
            </div>
          </div>

          <div style={{ marginBottom: '20px' }}>
            <strong>Status:</strong> {task.completed ? 'Completed' : 'Incomplete'}
          </div>

          {task.description && (
            <div style={{ marginBottom: '20px' }}>
              <strong>Description:</strong>
              <p style={{ whiteSpace: 'pre-wrap' }}>{task.description}</p>
            </div>
          )}

          <div style={{ fontSize: '14px', color: '#666' }}>
            <div>Created: {new Date(task.created_at).toLocaleString()}</div>
            <div>Updated: {new Date(task.updated_at).toLocaleString()}</div>
          </div>
        </div>
      )}
    </div>
  );
}
