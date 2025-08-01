from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

class User(db.Model):
    """Enhanced User model with project tracking"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False, index=True)
    email = db.Column(db.String(150), unique=True, nullable=False, index=True)
    password = db.Column(db.String(255), nullable=False)
    is_verified = db.Column(db.Boolean, default=False)
    reset_token_sent_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    projects = db.relationship('Project', backref='owner', lazy=True, cascade='all, delete-orphan')
    scenes = db.relationship('Scene', backref='creator', lazy=True, cascade='all, delete-orphan')
    ai_sessions = db.relationship('AISession', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"<User {self.username}>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'is_verified': self.is_verified,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'project_count': len(self.projects),
            'scene_count': len(self.scenes)
        }

class Project(db.Model):
    """Project model for storing complete IDE projects"""
    __tablename__ = 'projects'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    
    # Code and configuration
    code = db.Column(db.Text, nullable=True)
    language = db.Column(db.String(50), default='javascript')
    
    # Hardware configuration
    selected_board = db.Column(db.String(100), nullable=True)
    connected_sensors = db.Column(db.JSON, nullable=True)  # Store as JSON array
    
    # 3D Scene data
    scene_data = db.Column(db.JSON, nullable=True)  # Store Three.js scene as JSON
    mesh_objects = db.Column(db.JSON, nullable=True)  # Store mesh configurations
    
    # Project metadata
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    is_public = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Version control
    version = db.Column(db.String(20), default='1.0.0')
    parent_project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=True)
    
    # Deployment
    deployed_url = db.Column(db.String(500), nullable=True)
    deployment_status = db.Column(db.String(50), default='draft')  # draft, deployed, failed
    
    # Statistics
    view_count = db.Column(db.Integer, default=0)
    like_count = db.Column(db.Integer, default=0)
    
    # Relationships
    versions = db.relationship('Project', backref=db.backref('parent_project', remote_side=[id]))
    
    def __repr__(self):
        return f"<Project {self.name} by {self.owner.username}>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'code': self.code,
            'language': self.language,
            'selected_board': self.selected_board,
            'connected_sensors': self.connected_sensors or [],
            'scene_data': self.scene_data,
            'mesh_objects': self.mesh_objects or [],
            'owner': self.owner.username,
            'is_public': self.is_public,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'version': self.version,
            'deployed_url': self.deployed_url,
            'deployment_status': self.deployment_status,
            'view_count': self.view_count,
            'like_count': self.like_count
        }
    
    def get_connected_sensors_list(self):
        """Get connected sensors as a Python list"""
        if isinstance(self.connected_sensors, str):
            try:
                return json.loads(self.connected_sensors)
            except json.JSONDecodeError:
                return []
        return self.connected_sensors or []
    
    def set_connected_sensors(self, sensors_list):
        """Set connected sensors from a Python list"""
        self.connected_sensors = sensors_list

class Scene(db.Model):
    """Scene model for storing 3D scene configurations"""
    __tablename__ = 'scenes'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    
    #