function StatusBadge({ status }) {
  const statusClasses = {
    pending: 'bg-yellow-100 text-yellow-800',
    queued: 'bg-blue-100 text-blue-800',
    running: 'bg-purple-100 text-purple-800',
    success: 'bg-green-100 text-green-800',
    failed: 'bg-red-100 text-red-800',
    cancelled: 'bg-gray-100 text-gray-800',
    scheduled: 'bg-indigo-100 text-indigo-800',
  }

  return (
    <span className={`px-2 py-1 text-xs font-medium rounded ${statusClasses[status] || 'bg-gray-100 text-gray-800'}`}>
      {status}
    </span>
  )
}

export default StatusBadge
