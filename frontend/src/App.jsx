import { useState, useEffect, useCallback } from 'react'
import { listRecords, deleteRecord } from './api.js'
import SearchBar from './components/SearchBar.jsx'
import RecordList from './components/RecordList.jsx'
import RecordForm from './components/RecordForm.jsx'
import RecordDetail from './components/RecordDetail.jsx'
import './App.css'

export default function App() {
  const [records, setRecords] = useState([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [filters, setFilters] = useState({})
  const [pagination, setPagination] = useState({ limit: 20, offset: 0 })
  const [showForm, setShowForm] = useState(false)
  const [editingRecord, setEditingRecord] = useState(null)
  const [detailRecord, setDetailRecord] = useState(null)
  const [refreshKey, setRefreshKey] = useState(0)

  const fetchRecords = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const params = { ...filters, ...pagination }
      const data = await listRecords(params)
      setRecords(data.items)
      setTotal(data.total)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }, [filters, pagination])

  useEffect(() => {
    fetchRecords()
  }, [fetchRecords, refreshKey])

  const handleSearch = (newFilters) => {
    setFilters(newFilters)
    setPagination((p) => ({ ...p, offset: 0 }))
  }

  const handlePage = (offset) => {
    setPagination((p) => ({ ...p, offset }))
  }

  const handleSaved = () => {
    setShowForm(false)
    setEditingRecord(null)
    setRefreshKey((k) => k + 1)
  }

  const handleEdit = (record) => {
    setEditingRecord(record)
    setShowForm(true)
  }

  const handleDelete = async (id) => {
    if (!window.confirm('Tem certeza que deseja excluir este disco?')) return
    try {
      await deleteRecord(id)
      setRefreshKey((k) => k + 1)
    } catch (e) {
      alert(e.message)
    }
  }

  const handleView = (record) => {
    setDetailRecord(record)
  }

  return (
    <div className="app">
      <header className="header">
        <div className="header-content">
          <div className="header-icon">&#9833;</div>
          <div>
            <h1 className="header-title">Vinyl Vault</h1>
            <p className="header-subtitle">Catálogo de Discos • Record Store</p>
          </div>
        </div>
        <div className="header-ornament">
          <span className="ornament-line"></span>
          <span className="ornament-diamond">&#9670;</span>
          <span className="ornament-line"></span>
        </div>
      </header>

      <main className="main">
        <div className="toolbar">
          <SearchBar onSearch={handleSearch} />
          <button className="btn btn-primary" onClick={() => { setEditingRecord(null); setShowForm(true) }}>
            + Novo Disco
          </button>
        </div>

        {error && (
          <div className="error-banner">
            <span>&#9888;</span> {error}
          </div>
        )}

        <div className="catalog-info">
          <span className="record-count">{total} disco{total !== 1 ? 's' : ''} no catálogo</span>
        </div>

        <RecordList
          records={records}
          loading={loading}
          total={total}
          limit={pagination.limit}
          offset={pagination.offset}
          onPage={handlePage}
          onEdit={handleEdit}
          onDelete={handleDelete}
          onView={handleView}
        />
      </main>

      {showForm && (
        <RecordForm
          record={editingRecord}
          onSaved={handleSaved}
          onClose={() => { setShowForm(false); setEditingRecord(null) }}
        />
      )}

      {detailRecord && (
        <RecordDetail
          record={detailRecord}
          onClose={() => setDetailRecord(null)}
          onEdit={() => {
            setDetailRecord(null)
            handleEdit(detailRecord)
          }}
        />
      )}

      <footer className="footer">
        <div className="footer-ornament">
          <span className="ornament-line"></span>
          <span className="ornament-diamond">&#9834;</span>
          <span className="ornament-line"></span>
        </div>
        <p>Vinyl Vault &copy; 2026 &mdash; Keep the music spinning</p>
      </footer>
    </div>
  )
}