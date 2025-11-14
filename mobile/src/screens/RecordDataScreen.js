import React, { useState } from 'react';
import { View, Text, StyleSheet, TextInput, TouchableOpacity, ScrollView, Alert } from 'react-native';
import apiService from '../services/apiService';

export default function RecordDataScreen({ route, navigation }) {
  const { qrId } = route.params || {};
  const [formData, setFormData] = useState({
    qrId: qrId || '',
    dataType: 'maintenance',
    notes: '',
    issueType: '',
    severity: '',
  });

  const handleSubmit = async () => {
    if (!formData.qrId || !formData.notes) {
      Alert.alert('Error', 'Please fill in all required fields');
      return;
    }

    try {
      await apiService.recordData({
        qrId: formData.qrId,
        dataType: formData.dataType,
        data: {
          notes: formData.notes,
          issueType: formData.issueType,
          severity: formData.severity,
          recordedBy: 'field_staff',
          timestamp: new Date().toISOString(),
        },
        source: 'mobile',
      });

      Alert.alert(
        'Success',
        'Data recorded successfully!',
        [
          {
            text: 'OK',
            onPress: () => navigation.goBack(),
          },
        ]
      );
    } catch (error) {
      Alert.alert('Error', 'Failed to record data');
    }
  };

  return (
    <ScrollView style={styles.container}>
      <View style={styles.form}>
        <View style={styles.field}>
          <Text style={styles.label}>QR Code ID *</Text>
          <TextInput
            style={styles.input}
            value={formData.qrId}
            onChangeText={(text) => setFormData({ ...formData, qrId: text })}
            placeholder="Enter QR Code ID"
            editable={!qrId}
          />
        </View>

        <View style={styles.field}>
          <Text style={styles.label}>Data Type *</Text>
          <View style={styles.radioGroup}>
            {['maintenance', 'inspection', 'incident'].map((type) => (
              <TouchableOpacity
                key={type}
                style={[
                  styles.radioButton,
                  formData.dataType === type && styles.radioButtonActive,
                ]}
                onPress={() => setFormData({ ...formData, dataType: type })}
              >
                <Text
                  style={[
                    styles.radioText,
                    formData.dataType === type && styles.radioTextActive,
                  ]}
                >
                  {type}
                </Text>
              </TouchableOpacity>
            ))}
          </View>
        </View>

        <View style={styles.field}>
          <Text style={styles.label}>Issue Type</Text>
          <TextInput
            style={styles.input}
            value={formData.issueType}
            onChangeText={(text) => setFormData({ ...formData, issueType: text })}
            placeholder="e.g., Surface damage, Fading"
          />
        </View>

        <View style={styles.field}>
          <Text style={styles.label}>Severity</Text>
          <View style={styles.radioGroup}>
            {['low', 'medium', 'high'].map((severity) => (
              <TouchableOpacity
                key={severity}
                style={[
                  styles.radioButton,
                  formData.severity === severity && styles.radioButtonActive,
                ]}
                onPress={() => setFormData({ ...formData, severity })}
              >
                <Text
                  style={[
                    styles.radioText,
                    formData.severity === severity && styles.radioTextActive,
                  ]}
                >
                  {severity}
                </Text>
              </TouchableOpacity>
            ))}
          </View>
        </View>

        <View style={styles.field}>
          <Text style={styles.label}>Notes *</Text>
          <TextInput
            style={[styles.input, styles.textArea]}
            value={formData.notes}
            onChangeText={(text) => setFormData({ ...formData, notes: text })}
            placeholder="Enter detailed notes..."
            multiline
            numberOfLines={6}
          />
        </View>

        <TouchableOpacity style={styles.submitButton} onPress={handleSubmit}>
          <Text style={styles.submitButtonText}>Submit Record</Text>
        </TouchableOpacity>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  form: {
    padding: 16,
  },
  field: {
    marginBottom: 24,
  },
  label: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1a1a2e',
    marginBottom: 8,
  },
  input: {
    backgroundColor: 'white',
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 8,
    padding: 12,
    fontSize: 16,
  },
  textArea: {
    minHeight: 120,
    textAlignVertical: 'top',
  },
  radioGroup: {
    flexDirection: 'row',
    gap: 12,
  },
  radioButton: {
    flex: 1,
    padding: 12,
    backgroundColor: 'white',
    borderWidth: 2,
    borderColor: '#ddd',
    borderRadius: 8,
    alignItems: 'center',
  },
  radioButtonActive: {
    borderColor: '#007bff',
    backgroundColor: '#007bff',
  },
  radioText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#666',
    textTransform: 'capitalize',
  },
  radioTextActive: {
    color: 'white',
  },
  submitButton: {
    backgroundColor: '#007bff',
    padding: 16,
    borderRadius: 8,
    alignItems: 'center',
    marginTop: 16,
    marginBottom: 32,
  },
  submitButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: 'bold',
  },
});
