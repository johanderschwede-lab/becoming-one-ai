# 🗄️ Storage Strategy
## Clean Data Architecture with Supabase as Foundation

### 1. Core Data Types & Their Homes

#### Identity & Core User Data (Supabase)
```sql
-- Already set up in Supabase
CREATE TABLE identity_registry (
    person_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    last_seen_at TIMESTAMPTZ,
    consent_status JSONB DEFAULT '{}',
    metadata JSONB DEFAULT '{}'
);

-- Cross-platform identity links
CREATE TABLE identity_links (
    link_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    person_id UUID REFERENCES identity_registry(person_id),
    platform TEXT NOT NULL,
    platform_id TEXT NOT NULL,
    verified BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(platform, platform_id)
);
```

#### Interaction Events (Supabase)
```sql
-- High-volume event logging
CREATE TABLE event_log (
    event_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    person_id UUID REFERENCES identity_registry(person_id),
    event_type TEXT NOT NULL,
    platform TEXT NOT NULL,
    content JSONB NOT NULL,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Add hypertable for time-series optimization
SELECT create_hypertable('event_log', 'created_at');
```

#### Knowledge Base (Pinecone + Supabase)
```python
class KnowledgeStore:
    def __init__(self):
        self.pinecone = PineconeClient()  # Semantic vectors
        self.supabase = SupabaseClient()  # Metadata & content
    
    async def store_knowledge(self, content: str, metadata: dict):
        # Get embedding
        embedding = await self.get_embedding(content)
        
        # Store in Pinecone
        vector_id = await self.pinecone.upsert(
            vectors=[(str(uuid4()), embedding)],
            namespace="knowledge"
        )
        
        # Store metadata in Supabase
        await self.supabase.table('knowledge_items').insert({
            'vector_id': vector_id,
            'content': content,
            'metadata': metadata
        })
```

### 2. Data Access Patterns

#### Direct Queries (Supabase)
```python
class IdentityService:
    async def get_identity(self, platform: str, platform_id: str):
        # Direct SQL query for identity lookup
        result = await self.supabase.rpc(
            'get_identity_by_platform',
            {
                'p_platform': platform,
                'p_platform_id': platform_id
            }
        )
        return result.data
```

#### Semantic Search (Pinecone)
```python
class KnowledgeService:
    async def search_knowledge(self, query: str, limit: int = 5):
        # Get query embedding
        query_embedding = await self.get_embedding(query)
        
        # Search Pinecone
        results = await self.pinecone.query(
            vector=query_embedding,
            top_k=limit,
            namespace="knowledge"
        )
        
        # Get metadata from Supabase
        vector_ids = [r.id for r in results.matches]
        metadata = await self.supabase.table('knowledge_items').select(
            '*'
        ).in_('vector_id', vector_ids).execute()
        
        return self.combine_results(results.matches, metadata)
```

#### Event Streaming (Supabase Realtime)
```python
class EventService:
    async def subscribe_to_events(self, person_id: UUID):
        # Subscribe to real-time events
        channel = await self.supabase.channel('events')
        channel.on(
            'postgres_changes',
            event='INSERT',
            schema='public',
            table='event_log',
            filter=f"person_id=eq.{person_id}",
            callback=self.handle_event
        )
```

### 3. Data Separation Principles

#### Identity Data (Supabase)
- Core user information
- Cross-platform links
- Consent & preferences
- Stable, rarely changes

#### Event Data (Supabase with TimescaleDB)
- All interactions
- System events
- Analytics data
- High volume, time-series

#### Knowledge Data (Pinecone + Supabase)
- Semantic vectors in Pinecone
- Content & metadata in Supabase
- Cross-referenced by vector_id

### 4. Data Flow Examples

#### New User Registration
```python
async def register_user(platform: str, platform_id: str, metadata: dict):
    # Create identity
    person_id = await identity_service.create_identity(metadata)
    
    # Link platform
    await identity_service.create_link(person_id, platform, platform_id)
    
    # Log event
    await event_service.log_event(
        person_id=person_id,
        event_type="registration",
        platform=platform,
        content={"platform_id": platform_id}
    )
    
    return person_id
```

#### Message Processing
```python
async def process_message(platform: str, message: dict):
    # Get identity
    identity = await identity_service.get_identity(
        platform=platform,
        platform_id=message['sender_id']
    )
    
    # Log interaction
    await event_service.log_event(
        person_id=identity.person_id,
        event_type="message",
        platform=platform,
        content=message
    )
    
    # Store as knowledge if relevant
    if should_store_as_knowledge(message):
        await knowledge_service.store_knowledge(
            content=message['text'],
            metadata={
                'person_id': identity.person_id,
                'platform': platform,
                'timestamp': message['timestamp']
            }
        )
```

### 5. Performance Considerations

#### Supabase Optimization
```sql
-- Add indexes for common queries
CREATE INDEX idx_event_log_person_type 
ON event_log (person_id, event_type, created_at DESC);

-- Partition large tables
SELECT create_hypertable(
    'event_log',
    'created_at',
    chunk_time_interval => INTERVAL '1 day'
);
```

#### Pinecone Optimization
```python
# Batch vector operations
async def batch_store_knowledge(items: List[dict]):
    # Prepare vectors
    vectors = []
    metadata = []
    
    for item in items:
        embedding = await self.get_embedding(item['content'])
        vector_id = str(uuid4())
        vectors.append((vector_id, embedding))
        metadata.append({
            'vector_id': vector_id,
            **item['metadata']
        })
    
    # Batch insert to Pinecone
    await self.pinecone.upsert(vectors=vectors)
    
    # Batch insert to Supabase
    await self.supabase.table('knowledge_items').insert(metadata)
```

This strategy:
1. Uses Supabase for structured data and real-time features
2. Uses Pinecone for semantic search capabilities
3. Keeps clear boundaries between data types
4. Maintains high performance at scale
5. Supports real-time features through Supabase

Each component can evolve independently while maintaining clean interfaces with the others.
