const axios = require('axios');

class LLMService {
  constructor() {
    this.apiKey = process.env.LLM_API_KEY;
    this.apiUrl = process.env.LLM_API_URL || 'https://api.openai.com/v1/chat/completions';
    this.model = process.env.LLM_MODEL || 'gpt-3.5-turbo';
  }

  /**
   * Process QR code data and generate insights
   * @param {Object} qrData - QR code data object
   * @param {Array} historicalData - Array of historical data records
   * @returns {Object} - LLM generated insights and suggestions
   */
  async processQRData(qrData, historicalData) {
    try {
      const prompt = this.buildAnalysisPrompt(qrData, historicalData);
      const response = await this.callLLM(prompt);
      return this.parseResponse(response);
    } catch (error) {
      console.error('LLM processing error:', error.message);
      return {
        insights: 'Error processing data with LLM',
        suggestions: [],
        notifications: [],
      };
    }
  }

  /**
   * Generate maintenance recommendations
   * @param {Object} qrData - QR code data
   * @param {Array} scanHistory - Scan history
   * @returns {Object} - Maintenance recommendations
   */
  async generateMaintenanceRecommendations(qrData, scanHistory) {
    try {
      const prompt = `Analyze the following railway QR code data and scan history to provide maintenance recommendations:
      
QR Code Location: ${qrData.location?.station}, Platform ${qrData.location?.platform}
Material Type: ${qrData.materialType}
Status: ${qrData.status}
Total Scans: ${scanHistory.length}
Last Scan: ${scanHistory[0]?.scannedAt}

Based on this data, provide:
1. Maintenance priority (low/medium/high/critical)
2. Specific recommendations
3. Potential issues to watch for
4. Estimated timeline for next inspection

Respond in JSON format with keys: priority, recommendations, potentialIssues, nextInspection`;

      const response = await this.callLLM(prompt);
      return JSON.parse(response);
    } catch (error) {
      console.error('Error generating maintenance recommendations:', error.message);
      return null;
    }
  }

  /**
   * Detect anomalies in scan patterns
   * @param {Array} scanData - Array of scan records
   * @returns {Object} - Anomaly detection results
   */
  async detectAnomalies(scanData) {
    try {
      const prompt = `Analyze the following scan pattern data for a railway QR code and detect any anomalies:

Scan Data: ${JSON.stringify(scanData, null, 2)}

Identify:
1. Unusual scan frequency patterns
2. Suspicious scan locations or times
3. Potential security concerns
4. Equipment malfunction indicators

Respond in JSON format with keys: anomaliesDetected, anomalyType, severity, description, recommendedAction`;

      const response = await this.callLLM(prompt);
      return JSON.parse(response);
    } catch (error) {
      console.error('Error detecting anomalies:', error.message);
      return { anomaliesDetected: false };
    }
  }

  /**
   * Generate contextual notifications
   * @param {Object} context - Context data
   * @returns {Array} - Array of notification objects
   */
  async generateNotifications(context) {
    try {
      const prompt = `Based on the following railway QR system data, generate relevant notifications for the railway department:

Context: ${JSON.stringify(context, null, 2)}

Generate notifications for:
1. Urgent maintenance needs
2. Security alerts
3. Usage insights
4. Efficiency improvements

Respond with a JSON array of notifications, each having: type, priority, title, message`;

      const response = await this.callLLM(prompt);
      return JSON.parse(response);
    } catch (error) {
      console.error('Error generating notifications:', error.message);
      return [];
    }
  }

  /**
   * Build analysis prompt from data
   * @private
   */
  buildAnalysisPrompt(qrData, historicalData) {
    return `Analyze this railway QR code tracking data:

Current QR Code:
- ID: ${qrData.qrId}
- Location: ${qrData.location?.station}
- Material: ${qrData.materialType}
- Status: ${qrData.status}

Historical Data Points: ${historicalData.length}

Provide insights on:
1. Usage patterns
2. Potential issues
3. Optimization suggestions
4. Predictive maintenance needs

Format response as JSON with keys: insights, suggestions, notifications`;
  }

  /**
   * Call LLM API
   * @private
   */
  async callLLM(prompt) {
    if (!this.apiKey) {
      // Return mock response if no API key
      return this.getMockResponse(prompt);
    }

    const response = await axios.post(
      this.apiUrl,
      {
        model: this.model,
        messages: [
          {
            role: 'system',
            content: 'You are an AI assistant helping analyze railway QR code tracking data. Provide concise, actionable insights.',
          },
          {
            role: 'user',
            content: prompt,
          },
        ],
        temperature: 0.7,
        max_tokens: 1000,
      },
      {
        headers: {
          'Authorization': `Bearer ${this.apiKey}`,
          'Content-Type': 'application/json',
        },
      }
    );

    return response.data.choices[0].message.content;
  }

  /**
   * Parse LLM response
   * @private
   */
  parseResponse(response) {
    try {
      return JSON.parse(response);
    } catch (error) {
      return {
        insights: response,
        suggestions: [],
        notifications: [],
      };
    }
  }

  /**
   * Get mock response for development/testing
   * @private
   */
  getMockResponse(prompt) {
    return JSON.stringify({
      insights: 'QR code is functioning normally. Scan frequency is within expected parameters.',
      suggestions: [
        {
          suggestion: 'Schedule routine inspection within next 30 days',
          confidence: 0.85,
        },
        {
          suggestion: 'Monitor for increased wear on material surface',
          confidence: 0.72,
        },
      ],
      notifications: [
        {
          type: 'maintenance',
          priority: 'low',
          title: 'Routine Inspection Due',
          message: 'QR code has been in service for 90 days. Schedule routine inspection.',
        },
      ],
    });
  }
}

module.exports = new LLMService();
