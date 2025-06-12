import fs from 'fs';
import crypto from 'crypto';
import os from 'os';
import path from 'path';
import dotenv from 'dotenv';

import { fileURLToPath } from 'url';
import { dirname } from 'path';
const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Load .env if present
dotenv.config({ path: path.resolve(__dirname, '../../../.env') });

const ACCOUNT_ID = process.env.CF_ACCOUNT_ID;
const DATABASE_ID = process.env.CF_D1_DB_ID;
const D1_API_KEY = process.env.CF_D1_API_KEY;
const D1_URL = `https://api.cloudflare.com/client/v4/accounts/${ACCOUNT_ID}/d1/database/${DATABASE_ID}/import`;
const headers = {
  'Content-Type': 'application/json',
  Authorization: `Bearer ${D1_API_KEY}`,
};

async function pollImport(bookmark) {
  const payload = {
    action: 'poll',
    current_bookmark: bookmark,
  };
  while (true) {
    const pollResponse = await fetch(D1_URL, {
      method: 'POST',
      headers,
      body: JSON.stringify(payload),
    });
    const result = await pollResponse.json();
    console.log('Poll Response:', result.result);
    const { success, error } = result.result;
    if (success || (!success && error === 'Not currently importing anything.')) {
      break;
    }
    await new Promise(resolve => setTimeout(resolve, 1000));
  }
}

async function uploadToD1(sqlString) {
  const hashStr = crypto.createHash('md5').update(sqlString).digest('hex');
  try {
    // 1. Init upload
    const initResponse = await fetch(D1_URL, {
      method: 'POST',
      headers,
      body: JSON.stringify({
        action: 'init',
        etag: hashStr,
      }),
    });
    const uploadData = await initResponse.json();
    console.log('Init upload response:', uploadData);
    if (!uploadData.result?.upload_url) {
      console.error('Missing upload_url in init response. Full response:', uploadData);
      return 'Import failed';
    }
    const uploadUrl = uploadData.result.upload_url;
    const filename = uploadData.result.filename;
    // 2. Upload to R2
    console.log('Uploading SQL to:', uploadUrl);
    const r2Response = await fetch(uploadUrl, {
      method: 'PUT',
      body: sqlString,
    });
    const r2Etag = r2Response.headers.get('ETag').replace(/"/g, '');
    if (r2Etag !== hashStr) {
      throw new Error('ETag mismatch');
    }
    // 3. Start ingestion
    const ingestResponse = await fetch(D1_URL, {
      method: 'POST',
      headers,
      body: JSON.stringify({
        action: 'ingest',
        etag: hashStr,
        filename,
      }),
    });
    const ingestData = await ingestResponse.json();
    console.log('Ingestion Response:', ingestData);
    // 4. Polling
    await pollImport(ingestData.result.at_bookmark);
    return 'Import completed successfully';
  } catch (e) {
    console.error('Error:', e);
    return 'Import failed';
  }
}

async function main() {
  const filePath = process.argv[2];
  if (!filePath) {
    console.error('Usage: node ingest_to_d1.js <deals.sql>');
    process.exit(1);
  }
  if (!ACCOUNT_ID || !DATABASE_ID || !D1_API_KEY) {
    console.error('Missing required environment variables.');
    process.exit(1);
  }
  // Read SQL file
  const sqlString = fs.readFileSync(filePath, 'utf-8');
  // Upload
  const result = await uploadToD1(sqlString);
  console.log(result);
}

main();
