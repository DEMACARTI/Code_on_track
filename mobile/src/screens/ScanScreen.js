import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, Button, Alert } from 'react-native';
import { BarCodeScanner } from 'expo-barcode-scanner';
import apiService from '../services/apiService';

export default function ScanScreen({ navigation }) {
  const [hasPermission, setHasPermission] = useState(null);
  const [scanned, setScanned] = useState(false);

  useEffect(() => {
    (async () => {
      const { status } = await BarCodeScanner.requestPermissionsAsync();
      setHasPermission(status === 'granted');
    })();
  }, []);

  const handleBarCodeScanned = async ({ type, data }) => {
    setScanned(true);
    
    try {
      // Parse QR code data
      const qrData = JSON.parse(data);
      
      // Record scan
      await apiService.scanQRCode(qrData.qrId, {
        scannedBy: 'field_staff',
        deviceId: 'mobile_device_001',
      });

      Alert.alert(
        'QR Code Scanned',
        'QR code scanned successfully!',
        [
          {
            text: 'View Details',
            onPress: () => navigation.navigate('QRDetails', { qrId: qrData.qrId }),
          },
          {
            text: 'Scan Another',
            onPress: () => setScanned(false),
          },
        ]
      );
    } catch (error) {
      Alert.alert('Error', 'Failed to process QR code');
      setScanned(false);
    }
  };

  if (hasPermission === null) {
    return <Text style={styles.message}>Requesting camera permission...</Text>;
  }
  
  if (hasPermission === false) {
    return <Text style={styles.message}>No access to camera</Text>;
  }

  return (
    <View style={styles.container}>
      <BarCodeScanner
        onBarCodeScanned={scanned ? undefined : handleBarCodeScanned}
        style={StyleSheet.absoluteFillObject}
      />
      
      <View style={styles.overlay}>
        <View style={styles.scanArea} />
        <Text style={styles.instructions}>
          Align QR code within the frame
        </Text>
        
        {scanned && (
          <Button
            title="Tap to Scan Again"
            onPress={() => setScanned(false)}
          />
        )}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: 'black',
  },
  overlay: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  scanArea: {
    width: 250,
    height: 250,
    borderWidth: 2,
    borderColor: 'white',
    borderRadius: 12,
    backgroundColor: 'transparent',
  },
  instructions: {
    color: 'white',
    fontSize: 16,
    marginTop: 20,
    textAlign: 'center',
    backgroundColor: 'rgba(0, 0, 0, 0.7)',
    padding: 12,
    borderRadius: 8,
  },
  message: {
    flex: 1,
    textAlign: 'center',
    padding: 20,
    fontSize: 16,
  },
});
