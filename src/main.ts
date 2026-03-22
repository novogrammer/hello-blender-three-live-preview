import './style.css'
import * as THREE from 'three'
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js'

const app = document.querySelector<HTMLDivElement>('#app')

if (!app) {
  throw new Error('#app element was not found')
}

const scene = new THREE.Scene()
scene.background = new THREE.Color(0xe7ecf3)

const camera = new THREE.PerspectiveCamera(
  50,
  window.innerWidth / window.innerHeight,
  0.1,
  100,
)

const renderer = new THREE.WebGLRenderer({ antialias: true })
renderer.setPixelRatio(window.devicePixelRatio)
renderer.setSize(window.innerWidth, window.innerHeight)
app.appendChild(renderer.domElement)

const hemisphereLight = new THREE.HemisphereLight(0xffffff, 0x4f5d73, 1.8)
scene.add(hemisphereLight)

const directionalLight = new THREE.DirectionalLight(0xffffff, 2.4)
directionalLight.position.set(4, 6, 8)
scene.add(directionalLight)

const loader = new GLTFLoader()

loader.load(
  '/models/scene.glb',
  (gltf) => {
    const model = gltf.scene
    scene.add(model)

    const box = new THREE.Box3().setFromObject(model)
    const size = box.getSize(new THREE.Vector3())
    const center = box.getCenter(new THREE.Vector3())

    model.position.sub(center)

    const maxSize = Math.max(size.x, size.y, size.z)
    const distance = Math.max(maxSize * 1.8, 2)
    camera.position.set(distance * 0.6, distance * 0.45, distance)
    camera.lookAt(0, 0, 0)
  },
  undefined,
  (error) => {
    console.error('Failed to load /models/scene.glb', error)
  },
)

const clock = new THREE.Clock()

function render() {
  const elapsedTime = clock.getElapsedTime()
  scene.rotation.y = elapsedTime * 0.2
  renderer.render(scene, camera)
  requestAnimationFrame(render)
}

render()

window.addEventListener('resize', () => {
  camera.aspect = window.innerWidth / window.innerHeight
  camera.updateProjectionMatrix()
  renderer.setSize(window.innerWidth, window.innerHeight)
})
