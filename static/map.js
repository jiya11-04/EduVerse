import * as THREE from 'three';
import { GLTFLoader } from 'https://cdn.jsdelivr.net/npm/three@0.161/examples/jsm/loaders/GLTFLoader.js';
import { OrbitControls } from 'https://cdn.jsdelivr.net/npm/three@0.161/examples/jsm/controls/OrbitControls.js';

const canvas = document.querySelector("canvas");
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true });
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.setSize(window.innerWidth * 0.75, window.innerHeight * 0.75);
renderer.setClearColor(0x000000, 0);
renderer.setPixelRatio(window.devicePixelRatio);

renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;

document.body.appendChild(renderer.domElement);

const scene = new THREE.Scene();
scene.background = null;

const camera = new THREE.PerspectiveCamera(50, window.innerWidth / window.innerHeight, 1, 500);
camera.position.set(0, 10, 0);
camera.lookAt(0, 0, -10);

const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.enablePan = false;
controls.minDistance = 3;
controls.maxDistance = 10;
controls.minPolarAngle = 0;
controls.maxPolarAngle = Math.PI;
controls.autoRotate = false;
controls.target = new THREE.Vector3(0, 1, 0);
controls.update();

const spotLight = new THREE.SpotLight(0xffffff, 2, 100, 0.22, 1);
spotLight.position.set(0, 25, 0);
spotLight.castShadow = true;
spotLight.shadow.bias = -0.0001;
scene.add(spotLight);

const ambientLight = new THREE.AmbientLight(0x404040, 2);
scene.add(ambientLight);

const directionalLight1 = new THREE.DirectionalLight(0xffffff, 2);
directionalLight1.position.set(10, 10, 0);
scene.add(directionalLight1);

const directionalLight2 = new THREE.DirectionalLight(0xffffff, 2);
directionalLight2.position.set(-10, 10, 0);
scene.add(directionalLight2);

let moonMesh;
const clock = new THREE.Clock();

const loader = new GLTFLoader().setPath('/static/pictures/');
loader.load('map4.gltf', (gltf) => {
  console.log('loading model');
  moonMesh = gltf.scene;

  moonMesh.traverse((child) => {
    if (child.isMesh) {
      child.castShadow = true;
      child.receiveShadow = true;
    }
  });

  moonMesh.position.set(0, 0, -10);
  moonMesh.scale.set(3, 3, 3);
  scene.add(moonMesh);
  controls.target.copy(moonMesh.position);
  controls.update();
}, (xhr) => {
  console.log(`loading ${xhr.loaded / xhr.total * 100}%`);
}, (error) => {
  console.error(error);
});

window.addEventListener('resize', () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});

function animate() {
  requestAnimationFrame(animate);
  controls.update();
  renderer.render(scene, camera);
}
animate();

// --- Classroom Locations ---
const classroomMarkers = {
    "AI": new THREE.Vector3(-1.5, 5, -5),
     "OS": new THREE.Vector3(-3.5, 0.6, -8.5),

    "ML": new THREE.Vector3(-1, 0.6, -11),
    "DS": new THREE.Vector3(3, 0.1, 0),
    "DB": new THREE.Vector3(-3, 0.1, 0),
    "SE": new THREE.Vector3(1, 0.1, 2),
    "CN": new THREE.Vector3(-1, 0.1, 2),
    "WT": new THREE.Vector3(2, 0.1, 4),
    "IOT": new THREE.Vector3(-2, 0.1, 4),
    "CYBER": new THREE.Vector3(0, 0.1, 6),
  };
  
  // --- Reusable Marker and Ring ---
const marker = new THREE.Mesh(
  new THREE.SphereGeometry(0.1),
  new THREE.MeshBasicMaterial({ color: 0xff0000 })
);
marker.visible = false;
scene.add(marker);

let ring = null;

// --- Highlight Effect ---
function highlightClassroom(position) {
  // Move the red dot
  marker.position.copy(position);
  marker.visible = true;

  // Remove existing ring if present
  if (ring) scene.remove(ring);

  // Add new ring
  ring = new THREE.Mesh(
    new THREE.RingGeometry(0.4, 0.5, 32),
    new THREE.MeshBasicMaterial({
      color: 0x00fff7,
      transparent: true,
      opacity: 0.6,
      side: THREE.DoubleSide,
    })
  );
  ring.rotation.x = -Math.PI / 2;
  ring.position.copy(position);
  scene.add(ring);

  // Optional: pulsating animation
  function pulse() {
    if (!ring) return;
    ring.rotation.z += 0.01;
    ring.scale.setScalar(1 + 0.1 * Math.sin(Date.now() * 0.005));
    requestAnimationFrame(pulse);
  }
  pulse();
}

// --- Main Function to Focus Classroom ---
function focusOnClassroom(roomId) {
  const pos = classroomMarkers[roomId];
  if (pos) {
    camera.position.set(pos.x, pos.y + 5, pos.z + 5);
    controls.target.copy(pos);
    controls.update();
    highlightClassroom(pos);
  } else {
    console.warn("Unknown classroom:", roomId);
  }
}

// --- Helper to Get Room from URL ---
function getRoomFromURL() {
  const params = new URLSearchParams(window.location.search);
  return params.get("room");
}

// --- Auto focus on load if URL has room param ---
const targetRoom = getRoomFromURL();
if (targetRoom) {
  focusOnClassroom(targetRoom);
}
