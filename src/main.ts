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
const clock = new THREE.Clock()
const mixers: THREE.AnimationMixer[] = []
const modelPaths = ['/models/suzanne.glb', '/models/torus.glb']
let pendingModelCount = modelPaths.length
let hasLoadedModel = false

function layoutScene() {
  const loadedModels = scene.children.filter((child) => child.userData.isLoadedModel)

  if (loadedModels.length === 0) {
    return
  }

  const totalBox = new THREE.Box3()

  for (const model of loadedModels) {
    totalBox.expandByObject(model)
  }

  const size = totalBox.getSize(new THREE.Vector3())
  const center = totalBox.getCenter(new THREE.Vector3())

  for (const model of loadedModels) {
    model.position.sub(center)
  }

  const maxSize = Math.max(size.x, size.y, size.z)
  const distance = Math.max(maxSize * 1.8, 2)
  camera.position.set(distance * 0.6, distance * 0.45, distance)
  camera.lookAt(0, 0, 0)
}

for (const path of modelPaths) {
  loader.load(
    path,
    (gltf) => {
      const model = gltf.scene
      model.userData.isLoadedModel = true
      scene.add(model)
      hasLoadedModel = true

      if (gltf.animations.length > 0) {
        const mixer = new THREE.AnimationMixer(model)
        const action = mixer.clipAction(gltf.animations[0])
        action.play()
        mixers.push(mixer)
      }

      pendingModelCount -= 1
      if (pendingModelCount === 0) {
        layoutScene()
      }
    },
    undefined,
    (error) => {
      pendingModelCount -= 1
      console.error(`Failed to load ${path}`, error)

      if (pendingModelCount === 0 && hasLoadedModel) {
        layoutScene()
      }
    },
  )
}

function render() {
  const delta = clock.getDelta()
  for (const mixer of mixers) {
    mixer.update(delta)
  }
  renderer.render(scene, camera)
  requestAnimationFrame(render)
}

render()

window.addEventListener('resize', () => {
  camera.aspect = window.innerWidth / window.innerHeight
  camera.updateProjectionMatrix()
  renderer.setSize(window.innerWidth, window.innerHeight)
})
