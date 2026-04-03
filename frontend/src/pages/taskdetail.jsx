import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import Layout from '../components/layout'
import { tasksApi } from '../api'
import StatusBadge from '../components/statusbadge'

function TaskDetail() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [task, setTask] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchTask()
  }, [id])

  const fetchTask = async () => {
    try {
      const response = await tasksApi.get(id)
      setTask(response.data)
    } catch (error) {
      console.error('Failed to fetch task:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleRun = async () => {
    try {
      await tasksApi.run(id)
      fetchTask()
    } catch (error) {
      console.error('Failed to run task:', error)
    }
  }

  const handleCancel = async () => {
    try {
      await tasksApi.cancel(id)
      fetchTask()
    } catch (error) {
      console.error('Failed to cancel task:', error)
    }
  }

  if (loading) {
    return (
      <Layout>
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
        </div>
      </Layout>
    )
  }

  if (!task) {
    return (
      <Layout>
        <div className="text-center text-gray-500">Task not found</div>
      </Layout>
    )
  }

  return (
    <Layout>
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <h1 className="text-3xl font-bold text-gray-900">{task.name}</h1>
          <button
            onClick={() => navigate('/tasks')}
            className="text-gray-500 hover:text-gray-700"
          >
            ← Back to Tasks
          </button>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6 space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-sm text-gray-500">ID</label>
              <p className="font-mono text-sm">{task.id}</p>
            </div>
            <div>
              <label className="text-sm text-gray-500">Status</label>
              <div className="mt-1">
                <StatusBadge status={task.status} />
              </div>
            </div>
            <div>
              <label className="text-sm text-gray-500">Type</label>
              <p className="font-medium">{task.task_type}</p>
            </div>
            <div>
              <label className="text-sm text-gray-500">Priority</label>
              <p className="font-medium">{task.priority}</p>
            </div>
            <div>
              <label className="text-sm text-gray-500">Attempts</label>
              <p className="font-medium">
                {task.attempt_count} / {task.max_attempts}
              </p>
            </div>
            <div>
              <label className="text-sm text-gray-500">Schedule</label>
              <p className="font-mono text-sm">{task.schedule_cron || 'Not scheduled'}</p>
            </div>
            <div>
              <label className="text-sm text-gray-500">Created</label>
              <p className="font-medium">{new Date(task.created_at).toLocaleString()}</p>
            </div>
            <div>
              <label className="text-sm text-gray-500">Started</label>
              <p className="font-medium">{task.started_at ? new Date(task.started_at).toLocaleString() : '-'}</p>
            </div>
            <div>
              <label className="text-sm text-gray-500">Finished</label>
              <p className="font-medium">{task.finished_at ? new Date(task.finished_at).toLocaleString() : '-'}</p>
            </div>
          </div>

          {task.description && (
            <div>
              <label className="text-sm text-gray-500">Description</label>
              <p className="mt-1">{task.description}</p>
            </div>
          )}

          {task.payload && (
            <div>
              <label className="text-sm text-gray-500">Payload</label>
              <pre className="mt-1 bg-gray-100 p-3 rounded text-sm overflow-auto">
                {JSON.stringify(task.payload, null, 2)}
              </pre>
            </div>
          )}

          {task.result && (
            <div>
              <label className="text-sm text-gray-500">Result</label>
              <pre className="mt-1 bg-gray-100 p-3 rounded text-sm overflow-auto">
                {JSON.stringify(task.result, null, 2)}
              </pre>
            </div>
          )}

          {task.error_message && (
            <div>
              <label className="text-sm text-gray-500">Error</label>
              <p className="mt-1 text-red-600 bg-red-50 p-3 rounded">{task.error_message}</p>
            </div>
          )}

          <div className="flex space-x-4 pt-4">
            {task.status === 'pending' && (
              <button
                onClick={handleRun}
                className="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600 transition"
              >
                Run Now
              </button>
            )}
            {task.status === 'running' && (
              <button
                onClick={handleCancel}
                className="bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600 transition"
              >
                Cancel
              </button>
            )}
          </div>
        </div>
      </div>
    </Layout>
  )
}

export default TaskDetail
