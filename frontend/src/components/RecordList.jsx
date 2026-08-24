import { CONDITION_LABELS } from '../api.js'

export default function RecordList({ records, loading, total, limit, offset, onPage, onEdit, onDelete, onView }) {
  if (loading) {
    return (
      <div className="loading-spinner">
        <p>Carregando catálogo...</p>
      </div>
    )
  }

  if (records.length === 0) {
    return (
      <div className="empty-state">
        <span className="empty-state-icon">&#9835;</span>
        <h3>Nenhum disco encontrado</h3>
        <p>Comece adicionando um novo disco ao catálogo.</p>
      </div>
    )
  }

  const totalPages = Math.ceil(total / limit)
  const currentPage = Math.floor(offset / limit) + 1

  return (
    <div className="record-list">
      <div className="record-grid">
        {records.map((record) => (
          <div key={record.id} className="record-card" onClick={() => onView(record)}>
            <div className="record-card-spine">
              <div className="record-label">
                <span className="record-label-icon">&#9833;</span>
              </div>
            </div>
            <div className="record-card-body">
              <h3 className="record-artist">{record.artist}</h3>
              <h4 className="record-album">{record.album}</h4>
              <div className="record-meta">
                {record.year && <span className="record-year">{record.year}</span>}
                {record.genre && <span className="record-genre">{record.genre}</span>}
                {record.label && <span className="record-label-name">{record.label}</span>}
              </div>
              {record.condition && (
                <span className={`record-condition condition-${record.condition}`}>
                  {CONDITION_LABELS[record.condition] || record.condition}
                </span>
              )}
              {record.tracks && record.tracks.length > 0 && (
                <div className="record-tracks">
                  <span className="track-count">{record.tracks.length} faixa{record.tracks.length !== 1 ? 's' : ''}</span>
                </div>
              )}
            </div>
            <div className="record-card-actions" onClick={(e) => e.stopPropagation()}>
              <button className="btn btn-sm btn-secondary" onClick={() => onEdit(record)}>Editar</button>
              <button className="btn btn-sm btn-danger" onClick={() => onDelete(record.id)}>Excluir</button>
            </div>
          </div>
        ))}
      </div>

      {totalPages > 1 && (
        <div className="pagination">
          <button
            className="btn btn-sm btn-secondary"
            disabled={offset === 0}
            onClick={() => onPage(offset - limit)}
          >
            &laquo; Anterior
          </button>
          <span className="pagination-info">
            Página {currentPage} de {totalPages}
          </span>
          <button
            className="btn btn-sm btn-secondary"
            disabled={offset + limit >= total}
            onClick={() => onPage(offset + limit)}
          >
            Próxima &raquo;
          </button>
        </div>
      )}
    </div>
  )
}