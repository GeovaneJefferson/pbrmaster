// Set up the scene, camera, and renderer
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 0.1, 1000);
camera.position.z = 1;

const renderer = new THREE.WebGLRenderer();
renderer.setSize(300, 300); // Match the size of your div
document.getElementById('three-js-preview').appendChild(renderer.domElement);

// Load textures
const textureLoader = new THREE.TextureLoader();
const colorTexture = textureLoader.load('/media/3ed5615f82d6ae9a37613d27906f7247.jpg'); // Example: /media/3ed5615f82d6ae9a37613d27906f7247.jpg
const normalTexture = textureLoader.load('/media/3ed5615f82d6ae9a37613d27906f7247.jpg');  // /media/3ed5615f82d6ae9a37613d27906f7247_Normal.jpg
const roughnessTexture = textureLoader.load('/media/3ed5615f82d6ae9a37613d27906f7247.jpg'); // Replace with correct URL for roughness
const displacementTexture = textureLoader.load('/media/3ed5615f82d6ae9a37613d27906f7247.jpg'); // Replace with correct URL for displacement

// Create a mesh using the geometry and material
const geometry = new THREE.BoxGeometry();
const material = new THREE.MeshBasicMaterial(
    {
    map: colorTexture,
    normalMap: normalTexture,
    roughnessMap: roughnessTexture,
    displacementMap: displacementTexture,
    displacementScale: 2.436143, // Control the displacement
    roughness: 0.5,
    metalness: 0.5,
    side: THREE.DoubleSide // Render both sides
    }
);
const cube = new THREE.Mesh(geometry, material);
scene.add(cube);

// Handle window resize
window.addEventListener('resize', () => {
    renderer.setSize(window.innerWidth, window.innerHeight);
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
});

function animate() {
    requestAnimationFrame(animate);
    // cube.rotation.x += 0.001;
    cube.rotation.y += 0.001;
    renderer.render(scene, camera);
}

animate();


//
// import * as THREE from "three";
// import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
// import { HDRCubeTextureLoader } from 'three/addons/loaders/HDRCubeTextureLoader.js';
//
// // Scene and Camera setup
// const scene = new THREE.Scene();
// const camera = new THREE.PerspectiveCamera(
//   27,
//   window.innerWidth / window.innerHeight,
//   0.25,
//   50
// );
//
// // Renderer setup
// const renderer = new THREE.WebGLRenderer();
// renderer.setSize(window.innerWidth, window.innerHeight);
// renderer.toneMapping = THREE.ACESFilmicToneMapping; // Set tone mapping
// renderer.toneMappingExposure = 1.25; // Adjust exposure
// renderer.setAnimationLoop(animate);
// document.body.appendChild(renderer.domElement);
//
// // OrbitControls setup
// const controls = new OrbitControls(camera, renderer.domElement);
// controls.minDistance = 3;
// controls.maxDistance = 30;
//
// // HDR environment map loading
// new HDRCubeTextureLoader()
//   .setPath('textures/cube/pisaHDR/')
//   .load(['px.hdr', 'nx.hdr', 'py.hdr', 'ny.hdr', 'pz.hdr', 'nz.hdr'], function (texture) {
//     texture.colorSpace = THREE.SRGBColorSpace;
//     scene.background = texture;
//     scene.environment = texture;
//   });
//
// // Geometry and Texture Loading
// const geometry = new THREE.SphereGeometry(0.8, 64, 32);
// const textureLoader = new THREE.TextureLoader();
//
// const diffuse = textureLoader.load(
//   "https://threejsfundamentals.org/threejs/resources/images/wall.jpg"
// );
// diffuse.colorSpace = THREE.SRGBColorSpace;
// diffuse.wrapS = THREE.RepeatWrapping;
// diffuse.wrapT = THREE.RepeatWrapping;
// diffuse.repeat.set(10, 10);
//
// const normalMap = textureLoader.load(
//   "https://threejsfundamentals.org/threejs/resources/images/wall.jpg"
// );
// normalMap.wrapS = THREE.RepeatWrapping;
// normalMap.wrapT = THREE.RepeatWrapping;
// normalMap.repeat.set(10, 10);
//
// // Material setup
// let material = new THREE.MeshPhysicalMaterial({
//   clearcoat: 1.0,
//   clearcoatRoughness: 0.1,
//   metalness: 0.9,
//   roughness: 0.5,
//   color: 0x0000ff,
//   map: diffuse,
//   normalMap: normalMap,
//   normalScale: new THREE.Vector2(0.15, 0.15),
// });
//
// // Create the mesh and add to the scene
// let mesh = new THREE.Mesh(geometry, material);
// mesh.position.set(-1, 1, 0);
// scene.add(mesh);
//
// // LIGHTS
// const particleLight = new THREE.Mesh(
//   new THREE.SphereGeometry(0.05, 8, 8),
//   new THREE.MeshBasicMaterial({ color: 0xffffff })
// );
// scene.add(particleLight);
//
// // Add PointLight to the particleLight for dynamic lighting
// const pointLight = new THREE.PointLight(0xffffff, 30);
// particleLight.add(pointLight);
//
// // Position the camera
// camera.position.z = 5;
//
// // Animation loop
// function animate() {
//   // Rotate the mesh for some animation
//   mesh.rotation.x += 0.01;
//   mesh.rotation.y += 0.01;
//
//   // Move the particle light to create dynamic lighting
//   const timer = Date.now() * 0.00025;
//   particleLight.position.x = Math.sin(timer * 7) * 3;
//   particleLight.position.y = Math.cos(timer * 5) * 4;
//   particleLight.position.z = Math.cos(timer * 3) * 3;
//
//   renderer.render(scene, camera);
// }
//
// // Handle window resizing
// window.addEventListener("resize", () => {
//   renderer.setSize(window.innerWidth, window.innerHeight);
//   camera.aspect = window.innerWidth / window.innerHeight;
//   camera.updateProjectionMatrix();
// });
