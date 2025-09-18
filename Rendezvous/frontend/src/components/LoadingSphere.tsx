import React, { useRef, useEffect } from 'react';
import { Canvas, useThree } from '@react-three/fiber';
import { Points, PointMaterial } from '@react-three/drei';
import * as THREE from 'three';
import { gsap } from 'gsap';

const AnimatedPointCloudSphere = ({ onAnimationComplete }) => {
  const ref = useRef<THREE.Points>(null!);
  const materialRef = useRef<any>(null!);
  const { camera } = useThree();

  useEffect(() => {
    const tl = gsap.timeline({ onComplete: onAnimationComplete });

    // Animate camera and points
    tl.to(camera.position, {
      z: 0,
      duration: 2.5,
      ease: 'power3.inOut',
    })
    .to(ref.current.rotation, {
      x: 'random(-0.5, 0.5)',
      y: 'random(-0.5, 0.5)',
      duration: 2.5,
      ease: 'power3.inOut',
    }, '<')
    .to(materialRef.current, {
      opacity: 0,
      duration: 1.5,
      ease: 'power3.inOut',
    }, '-=1.5');

  }, [camera, onAnimationComplete]);


  const points = React.useMemo(() => {
    const sphere = new THREE.SphereGeometry(1.5, 48, 48);
    // Always return as Float32Array
    const arr = sphere.attributes.position.array;
    return (arr instanceof Float32Array) ? arr : new Float32Array(arr);
  }, []);

  return (
    <Points ref={ref} positions={points} stride={3} frustumCulled={false}>
      <PointMaterial
        ref={materialRef}
        transparent
        color="#00bcd4"
        size={0.015}
        sizeAttenuation={true}
        dithering={false}
        opacity={1}
      />
    </Points>
  );
};

const LoadingSphere = ({ onAnimationComplete }) => {
  return (
    <Canvas camera={{ position: [0, 0, 3] }}>
      <AnimatedPointCloudSphere onAnimationComplete={onAnimationComplete} />
    </Canvas>
  );
};

export default LoadingSphere;