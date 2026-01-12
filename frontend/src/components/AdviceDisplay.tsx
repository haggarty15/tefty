import React from 'react';
import { StrategicAdvice } from '../types/api';

interface AdviceDisplayProps {
  advice: StrategicAdvice;
}

export const AdviceDisplay: React.FC<AdviceDisplayProps> = ({ advice }) => {
  return (
    <div style={styles.container}>
      <h2 style={styles.heading}>Strategic Advice</h2>

      {/* General Advice */}
      <div style={styles.generalAdvice}>
        <h3 style={styles.subheading}>Overview</h3>
        <p style={styles.text}>{advice.general_advice}</p>
      </div>

      {/* Strategic Options */}
      <div style={styles.optionsSection}>
        <h3 style={styles.subheading}>Recommended Options</h3>
        {advice.options.map((option, index) => (
          <div key={index} style={styles.option}>
            <div style={styles.optionHeader}>
              <div style={styles.rankBadge}>#{option.rank}</div>
              <h4 style={styles.optionTitle}>{option.title}</h4>
              <div
                style={{
                  ...styles.confidenceBadge,
                  backgroundColor: getConfidenceColor(option.confidence),
                }}
              >
                {(option.confidence * 100).toFixed(0)}% confidence
              </div>
            </div>
            <p style={styles.description}>{option.description}</p>
            <div style={styles.reasoning}>
              <strong>Reasoning:</strong> {option.reasoning}
            </div>
            {Object.keys(option.key_stats).length > 0 && (
              <div style={styles.stats}>
                <strong>Key Stats:</strong>
                <ul style={styles.statsList}>
                  {Object.entries(option.key_stats).map(([key, value]) => (
                    <li key={key}>
                      {key}: {typeof value === 'number' ? value.toFixed(2) : value}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Retrieved Context */}
      {advice.retrieved_context.length > 0 && (
        <div style={styles.contextSection}>
          <h3 style={styles.subheading}>Data Sources</h3>
          <p style={styles.contextNote}>
            This advice is based on the following retrieved data:
          </p>
          <ul style={styles.contextList}>
            {advice.retrieved_context.map((context, index) => (
              <li key={index} style={styles.contextItem}>
                {context}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

const getConfidenceColor = (confidence: number): string => {
  if (confidence >= 0.8) return '#4CAF50';
  if (confidence >= 0.6) return '#FFC107';
  return '#FF9800';
};

const styles = {
  container: {
    backgroundColor: 'white',
    padding: '24px',
    borderRadius: '8px',
    boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
    marginTop: '24px',
  },
  heading: {
    marginTop: 0,
    marginBottom: '20px',
    color: '#333',
  },
  subheading: {
    color: '#555',
    marginTop: 0,
    marginBottom: '12px',
  },
  generalAdvice: {
    backgroundColor: '#E3F2FD',
    padding: '16px',
    borderRadius: '4px',
    marginBottom: '24px',
  },
  text: {
    margin: 0,
    lineHeight: '1.6',
    color: '#333',
  },
  optionsSection: {
    marginBottom: '24px',
  },
  option: {
    backgroundColor: '#f9f9f9',
    padding: '16px',
    borderRadius: '4px',
    marginBottom: '16px',
    border: '1px solid #e0e0e0',
  },
  optionHeader: {
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
    marginBottom: '12px',
  },
  rankBadge: {
    backgroundColor: '#2196F3',
    color: 'white',
    padding: '4px 12px',
    borderRadius: '12px',
    fontSize: '14px',
    fontWeight: 'bold' as const,
  },
  optionTitle: {
    flex: 1,
    margin: 0,
    color: '#333',
  },
  confidenceBadge: {
    color: 'white',
    padding: '4px 12px',
    borderRadius: '12px',
    fontSize: '12px',
    fontWeight: 'bold' as const,
  },
  description: {
    margin: '0 0 12px 0',
    color: '#555',
    lineHeight: '1.6',
  },
  reasoning: {
    backgroundColor: 'white',
    padding: '12px',
    borderRadius: '4px',
    marginBottom: '12px',
    fontSize: '14px',
    lineHeight: '1.6',
    color: '#666',
  },
  stats: {
    fontSize: '14px',
    color: '#666',
  },
  statsList: {
    margin: '8px 0 0 20px',
    padding: 0,
  },
  contextSection: {
    borderTop: '2px solid #e0e0e0',
    paddingTop: '20px',
  },
  contextNote: {
    fontSize: '14px',
    color: '#666',
    fontStyle: 'italic' as const,
    marginBottom: '12px',
  },
  contextList: {
    margin: '0',
    padding: '0 0 0 20px',
  },
  contextItem: {
    fontSize: '14px',
    color: '#666',
    marginBottom: '8px',
    lineHeight: '1.5',
  },
};
