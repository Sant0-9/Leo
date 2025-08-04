#!/usr/bin/env python3
"""
ChromaDB Service for Leo AI Assistant
Handles long-term memory storage and retrieval
"""

import os
import json
from datetime import datetime
from typing import List, Dict, Optional
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import uuid

class ChromaService:
    def __init__(self, persist_directory: str = "./chroma_db"):
        """Initialize ChromaDB service"""
        self.persist_directory = persist_directory
        self.embedding_model = None
        self.client = None
        self.collection = None
        
        try:
            self._initialize_chroma()
            self._initialize_embedding_model()
            print("✅ ChromaDB service initialized successfully")
        except Exception as e:
            print(f"⚠️ ChromaDB initialization failed: {e}")
            print("📝 Long-term memory features will be limited")
    
    def _initialize_chroma(self):
        """Initialize ChromaDB client and collection"""
        try:
            # Create ChromaDB client with persistence
            self.client = chromadb.PersistentClient(path=self.persist_directory)
            
            # Get or create collection for Leo's memory
            self.collection = self.client.get_or_create_collection(
                name="leo_memory",
                metadata={"description": "Long-term memory for Leo AI Assistant"}
            )
            
        except Exception as e:
            print(f"Error initializing ChromaDB: {e}")
            # Fallback to in-memory client
            try:
                self.client = chromadb.Client()
                self.collection = self.client.get_or_create_collection(
                    name="leo_memory",
                    metadata={"description": "Long-term memory for Leo AI Assistant (in-memory)"}
                )
                print("⚠️ Using in-memory ChromaDB (data will not persist)")
            except Exception as fallback_error:
                print(f"Fallback ChromaDB initialization failed: {fallback_error}")
                raise
    
    def _initialize_embedding_model(self):
        """Initialize sentence transformer for embeddings"""
        try:
            # Use a lightweight model for embeddings
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        except Exception as e:
            print(f"Error loading embedding model: {e}")
            print("⚠️ Using basic ChromaDB embeddings")
    
    def health_check(self) -> bool:
        """Check if ChromaDB service is healthy"""
        try:
            if self.client and self.collection:
                # Try to get collection info
                self.collection.count()
                return True
            return False
        except Exception:
            return False
    
    def add_message(self, user_id: str, role: str, content: str, metadata: Optional[Dict] = None) -> str:
        """Add a message to long-term memory"""
        try:
            if not self.collection:
                return "chroma_not_available"
            
            # Create unique ID for the message
            message_id = str(uuid.uuid4())
            
            # Prepare metadata
            message_metadata = {
                "user_id": user_id,
                "role": role,
                "timestamp": datetime.now().isoformat(),
                "type": "chat_message"
            }
            
            if metadata:
                message_metadata.update(metadata)
            
            # Generate embedding if model is available
            if self.embedding_model:
                embedding = self.embedding_model.encode([content])[0].tolist()
                
                self.collection.add(
                    ids=[message_id],
                    embeddings=[embedding],
                    documents=[content],
                    metadatas=[message_metadata]
                )
            else:
                # Use ChromaDB's default embedding
                self.collection.add(
                    ids=[message_id],
                    documents=[content],
                    metadatas=[message_metadata]
                )
            
            return message_id
            
        except Exception as e:
            print(f"Error adding message to ChromaDB: {e}")
            return "error"
    
    def search_similar(self, user_id: str, query: str, limit: int = 10) -> List[Dict]:
        """Search for similar messages in long-term memory"""
        try:
            if not self.collection:
                return []
            
            # Generate query embedding if model is available
            if self.embedding_model:
                query_embedding = self.embedding_model.encode([query])[0].tolist()
                
                results = self.collection.query(
                    query_embeddings=[query_embedding],
                    where={"user_id": user_id},
                    n_results=limit
                )
            else:
                # Use ChromaDB's default query
                results = self.collection.query(
                    query_texts=[query],
                    where={"user_id": user_id},
                    n_results=limit
                )
            
            # Format results
            formatted_results = []
            if results and results['documents']:
                for i, document in enumerate(results['documents'][0]):
                    metadata = results['metadatas'][0][i] if results['metadatas'] else {}
                    distance = results['distances'][0][i] if results['distances'] else 0
                    
                    formatted_results.append({
                        'content': document,
                        'metadata': metadata,
                        'similarity': 1 - distance if distance else 1,  # Convert distance to similarity
                        'timestamp': metadata.get('timestamp', ''),
                        'role': metadata.get('role', 'unknown')
                    })
            
            return formatted_results
            
        except Exception as e:
            print(f"Error searching ChromaDB: {e}")
            return []
    
    def get_recent_memories(self, user_id: str, limit: int = 20) -> List[Dict]:
        """Get recent memories for a user"""
        try:
            if not self.collection:
                return []
            
            # Get all messages for user (ChromaDB doesn't have direct ordering)
            results = self.collection.get(
                where={"user_id": user_id},
                limit=limit * 2  # Get more to sort and limit properly
            )
            
            formatted_results = []
            if results and results['documents']:
                for i, document in enumerate(results['documents']):
                    metadata = results['metadatas'][i] if results['metadatas'] else {}
                    
                    formatted_results.append({
                        'content': document,
                        'metadata': metadata,
                        'timestamp': metadata.get('timestamp', ''),
                        'role': metadata.get('role', 'unknown')
                    })
            
            # Sort by timestamp and limit
            formatted_results.sort(key=lambda x: x['timestamp'], reverse=True)
            return formatted_results[:limit]
            
        except Exception as e:
            print(f"Error getting recent memories: {e}")
            return []
    
    def add_goal_plan(self, user_id: str, goal_data: Dict) -> str:
        """Add a goal and plan to long-term memory"""
        try:
            if not self.collection:
                return "chroma_not_available"
            
            plan_id = str(uuid.uuid4())
            
            # Create searchable content from goal data
            content = f"Goal: {goal_data.get('goal', '')} Plan: {json.dumps(goal_data.get('plan', {}))}"
            
            metadata = {
                "user_id": user_id,
                "type": "goal_plan",
                "goal": goal_data.get('goal', ''),
                "timeline": goal_data.get('timeline', ''),
                "timestamp": datetime.now().isoformat()
            }
            
            if self.embedding_model:
                embedding = self.embedding_model.encode([content])[0].tolist()
                self.collection.add(
                    ids=[plan_id],
                    embeddings=[embedding],
                    documents=[content],
                    metadatas=[metadata]
                )
            else:
                self.collection.add(
                    ids=[plan_id],
                    documents=[content],
                    metadatas=[metadata]
                )
            
            return plan_id
            
        except Exception as e:
            print(f"Error adding goal plan to ChromaDB: {e}")
            return "error"
    
    def search_goals(self, user_id: str, query: str, limit: int = 5) -> List[Dict]:
        """Search for relevant goals and plans"""
        try:
            if not self.collection:
                return []
            
            if self.embedding_model:
                query_embedding = self.embedding_model.encode([query])[0].tolist()
                results = self.collection.query(
                    query_embeddings=[query_embedding],
                    where={"user_id": user_id, "type": "goal_plan"},
                    n_results=limit
                )
            else:
                results = self.collection.query(
                    query_texts=[query],
                    where={"user_id": user_id, "type": "goal_plan"},
                    n_results=limit
                )
            
            formatted_results = []
            if results and results['documents']:
                for i, document in enumerate(results['documents'][0]):
                    metadata = results['metadatas'][0][i] if results['metadatas'] else {}
                    
                    formatted_results.append({
                        'content': document,
                        'metadata': metadata,
                        'goal': metadata.get('goal', ''),
                        'timeline': metadata.get('timeline', ''),
                        'timestamp': metadata.get('timestamp', '')
                    })
            
            return formatted_results
            
        except Exception as e:
            print(f"Error searching goals: {e}")
            return []
    
    def get_memory_stats(self, user_id: str) -> Dict:
        """Get memory statistics for a user"""
        try:
            if not self.collection:
                return {"total_memories": 0, "status": "unavailable"}
            
            # Get all user data
            results = self.collection.get(where={"user_id": user_id})
            
            total_memories = len(results['documents']) if results and results['documents'] else 0
            
            # Count by type
            type_counts = {}
            if results and results['metadatas']:
                for metadata in results['metadatas']:
                    msg_type = metadata.get('type', 'unknown')
                    type_counts[msg_type] = type_counts.get(msg_type, 0) + 1
            
            return {
                "total_memories": total_memories,
                "type_breakdown": type_counts,
                "status": "healthy" if self.health_check() else "error",
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Error getting memory stats: {e}")
            return {"total_memories": 0, "status": "error", "error": str(e)}
    
    def clear_user_memory(self, user_id: str) -> bool:
        """Clear all memories for a specific user"""
        try:
            if not self.collection:
                return False
            
            # Get all user documents
            results = self.collection.get(where={"user_id": user_id})
            
            if results and results['ids']:
                # Delete all user documents
                self.collection.delete(ids=results['ids'])
                return True
            
            return True  # No documents to delete is also success
            
        except Exception as e:
            print(f"Error clearing user memory: {e}")
            return False