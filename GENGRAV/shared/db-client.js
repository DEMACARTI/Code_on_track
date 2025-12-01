const { Pool } = require('pg');
const path = require('path');
require('dotenv').config({ path: path.join(__dirname, '../../App_a/.env') });

class DatabaseClient {
  constructor() {
    this.pool = new Pool({
      host: 'localhost',
      port: 5433,
      database: 'irf_dev',
      user: 'irf_user',
      password: 'irf_pass'
    });
  }

  async query(text, params) {
    const client = await this.pool.connect();
    try {
      const result = await client.query(text, params);
      return result;
    } finally {
      client.release();
    }
  }

  async createItem(itemData) {
    const { uid, component_type, lot_number, vendor_id, quantity, warranty_years, manufacture_date, qr_image_url, current_status, metadata } = itemData;
    
    const query = `
      INSERT INTO items (uid, component_type, lot_number, vendor_id, quantity, warranty_years, manufacture_date, qr_image_url, current_status, metadata)
      VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
      RETURNING *
    `;
    
    const values = [uid, component_type, lot_number, vendor_id, quantity, warranty_years, manufacture_date, qr_image_url, current_status, metadata];
    const result = await this.query(query, values);
    return result.rows[0];
  }

  async getItemByUid(uid) {
    const query = 'SELECT * FROM items WHERE uid = $1';
    const result = await this.query(query, [uid]);
    return result.rows[0];
  }

  async getAllItems() {
    const query = 'SELECT * FROM items ORDER BY created_at DESC';
    const result = await this.query(query);
    return result.rows;
  }

  async updateItem(uid, updates) {
    const fields = Object.keys(updates);
    const values = Object.values(updates);
    const setClause = fields.map((field, i) => `${field} = $${i + 2}`).join(', ');
    
    const query = `
      UPDATE items 
      SET ${setClause}, updated_at = NOW()
      WHERE uid = $1
      RETURNING *
    `;
    
    const result = await this.query(query, [uid, ...values]);
    return result.rows[0];
  }

  async createEngravingJob(jobData) {
    const { item_uid, svg_url, max_attempts = 3 } = jobData;
    
    const query = `
      INSERT INTO engraving_queue (item_uid, svg_url, status, attempts, max_attempts)
      VALUES ($1, $2, $3, $4, $5)
      RETURNING *
    `;
    
    const values = [item_uid, svg_url, 'PENDING', 0, max_attempts];
    const result = await this.query(query, values);
    return result.rows[0];
  }

  async getEngravingJob(jobId) {
    const query = 'SELECT * FROM engraving_queue WHERE id = $1';
    const result = await this.query(query, [jobId]);
    return result.rows[0];
  }

  async getEngravingJobsByStatus(status) {
    const query = 'SELECT * FROM engraving_queue WHERE status = $1 ORDER BY created_at ASC';
    const result = await this.query(query, [status.toUpperCase()]);
    return result.rows;
  }

  async getPendingEngravingJobs() {
    return await this.getEngravingJobsByStatus('PENDING');
  }

  async updateEngravingJobStatus(jobId, status, errorMessage = null) {
    let query;
    let values;
    const statusUpper = status.toUpperCase();
    
    if (statusUpper === 'IN_PROGRESS') {
      query = `
        UPDATE engraving_queue 
        SET status = $2, started_at = NOW(), error_message = $3
        WHERE id = $1
        RETURNING *
      `;
      values = [jobId, statusUpper, errorMessage];
    } else if (statusUpper === 'COMPLETED') {
      query = `
        UPDATE engraving_queue 
        SET status = $2, completed_at = NOW(), error_message = $3
        WHERE id = $1
        RETURNING *
      `;
      values = [jobId, statusUpper, errorMessage];
    } else {
      query = `
        UPDATE engraving_queue 
        SET status = $2, error_message = $3
        WHERE id = $1
        RETURNING *
      `;
      values = [jobId, statusUpper, errorMessage];
    }
    
    const result = await this.query(query, values);
    
    // Add to history
    await this.addEngravingHistory(jobId, statusUpper, errorMessage);
    
    return result.rows[0];
  }

  async incrementJobAttempts(jobId) {
    const query = `
      UPDATE engraving_queue 
      SET attempts = attempts + 1
      WHERE id = $1
      RETURNING *
    `;
    
    const result = await this.query(query, [jobId]);
    return result.rows[0];
  }

  async addEngravingHistory(jobId, status, message = null) {
    const query = `
      INSERT INTO engraving_history (engraving_job_id, status, message)
      VALUES ($1, $2, $3)
      RETURNING *
    `;
    
    const values = [jobId, status, message];
    const result = await this.query(query, values);
    return result.rows[0];
  }

  async getEngravingHistory(jobId) {
    const query = `
      SELECT * FROM engraving_history 
      WHERE engraving_job_id = $1 
      ORDER BY created_at DESC
    `;
    const result = await this.query(query, [jobId]);
    return result.rows;
  }

  async getItemsWithEngravingStatus() {
    const query = `
      SELECT 
        i.*,
        eq.id as engraving_job_id,
        eq.status as engraving_status,
        eq.attempts,
        eq.created_at as engraving_created_at,
        eq.started_at as engraving_started_at,
        eq.completed_at as engraving_completed_at,
        eq.error_message
      FROM items i
      LEFT JOIN engraving_queue eq ON i.uid = eq.item_uid
      ORDER BY i.created_at DESC
    `;
    const result = await this.query(query);
    return result.rows;
  }

  async close() {
    await this.pool.end();
  }
}

module.exports = DatabaseClient;
