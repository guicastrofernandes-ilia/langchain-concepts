import { CONDITION_LABELS } from '../api.js'

export default function RecordDetail({ record, onClose, onEdit }) {
  const formatDuration = (d) => d || '--:--'

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal modal-detail" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>{record.artist} &mdash; {record.album}</h2>
          <button className="modal-close" onClick={onClose}>&times;</button>
        </div>

        <div className="modal-body">
          <div className="detail-grid">
            <div className="detail-section">
              <h3 className="detail-section-title">Informações</h3>
              <dl className="detail-list">
                {record.year && (
                  <>
                    <dt>Ano</dt>
                    <dd>{record.year}</dd>
                  </>
                )}
                {record.genre && (
                  <>
                    <dt>Gênero</dt>
                    <dd>{record.genre}</dd>
                  </>
                )}
                {record.label && (
                  <>
                    <dt>Gravadora</dt>
                    <dd>{record.label}</dd>
                  </>
                )}
                {record.condition && (
                  <>
                    <dt>Estado</dt>
                    <dd><span className={`record-condition condition-${record.condition}`}>
                      {CONDITION_LABELS[record.condition] || record.condition}
                    </span></dd>
                  </>
                )}
                <dt>ID</dt>
                <dd className="detail-id">#{record.id}</dd>
              </dl>
            </div>

            {record.tracks && record.tracks.length > 0 && (
              <div className="detail-section">
                <h3 className="detail-section-title">Faixas ({record.tracks.length})</h3>
                <ol className="track-list">
                  {record.tracks.map((track, i) => (
                    <li key={i} className="track-list-item">
                      <span className="track-number">{i + 1}.</span>
                      <span className="track-title">{track.title}</span>
                      <span className="track-duration">{formatDuration(track.duration)}</span>
                    </li>
                  ))}
                </ol>
              </div>
            )}
          </div>

          <div className="detail-timestamps">
            <span>Criado em: {new Date(record.created_at).toLocaleDateString('pt-BR')}</span>
            {record.updated_at && (
              <span>Atualizado em: {new Date(record.updated_at).toLocaleDateString('pt-BR')}</span>
            )}
          </div>
        </div>

        <div className="modal-actions">
          <button className="btn btn-secondary" onClick={onClose}>Fechar</button>
          <button className="btn btn-primary" onClick={onEdit}>Editar disco</button>
        </div>
      </div>
    </div>
  )
}