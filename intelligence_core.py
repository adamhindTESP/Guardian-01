import sqlite3
import json
import time
import random
from typing import Dict, List, Any

# NOTE: The 'benevolence' function is imported from benevolent_robot.py
# and run inside the IPC process to check LLM output.

class SpatialMemory:
    """
    Tier 1 Intelligence: The World Model.
    Provides persistent map and object detection, combining LiDAR (SLAM) 
    and Camera (CV/Depth) data.
    """
    def __init__(self, map_db_path: str = "/var/lib/guardian_01/spatial_map.db"):
        print("💡 Initializing Spatial Memory: World Model Active.")
        
        # SLAM (Simultaneous Localization and Mapping)
        self.occupancy_grid: Dict = {}  # Stores the 2D map from LiDAR
        self.pose: Dict[str, float] = {'x': 0.0, 'y': 0.0, 'theta': 0.0}
        
        # Object Database (For tracking entities like 'weed', 'waste', 'human')
        self.objects: Dict[str, Any] = {}
        self.last_update_time = time.time()
        
    def update(self, sensor_data: Dict):
        """Integrate new data from LiDAR, Camera, and IMU."""
        
        # --- 1. SLAM / Pose Update (Requires ROS/SLAM tool integration) ---
        if 'lidar_scan' in sensor_data:
            # Placeholder for SLAM algorithm: Update occupancy grid based on scan and pose
            # self.occupancy_grid = SLAM.integrate(sensor_data['lidar_scan']) 
            pass 
        
        # --- 2. Object Detection (Requires YOLO/CV integration) ---
        if 'camera_frame' in sensor_data:
            detections = self._detect_objects(sensor_data['camera_frame'])
            for obj in detections:
                self.objects[obj['id']] = obj
        
        self.last_update_time = time.time()
        
    def query_local(self, radius: float = 5.0) -> List[Dict]:
        """Returns detected objects within a given radius of the current pose."""
        # In a real system, this would calculate distances from self.pose
        return list(self.objects.values())

    def _detect_objects(self, frame) -> List[Dict]:
        """Placeholder for computer vision model (e.g., YOLOv8)."""
        # Actual implementation requires running a model on the Pi 5 GPU/NPU
        return [{'id': 'weed_A', 'type': 'weed', 'confidence': 0.95, 'location': (1.2, 0.5)}]


class ExperienceLibrary:
    """
    Tier 1 Intelligence: The Learning System.
    Stores every action, outcome, and Guardian verdict for experience replay.
    """
    def __init__(self, db_path: str = "/var/lib/guardian_01/experiences.db"):
        print("💡 Initializing Experience Library: Memory Active.")
        self.conn = sqlite3.connect(db_path)
        self._create_tables()

    def _create_tables(self):
        """Creates the SQLite table to store experiences."""
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS experiences (
                timestamp REAL,
                observation TEXT,      -- JSON of sensor/world data
                action TEXT,           -- JSON of the proposed plan/skill
                outcome TEXT,          -- JSON of the result (e.g., "weed removed: true")
                success BOOLEAN,       -- Was the goal achieved?
                risk_level REAL        -- Planner's estimated risk
            )
        """)
        self.conn.commit()

    def log_experience(self, observation: Dict, action: Dict, outcome: Dict, success: bool, risk_level: float):
        """Records a completed action cycle."""
        self.conn.execute("""
            INSERT INTO experiences 
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            time.time(),
            json.dumps(observation),
            json.dumps(action),
            json.dumps(outcome),
            success,
            risk_level
        ))
        self.conn.commit()
        print(f"   [MEMORY] Logged experience (Success: {success})")

    def query_similar(self, context: str, limit: int = 5) -> List[Dict]:
        """
        Retrieves past experiences relevant to the current context.
        Used to ground the LLM's reasoning.
        """
        # Simple implementation: searching for keywords in the observation
        query = f"%{context}%"
        cursor = self.conn.execute("""
            SELECT action, outcome, success 
            FROM experiences 
            WHERE observation LIKE ? 
            ORDER BY timestamp DESC 
            LIMIT ?
        """, (query, limit))
        
        # Convert results to list of dictionaries for the LLM prompt
        results = []
        for row in cursor:
            results.append({
                'action': json.loads(row[0]),
                'outcome': json.loads(row[1]),
                'success': bool(row[2])
            })
        return results


class LLMPlanner:
    """
    Tier 1 Intelligence: The Reasoning Layer.
    Generates action proposals based on world state and experience, 
    constrained by the Policy Gate.
    """
    # NOTE: The 'benevolence' function would be passed into __init__ 
    # from the main script for the VETO check.
    
    def __init__(self, experience_library: ExperienceLibrary, policy_gate_check: callable):
        print("💡 Initializing LLM Planner: Reasoning Active.")
        self.experiences = experience_library
        self.policy_gate_check = policy_gate_check
        # Placeholder for Ollama API client on the Pi 5
        # self.llm_client = Ollama("http://localhost:11434") 
        self.model_name = "llama3.3:8b" # Target model for local execution

    def _generate_plan_via_llm(self, prompt: str) -> Dict:
        """
        Simulates sending a request to the local Ollama LLM and receiving JSON.
        """
        # Placeholder for actual LLM API call
        print(f"   [LLM] Generating plan with {self.model_name}...")
        
        # SIMULATED LLM RESPONSE for 'weed_A'
        return {
            "action": "Use skill 'pull_gentle' at location (1.2, 0.5) to remove weed.",
            "skill_name": "pull_gentle",
            "reasoning": "Past experience shows gentle pull is successful for this type of plant.",
            "estimated_risk": random.uniform(0.01, 0.05),
            "estimated_dignity": 0.85
        }

    def plan_action(self, observation: Dict, goal: str) -> Dict:
        """
        The core planning loop: reason, check, and refine.
        """
        context = observation.get('context', goal)
        similar_experiences = self.experiences.query_similar(context)
        
        # --- 1. REASONING (The LLM Call) ---
        prompt = self._build_prompt(observation, goal, similar_experiences)
        plan = self._generate_plan_via_llm(prompt) # First attempt
        
        # --- 2. VETO CHECK (The Guardian Policy Gate) ---
        verdict = self.policy_gate_check(plan)
        
        if verdict['status'] == 'VETO':
            print(f"   [VETO] Policy Gate rejected plan: {verdict['reason']}")
            
            # --- 3. REFINEMENT LOOP (LLM must self-correct) ---
            # In a real system, the LLM is prompted again with the VETO reason
            # to generate a safer plan. For this stub, we return the veto.
            raise ValueError(f"Plan Vetoed by Policy Gate: {verdict['reason']}")
            
        print("   [APPROVE] Plan approved by Policy Gate.")
        return plan

    def _build_prompt(self, observation, goal, experiences) -> str:
        """Constructs the grounding prompt for the LLM."""
        return f"""
        GOAL: {goal}
        OBSERVATION: {observation}
        PAST EXPERIENCES (for grounding): {json.dumps(experiences)}
        ... [Detailed instructions for JSON output format] ...
        """

