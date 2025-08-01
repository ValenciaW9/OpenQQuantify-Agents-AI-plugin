import openai
import os
import logging
import json
import re
from typing import Dict, List, Optional, Tuple
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set OpenAI API key
openai.api_key = os.getenv('OPENAI_API_KEY')

class AICodeGenerator:
    """Enhanced AI service for code generation and IDE integration"""
    
    def __init__(self):
        self.api_key = openai.api_key
        self.model = "gpt-4o-mini"  # Fixed model name
        self.templates = self._load_templates()
        
    def _load_templates(self) -> Dict:
        """Load pre-defined code templates for common patterns"""
        return {
            "javascript": {
                "3d_cube": """
// AI-Generated: 3D Rotating Cube
const geometry = new THREE.BoxGeometry(1, 1, 1);
const material = new THREE.MeshPhongMaterial({ 
    color: 0x{color},
    transparent: true,
    opacity: 0.8
});
const cube = new THREE.Mesh(geometry, material);

// Position the cube
cube.position.set({x}, {y}, {z});
cube.castShadow = true;
cube.receiveShadow = true;

// Add to scene
scene.add(cube);
meshObjects.push(cube);

// Animation loop
function animateCube() {{
    cube.rotation.x += {rotation_speed};
    cube.rotation.y += {rotation_speed};
    requestAnimationFrame(animateCube);
}}
animateCube();
""",
                
                "physics_system": """
// AI-Generated: Physics System
class PhysicsEngine {{
    constructor() {{
        this.objects = [];
        this.gravity = new THREE.Vector3(0, -9.81, 0);
        this.enabled = true;
    }}
    
    addObject(mesh, mass = 1, restitution = 0.8) {{
        if (!mesh.physics) {{
            mesh.physics = {{
                velocity: new THREE.Vector3(0, 0, 0),
                acceleration: new THREE.Vector3(0, 0, 0),
                mass: mass,
                restitution: restitution,
                grounded: false
            }};
        }}
        this.objects.push(mesh);
    }}
    
    update(deltaTime = 0.016) {{
        if (!this.enabled) return;
        
        this.objects.forEach(obj => {{
            if (!obj.physics) return;
            
            // Apply gravity
            obj.physics.acceleration.copy(this.gravity);
            
            // Update velocity
            obj.physics.velocity.addScaledVector(obj.physics.acceleration, deltaTime);
            
            // Update position
            obj.position.addScaledVector(obj.physics.velocity, deltaTime);
            
            // Ground collision
            if (obj.position.y <= 0.5) {{
                obj.position.y = 0.5;
                obj.physics.velocity.y *= -obj.physics.restitution;
                obj.physics.grounded = true;
            }}
            
            // Boundary collision
            const boundary = 5;
            if (Math.abs(obj.position.x) > boundary) {{
                obj.physics.velocity.x *= -obj.physics.restitution;
                obj.position.x = Math.sign(obj.position.x) * boundary;
            }}
            if (Math.abs(obj.position.z) > boundary) {{
                obj.physics.velocity.z *= -obj.physics.restitution;
                obj.position.z = Math.sign(obj.position.z) * boundary;
            }}
        }});
    }}
    
    toggle() {{
        this.enabled = !this.enabled;
    }}
}}

// Initialize physics
const physicsEngine = new PhysicsEngine();

// Add physics to existing meshes
meshObjects.forEach(mesh => physicsEngine.addObject(mesh));

// Update physics in animation loop
function updatePhysics() {{
    physicsEngine.update();
    requestAnimationFrame(updatePhysics);
}}
updatePhysics();
""",
                
                "sensor_integration": """
// AI-Generated: Sensor Data Integration
class SensorManager {{
    constructor() {{
        this.sensors = new Map();
        this.updateInterval = 1000; // 1 second
        this.callbacks = new Map();
    }}
    
    addSensor(type, config = {{}}) {{
        const sensor = {{
            type: type,
            value: 0,
            lastUpdate: Date.now(),
            config: config,
            connected: false
        }};
        
        this.sensors.set(type, sensor);
        this.startSimulation(type);
        return sensor;
    }}
    
    startSimulation(type) {{
        const sensor = this.sensors.get(type);
        if (!sensor) return;
        
        const simulate = () => {{
            switch(type) {{
                case 'temperature':
                    sensor.value = 20 + Math.random() * 15; // 20-35°C
                    break;
                case 'motion':
                    sensor.value = Math.random() > 0.8; // 20% chance
                    break;
                case 'light':
                    sensor.value = Math.floor(Math.random() * 1024); // 0-1023
                    break;
                case 'humidity':
                    sensor.value = 30 + Math.random() * 50; // 30-80%
                    break;
                case 'gyroscope':
                    sensor.value = {{
                        x: (Math.random() - 0.5) * 360,
                        y: (Math.random() - 0.5) * 360,
                        z: (Math.random() - 0.5) * 360
                    }};
                    break;
            }}
            
            sensor.lastUpdate = Date.now();
            sensor.connected = true;
            
            // Trigger callbacks
            if (this.callbacks.has(type)) {{
                this.callbacks.get(type).forEach(callback => callback(sensor.value));
            }}
            
            setTimeout(simulate, this.updateInterval);
        }};
        
        simulate();
    }}
    
    onUpdate(sensorType, callback) {{
        if (!this.callbacks.has(sensorType)) {{
            this.callbacks.set(sensorType, []);
        }}
        this.callbacks.get(sensorType).push(callback);
    }}
    
    getSensorValue(type) {{
        const sensor = this.sensors.get(type);
        return sensor ? sensor.value : null;
    }}
}}

// Initialize sensor manager
const sensorManager = new SensorManager();

// Example usage:
// sensorManager.addSensor('temperature');
// sensorManager.onUpdate('temperature', (temp) => {{
//     console.log('Temperature:', temp + '°C');
//     // Update 3D visualization based on temperature
// }});
""",
                
                "ai_controls": """
// AI-Generated: AI-Powered Scene Controls
class AISceneController {{
    constructor(scene, camera, renderer) {{
        this.scene = scene;
        this.camera = camera;
        this.renderer = renderer;
        this.commands = new Map();
        this.setupCommands();
    }}
    
    setupCommands() {{
        // Color commands
        this.commands.set('change_color', (params) => {{
            const color = new THREE.Color(params.color || Math.random() * 0xffffff);
            meshObjects.forEach(mesh => {{
                if (mesh.material) {{
                    mesh.material.color.copy(color);
                }}
            }});
        }});
        
        // Animation commands
        this.commands.set('start_rotation', (params) => {{
            const speed = params.speed || 0.01;
            meshObjects.forEach(mesh => {{
                if (!mesh.aiAnimation) {{
                    mesh.aiAnimation = () => {{
                        mesh.rotation.x += speed;
                        mesh.rotation.y += speed;
                    }};
                }}
            }});
        }});
        
        // Physics commands
        this.commands.set('add_physics', (params) => {{
            meshObjects.forEach(mesh => {{
                if (window.physicsEngine) {{
                    physicsEngine.addObject(mesh, params.mass || 1);
                }}
            }});
        }});
        
        // Lighting commands
        this.commands.set('dramatic_lighting', (params) => {{
            // Remove existing lights
            const lightsToRemove = [];
            this.scene.traverse((child) => {{
                if (child instanceof THREE.DirectionalLight || 
                    child instanceof THREE.PointLight ||
                    child instanceof THREE.SpotLight) {{
                    lightsToRemove.push(child);
                }}
            }});
            lightsToRemove.forEach(light => this.scene.remove(light));
            
            // Add dramatic lighting
            const spotLight = new THREE.SpotLight(0xffffff, 2, 30, Math.PI / 6);
            spotLight.position.set(10, 20, 10);
            spotLight.castShadow = true;
            this.scene.add(spotLight);
            
            const fillLight = new THREE.DirectionalLight(0x4444ff, 0.3);
            fillLight.position.set(-5, 5, -5);
            this.scene.add(fillLight);
        }});
        
        // Camera commands
        this.commands.set('orbit_camera', (params) => {{
            const radius = params.radius || 10;
            const speed = params.speed || 0.01;
            let angle = 0;
            
            const orbitAnimation = () => {{
                angle += speed;
                this.camera.position.x = Math.cos(angle) * radius;
                this.camera.position.z = Math.sin(angle) * radius;
                this.camera.lookAt(0, 0, 0);
                requestAnimationFrame(orbitAnimation);
            }};
            orbitAnimation();
        }});
    }}
    
    executeCommand(commandText) {{
        const processed = this.processNaturalLanguage(commandText);
        
        if (this.commands.has(processed.command)) {{
            this.commands.get(processed.command)(processed.params);
            return `Executed: ${{processed.command}}`;
        }} else {{
            return `Unknown command: ${{commandText}}`;
        }}
    }}
    
    processNaturalLanguage(text) {{
        const textLower = text.toLowerCase();
        
        // Color detection
        if (textLower.includes('color') || textLower.includes('red') || 
            textLower.includes('blue') || textLower.includes('green')) {{
            const colors = {{
                'red': 0xff0000,
                'blue': 0x0000ff,
                'green': 0x00ff00,
                'yellow': 0xffff00,
                'purple': 0xff00ff,
                'orange': 0xff8800
            }};
            
            for (const [colorName, colorValue] of Object.entries(colors)) {{
                if (textLower.includes(colorName)) {{
                    return {{ command: 'change_color', params: {{ color: colorValue }} }};
                }}
            }}
            return {{ command: 'change_color', params: {{}} }};
        }}
        
        // Rotation detection
        if (textLower.includes('rotate') || textLower.includes('spin')) {{
            const speed = textLower.includes('fast') ? 0.05 : 
                         textLower.includes('slow') ? 0.005 : 0.01;
            return {{ command: 'start_rotation', params: {{ speed }} }};
        }}
        
        // Physics detection
        if (textLower.includes('physics') || textLower.includes('gravity') || 
            textLower.includes('fall')) {{
            return {{ command: 'add_physics', params: {{}} }};
        }}
        
        // Lighting detection
        if (textLower.includes('dramatic') || textLower.includes('moody') || 
            textLower.includes('cinematic')) {{
            return {{ command: 'dramatic_lighting', params: {{}} }};
        }}
        
        // Camera detection
        if (textLower.includes('orbit') || textLower.includes('circle')) {{
            return {{ command: 'orbit_camera', params: {{}} }};
        }}
        
        return {{ command: 'unknown', params: {{}} }};
    }}
}}

// Initialize AI controller
const aiController = new AISceneController(scene, camera, renderer);

// Example usage:
// aiController.executeCommand('make everything red');
// aiController.executeCommand('start rotating fast');
// aiController.executeCommand('add physics to objects');
"""
            },
            
            "arduino": {
                "sensor_hub": """
// AI-Generated: Multi-Sensor Hub
#include <ArduinoJson.h>

// Sensor pins
#define TEMP_PIN A0
#define LIGHT_PIN A1
#define MOTION_PIN 2
#define LED_PIN 13

// Sensor data structure
struct SensorData {{
    float temperature;
    int lightLevel;
    bool motionDetected;
    unsigned long timestamp;
}};

SensorData currentData;
unsigned long lastReading = 0;
const unsigned long READING_INTERVAL = 1000; // 1 second

void setup() {{
    Serial.begin(9600);
    pinMode(MOTION_PIN, INPUT);
    pinMode(LED_PIN, OUTPUT);
    
    Serial.println("Multi-Sensor Hub Initialized");
}}

void loop() {{
    if (millis() - lastReading >= READING_INTERVAL) {{
        readSensors();
        sendSensorData();
        lastReading = millis();
    }}
    
    // Handle incoming commands
    if (Serial.available()) {{
        String command = Serial.readStringUntil('\\n');
        processCommand(command);
    }}
}}

void readSensors() {{
    // Read temperature (assuming TMP36)
    int tempReading = analogRead(TEMP_PIN);
    float voltage = tempReading * (5.0 / 1023.0);
    currentData.temperature = (voltage - 0.5) * 100.0;
    
    // Read light level
    currentData.lightLevel = analogRead(LIGHT_PIN);
    
    // Read motion sensor
    currentData.motionDetected = digitalRead(MOTION_PIN);
    
    // Update timestamp
    currentData.timestamp = millis();
    
    // Visual feedback
    if (currentData.motionDetected) {{
        digitalWrite(LED_PIN, HIGH);
    }} else {{
        digitalWrite(LED_PIN, LOW);
    }}
}}

void sendSensorData() {{
    // Create JSON object
    DynamicJsonDocument doc(200);
    doc["temperature"] = currentData.temperature;
    doc["light"] = currentData.lightLevel;
    doc["motion"] = currentData.motionDetected;
    doc["timestamp"] = currentData.timestamp;
    
    // Send JSON data
    serializeJson(doc, Serial);
    Serial.println();
}}

void processCommand(String command) {{
    command.trim();
    
    if (command == "STATUS") {{
        Serial.println("Sensor Hub Status: ONLINE");
    }}
    else if (command == "LED_ON") {{
        digitalWrite(LED_PIN, HIGH);
        Serial.println("LED: ON");
    }}
    else if (command == "LED_OFF") {{
        digitalWrite(LED_PIN, LOW);
        Serial.println("LED: OFF");
    }}
    else if (command == "RESET") {{
        Serial.println("Resetting sensor readings...");
        // Reset any calibration if needed
    }}
    else {{
        Serial.println("Unknown command: " + command);
    }}
}}
""",
                
                "wifi_sensor": """
// AI-Generated: WiFi-Enabled Sensor Station
#include <WiFi.h>
#include <WebServer.h>
#include <ArduinoJson.h>

// WiFi credentials
const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";

// Web server
WebServer server(80);

// Sensor pins
#define TEMP_PIN 34
#define LIGHT_PIN 35
#define MOTION_PIN 2

// Sensor data
struct SensorReading {{
    float temperature;
    int lightLevel;
    bool motionDetected;
    unsigned long timestamp;
}};

SensorReading latestReading;

void setup() {{
    Serial.begin(115200);
    
    // Initialize pins
    pinMode(MOTION_PIN, INPUT);
    
    // Connect to WiFi
    WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED) {{
        delay(1000);
        Serial.println("Connecting to WiFi...");
    }}
    
    Serial.println("WiFi connected!");
    Serial.print("IP address: ");
    Serial.println(WiFi.localIP());
    
    // Setup web server routes
    server.on("/", handleRoot);
    server.on("/sensors", HTTP_GET, handleSensors);
    server.on("/sensors", HTTP_POST, handleSensorUpdate);
    server.onNotFound(handleNotFound);
    
    server.begin();
    Serial.println("HTTP server started");
}}

void loop() {{
    server.handleClient();
    
    // Update sensor readings every 5 seconds
    static unsigned long lastUpdate = 0;
    if (millis() - lastUpdate > 5000) {{
        updateSensorReadings();
        lastUpdate = millis();
    }}
}}

void updateSensorReadings() {{
    // Read temperature (convert ADC to temperature)
    int tempRaw = analogRead(TEMP_PIN);
    latestReading.temperature = map(tempRaw, 0, 4095, -40, 85);
    
    // Read light level
    latestReading.lightLevel = map(analogRead(LIGHT_PIN), 0,