import { useState, useEffect } from 'react'

function App() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [postData, setPostData] = useState('')

  const fetchData = async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await fetch('http://localhost:8000/api/test/')
      const result = await response.json()
      setData(result)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const sendPost = async () => {
    setLoading(true)
    try {
      const response = await fetch('http://localhost:8000/api/test/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: postData })
      })
      const result = await response.json()
      setData(result)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchData()
  }, [])

  return (
    <div className="p-8 max-w-2xl mx-auto">
      <h1 className="text-3xl font-bold mb-8">🧪 Тест Frontend → Backend</h1>
      
      <div className="space-y-6">
        {/* GET запрос */}
        <div className="p-6 bg-green-50 border border-green-200 rounded-lg">
          <h2 className="text-xl font-semibold mb-4">GET /api/test/</h2>
          <button
            onClick={fetchData}
            disabled={loading}
            className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 disabled:opacity-50"
          >
            {loading ? 'Загрузка...' : 'GET запрос'}
          </button>
        </div>

        {/* POST запрос */}
        <div className="p-6 bg-blue-50 border border-blue-200 rounded-lg">
          <h2 className="text-xl font-semibold mb-4">POST /api/test/</h2>
          <input
            value={postData}
            onChange={(e) => setPostData(e.target.value)}
            placeholder="Введите сообщение"
            className="w-full p-2 border rounded mb-4"
          />
          <button
            onClick={sendPost}
            disabled={loading}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
          >
            {loading ? 'Отправка...' : 'POST запрос'}
          </button>
        </div>

        {/* Результат */}
        {data && (
          <div className="p-6 bg-gray-50 border rounded-lg">
            <h2 className="text-xl font-semibold mb-4">✅ Ответ от Backend:</h2>
            <pre className="bg-white p-4 rounded text-sm overflow-auto">
              {JSON.stringify(data, null, 2)}
            </pre>
          </div>
        )}

        {error && (
          <div className="p-6 bg-red-50 border border-red-200 rounded-lg">
            <h2 className="text-xl font-semibold text-red-800 mb-4">❌ Ошибка:</h2>
            <pre className="text-red-800">{error}</pre>
          </div>
        )}
      </div>
    </div>
  )
}

export default App
