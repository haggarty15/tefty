import React, { useState, useEffect } from 'react';
import { GameSnapshotForm } from './components/GameSnapshotForm';
import { AdviceDisplay } from './components/AdviceDisplay';
import { api } from './services/api';
import { GameSnapshot, StrategicAdvice, HealthStatus } from './types/api';

function App() {
  const [advice, setAdvice] = useState<StrategicAdvice | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [health, setHealth] = useState<HealthStatus | null>(null);

  useEffect(() => {
    // Check API health on mount
    api
      .checkHealth()
      .then((h) => setHealth(h))
      .catch((err) => console.error('Health check failed:', err));
  }, []);

  const handleSubmit = async (snapshot: GameSnapshot) => {
    setIsLoading(true);
    setError(null);

    try {
      const result = await api.getAdvice(snapshot);
      setAdvice(result);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to get advice');
      console.error('Error getting advice:', err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div style={styles.app}>
      <header style={styles.header}>
        <h1 style={styles.title}>TFT Strategic Advisor</h1>
        <p style={styles.subtitle}>
          AI-powered strategic advice using real match data and expert playbooks
        </p>
        {health && (
          <div style={styles.healthStatus}>
            <span style={health.status === 'healthy' ? styles.statusHealthy : styles.statusDegraded}>
              ● {health.status}
            </span>
            {!health.riot_api_configured && (
              <span style={styles.warning}> (Riot API not configured)</span>
            )}
          </div>
        )}
      </header>

      <main style={styles.main}>
        <div style={styles.container}>
          <GameSnapshotForm onSubmit={handleSubmit} isLoading={isLoading} />

          {error && (
            <div style={styles.error}>
              <strong>Error:</strong> {error}
            </div>
          )}

          {advice && <AdviceDisplay advice={advice} />}

          {!advice && !isLoading && (
            <div style={styles.instructions}>
              <h3>How to use:</h3>
              <ol>
                <li>Fill in your current game state above</li>
                <li>Add champions on your board and bench</li>
                <li>Specify active traits and available augments</li>
                <li>Add any specific questions or context</li>
                <li>Click "Get Strategic Advice" to receive data-driven recommendations</li>
              </ol>
              <p>
                <strong>Note:</strong> This app uses retrieval-augmented generation (RAG) to
                provide advice based on real match statistics and strategic playbooks.
              </p>
            </div>
          )}
        </div>
      </main>

      <footer style={styles.footer}>
        <p>
          TFT Strategic Advisor v1.0.0 | Data-driven advice using Riot Games TFT API
        </p>
        <p style={styles.disclaimer}>
          This app is not endorsed by Riot Games and does not reflect the views or opinions
          of Riot Games or anyone officially involved in producing or managing Riot Games
          properties.
        </p>
      </footer>
    </div>
  );
}

const styles = {
  app: {
    minHeight: '100vh',
    backgroundColor: '#f5f5f5',
    display: 'flex',
    flexDirection: 'column' as const,
  },
  header: {
    backgroundColor: '#1a237e',
    color: 'white',
    padding: '24px',
    textAlign: 'center' as const,
  },
  title: {
    margin: '0 0 8px 0',
    fontSize: '32px',
  },
  subtitle: {
    margin: '0',
    fontSize: '16px',
    opacity: 0.9,
  },
  healthStatus: {
    marginTop: '12px',
    fontSize: '14px',
  },
  statusHealthy: {
    color: '#4CAF50',
    fontWeight: 'bold' as const,
  },
  statusDegraded: {
    color: '#FFC107',
    fontWeight: 'bold' as const,
  },
  warning: {
    color: '#FFC107',
  },
  main: {
    flex: 1,
    padding: '24px',
  },
  container: {
    maxWidth: '1200px',
    margin: '0 auto',
  },
  error: {
    backgroundColor: '#ffebee',
    color: '#c62828',
    padding: '16px',
    borderRadius: '4px',
    marginTop: '24px',
    border: '1px solid #ef5350',
  },
  instructions: {
    backgroundColor: 'white',
    padding: '24px',
    borderRadius: '8px',
    boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
    marginTop: '24px',
  },
  footer: {
    backgroundColor: '#333',
    color: 'white',
    padding: '20px',
    textAlign: 'center' as const,
    fontSize: '14px',
  },
  disclaimer: {
    fontSize: '12px',
    opacity: 0.7,
    margin: '8px 0 0 0',
  },
};

export default App;
