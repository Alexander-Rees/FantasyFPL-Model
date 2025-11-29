"""
RAG Pipeline - Retrieval-Augmented Generation
"""
from app.models.vector_store import get_vector_store
from app.models.llm import get_llm
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class RAGPipeline:
    """RAG pipeline for FPL insights"""
    
    def __init__(self):
        """Initialize RAG pipeline"""
        self.vector_store = get_vector_store()
        self.llm = get_llm()
    
    def retrieve_context(
        self,
        query: str,
        category: str = None,
        gameweek: int = None,
        top_k: int = None
    ) -> list[dict]:
        """
        Retrieve relevant context from vector store
        
        Args:
            query: User query
            category: Filter by category (optional)
            gameweek: Filter by gameweek (optional)
            top_k: Number of results
            
        Returns:
            List of relevant document chunks with metadata
        """
        # Build metadata filter
        where = {}
        if category:
            where["category"] = category
        if gameweek:
            where["gameweek"] = gameweek
        
        # Query vector store
        results = self.vector_store.query(
            query_text=query,
            n_results=top_k or settings.TOP_K_RETRIEVAL,
            where=where if where else None
        )
        
        # Format results
        context_chunks = []
        for i in range(len(results['ids'][0])):
            context_chunks.append({
                'text': results['documents'][0][i],
                'metadata': results['metadatas'][0][i],
                'distance': results['distances'][0][i]
            })
        
        return context_chunks
    
    def generate_response(
        self,
        query: str,
        context_chunks: list[dict],
        system_prompt: str = None,
        user_context: dict = None
    ) -> str:
        """
        Generate response using LLM with retrieved context
        
        Args:
            query: User query
            context_chunks: Retrieved context chunks
            system_prompt: Custom system prompt (optional)
            user_context: User's team context (optional)
            
        Returns:
            Generated response
        """
        # Build context string
        context_text = "\n\n".join([
            f"[Source: {chunk['metadata']['title']} - GW{chunk['metadata']['gameweek']}]\n{chunk['text']}"
            for chunk in context_chunks
        ])
        
        # Build user team context if provided
        team_context_text = ""
        if user_context:
            team_context_text = "\n\n--- USER'S TEAM CONTEXT ---\n"
            
            if user_context.get('team_players'):
                players = user_context['team_players']
                team_context_text += f"Current Squad ({len(players)} players):\n"
                for p in players[:15]:
                    name = p.get('name', 'Unknown')
                    position = p.get('position', '?')
                    team = p.get('team', '?')
                    points = p.get('totalPoints', p.get('total_points', 0))
                    value = p.get('value', 0)
                    team_context_text += f"- {name} ({position}, {team}) - £{value}m, {points} pts\n"
            
            if user_context.get('budget'):
                team_context_text += f"\nRemaining Budget: £{user_context['budget']}m\n"
            
            if user_context.get('free_transfers') is not None:
                team_context_text += f"Free Transfers: {user_context['free_transfers']}\n"
            
            team_context_text += "--- END TEAM CONTEXT ---\n"
        
        # Default system prompt - updated to reference team context
        if system_prompt is None:
            if user_context:
                system_prompt = """You are an expert Fantasy Premier League (FPL) assistant. 
You provide helpful, accurate advice based on expert analysis and data.
Use the provided context to answer questions, but also apply your FPL knowledge.
IMPORTANT: The user has provided their current team. Tailor your advice specifically to their squad, budget, and available transfers.
Be concise and actionable in your recommendations."""
            else:
                system_prompt = """You are an expert Fantasy Premier League (FPL) assistant. 
You provide helpful, accurate advice based on expert analysis and data.
Use the provided context to answer questions, but also apply your FPL knowledge.
Be concise and actionable in your recommendations."""
        
        # Build user message with context
        user_message = f"""Context from FPL experts:

{context_text}
{team_context_text}
Question: {query}

Please provide a helpful answer based on the expert context above."""
        
        # Format prompt for Llama 3.1
        prompt = self.llm.format_prompt(system_prompt, user_message)
        
        # Generate response
        response = self.llm.generate_text(prompt)
        
        return response
    
    def answer_question(
        self,
        query: str,
        category: str = None,
        gameweek: int = None,
        include_sources: bool = True,
        user_context: dict = None
    ) -> dict:
        """
        Complete RAG pipeline: retrieve + generate
        
        Args:
            query: User question
            category: Filter by category
            gameweek: Filter by gameweek
            include_sources: Include source metadata in response
            user_context: User's team context (optional)
            
        Returns:
            Dict with 'answer' and optionally 'sources'
        """
        logger.info(f"RAG query: {query}")
        if user_context:
            player_count = len(user_context.get('team_players', []))
            logger.info(f"User context: {player_count} players, budget={user_context.get('budget')}, transfers={user_context.get('free_transfers')}")
        
        # Retrieve context
        context_chunks = self.retrieve_context(
            query=query,
            category=category,
            gameweek=gameweek
        )
        
        logger.info(f"Retrieved {len(context_chunks)} relevant chunks")
        
        if not context_chunks:
            return {
                "answer": "I don't have enough context to answer that question. Please try rephrasing or check if articles have been ingested.",
                "sources": []
            }
        
        # Generate response with user context
        answer = self.generate_response(query, context_chunks, user_context=user_context)
        
        result = {"answer": answer}
        
        if include_sources:
            result["sources"] = [
                {
                    "title": chunk['metadata']['title'],
                    "gameweek": chunk['metadata']['gameweek'],
                    "category": chunk['metadata']['category'],
                    "url": chunk['metadata']['url'],
                    "relevance": 1 - chunk['distance']  # Convert distance to relevance
                }
                for chunk in context_chunks
            ]
        
        return result


# Global RAG pipeline instance
_rag_instance = None


def get_rag_pipeline() -> RAGPipeline:
    """Get global RAG pipeline instance (singleton pattern)"""
    global _rag_instance
    if _rag_instance is None:
        _rag_instance = RAGPipeline()
    return _rag_instance
