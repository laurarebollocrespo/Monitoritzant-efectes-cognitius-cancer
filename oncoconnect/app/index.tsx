import React from 'react';
import { StyleSheet, View } from 'react-native';
import { WebView } from 'react-native-webview';

export default function TabOneScreen() {
  return (
    <View style={styles.container}>
      <WebView source={{ uri: 'http://10.66.51.224:8501' }} />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    marginTop: 50,
  },
});
