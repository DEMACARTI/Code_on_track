import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import HomeScreen from './src/screens/HomeScreen';
import ScanScreen from './src/screens/ScanScreen';
import QRDetailsScreen from './src/screens/QRDetailsScreen';
import RecordDataScreen from './src/screens/RecordDataScreen';

const Stack = createStackNavigator();

export default function App() {
  return (
    <NavigationContainer>
      <Stack.Navigator
        initialRouteName="Home"
        screenOptions={{
          headerStyle: {
            backgroundColor: '#1a1a2e',
          },
          headerTintColor: '#fff',
          headerTitleStyle: {
            fontWeight: 'bold',
          },
        }}
      >
        <Stack.Screen 
          name="Home" 
          component={HomeScreen}
          options={{ title: 'Railway QR Scanner' }}
        />
        <Stack.Screen 
          name="Scan" 
          component={ScanScreen}
          options={{ title: 'Scan QR Code' }}
        />
        <Stack.Screen 
          name="QRDetails" 
          component={QRDetailsScreen}
          options={{ title: 'QR Code Details' }}
        />
        <Stack.Screen 
          name="RecordData" 
          component={RecordDataScreen}
          options={{ title: 'Record Data' }}
        />
      </Stack.Navigator>
    </NavigationContainer>
  );
}
