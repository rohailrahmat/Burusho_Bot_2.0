import React, { useState } from 'react';
import api from '../utils/api';

export default function DictionaryDemo() {
  const [q, setQ] = useState('');
  const [results, setResults] = useState([]);
  const [error, setError] = useState(null);

  async function doSearch(e) {
    e.preventDefault();
    setError(null);
    try {
      const res = await api.searchDictionary(q);
      setResults(res);
    } catch (err) {
      setError(String(err));
    }
  }

  return (
    <div style={{ padding: 16 }}>
      <h2>Dictionary Search Demo</h2>
      <form onSubmit={doSearch}>
        <input value={q} onChange={(e) => setQ(e.target.value)} placeholder="Search burushaski / english / urdu" />
        <button type="submit">Search</button>
      </form>
      {error && <div style={{ color: 'red' }}>{error}</div>}
      <ul>
        {results.map((w) => (
          <li key={w.id}>
            <strong>{w.burushaski}</strong> — {w.english} {w.urdu ? `(${w.urdu})` : ''}
          </li>
        ))}
      </ul>
    </div>
  );
}
