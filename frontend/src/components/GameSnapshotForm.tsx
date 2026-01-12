import React, { useState } from 'react';
import { GameSnapshot, Champion } from '../types/api';
import { ChampionInput } from './ChampionInput';

interface GameSnapshotFormProps {
  onSubmit: (snapshot: GameSnapshot) => void;
  isLoading: boolean;
}

export const GameSnapshotForm: React.FC<GameSnapshotFormProps> = ({
  onSubmit,
  isLoading,
}) => {
  const [snapshot, setSnapshot] = useState<GameSnapshot>({
    set_version: '12',
    stage: '4-2',
    level: 7,
    gold: 30,
    health: 60,
    board: [],
    bench: [],
    available_augments: [],
    shop_champions: [],
    active_traits: [],
    context: '',
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(snapshot);
  };

  const addChampion = (type: 'board' | 'bench') => {
    const newChamp: Champion = { name: '', stars: 1, items: [] };
    setSnapshot((prev) => ({
      ...prev,
      [type]: [...prev[type], newChamp],
    }));
  };

  const updateChampion = (type: 'board' | 'bench', index: number, champion: Champion) => {
    setSnapshot((prev) => ({
      ...prev,
      [type]: prev[type].map((c, i) => (i === index ? champion : c)),
    }));
  };

  const removeChampion = (type: 'board' | 'bench', index: number) => {
    setSnapshot((prev) => ({
      ...prev,
      [type]: prev[type].filter((_, i) => i !== index),
    }));
  };

  return (
    <form onSubmit={handleSubmit} style={styles.form}>
      <h2 style={styles.heading}>Current Game State</h2>

      <div style={styles.row}>
        <div style={styles.field}>
          <label style={styles.label}>Set Version</label>
          <select
            value={snapshot.set_version}
            onChange={(e) => setSnapshot({ ...snapshot, set_version: e.target.value })}
            style={styles.input}
          >
            <option value="10">Set 10</option>
            <option value="11">Set 11</option>
            <option value="12">Set 12</option>
          </select>
        </div>

        <div style={styles.field}>
          <label style={styles.label}>Stage</label>
          <input
            type="text"
            value={snapshot.stage}
            onChange={(e) => setSnapshot({ ...snapshot, stage: e.target.value })}
            placeholder="e.g., 4-2"
            style={styles.input}
          />
        </div>

        <div style={styles.field}>
          <label style={styles.label}>Level</label>
          <input
            type="number"
            min="1"
            max="10"
            value={snapshot.level}
            onChange={(e) => setSnapshot({ ...snapshot, level: parseInt(e.target.value) })}
            style={styles.input}
          />
        </div>

        <div style={styles.field}>
          <label style={styles.label}>Gold</label>
          <input
            type="number"
            min="0"
            value={snapshot.gold}
            onChange={(e) => setSnapshot({ ...snapshot, gold: parseInt(e.target.value) })}
            style={styles.input}
          />
        </div>

        <div style={styles.field}>
          <label style={styles.label}>Health</label>
          <input
            type="number"
            min="0"
            max="100"
            value={snapshot.health}
            onChange={(e) => setSnapshot({ ...snapshot, health: parseInt(e.target.value) })}
            style={styles.input}
          />
        </div>
      </div>

      <div style={styles.section}>
        <div style={styles.sectionHeader}>
          <label style={styles.label}>Board</label>
          <button type="button" onClick={() => addChampion('board')} style={styles.addBtn}>
            + Add Champion
          </button>
        </div>
        {snapshot.board.map((champ, i) => (
          <ChampionInput
            key={i}
            champion={champ}
            onChange={(c) => updateChampion('board', i, c)}
            onRemove={() => removeChampion('board', i)}
          />
        ))}
      </div>

      <div style={styles.section}>
        <div style={styles.sectionHeader}>
          <label style={styles.label}>Bench</label>
          <button type="button" onClick={() => addChampion('bench')} style={styles.addBtn}>
            + Add Champion
          </button>
        </div>
        {snapshot.bench.map((champ, i) => (
          <ChampionInput
            key={i}
            champion={champ}
            onChange={(c) => updateChampion('bench', i, c)}
            onRemove={() => removeChampion('bench', i)}
          />
        ))}
      </div>

      <div style={styles.field}>
        <label style={styles.label}>Active Traits</label>
        <input
          type="text"
          placeholder="Comma separated (e.g., Invoker, Arcanist)"
          value={snapshot.active_traits.join(', ')}
          onChange={(e) =>
            setSnapshot({
              ...snapshot,
              active_traits: e.target.value.split(',').map((s) => s.trim()).filter(Boolean),
            })
          }
          style={styles.input}
        />
      </div>

      <div style={styles.field}>
        <label style={styles.label}>Available Augments</label>
        <input
          type="text"
          placeholder="Comma separated augment choices"
          value={snapshot.available_augments.join(', ')}
          onChange={(e) =>
            setSnapshot({
              ...snapshot,
              available_augments: e.target.value.split(',').map((s) => s.trim()).filter(Boolean),
            })
          }
          style={styles.input}
        />
      </div>

      <div style={styles.field}>
        <label style={styles.label}>Additional Context / Questions</label>
        <textarea
          value={snapshot.context}
          onChange={(e) => setSnapshot({ ...snapshot, context: e.target.value })}
          placeholder="Any specific questions or context about your situation..."
          style={{ ...styles.input, minHeight: '80px', resize: 'vertical' }}
        />
      </div>

      <button type="submit" disabled={isLoading} style={styles.submitBtn}>
        {isLoading ? 'Analyzing...' : 'Get Strategic Advice'}
      </button>
    </form>
  );
};

const styles = {
  form: {
    backgroundColor: 'white',
    padding: '24px',
    borderRadius: '8px',
    boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
  },
  heading: {
    marginTop: 0,
    marginBottom: '20px',
    color: '#333',
  },
  row: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(120px, 1fr))',
    gap: '16px',
    marginBottom: '20px',
  },
  field: {
    display: 'flex',
    flexDirection: 'column' as const,
    marginBottom: '16px',
  },
  label: {
    fontWeight: 'bold' as const,
    marginBottom: '8px',
    color: '#555',
  },
  input: {
    padding: '10px',
    borderRadius: '4px',
    border: '1px solid #ccc',
    fontSize: '14px',
  },
  section: {
    marginBottom: '20px',
    padding: '16px',
    backgroundColor: '#f9f9f9',
    borderRadius: '4px',
  },
  sectionHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '12px',
  },
  addBtn: {
    padding: '6px 12px',
    backgroundColor: '#4CAF50',
    color: 'white',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
    fontSize: '14px',
  },
  submitBtn: {
    width: '100%',
    padding: '14px',
    backgroundColor: '#2196F3',
    color: 'white',
    border: 'none',
    borderRadius: '4px',
    fontSize: '16px',
    fontWeight: 'bold' as const,
    cursor: 'pointer',
    marginTop: '10px',
  },
};
