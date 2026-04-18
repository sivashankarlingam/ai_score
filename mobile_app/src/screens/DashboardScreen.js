import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import { theme } from '../theme';

export default function DashboardScreen({ route, navigation }) {
  const { user } = route.params;

  return (
    <View style={styles.container}>
      <View style={styles.headerBox}>
        <Text style={styles.welcomeText}>Welcome back,</Text>
        <Text style={styles.nameText}>{user.name}</Text>
      </View>

      <View style={styles.card}>
        <Text style={styles.cardTitle}>Ready to analyze an essay?</Text>
        <Text style={styles.cardDesc}>
          Use our AI model to score your essays. You can type it, paste it, or even upload a handwritten picture for OCR transcription.
        </Text>
        
        <TouchableOpacity 
          style={styles.button}
          onPress={() => navigation.navigate('Predict')}
        >
          <Text style={styles.buttonText}>Start Prediction</Text>
        </TouchableOpacity>
      </View>
      
      <View style={styles.statsRow}>
        <View style={styles.statBox}>
          <Text style={styles.statValue}>Live</Text>
          <Text style={styles.statLabel}>Model Status</Text>
        </View>
        <View style={styles.statBox}>
          <Text style={styles.statValue}>12k+</Text>
          <Text style={styles.statLabel}>Trained Set</Text>
        </View>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: theme.colors.bg,
    padding: 20,
  },
  headerBox: {
    marginBottom: 30,
    marginTop: 20,
  },
  welcomeText: {
    fontSize: 18,
    color: theme.colors.textSecondary,
  },
  nameText: {
    fontSize: 32,
    fontWeight: 'bold',
    color: theme.colors.primary,
  },
  card: {
    backgroundColor: theme.colors.surface,
    padding: 20,
    borderRadius: 16,
    elevation: 3,
    shadowColor: '#000',
    shadowOpacity: 0.05,
    shadowRadius: 10,
    marginBottom: 20,
  },
  cardTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: theme.colors.navy,
    marginBottom: 10,
  },
  cardDesc: {
    fontSize: 15,
    color: theme.colors.textSecondary,
    lineHeight: 22,
    marginBottom: 20,
  },
  button: {
    backgroundColor: theme.colors.primary,
    padding: 15,
    borderRadius: 8,
    alignItems: 'center',
  },
  buttonText: {
    color: '#fff',
    fontWeight: 'bold',
    fontSize: 16,
  },
  statsRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  statBox: {
    backgroundColor: theme.colors.surface,
    width: '48%',
    padding: 20,
    borderRadius: 12,
    alignItems: 'center',
    elevation: 2,
  },
  statValue: {
    fontSize: 24,
    fontWeight: 'bold',
    color: theme.colors.success,
  },
  statLabel: {
    fontSize: 14,
    color: theme.colors.textMuted,
    marginTop: 5,
  }
});
