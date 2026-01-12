import React, { useState } from 'react';
import { Champion } from '../types/api';

interface ChampionInputProps {
  champion: Champion;
  onChange: (champion: Champion) => void;
  onRemove: () => void;
}

export const ChampionInput: React.FC<ChampionInputProps> = ({
  champion,
  onChange,
  onRemove,
}) => {
  return (
    <div style={styles.championRow}>
      <input
        type="text"
        placeholder="Champion name"
        value={champion.name}
        onChange={(e) => onChange({ ...champion, name: e.target.value })}
        style={styles.input}
      />
      <select
        value={champion.stars}
        onChange={(e) => onChange({ ...champion, stars: parseInt(e.target.value) })}
        style={styles.select}
      >
        <option value={1}>1★</option>
        <option value={2}>2★</option>
        <option value={3}>3★</option>
      </select>
      <input
        type="text"
        placeholder="Items (comma separated)"
        value={champion.items.join(', ')}
        onChange={(e) =>
          onChange({
            ...champion,
            items: e.target.value.split(',').map((s) => s.trim()).filter(Boolean),
          })
        }
        style={styles.input}
      />
      <button onClick={onRemove} style={styles.removeBtn}>
        ✕
      </button>
    </div>
  );
};

const styles = {
  championRow: {
    display: 'flex',
    gap: '8px',
    marginBottom: '8px',
    alignItems: 'center',
  },
  input: {
    flex: 1,
    padding: '8px',
    borderRadius: '4px',
    border: '1px solid #ccc',
    fontSize: '14px',
  },
  select: {
    padding: '8px',
    borderRadius: '4px',
    border: '1px solid #ccc',
    fontSize: '14px',
  },
  removeBtn: {
    padding: '8px 12px',
    backgroundColor: '#ff4444',
    color: 'white',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
    fontSize: '14px',
  },
};
