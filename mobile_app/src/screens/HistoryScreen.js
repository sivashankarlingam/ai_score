import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, FlatList, ActivityIndicator } from 'react-native';
import { theme } from '../theme';
import api from '../api';

export default function HistoryScreen({ route }) {
  const { user } = route.params;
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    try {
      const response = await api.get(`/history/${user.loginid}`);
      setHistory(response.data);
    } catch (error) {
      console.log('Error fetching history:', error);
    } finally {
      setLoading(false);
    }
  };

  const renderItem = ({ item }) => (
    <View style={styles.card}>
      <View style={styles.scoreBox}>
        <Text style={styles.scoreNumber}>{item.score}</Text>
        <Text style={styles.scoreLabel}>Pts</Text>
      </View>
      <View style={styles.infoBox}>
        <Text style={styles.snippet} numberOfLines={3}>
          {item.essay_snippet}
        </Text>
        <Text style={styles.date}>
          {new Date(item.scored_at).toLocaleString()}
        </Text>
      </View>
    </View>
  );

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Score History</Text>
      
      {loading ? (
        <ActivityIndicator size="large" color={theme.colors.primary} style={{marginTop: 50}} />
      ) : (
        <FlatList
          data={history}
          keyExtractor={(item, index) => index.toString()}
          renderItem={renderItem}
          contentContainerStyle={{ paddingBottom: 20 }}
          ListEmptyComponent={
            <Text style={styles.emptyText}>You haven't scored any essays yet.</Text>
          }
        />
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: theme.colors.bg,
    padding: 20,
    paddingTop: 40,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: theme.colors.navy,
    marginBottom: 20,
  },
  card: {
    backgroundColor: theme.colors.surface,
    borderRadius: 12,
    padding: 15,
    marginBottom: 15,
    flexDirection: 'row',
    alignItems: 'center',
    elevation: 2,
  },
  scoreBox: {
    backgroundColor: theme.colors.blue100,
    borderRadius: 8,
    padding: 10,
    alignItems: 'center',
    justifyContent: 'center',
    width: 60,
    height: 60,
    marginRight: 15,
  },
  scoreNumber: {
    fontSize: 22,
    fontWeight: 'bold',
    color: theme.colors.primary,
  },
  scoreLabel: {
    fontSize: 10,
    color: theme.colors.primary,
    textTransform: 'uppercase',
  },
  infoBox: {
    flex: 1,
  },
  snippet: {
    fontSize: 14,
    color: theme.colors.textPrimary,
    fontStyle: 'italic',
    marginBottom: 8,
  },
  date: {
    fontSize: 12,
    color: theme.colors.textMuted,
  },
  emptyText: {
    textAlign: 'center',
    color: theme.colors.textMuted,
    marginTop: 40,
    fontSize: 16,
  }
});
