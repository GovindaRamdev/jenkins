require('dotenv').config();
const fs = require('fs');
const path = require('path');
const { OpenAI } = require('openai');
const { Pinecone } = require('@pinecone-database/pinecone');

class TextEmbedder {
  constructor(directory, chunkSize = 1000, overlap = 100) {
    this.directory = directory;
    this.chunkSize = chunkSize;
    this.overlap = overlap;
    this.apiKey = process.env.API_KEY;
    this.pineconeApiKey = process.env.PINECONE_API_KEY;
    this.indexName = process.env.INDEX_NAME;

    this.openai = new OpenAI({ apiKey: this.apiKey });
    this.pinecone = new Pinecone({ apiKey: this.pineconeApiKey });
    this.index = null;
  }

  async initIndex() {
    const existingIndexes = await this.pinecone.listIndexes();
    if (!existingIndexes.includes(this.indexName)) {
      console.log(`Creating index: ${this.indexName}`);
      await this.pinecone.createIndex({
        name: this.indexName,
        dimension: 1536,
        metric: 'cosine',
        spec: {
          serverless: {
            cloud: 'aws',
            region: 'us-east-1'
          }
        }
      });
    } else {
      console.log(`Index ${this.indexName} already exists.`);
    }

    this.index = this.pinecone.Index(this.indexName);
  }

  readTextFiles() {
    const files = fs.readdirSync(this.directory);
    const texts = [];

    files.forEach(file => {
      if (file.endsWith('.txt')) {
        const filePath = path.join(this.directory, file);
        console.log(`Reading file: ${filePath}`);
        const content = fs.readFileSync(filePath, 'utf8');
        if (content.trim()) {
          texts.push(content);
          console.log(`Successfully read file ${file}`);
        } else {
          console.warn(`File ${file} is empty.`);
        }
      }
    });

    if (texts.length === 0) throw new Error('No valid text files found.');
    return texts;
  }

  splitTextIntoChunks(text) {
    const separator = '-- --------------------------------------------';
    return text.split(separator).map(chunk => chunk.trim()).filter(Boolean);
  }

  async getEmbeddings(texts) {
    const embeddings = [];

    for (const text of texts) {
      const chunks = this.splitTextIntoChunks(text);
      for (const chunk of chunks) {
        const res = await this.openai.embeddings.create({
          input: chunk,
          model: 'text-embedding-3-small'
        });
        const embedding = res.data[0].embedding;
        embeddings.push({ chunk, embedding });
        console.log(`Embedded chunk: ${chunk.substring(0, 50)}...`);
      }
    }

    return embeddings;
  }

  async upsertToPinecone(embeddings) {
    const vectors = embeddings.map((item, i) => ({
      id: `embedding_${i}`,
      values: item.embedding,
      metadata: { text: item.chunk }
    }));

    console.log('Upserting to Pinecone...');
    await this.index.upsert(vectors);
    console.log('Upsert complete.');
  }

  async queryPinecone(userQuery) {
    console.log(`Embedding user query: ${userQuery}`);
    const res = await this.openai.embeddings.create({
      input: userQuery,
      model: 'text-embedding-3-small'
    });

    const embedding = res.data[0].embedding;
    const results = await this.index.query({
      vector: embedding,
      topK: 10,
      includeMetadata: true,
      includeValues: true
    });

    console.log('Query Results:', JSON.stringify(results, null, 2));
    return results;
  }

  async process() {
    await this.initIndex();
    const texts = this.readTextFiles();
    const embeddings = await this.getEmbeddings(texts);
    await this.upsertToPinecone(embeddings);
  }
}

(async () => {
  const embedder = new TextEmbedder('files');
  await embedder.process();
})();
