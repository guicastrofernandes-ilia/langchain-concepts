import { useState } from 'react'
import { createRecord, updateRecord, CONDITION_LABELS } from '../api.js'

export default function RecordForm({ record, onSaved, onClose }) {
  const isEditing = !!record
  const [form, setForm] = useState({
    artist: record?.artist || '',
    album: record?.album || '',
    year: record?.year || '',
    genre: record?.genre || '',
    label: record?.label || '',
    condition: record?.condition || '',
    tracks: record?.tracks?.map((t) => ({ ...t })) || [{ title: '', duration: '' }],
  })
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState(null)

  const handleChange = (field, value) => {
    setForm((f) => ({ ...f, [field]: value }))
  }

  const handleTrackChange = (index, field, value) => {
    const tracks = [...form.tracks]
    tracks[index] = { ...tracks[index], [field]: value }
    setForm((f) => ({ ...f, tracks }))
  }

  const addTrack = () => {
    setForm((f) => ({ ...f, tracks: [...f.tracks, { title: '', duration: '' }] }))
  }

  const removeTrack = (index) => {
    const tracks = form.tracks.filter((_, i) => i !== index)
    setForm((f) => ({ ...f, tracks: tracks.length ? tracks : [{ title: '', duration: '' }] }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setSaving(true)
    setError(null)
    try {
      const payload = {
        artist: form.artist.trim(),
        album: form.album.trim(),
        year: form.year ? Number(form.year) : null,
        genre: form.genre.trim() || null,
        label: form.label.trim() || null,
        condition: form.condition || null,
        tracks: form.tracks
          .filter((t) => t.title.trim())
          .map((t) => ({
            title: t.title.trim(),
            duration: t.duration.trim() || null,
          })),
      }
      if (isEditing) {
        await updateRecord(record.id, payload)
      } else {
        await createRecord(payload)
      }
      onSaved()
    } catch (e) {
      setError(e.message)
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>{isEditing ? 'Editar Disco' : 'Novo Disco'}</h2>
          <button className="modal-close" onClick={onClose}>&times;</button>
        </div>

        <form onSubmit={handleSubmit} className="modal-body">
          {error && <div className="error-banner"><span>&#9888;</span> {error}</div>}

          <div className="form-row">
            <div className="form-group">
              <label>Artista *</label>
              <input
                type="text"
                required
                value={form.artist}
                onChange={(e) => handleChange('artist', e.target.value)}
                placeholder="Nome do artista"
              />
            </div>
            <div className="form-group">
              <label>Álbum *</label>
              <input
                type="text"
                required
                value={form.album}
                onChange={(e) => handleChange('album', e.target.value)}
                placeholder="Nome do álbum"
              />
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>Ano</label>
              <input
                type="number"
                value={form.year}
                onChange={(e) => handleChange('year', e.target.value)}
                placeholder="Ex: 1973"
                min="1901"
                max={new Date().getFullYear() + 1}
              />
            </div>
            <div className="form-group">
              <label>Gênero</label>
              <input
                type="text"
                value={form.genre}
                onChange={(e) => handleChange('genre', e.target.value)}
                placeholder="rock, jazz, mpb..."
              />
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>Gravadora</label>
              <input
                type="text"
                value={form.label}
                onChange={(e) => handleChange('label', e.target.value)}
                placeholder="Ex: Apple, Blue Note"
              />
            </div>
            <div className="form-group">
              <label>Estado de conservação</label>
              <select
                value={form.condition}
                onChange={(e) => handleChange('condition', e.target.value)}
              >
                <option value="">Selecione...</option>
                {Object.entries(CONDITION_LABELS).map(([k, v]) => (
                  <option key={k} value={k}>{v}</option>
                ))}
              </select>
            </div>
          </div>

          <div className="form-section">
            <label className="section-label">Faixas</label>
            {form.tracks.map((track, i) => (
              <div key={i} className="track-row">
                <input
                  type="text"
                  value={track.title}
                  onChange={(e) => handleTrackChange(i, 'title', e.target.value)}
                  placeholder="Título da faixa"
                />
                <input
                  type="text"
                  value={track.duration}
                  onChange={(e) => handleTrackChange(i, 'duration', e.target.value)}
                  placeholder="Duração"
                  className="track-duration"
                />
                <button type="button" className="btn btn-sm btn-danger" onClick={() => removeTrack(i)}>
                  &times;
                </button>
              </div>
            ))}
            <button type="button" className="btn btn-sm btn-secondary" onClick={addTrack} style={{ marginTop: '0.5rem' }}>
              + Adicionar faixa
            </button>
          </div>

          <div className="modal-actions">
            <button type="button" className="btn btn-secondary" onClick={onClose}>Cancelar</button>
            <button type="submit" className="btn btn-primary" disabled={saving}>
              {saving ? 'Salvando...' : isEditing ? 'Salvar alterações' : 'Adicionar disco'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}