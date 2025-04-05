import numpy as np
from sklearn.neighbors import NearestNeighbors
from flask import current_app
from flask_sqlalchemy import SQLAlchemy

# Initialize SQLAlchemy
db = SQLAlchemy()

class RecommendationEngine:
    def __init__(self, app=None):
        self.knowledge_model = None
        self.video_recommender = None
        if app:
            self.init_app(app)
        
    def init_app(self, app):
        """Initialize with Flask app context"""
        with app.app_context():
            self.knowledge_model = self._build_knowledge_model()
            
    def _build_knowledge_model(self):
        """Create a knowledge graph of components and modules"""
        from .models import KnowledgeComponent, ModuleKnowledgeMapping
        
        kcs = KnowledgeComponent.query.all()
        if not kcs:
            current_app.logger.warning("No knowledge components found in database")
            return None
            
        kc_dict = {kc.kc_id: idx for idx, kc in enumerate(kcs)}
        module_kcs = ModuleKnowledgeMapping.query.all()
        
        # Create adjacency matrix
        num_kcs = len(kcs)
        knowledge_graph = np.zeros((num_kcs, num_kcs))
        
        for mk in module_kcs:
            kc_idx = kc_dict[mk.kc_id]
            if mk.parent_kc_id:
                parent_idx = kc_dict[mk.parent_kc_id]
                knowledge_graph[parent_idx][kc_idx] = mk.weight
        
        return knowledge_graph
    
    def initialize_video_recommender(self):
        """Initialize content-based video recommender"""
        from .models import Video
        
        videos = Video.query.all()
        if not videos:
            current_app.logger.warning("No videos found in database")
            return
            
        video_features = []
        
        # Extract features (simplified example)
        for video in videos:
            features = [
                len(video.title.split()),  # Title length
                video.duration / 60 if video.duration else 0,  # Duration in minutes
                1 if video.difficulty_level == 'easy' else 
                2 if video.difficulty_level == 'medium' else 3,
                len(video.description.split()) if video.description else 0
            ]
            video_features.append(features)
        
        # Normalize features
        video_features = np.array(video_features)
        self.video_recommender = NearestNeighbors(n_neighbors=3, metric='cosine')
        self.video_recommender.fit(video_features)
    
    def recommend_videos(self, module_id, user_id):
        """Recommend videos based on user's needs"""
        from .models import Video, UserProgress, ModuleKnowledgeMapping
        
        if not self.video_recommender:
            self.initialize_video_recommender()
            if not self.video_recommender:
                return Video.query.filter_by(module_id=module_id).order_by(Video.sequence_order).limit(3).all()
            
        # Get user's weak areas
        weak_kcs = self._get_weak_knowledge_components(user_id, module_id)
        
        # Get module videos
        module_videos = Video.query.filter_by(module_id=module_id).order_by(Video.sequence_order).all()
        
        # If no weak areas, return default sequence
        if not weak_kcs or not module_videos:
            return module_videos[:3] if module_videos else []
        
        # Find videos that best address weak areas
        video_scores = []
        for video in module_videos:
            score = self._calculate_video_relevance(video, weak_kcs)
            video_scores.append((video, score))
        
        # Sort by relevance and return top 3
        video_scores.sort(key=lambda x: x[1], reverse=True)
        return [v[0] for v in video_scores[:3]]
    
    def _calculate_video_relevance(self, video, weak_kcs):
        """Calculate how well a video addresses weak knowledge components"""
        # In a real implementation, you would use NLP or predefined mappings
        # This is a simplified version
        if not video.description:
            return 0
            
        # Check if video description mentions any weak KC keywords
        score = 0
        for kc_id in weak_kcs:
            # This would actually query the KC name from database
            kc_keyword = f"kc_{kc_id}"  # Placeholder
            if kc_keyword.lower() in video.description.lower():
                score += 1
        return score
    
    def _get_weak_knowledge_components(self, user_id, module_id):
        """Identify knowledge gaps based on assessment results"""
        from .models import UserProgress, ModuleKnowledgeMapping
        
        # Get user's pre-assessment results
        user_results = UserProgress.query.filter_by(
            user_id=user_id,
            module_id=module_id
        ).first()
        
        if not user_results or not user_results.score:
            return []
        
        # Get all KCs for this module
        module_kcs = ModuleKnowledgeMapping.query.filter_by(
            module_id=module_id
        ).all()
        
        # Identify weak KCs (score < 70%)
        weak_kcs = []
        for mk in module_kcs:
            if mk.coverage_level == 'assesses' and user_results.score < 70:
                weak_kcs.append(mk.kc_id)
        
        return weak_kcs
    
    def determine_learning_path(self, user_id, course_id):
        """Decide if user can skip modules based on performance"""
        from .models import UserProgress
        
        completed_modules = UserProgress.query.filter_by(
            user_id=user_id,
            status='completed'
        ).all()
        
        avg_score = np.mean([m.score for m in completed_modules]) if completed_modules else 0
        
        if avg_score > 85:
            return 'advanced'
        elif avg_score > 60:
            return 'standard'
        else:
            return 'remedial'