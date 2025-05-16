import React, { useEffect, useRef } from 'react';
import * as THREE from 'three';

const ThreeD = () => {
  const mountRef = useRef(null);

  useEffect(() => {
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(75, window.innerWidth / 300, 0.1, 1000);
    const renderer = new THREE.WebGLRenderer();
    renderer.setSize(window.innerWidth, 300);
    mountRef.current.appendChild(renderer.domElement);

    // Add terrain
    const geometry = new THREE.PlaneGeometry(100, 100, 32, 32);
    const material = new THREE.MeshBasicMaterial({ color: 0x00ff00, wireframe: true });
    const terrain = new THREE.Mesh(geometry, material);
    scene.add(terrain);

    // Add building (representing a relief center)
    const buildingGeometry = new THREE.BoxGeometry(10, 20, 10);
    const buildingMaterial = new THREE.MeshBasicMaterial({ color: 0xff0000 });
    const building = new THREE.Mesh(buildingGeometry, buildingMaterial);
    building.position.set(0, 10, 0);
    scene.add(building);

    camera.position.z = 50;

    const animate = () => {
      requestAnimationFrame(animate);
      terrain.rotation.x += 0.01;
      renderer.render(scene, camera);
    };
    animate();

    return () => {
      mountRef.current.removeChild(renderer.domElement);
    };
  }, []);

  return <div ref={mountRef} id="three-d" />;
};

export default ThreeD;