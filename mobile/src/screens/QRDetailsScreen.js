import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity, ActivityIndicator } from 'react-native';
import apiService from '../services/apiService';

export default function QRDetailsScreen({ route, navigation }) {
  const { qrId } = route.params;
  const [qrData, setQrData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchQRDetails();
  }, [qrId]);

  const fetchQRDetails = async () => {
    try {
      const response = await apiService.getQRCode(qrId);
      setQrData(response.qrCode);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching QR details:', error);
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <View style={styles.centered}>
        <ActivityIndicator size="large" color="#007bff" />
      </View>
    );
  }

  if (!qrData) {
    return (
      <View style={styles.centered}>
        <Text>QR code not found</Text>
      </View>
    );
  }

  return (
    <ScrollView style={styles.container}>
      <View style={styles.card}>
        <Text style={styles.label}>QR Code ID</Text>
        <Text style={styles.value}>{qrData.qrId}</Text>
      </View>

      <View style={styles.card}>
        <Text style={styles.label}>Location</Text>
        <Text style={styles.value}>
          {qrData.location?.station || 'N/A'}
        </Text>
        {qrData.location?.platform && (
          <Text style={styles.subValue}>Platform {qrData.location.platform}</Text>
        )}
        {qrData.location?.area && (
          <Text style={styles.subValue}>{qrData.location.area}</Text>
        )}
      </View>

      <View style={styles.card}>
        <Text style={styles.label}>Material Type</Text>
        <Text style={styles.value}>{qrData.materialType}</Text>
      </View>

      <View style={styles.card}>
        <Text style={styles.label}>Dimensions</Text>
        <Text style={styles.value}>
          {qrData.dimensions?.width} × {qrData.dimensions?.height} {qrData.dimensions?.unit}
        </Text>
      </View>

      <View style={styles.card}>
        <Text style={styles.label}>Status</Text>
        <View style={[styles.badge, getBadgeColor(qrData.status)]}>
          <Text style={styles.badgeText}>{qrData.status}</Text>
        </View>
      </View>

      <View style={styles.card}>
        <Text style={styles.label}>Total Scans</Text>
        <Text style={styles.value}>{qrData.scans?.length || 0}</Text>
      </View>

      <View style={styles.actions}>
        <TouchableOpacity
          style={[styles.button, styles.primaryButton]}
          onPress={() => navigation.navigate('RecordData', { qrId: qrData.qrId })}
        >
          <Text style={styles.buttonText}>Record Data</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={[styles.button, styles.secondaryButton]}
          onPress={() => navigation.goBack()}
        >
          <Text style={[styles.buttonText, { color: '#007bff' }]}>Back</Text>
        </TouchableOpacity>
      </View>
    </ScrollView>
  );
}

function getBadgeColor(status) {
  const colors = {
    active: { backgroundColor: '#28a745' },
    inactive: { backgroundColor: '#ffc107' },
    damaged: { backgroundColor: '#dc3545' },
    replaced: { backgroundColor: '#17a2b8' },
  };
  return colors[status] || { backgroundColor: '#6c757d' };
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
    padding: 16,
  },
  centered: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  card: {
    backgroundColor: 'white',
    borderRadius: 8,
    padding: 16,
    marginBottom: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  label: {
    fontSize: 14,
    color: '#666',
    marginBottom: 8,
    fontWeight: '600',
  },
  value: {
    fontSize: 16,
    color: '#1a1a2e',
    fontWeight: '500',
  },
  subValue: {
    fontSize: 14,
    color: '#666',
    marginTop: 4,
  },
  badge: {
    alignSelf: 'flex-start',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 4,
  },
  badgeText: {
    color: 'white',
    fontSize: 14,
    fontWeight: 'bold',
    textTransform: 'uppercase',
  },
  actions: {
    marginTop: 16,
    marginBottom: 32,
  },
  button: {
    padding: 16,
    borderRadius: 8,
    alignItems: 'center',
    marginBottom: 12,
  },
  primaryButton: {
    backgroundColor: '#007bff',
  },
  secondaryButton: {
    backgroundColor: 'white',
    borderWidth: 2,
    borderColor: '#007bff',
  },
  buttonText: {
    fontSize: 16,
    fontWeight: 'bold',
    color: 'white',
  },
});
