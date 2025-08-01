from flask import Flask, request, jsonify, send_from_directory, render_template, redirect, url_for, flash, render_template_string
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from flask_cors import CORS
from auth import auth_bp 
from models import db, User 
from itsdangerous import URLSafeTimedSerializer
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv
import os
import json
import logging
import requests
import openai
import flask_jwt_extended
from datetime import datetime
import re

load_dotenv()

# === Flask App Initialization ===
app = Flask(__name__)

# === App Configurations ===
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("SQLALCHEMY_DATABASE_URI", "postgresql://openq_user:postgres1234@localhost:5432/openquantify")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "super-secret")
db.init_app(app)
jwt = JWTManager(app)
CORS(app)
app.register_blueprint(auth_bp)

# === Logging Configuration ===
logging.basicConfig(level=logging.INFO)

# === Load Products Database ===
PRODUCTS_FILE = "products.json"
try:
    with open(PRODUCTS_FILE, "r") as f:
        PRODUCTS = json.load(f)
except FileNotFoundError:
    logging.error(f"Products file not found: {PRODUCTS_FILE}")
    PRODUCTS = []
except Exception as e:
    logging.error(f"Failed to load products: {e}")
    PRODUCTS = []

# === Set OpenAI API Key ===
openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    logging.warning("OPENAI_API_KEY environment variable not set!")

# === Agent Service Registry ===
AGENT_ENDPOINTS = {
    "tutoring": "http://localhost:5001/tutor",
    "resume": "http://localhost:5002/resume",
    "startup": "http://localhost:5003/startup"
}

# === AI Code Generation Templates ===
AI_TEMPLATES = {
    "gravity": """
// AI-Generated: Gravity Physics System
const gravitySystem = {
    enabled: true,
    strength: -9.81,
    objects: [],
    
    addObject: function(mesh, mass = 1) {
        if (!mesh.physics) {
            mesh.physics = {
                velocity: new THREE.Vector3(0, 0, 0),
                mass: mass,
                grounded: false
            };
        }
        this.objects.push(mesh);
    },
    
    update: function() {
        if (!this.enabled) return;
        
        this.objects.forEach(obj => {
            if (obj.physics) {
                // Apply gravity
                obj.physics.velocity.y += this.strength * 0.001;
                
                // Update position
                obj.position.add(obj.physics.velocity);
                
                // Ground collision
                if (obj.position.y <= 0.5) {
                    obj.position.y = 0.5;
                    obj.physics.velocity.y *= -0.8; // Bounce
                    obj.physics.grounded = true;
                } else {
                    obj.physics.grounded = false;
                }
            }
        });
    },
    
    toggle: function() {
        this.enabled = !this.enabled;
    }
};

// Add gravity to existing meshes
meshObjects.forEach(mesh => gravitySystem.addObject(mesh));

// Update gravity in animation loop
function updateGravity() {
    gravitySystem.update();
    requestAnimationFrame(updateGravity);
}
updateGravity();
""",
    
    "draggable": """
// AI-Generated: Draggable Objects System
const dragSystem = {
    raycaster: new THREE.Raycaster(),
    mouse: new THREE.Vector2(),
    dragObject: null,
    dragPlane: new THREE.Plane(),
    offset: new THREE.Vector3(),
    
    init: function() {
        const canvas = document.getElementById('meshCanvas');
        canvas.addEventListener('mousedown', this.onMouseDown.bind(this));
        canvas.addEventListener('mousemove', this.onMouseMove.bind(this));
        canvas.addEventListener('mouseup', this.onMouseUp.bind(this));
    },
    
    onMouseDown: function(event) {
        const rect = event.target.getBoundingClientRect();
        this.mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
        this.mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
        
        this.raycaster.setFromCamera(this.mouse, camera);
        const intersects = this.raycaster.intersectObjects(meshObjects);
        
        if (intersects.length > 0) {
            this.dragObject = intersects[0].object;
            this.dragPlane.setFromNormalAndCoplanarPoint(camera.getWorldDirection(new THREE.Vector3()), intersects[0].point);
            this.offset.copy(intersects[0].point).sub(this.dragObject.position);
        }
    },
    
    onMouseMove: function(event) {
        if (!this.dragObject) return;
        
        const rect = event.target.getBoundingClientRect();
        this.mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
        this.mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
        
        this.raycaster.setFromCamera(this.mouse, camera);
        const intersection = new THREE.Vector3();
        this.raycaster.ray.intersectPlane(this.dragPlane, intersection);
        
        if (intersection) {
            this.dragObject.position.copy(intersection.sub(this.offset));
        }
    },
    
    onMouseUp: function(event) {
        this.dragObject = null;
    }
};

dragSystem.init();
""",
    
    "particles": """
// AI-Generated: Particle System
class ParticleSystem {
    constructor(position = new THREE.Vector3(0, 5, 0)) {
        this.particles = [];
        this.position = position;
        this.init();
    }
    
    init() {
        const geometry = new THREE.BufferGeometry();
        const positions = [];
        const colors = [];
        const velocities = [];
        
        const particleCount = 1000;
        
        for (let i = 0; i < particleCount; i++) {
            // Position
            positions.push(
                this.position.x + (Math.random() - 0.5) * 2,
                this.position.y + Math.random() * 2,
                this.position.z + (Math.random() - 0.5) * 2
            );
            
            // Color
            const color = new THREE.Color();
            color.setHSL(Math.random(), 0.7, 0.5);
            colors.push(color.r, color.g, color.b);
            
            // Velocity
            velocities.push(
                (Math.random() - 0.5) * 0.02,
                Math.random() * 0.02,
                (Math.random() - 0.5) * 0.02
            );
        }
        
        geometry.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
        geometry.setAttribute('color', new THREE.Float32BufferAttribute(colors, 3));
        geometry.setAttribute('velocity', new THREE.Float32BufferAttribute(velocities, 3));
        
        const material = new THREE.PointsMaterial({ 
            size: 0.05,
            vertexColors: true,
            transparent: true,
            opacity: 0.8
        });
        
        this.system = new THREE.Points(geometry, material);
        scene.add(this.system);
        
        this.animate();
    }
    
    animate() {
        const positions = this.system.geometry.attributes.position.array;
        const velocities = this.system.geometry.attributes.velocity.array;
        
        for (let i = 0; i < positions.length; i += 3) {
            positions[i] += velocities[i];
            positions[i + 1] += velocities[i + 1];
            positions[i + 2] += velocities[i + 2];
            
            // Reset particles that fall too low
            if (positions[i + 1] < -5) {
                positions[i + 1] = this.position.y + Math.random() * 2;
            }
        }
        
        this.system.geometry.attributes.position.needsUpdate = true;
        requestAnimationFrame(() => this.animate());
    }
}

const particleSystem = new ParticleSystem();
""",
    
    "lighting": """
// AI-Generated: Dynamic Lighting System
const lightingSystem = {
    lights: [],
    
    init: function() {
        // Remove existing lights except ambient
        scene.children = scene.children.filter(child => 
            !(child instanceof THREE.DirectionalLight || child instanceof THREE.SpotLight)
        );
        
        // Add dynamic point lights
        const colors = [0xff0040, 0x0040ff, 0x40ff00, 0xff4000];
        
        for (let i = 0; i < 4; i++) {
            const light = new THREE.PointLight(colors[i], 1, 10);
            light.position.set(
                Math.cos(i * Math.PI / 2) * 3,
                2,
                Math.sin(i * Math.PI / 2) * 3
            );
            
            // Add light helper
            const helper = new THREE.PointLightHelper(light, 0.3);
            scene.add(light);
            scene.add(helper);
            
            this.lights.push({ light, helper, angle: i * Math.PI / 2 });
        }
        
        this.animate();
    },
    
    animate: function() {
        this.lights.forEach((lightObj, index) => {
            lightObj.angle += 0.02;
            lightObj.light.position.set(
                Math.cos(lightObj.angle) * 3,
                2 + Math.sin(lightObj.angle * 2) * 0.5,
                Math.sin(lightObj.angle) * 3
            );
            lightObj.helper.update();
        });
        
        requestAnimationFrame(() => this.animate());
    }
};

lightingSystem.init();
""",
    
    "collision": """
// AI-Generated: Collision Detection System
const collisionSystem = {
    objects: [],
    
    addObject: function(mesh, type = 'sphere') {
        if (!mesh.collision) {
            mesh.collision = {
                type: type,
                radius: this.getBoundingRadius(mesh),
                onCollision: null
            };
        }
        this.objects.push(mesh);
    },
    
    getBoundingRadius: function(mesh) {
        const box = new THREE.Box3().setFromObject(mesh);
        return box.getSize(new THREE.Vector3()).length() / 2;
    },
    
    checkCollisions: function() {
        for (let i = 0; i < this.objects.length; i++) {
            for (let j = i + 1; j < this.objects.length; j++) {
                const objA = this.objects[i];
                const objB = this.objects[j];
                
                const distance = objA.position.distanceTo(objB.position);
                const minDistance = objA.collision.radius + objB.collision.radius;
                
                if (distance < minDistance) {
                    this.handleCollision(objA, objB);
                }
            }
        }
    },
    
    handleCollision: function(objA, objB) {
        // Simple collision response
        const direction = new THREE.Vector3().subVectors(objB.position, objA.position).normalize();
        const force = 0.1;
        
        if (objA.physics) {
            objA.physics.velocity.add(direction.clone().multiplyScalar(-force));
        }
        if (objB.physics) {
            objB.physics.velocity.add(direction.clone().multiplyScalar(force));
        }
        
        // Visual feedback
        objA.material.color.setHex(0xff0000);
        objB.material.color.setHex(0xff0000);
        
        setTimeout(() => {
            objA.material.color.setHex(0x00ff00);
            objB.material.color.setHex(0x00ff00);
        }, 200);
        
        // Trigger callbacks
        if (objA.collision.onCollision) objA.collision.onCollision(objB);
        if (objB.collision.onCollision) objB.collision.onCollision(objA);
    },
    
    update: function() {
        this.checkCollisions();
        requestAnimationFrame(() => this.update());
    }
};

// Add collision to existing meshes
meshObjects.forEach(mesh => collisionSystem.addObject(mesh));
collisionSystem.update();
"""
}

# === Device Integration Templates ===
DEVICE_TEMPLATES = {
    "arduino": {
        "temperature": """
// Arduino Temperature Sensor (DHT22)
#include "DHT.h"
#define DHTPIN 2
#define DHTTYPE DHT22
DHT dht(DHTPIN, DHTTYPE);

void setup() {
    Serial.begin(9600);
    dht.begin();
}

void loop() {
    float temperature = dht.readTemperature();
    float humidity = dht.readHumidity();
    
    if (!isnan(temperature)) {
        Serial.print("Temperature: ");
        Serial.print(temperature);
        Serial.println("°C");
        
        // Send to web interface
        Serial.print("DATA:");
        Serial.print(temperature);
        Serial.print(",");
        Serial.println(humidity);
    }
    
    delay(2000);
}""",
        
        "motion": """
// Arduino Motion Sensor (PIR)
#define PIR_PIN 2
#define LED_PIN 13

void setup() {
    Serial.begin(9600);
    pinMode(PIR_PIN, INPUT);
    pinMode(LED_PIN, OUTPUT);
}

void loop() {
    int motionState = digitalRead(PIR_PIN);
    
    if (motionState == HIGH) {
        digitalWrite(LED_PIN, HIGH);
        Serial.println("MOTION_DETECTED");
        delay(1000);
    } else {
        digitalWrite(LED_PIN, LOW);
    }
    
    delay(100);
}""",
        
        "light": """
// Arduino Light Sensor (LDR)
#define LDR_PIN A0
#define LED_PIN 9

void setup() {
    Serial.begin(9600);
    pinMode(LED_PIN, OUTPUT);
}

void loop() {
    int lightValue = analogRead(LDR_PIN);
    int brightness = map(lightValue, 0, 1023, 0, 255);
    
    analogWrite(LED_PIN, 255 - brightness); // Inverse control
    
    Serial.print("Light: ");
    Serial.print(lightValue);
    Serial.print(" Brightness: ");
    Serial.println(brightness);
    
    delay(500);
}"""
    },
    
    "raspberry": {
        "temperature": """
# Raspberry Pi Temperature Sensor (DS18B20)
import os
import glob
import time

os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'

def read_temp_raw():
    f = open(device_file, 'r')
    lines = f.readlines()
    f.close()
    return lines

def read_temp():
    lines = read_temp_raw()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        return temp_c

while True:
    temperature = read_temp()
    print(f"Temperature: {temperature}°C")
    time.sleep(1)""",
        
        "motion": """
# Raspberry Pi Motion Sensor (PIR)
import RPi.GPIO as GPIO
import time

PIR_PIN = 18
LED_PIN = 24

GPIO.setmode(GPIO.BCM)
GPIO.setup(PIR_PIN, GPIO.IN)
GPIO.setup(LED_PIN, GPIO.OUT)

def motion_detected(channel):
    print("Motion detected!")
    GPIO.output(LED_PIN, GPIO.HIGH)
    time.sleep(1)
    GPIO.output(LED_PIN, GPIO.LOW)

GPIO.add_event_detect(PIR_PIN, GPIO.RISING, callback=motion_detected)

try:
    print("PIR Module ready...")
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Quit")
    GPIO.cleanup()"""
    },
    
    "esp32": {
        "wifi_sensor": """
// ESP32 WiFi Sensor Hub
#include <WiFi.h>
#include <WebServer.h>
#include <ArduinoJson.h>

const char* ssid = "your_wifi";
const char* password = "your_password";

WebServer server(80);

// Sensor pins
#define TEMP_PIN 34
#define LIGHT_PIN 35
#define MOTION_PIN 2

void setup() {
    Serial.begin(115200);
    pinMode(MOTION_PIN, INPUT);
    
    WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED) {
        delay(1000);
        Serial.println("Connecting to WiFi...");
    }
    
    Serial.println("WiFi connected!");
    Serial.print("IP address: ");
    Serial.println(WiFi.localIP());
    
    server.on("/sensors", HTTP_GET, handleSensors);
    server.begin();
}

void loop() {
    server.handleClient();
    delay(10);
}

void handleSensors() {
    DynamicJsonDocument json(1024);
    
    // Read sensors
    int temperature = analogRead(TEMP_PIN);
    int light = analogRead(LIGHT_PIN);
    int motion = digitalRead(MOTION_PIN);
    
    json["temperature"] = map(temperature, 0, 4095, -40, 85);
    json["light"] = map(light, 0, 4095, 0, 100);
    json["motion"] = motion;
    json["timestamp"] = millis();
    
    String response;
    serializeJson(json, response);
    
    server.send(200, "application/json", response);
}"""
    }
}

# === Helper Functions ===
def filter_products(budget, use_case, preferred_specs):
    category_map = {
        "robotics": ["microcontroller", "sensors"],
        "iot": ["sensors", "boards"],
        "ai": ["gpu", "computer"],
        "gaming": ["computer", "graphics"],
        "learning": ["kits", "tools"]
    }
    categories = category_map.get(use_case.lower(), [use_case.lower()])
    filtered = []

    for p in PRODUCTS:
        if p["category"].lower() not in categories:
            continue
        try:
            if float(p["price"]) > float(budget):
                continue
        except ValueError:
            logging.warning(f"Invalid price format for product: {p.get('name')}")
            continue

        if preferred_specs:
            if not all(k in p["specs"] and str(v).lower() in str(p["specs"][k]).lower()
                       for k, v in preferred_specs.items()):
                continue
        filtered.append(p)

    return sorted(filtered, key=lambda x: float(x["price"]) if isinstance(x["price"], (int, float, str)) and str(x["price"]).replace('.', '', 1).isdigit() else 0)

def generate_ai_code(prompt, context=None):
    """Generate JavaScript code using OpenAI based on prompt and context"""
    if not openai.api_key:
        return generate_fallback_code(prompt)
    
    try:
        # Check for template matches first
        prompt_lower = prompt.lower()
        for template_key, template_code in AI_TEMPLATES.items():
            if template_key in prompt_lower:
                return template_code
        
        # Build context-aware system message
        system_message = """You are an expert JavaScript developer specializing in Three.js 3D programming and IoT device integration. 
        Generate clean, working JavaScript code that can be directly injected into a Three.js scene. 
        Always include proper error handling and comments.
        Focus on creating interactive, visually appealing 3D experiences."""
        
        if context:
            if context.get('selectedBoard'):
                system_message += f"\nTarget device: {context['selectedBoard']}."
            if context.get('connectedSensors'):
                system_message += f"\nConnected sensors: {', '.join(context['connectedSensors'])}."
        
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": f"Generate JavaScript code for: {prompt}"}
            ],
            max_tokens=1000,
            temperature=0.3
        )
        
        generated_code = response.choices[0].message.content
        
        # Clean up the response to extract just the code
        if "```javascript" in generated_code:
            generated_code = generated_code.split("```javascript")[1].split("```")[0]
        elif "```" in generated_code:
            generated_code = generated_code.split("```")[1].split("```")[0]
        
        return generated_code.strip()
        
    except Exception as e:
        logging.error(f"OpenAI API error: {e}")
        return generate_fallback_code(prompt)

def generate_fallback_code(prompt):
    """Generate fallback code when OpenAI is not available"""
    prompt_lower = prompt.lower()
    
    if "gravity" in prompt_lower:
        return AI_TEMPLATES["gravity"]
    elif "drag" in prompt_lower:
        return AI_TEMPLATES["draggable"]
    elif "particle" in prompt_lower:
        return AI_TEMPLATES["particles"]
    elif "light" in prompt_lower:
        return AI_TEMPLATES["lighting"]
    elif "collision" in prompt_lower:
        return AI_TEMPLATES["collision"]
    elif "cube" in prompt_lower or "box" in prompt_lower:
        return """
// AI-Generated: Create a rotating cube
const geometry = new THREE.BoxGeometry(1, 1, 1);
const material = new THREE.MeshPhongMaterial({ color: Math.random() * 0xffffff });
const cube = new THREE.Mesh(geometry, material);
cube.position.set(Math.random() * 4 - 2, 1, Math.random() * 4 - 2);
scene.add(cube);
meshObjects.push(cube);

// Add rotation animation
function animateCube() {
    cube.rotation.x += 0.01;
    cube.rotation.y += 0.01;
    requestAnimationFrame(animateCube);
}
animateCube();
"""
    else:
        return f"""
// AI-Generated code for: {prompt}
console.log('AI processing: {prompt}');
// This is a placeholder - OpenAI integration needed for full functionality
"""

# === Flask Routes ===
@app.route("/")
def home():
    try:
        with open("enhanced_ide_frontend.html", "r") as f:
            html = f.read()
        return render_template_string(html)
    except Exception as e:
        return f"Failed to load IDE: {e}", 500

@app.route("/recommend", methods=["POST"])
def recommend():
    try:
        data = request.get_json()
        budget = data.get("budget")
        use_case = data.get("use_case")
        preferred_specs = data.get("preferred_specs", {})

        if budget is None or use_case is None:
            return jsonify({"error": "Missing 'budget' or 'use_case
# === Start the Flask Server ===
if __name__ == "__main__":
    # Ensure database tables are created when the app starts if they don't exist
    with app.app_context():
        db.create_all() # This creates tables defined in models.py

    app.run(host="0.0.0.0", port=5000, debug=True)