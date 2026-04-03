import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import Layout from '../components/layout'
import { tasksApi } from '../api'
import StatusBadge from '../components/statusbadge'

function Tasks() {
  const navigate = useNavigate()
  const [tasks, setTasks] = useState([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState('')

  useEffect(() => {
    fetchTasks()
  }, [filter])

  const fetchTasks = async () => {
    try {
      const params = filter ? { status: filter } : {}
      const response = await tasksApi.list(params)
      setTasks(response.data)
    } catch (error) {
      console.error('Failed to fetch tasks:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleRun = async (id) => {
    try {
      await tasksApi.run(id)
      fetchTasks()
    } catch (error) {
      console.error('Failed to run task:', error)
    }
  }

  const handleCancel = async (id) => {
    try {
      await tasksApi.cancel(id)
      fetchTasks()
    } catch (error) {
      console.error('Failed to cancel task:', error)
    }
  }

  const handleDelete = async (id) => {
    if (!confirm('Are you sure?')) return
    try {
      await tasksApi.delete(id)
      fetchTasks()
    } catch (error) {
      console.error('Failed to delete task:', error)
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

  return (
    <Layout>
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <h1 className="text-3xl font-bold text-gray-900">Tasks</h1>
          <button
            onClick={() => navigate('/tasks/new')}
            className="bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600 transition"
          >
            + New Task
          </button>
        </div>

        <div className="bg-white p-4 rounded-lg shadow">
          <select
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-md"
          >
            <option value="">All Statuses</option>
            <option value="pending">Pending</option>
            <option value="running">Running</option>
            <option value="success">Success</option>
            <option value="failed">Failed</option>
            <option value="cancelled">Cancelled</option>
          </select>
        </div>

        <div className="bg-white rounded-lg shadow-md overflow-hidden">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Attempts</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Created</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {tasks.map((task) => (
                <tr key={task.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap font-medium">{task.name}</td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="px-2 py-1 text-xs font-medium bg-gray-100 rounded">
                      {task.task_type}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <StatusBadge status={task.status} />
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {task.attempt_count}/{task.max_attempts}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {new Date(task.created_at).toLocaleDateString()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap space-x-2">
                    <button
                      onClick={() => navigate(`/tasks/${task.id}`)}
                      className="text-blue-500 hover:text-blue-600"
                    >
                      View
                    </button>
                    {task.status === 'pending' && (
                      <button
                        onClick={() => handleRun(task.id)}
                        className="text-green-500 hover:text-green-600"
                      >
                        Run
                      </button>
                    )}
                    {task.status === 'running' && (
                      <button
                        onClick={() => handleCancel(task.id)}
                        className="text-red-500 hover:text-red-600"
                      >
                        Cancel
                      </button>
                    )}
                    {(task.status === 'failed' || task.status === 'cancelled') && (
                      <button
                        onClick={() => handleDelete(task.id)}
                        className="text-gray-500 hover:text-gray-600"
                      >
                        Delete
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {tasks.length === 0 && (
            <div className="p-8 text-center text-gray-500">
              No tasks found
            </div>
          )}
        </div>
      </div>
    </Layout>
  )
}

export default Tasks
