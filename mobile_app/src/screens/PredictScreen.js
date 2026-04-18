import React, { useState } from 'react';
import { View, Text, TextInput, TouchableOpacity, StyleSheet, Alert, ActivityIndicator, ScrollView, Image } from 'react-native';
import * as ImagePicker from 'expo-image-picker';
import { theme } from '../theme';
import api from '../api';

export default function PredictScreen({ route }) {
  const { user } = route.params;
  const [text, setText] = useState('');
  const [imageUri, setImageUri] = useState(null);
  const [base64Image, setBase64Image] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const pickImage = async () => {
    let permissionResult = await ImagePicker.requestMediaLibraryPermissionsAsync();
    if (permissionResult.granted === false) {
      Alert.alert("Permission to access camera roll is required!");
      return;
    }

    let result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      allowsEditing: true,
      base64: true,
      quality: 0.8,
    });

    if (!result.canceled) {
      setImageUri(result.assets[0].uri);
      setBase64Image(result.assets[0].base64);
      setText(''); // clear text when image is picked
    }
  };

  const clearSelection = () => {
    setImageUri(null);
    setBase64Image(null);
    setText('');
    setResult(null);
  };

  const handlePredict = async () => {
    if (!text.trim() && !base64Image) {
      Alert.alert('Error', 'Please enter text or upload an image.');
      return;
    }

    setLoading(true);
    setResult(null);
    try {
      const response = await api.post('/predict', {
        loginid: user.loginid,
        text: text,
        base64_image: base64Image
      });

      if (response.data.success) {
        setResult(response.data.score);
      }
    } catch (error) {
      const msg = error.response?.data?.message || 'Prediction failed';
      Alert.alert('Analysis Error', msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <ScrollView contentContainerStyle={styles.container}>
      <Text style={styles.title}>Predict Score</Text>

      {result && (
        <View style={styles.resultCard}>
          <Text style={styles.resultTitle}>Estimated Score</Text>
          <Text style={styles.resultScore}>{result}</Text>
        </View>
      )}

      <View style={styles.card}>
        <Text style={styles.label}>Upload Essay Image (OCR)</Text>
        <TouchableOpacity style={styles.imageButton} onPress={pickImage}>
          <Text style={styles.imageButtonText}>Select Image from Gallery</Text>
        </TouchableOpacity>

        {imageUri && (
          <View style={styles.previewContainer}>
            <Image source={{ uri: imageUri }} style={styles.previewImage} />
            <TouchableOpacity onPress={clearSelection}>
              <Text style={styles.clearText}>Remove Image</Text>
            </TouchableOpacity>
          </View>
        )}

        <Text style={styles.orText}>— OR —</Text>

        <Text style={styles.label}>Paste Essay Text</Text>
        <TextInput
          style={styles.textArea}
          placeholder="Start typing your essay here..."
          multiline
          numberOfLines={6}
          value={text}
          onChangeText={(val) => {
            setText(val);
            if (val.length > 0) {
              setImageUri(null);
              setBase64Image(null);
            }
          }}
        />

        <TouchableOpacity style={styles.submitButton} onPress={handlePredict} disabled={loading}>
          {loading ? <ActivityIndicator color="#fff" /> : <Text style={styles.submitButtonText}>Analyze</Text>}
        </TouchableOpacity>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flexGrow: 1,
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
    padding: 20,
    borderRadius: 12,
    elevation: 3,
  },
  label: {
    fontSize: 14,
    fontWeight: 'bold',
    color: theme.colors.textSecondary,
    marginBottom: 10,
  },
  imageButton: {
    backgroundColor: theme.colors.blue100,
    padding: 15,
    borderRadius: 8,
    alignItems: 'center',
    marginBottom: 10,
  },
  imageButtonText: {
    color: theme.colors.primary,
    fontWeight: '600',
  },
  previewContainer: {
    alignItems: 'center',
    marginVertical: 10,
  },
  previewImage: {
    width: '100%',
    height: 150,
    borderRadius: 8,
    resizeMode: 'cover',
  },
  clearText: {
    color: theme.colors.danger,
    marginTop: 10,
    fontWeight: '600',
  },
  orText: {
    textAlign: 'center',
    color: theme.colors.textMuted,
    marginVertical: 15,
    fontWeight: 'bold',
  },
  textArea: {
    backgroundColor: theme.colors.surface2,
    borderRadius: 8,
    padding: 15,
    textAlignVertical: 'top',
    minHeight: 120,
    color: theme.colors.textPrimary,
    marginBottom: 20,
  },
  submitButton: {
    backgroundColor: theme.colors.primary,
    padding: 15,
    borderRadius: 8,
    alignItems: 'center',
  },
  submitButtonText: {
    color: '#fff',
    fontWeight: 'bold',
    fontSize: 16,
  },
  resultCard: {
    backgroundColor: theme.colors.navy,
    padding: 20,
    borderRadius: 12,
    alignItems: 'center',
    marginBottom: 20,
  },
  resultTitle: {
    color: theme.colors.blue100,
    fontSize: 16,
    textTransform: 'uppercase',
  },
  resultScore: {
    color: '#fff',
    fontSize: 48,
    fontWeight: 'bold',
    marginTop: 5,
  }
});
