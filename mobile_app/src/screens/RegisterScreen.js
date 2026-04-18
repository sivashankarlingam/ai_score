import React, { useState } from 'react';
import { View, Text, TextInput, TouchableOpacity, StyleSheet, Alert, ActivityIndicator, ScrollView } from 'react-native';
import { theme } from '../theme';
import api from '../api';

export default function RegisterScreen({ navigation }) {
  const [formData, setFormData] = useState({
    name: '', loginid: '', password: '', mobile: '',
    email: '', locality: '', address: '', city: '', state: ''
  });
  const [loading, setLoading] = useState(false);

  const handleChange = (name, value) => {
    setFormData({ ...formData, [name]: value });
  };

  const handleRegister = async () => {
    setLoading(true);
    try {
      const response = await api.post('/auth/register', formData);
      if (response.status === 200) {
        Alert.alert('Success', response.data.message);
        navigation.navigate('Login');
      }
    } catch (error) {
      const msg = error.response?.data?.message || 'Registration Failed';
      Alert.alert('Error', msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <ScrollView contentContainerStyle={styles.container}>
      <Text style={styles.title}>Create Account</Text>
      
      <View style={styles.card}>
        {['name', 'loginid', 'password', 'mobile', 'email', 'locality', 'address', 'city', 'state'].map(field => (
          <TextInput
            key={field}
            style={styles.input}
            placeholder={field.charAt(0).toUpperCase() + field.slice(1)}
            secureTextEntry={field === 'password'}
            value={formData[field]}
            onChangeText={(val) => handleChange(field, val)}
          />
        ))}

        <TouchableOpacity style={styles.button} onPress={handleRegister} disabled={loading}>
          {loading ? <ActivityIndicator color="#fff" /> : <Text style={styles.buttonText}>Register</Text>}
        </TouchableOpacity>

        <TouchableOpacity onPress={() => navigation.navigate('Login')} style={{marginTop: 15}}>
          <Text style={styles.linkText}>Already have an account? Login</Text>
        </TouchableOpacity>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flexGrow: 1,
    backgroundColor: theme.colors.bg,
    justifyContent: 'center',
    padding: 20,
    paddingVertical: 50,
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: theme.colors.primary,
    textAlign: 'center',
    marginBottom: 20,
  },
  card: {
    backgroundColor: theme.colors.surface,
    padding: 20,
    borderRadius: 12,
    elevation: 3,
  },
  input: {
    backgroundColor: theme.colors.surface2,
    padding: 15,
    borderRadius: 8,
    marginBottom: 10,
    color: theme.colors.textPrimary,
  },
  button: {
    backgroundColor: theme.colors.primary,
    padding: 15,
    borderRadius: 8,
    alignItems: 'center',
    marginTop: 10,
  },
  buttonText: { color: '#fff', fontWeight: 'bold', fontSize: 16 },
  linkText: { color: theme.colors.primary, textAlign: 'center', fontWeight: '500' }
});
