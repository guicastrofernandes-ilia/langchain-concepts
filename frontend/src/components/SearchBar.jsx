import { useState } from 'react'
import { CONDITION_LABELS } from '../api.js'

export default function SearchBar({ onSearch }) {
  const [artist, setArtist] = useState('')
  const [album, setAlbum] = useState('')
  const [genre, setGenre] = useState('')
  const [year, setYear] = useState('')
  const [condition, setCondition] = useState('')
  const [expanded, setExpanded] = useState(false)

  const handleSearch = (e) => {
    e.preventDefault()
    onSearch({
      artist: artist.trim(),
      album: album.trim(),
      genre: genre.trim(),
      year: year || undefined,
      condition: condition || undefined,
    })
  }

  const handleClear = () => {
    setArtist('')
    setAlbum('')
    setGenre('')
    setYear('')
    setCondition('')
    onSearch({})
  }

  const hasFilters = artist || album || genre || year || condition

  return (
    <form className="search-bar" onSubmit={handleSearch}>
      <div className="search-row">
        <div className="search-input-group">
          <span className="search-icon">&#128269;</span>
          <input
            type="text"
            placeholder="Buscar por artista..."
            value={artist}
            onChange={(e) => setArtist(e.target.value)}
            className="search-input"
          />
        </div>
        <button type="submit" className="btn btn-primary btn-sm">Buscar</button>
        {hasFilters && (
          <button type="button" className="btn btn-sm btn-secondary" onClick={handleClear}>
            Limpar
          </button>
        )}
        <button
          type="button"
          className="btn btn-sm btn-secondary"
          onClick={() => setExpanded(!expanded)}
        >
          {expanded ? 'Menos' : 'Mais'} filtros
        </button>
      </div>

      {expanded && (
        <div className="search-filters">
          <div className="filter-group">
            <label>Álbum</label>
            <input
              type="text"
              placeholder="Nome do álbum..."
              value={album}
              onChange={(e) => setAlbum(e.target.value)}
              className="search-input"
            />
          </div>
          <div className="filter-group">
            <label>Gênero</label>
            <input
              type="text"
              placeholder="rock, jazz, mpb..."
              value={genre}
              onChange={(e) => setGenre(e.target.value)}
              className="search-input"
            />
          </div>
          <div className="filter-group">
            <label>Ano</label>
            <input
              type="number"
              placeholder="Ex: 1973"
              value={year}
              onChange={(e) => setYear(e.target.value)}
              className="search-input"
              min="1901"
              max={new Date().getFullYear() + 1}
            />
          </div>
          <div className="filter-group">
            <label>Estado</label>
            <select
              value={condition}
              onChange={(e) => setCondition(e.target.value)}
              className="search-input"
            >
              <option value="">Todos</option>
              {Object.entries(CONDITION_LABELS).map(([k, v]) => (
                <option key={k} value={k}>{v}</option>
              ))}
            </select>
          </div>
        </div>
      )}
    </form>
  )
}