/**
 * AETHELGARD: Interactive 3D Consequence Visualizer (Three.js WebGL Engine)
 * Human-Friendly Interactive Architecture:
 * - 4 Core Infrastructure Spheres: Users & Accounts, Money & Billing, System Settings, Outbound Emails
 * - 4 External Service Gateways: Security Shield, API Ingress, Stripe Rail, Email Relay
 * - 3D Precision Consequence Dial with Animated Rotating Indicator
 * - Expanding Dynamic Shockwave Toruses on Causal Impact
 * - Smooth Node Auto-Lock Animation on Safe Fix
 * - Mouse Drag Orbit & Scroll Zoom Controls
 * - Strict Monochromatic Palette: #FCF8F8, #FBEFEF, #F9DFDF, #F5AFAF, #2B1919
 */

(function () {
  'use strict';

  class BlastRadiusCanvas3D {
    constructor(containerId) {
      this.container = document.getElementById(containerId);
      if (!this.container) return;

      this.currentScore = 0.0;
      this.targetScore = 0.0;
      this.affectedNodeIds = [];
      this.shockwaves = [];
      this.nodeMeshes = {};
      this.edgeLines = [];
      this.selectedNodeId = null;
      this.hoveredNodeId = null;
      this.isSafeLocked = false;
      this.targetCameraPos = null;
      this.targetCameraLookAt = new THREE.Vector3(0, 0, 0);
      this.currentCameraLookAt = new THREE.Vector3(0, 0, 0);

      // Monochromatic Blush-Porcelain Editorial Palette Constants
      this.COLOR_BG = 0xFCF8F8;       // Blush Porcelain Primary Background
      this.COLOR_SURFACE = 0xFBEFEF;  // Secondary Surface
      this.COLOR_CARD = 0xF9DFDF;     // Card Tertiary Base Mesh
      this.COLOR_CORAL = 0xF5AFAF;    // Brand Accent Coral Shockwave & Node Pulse
      this.COLOR_INK = 0x2B1919;      // Deep Rose-Espresso Ink Structural Wireframes & Ticks
      this.COLOR_MUTED = 0x6E4747;    // Muted Rose-Espresso Connecting Rails

      this.initThree();
      this.buildTopologyGraph();
      this.buildMechanicalDial();
      this.setupInteraction();
      this.animate();
    }

    initThree() {
      const width = this.container.clientWidth || 800;
      const height = this.container.clientHeight || 450;

      // Scene
      this.scene = new THREE.Scene();
      this.scene.background = new THREE.Color(this.COLOR_BG);
      this.scene.fog = new THREE.FogExp2(this.COLOR_BG, 0.005);

      // Camera
      this.camera = new THREE.PerspectiveCamera(45, width / height, 1, 1000);
      this.setCameraPerspective('ISOMETRIC');

      // Renderer (Pure WebGL with explicit clear color matching blush porcelain)
      this.renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false });
      this.renderer.setClearColor(0xFCF8F8, 1);
      this.renderer.setSize(width, height);
      this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
      this.container.appendChild(this.renderer.domElement);

      // Ambient & Directional Lighting
      const ambientLight = new THREE.AmbientLight(this.COLOR_BG, 0.95);
      this.scene.add(ambientLight);

      const dirLight = new THREE.DirectionalLight(0xFFFFFF, 0.75);
      dirLight.position.set(40, 70, 50);
      this.scene.add(dirLight);

      // Architectural Base Grid (Deep Rose-Espresso / Card Tertiary Track)
      const gridHelper = new THREE.GridHelper(180, 24, this.COLOR_INK, this.COLOR_CARD);
      gridHelper.position.y = -24;
      this.scene.add(gridHelper);

      // Dynamic Resizing with ResizeObserver
      const updateSize = () => {
        if (!this.container || !this.renderer || !this.camera) return;
        const w = this.container.clientWidth || 800;
        const h = this.container.clientHeight || 450;
        this.camera.aspect = w / h;
        this.camera.updateProjectionMatrix();
        this.renderer.setSize(w, h);
      };
      window.addEventListener('resize', updateSize);
      if (typeof ResizeObserver !== 'undefined') {
        this.resizeObserver = new ResizeObserver(updateSize);
        this.resizeObserver.observe(this.container);
      }
    }

    buildTopologyGraph() {
      // 8 Concrete Infrastructure Entities with Human-Friendly Descriptions
      this.nodeData = [
        {
          id: 'enterprise_accounts',
          friendlyName: 'Users & Accounts',
          role: 'Customer Directory',
          type: 'DATABASE',
          x: -18, y: 8, z: -16,
          desc: '16 paying enterprise accounts and contracts.',
          dangerMsg: '⚠️ 16 customer accounts will be wiped out!',
          safeMsg: '✓ Safe: 0 customer accounts harmed.'
        },
        {
          id: 'payment_ledger',
          friendlyName: 'Money & Payments',
          role: 'Ledger Records',
          type: 'DATABASE',
          x: 6, y: -4, z: 2,
          desc: 'Settled transaction balances & escrow records.',
          dangerMsg: '⚠️ Payments & settlement balances will be lost!',
          safeMsg: '✓ Safe: $0 financial loss detected.'
        },
        {
          id: 'service_configs',
          friendlyName: 'System Settings',
          role: 'Security Policies',
          type: 'DATABASE',
          x: -10, y: 20, z: 16,
          desc: 'Access gates, encryption keys, and rate limits.',
          dangerMsg: '⚠️ Core authentication rules altered!',
          safeMsg: '✓ Safe: All 10 security settings intact.'
        },
        {
          id: 'outbound_mail_queue',
          friendlyName: 'Outbound Emails',
          role: 'Client Messages',
          type: 'DATABASE',
          x: 26, y: 10, z: -16,
          desc: 'Queued customer announcements and receipts.',
          dangerMsg: '⚠️ Secret API key leaked in email body!',
          safeMsg: '✓ Safe: Zero credentials or private data leaked.'
        },
        {
          id: 'AUTH_GATEWAY',
          friendlyName: 'Security Gate',
          role: 'Authentication',
          type: 'GATEWAY',
          x: -56, y: 4, z: -10,
          desc: 'Shield preventing unauthorized intrusion.',
          dangerMsg: '⚠️ Authentication bypassed or compromised!',
          safeMsg: '✓ Safe: Guard shield actively protecting login.'
        },
        {
          id: 'API_GATEWAY_V1',
          friendlyName: 'Traffic Router',
          role: 'Ingress Proxy',
          type: 'GATEWAY',
          x: -42, y: 16, z: 12,
          desc: 'Routes inbound API calls into internal servers.',
          dangerMsg: '⚠️ Inbound traffic limits flooded or altered!',
          safeMsg: '✓ Safe: Inbound routing operating normally.'
        },
        {
          id: 'STRIPE_CONNECTOR',
          friendlyName: 'Bank & Card Rail',
          role: 'Treasury Clearing',
          type: 'SERVICE',
          x: 40, y: -12, z: 14,
          desc: 'Processes bank transfers and credit cards.',
          dangerMsg: '⚠️ Unauthorized refund drain detected!',
          safeMsg: '✓ Safe: Treasury rail balances verified.'
        },
        {
          id: 'SES_SMTP_RELAY',
          friendlyName: 'Email Dispatcher',
          role: 'Mail Server',
          type: 'SERVICE',
          x: 54, y: 14, z: -22,
          desc: 'Delivers notifications to customer inboxes.',
          dangerMsg: '⚠️ Mass unauthorized broadcast in progress!',
          safeMsg: '✓ Safe: Outbound mail dispatch certified safe.'
        }
      ];

      this.nodeGroup = new THREE.Group();
      this.scene.add(this.nodeGroup);

      this.nodeData.forEach(node => {
        let geom;
        if (node.type === 'GATEWAY') {
          geom = new THREE.OctahedronGeometry(4.8, 0);
        } else if (node.type === 'DATABASE') {
          geom = new THREE.IcosahedronGeometry(5.4, 0);
        } else {
          geom = new THREE.BoxGeometry(6.4, 6.4, 6.4);
        }

        // Inner solid body in Card Tertiary (#F9DFDF)
        const mat = new THREE.MeshPhongMaterial({
          color: this.COLOR_CARD,
          shininess: 35,
          flatShading: true
        });
        const mesh = new THREE.Mesh(geom, mat);
        mesh.position.set(node.x, node.y, node.z);
        mesh.userData = node;

        // Outer wireframe shell in Deep Rose-Espresso Ink (#2B1919)
        const wireMat = new THREE.MeshBasicMaterial({
          color: this.COLOR_INK,
          wireframe: true,
          wireframeLinewidth: 1.5
        });
        const wireMesh = new THREE.Mesh(geom, wireMat);
        wireMesh.scale.set(1.12, 1.12, 1.12);
        mesh.add(wireMesh);

        // Subtly orbiting halo ring in Accent Coral (#F5AFAF)
        const ringGeom = new THREE.RingGeometry(6.6, 7.4, 28);
        const ringMat = new THREE.MeshBasicMaterial({
          color: this.COLOR_CORAL,
          side: THREE.DoubleSide,
          transparent: true,
          opacity: 0.75
        });
        const ringMesh = new THREE.Mesh(ringGeom, ringMat);
        ringMesh.rotation.x = Math.PI / 2;
        mesh.add(ringMesh);

        this.nodeGroup.add(mesh);
        this.nodeMeshes[node.id] = { mesh, mat, wireMat, ringMesh, data: node };
      });

      // Directed Causal Connection Lines
      const connections = [
        ['AUTH_GATEWAY', 'API_GATEWAY_V1'],
        ['AUTH_GATEWAY', 'enterprise_accounts'],
        ['API_GATEWAY_V1', 'service_configs'],
        ['API_GATEWAY_V1', 'payment_ledger'],
        ['enterprise_accounts', 'payment_ledger'],
        ['enterprise_accounts', 'outbound_mail_queue'],
        ['payment_ledger', 'STRIPE_CONNECTOR'],
        ['outbound_mail_queue', 'SES_SMTP_RELAY']
      ];

      this.edgesGroup = new THREE.Group();
      this.scene.add(this.edgesGroup);

      connections.forEach(([fromId, toId]) => {
        const fromNode = this.nodeData.find(n => n.id === fromId);
        const toNode = this.nodeData.find(n => n.id === toId);
        if (!fromNode || !toNode) return;

        const p1 = new THREE.Vector3(fromNode.x, fromNode.y, fromNode.z);
        const mid = new THREE.Vector3(
          (fromNode.x + toNode.x) / 2,
          (fromNode.y + toNode.y) / 2 + 3.5,
          (fromNode.z + toNode.z) / 2
        );
        const p2 = new THREE.Vector3(toNode.x, toNode.y, toNode.z);

        const curve = new THREE.QuadraticBezierCurve3(p1, mid, p2);
        const tubeGeom = new THREE.TubeGeometry(curve, 22, 0.45, 6, false);
        const tubeMat = new THREE.MeshBasicMaterial({
          color: this.COLOR_MUTED,
          transparent: true,
          opacity: 0.65
        });
        const tubeMesh = new THREE.Mesh(tubeGeom, tubeMat);
        this.edgesGroup.add(tubeMesh);
        this.edgeLines.push({ tubeMesh, fromId, toId });
      });
    }

    buildMechanicalDial() {
      // 3D Mechanical Precision Gauge Dial (threeui.com style)
      this.dialGroup = new THREE.Group();
      this.dialGroup.position.set(44, 26, -4);
      this.dialGroup.rotation.y = -Math.PI / 6;
      this.scene.add(this.dialGroup);

      // Outer bezel ring in Deep Rose-Espresso (#2B1919)
      const bezelGeom = new THREE.TorusGeometry(10.5, 0.85, 12, 48);
      const bezelMat = new THREE.MeshPhongMaterial({ color: this.COLOR_INK, shininess: 50 });
      const bezelMesh = new THREE.Mesh(bezelGeom, bezelMat);
      this.dialGroup.add(bezelMesh);

      // Dial face disc in Card Tertiary (#F9DFDF)
      const faceGeom = new THREE.CircleGeometry(10.0, 36);
      const faceMat = new THREE.MeshBasicMaterial({ color: this.COLOR_CARD, side: THREE.DoubleSide });
      const faceMesh = new THREE.Mesh(faceGeom, faceMat);
      faceMesh.position.z = -0.2;
      this.dialGroup.add(faceMesh);

      // Inner precision track ring in Card Tertiary (#F9DFDF)
      const trackGeom = new THREE.RingGeometry(7.0, 9.2, 36);
      const trackMat = new THREE.MeshBasicMaterial({ color: this.COLOR_CARD, side: THREE.DoubleSide });
      const trackMesh = new THREE.Mesh(trackGeom, trackMat);
      trackMesh.position.z = 0.05;
      this.dialGroup.add(trackMesh);

      // Active Rotating Risk Arc in Brand Accent Coral (#F5AFAF)
      const arcGeom = new THREE.RingGeometry(7.2, 8.8, 32, 1, Math.PI, Math.PI);
      const arcMat = new THREE.MeshBasicMaterial({
        color: this.COLOR_CORAL,
        side: THREE.DoubleSide,
        transparent: true,
        opacity: 0.85
      });
      this.activeRiskArcMesh = new THREE.Mesh(arcGeom, arcMat);
      this.activeRiskArcMesh.position.z = 0.12;
      this.dialGroup.add(this.activeRiskArcMesh);

      // Graduated ticks around 180° sweep in #2B1919 and #6E4747
      for (let i = 0; i <= 20; i++) {
        const angle = Math.PI - (i / 20) * Math.PI;
        const isMajor = i % 5 === 0;
        const tickLength = isMajor ? 2.0 : 1.0;
        const r1 = 9.2;
        const r2 = r1 - tickLength;

        const x1 = Math.cos(angle) * r1;
        const y1 = Math.sin(angle) * r1;
        const x2 = Math.cos(angle) * r2;
        const y2 = Math.sin(angle) * r2;

        const tickGeom = new THREE.BufferGeometry().setFromPoints([
          new THREE.Vector3(x1, y1, 0.15),
          new THREE.Vector3(x2, y2, 0.15)
        ]);
        const tickMat = new THREE.LineBasicMaterial({
          color: isMajor ? this.COLOR_INK : this.COLOR_MUTED,
          linewidth: isMajor ? 2 : 1
        });
        const tickLine = new THREE.Line(tickGeom, tickMat);
        this.dialGroup.add(tickLine);
      }

      // Indicator Needle Pointer in #2B1919
      const needleShape = new THREE.Shape();
      needleShape.moveTo(-0.45, 0);
      needleShape.lineTo(0.45, 0);
      needleShape.lineTo(0.12, 8.2);
      needleShape.lineTo(0, 8.7);
      needleShape.lineTo(-0.12, 8.2);
      needleShape.closePath();

      const needleGeom = new THREE.ShapeGeometry(needleShape);
      const needleMat = new THREE.MeshBasicMaterial({ color: this.COLOR_INK, side: THREE.DoubleSide });
      this.needleMesh = new THREE.Mesh(needleGeom, needleMat);
      this.needleMesh.position.z = 0.22;
      this.dialGroup.add(this.needleMesh);

      // Center cap in #2B1919
      const capGeom = new THREE.CylinderGeometry(1.3, 1.3, 0.7, 24);
      const capMat = new THREE.MeshPhongMaterial({ color: this.COLOR_INK });
      const capMesh = new THREE.Mesh(capGeom, capMat);
      capMesh.rotation.x = Math.PI / 2;
      capMesh.position.z = 0.32;
      this.dialGroup.add(capMesh);
    }

    setCameraPerspective(preset) {
      if (preset === 'ISOMETRIC') {
        this.camera.position.set(0, 48, 88);
        this.camera.lookAt(0, 0, 0);
      } else if (preset === 'TOPDOWN' || preset === 'RADIAL') {
        this.camera.position.set(0, 95, 8);
        this.camera.lookAt(0, 0, 0);
      } else if (preset === 'CLOSEUP' || preset === 'TIMELINE') {
        this.camera.position.set(0, 14, 76);
        this.camera.lookAt(0, 4, 0);
      }
    }

    setCameraPreset(preset) {
      return this.setCameraPerspective(preset);
    }

    setupInteraction() {
      this.raycaster = new THREE.Raycaster();
      this.mouse = new THREE.Vector2();
      this.isDragging = false;
      this.previousMousePosition = { x: 0, y: 0 };

      const dom = this.renderer.domElement;

      // Mouse Drag Rotation
      dom.addEventListener('mousedown', (e) => {
        this.isDragging = true;
        this.previousMousePosition = { x: e.clientX, y: e.clientY };
      });

      window.addEventListener('mouseup', () => {
        this.isDragging = false;
      });

      dom.addEventListener('mousemove', (e) => {
        const rect = dom.getBoundingClientRect();
        this.mouse.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
        this.mouse.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;

        if (this.isDragging) {
          const deltaX = e.clientX - this.previousMousePosition.x;
          const deltaY = e.clientY - this.previousMousePosition.y;

          const angleY = -deltaX * 0.005;
          this.camera.position.applyAxisAngle(new THREE.Vector3(0, 1, 0), angleY);
          this.camera.position.y += deltaY * 0.2;
          this.camera.lookAt(0, 0, 0);

          this.previousMousePosition = { x: e.clientX, y: e.clientY };
        } else {
          // Hover Raycast
          this.raycaster.setFromCamera(this.mouse, this.camera);
          const meshes = Object.values(this.nodeMeshes).map(n => n.mesh);
          const intersects = this.raycaster.intersectObjects(meshes, false);

          if (intersects.length > 0) {
            dom.style.cursor = 'pointer';
            const hoveredNode = intersects[0].object.userData;
            if (this.hoveredNodeId !== hoveredNode.id) {
              this.hoveredNodeId = hoveredNode.id;
              this.showNodePopover(hoveredNode, e.clientX, e.clientY);
              if (window.onNodeHover3D) {
                window.onNodeHover3D(hoveredNode.id, true);
              }
            }
          } else {
            dom.style.cursor = 'default';
            if (this.hoveredNodeId && !this.selectedNodeId) {
              const oldId = this.hoveredNodeId;
              this.hoveredNodeId = null;
              this.hideNodePopover();
              if (window.onNodeHover3D) {
                window.onNodeHover3D(oldId, false);
              }
            }
          }
        }
      });

      // Scroll Zoom
      dom.addEventListener('wheel', (e) => {
        e.preventDefault();
        const zoomDelta = e.deltaY * 0.08;
        const dir = this.camera.position.clone().normalize();
        this.camera.position.addScaledVector(dir, zoomDelta);
        this.camera.position.clampLength(35, 180);
      });

      // Node Click Selection & Smooth Camera Glide
      dom.addEventListener('click', (e) => {
        if (this.isDragging) return;
        this.raycaster.setFromCamera(this.mouse, this.camera);
        const meshes = Object.values(this.nodeMeshes).map(n => n.mesh);
        const intersects = this.raycaster.intersectObjects(meshes, false);

        if (intersects.length > 0) {
          const node = intersects[0].object.userData;
          this.selectedNodeId = node.id;
          this.showNodePopover(node, e.clientX, e.clientY, true);
          this.glideCameraToNode(node);
          if (window.onNodeHover3D) {
            window.onNodeHover3D(node.id, true);
          }
        } else {
          this.selectedNodeId = null;
          this.hideNodePopover();
        }
      });
    }

    glideCameraToNode(node) {
      if (!node) return;
      const targetVec = new THREE.Vector3(node.x, node.y, node.z);
      const camDir = this.camera.position.clone().sub(targetVec).normalize();
      this.targetCameraPos = targetVec.clone().add(camDir.multiplyScalar(50));
      this.targetCameraLookAt.copy(targetVec);
    }

    resetCamera() {
      this.selectedNodeId = null;
      this.hoveredNodeId = null;
      this.hideNodePopover();
      this.setCameraPerspective('ISOMETRIC');
      this.targetCameraPos = null;
      this.targetCameraLookAt.set(0, 0, 0);
      this.currentCameraLookAt.set(0, 0, 0);
      this.camera.lookAt(0, 0, 0);
    }

    showNodePopover(node, clientX, clientY, isSticky = false) {
      const popover = document.getElementById('node-hud-popover');
      if (!popover) return;

      const isDanger = this.affectedNodeIds.includes(node.id);
      const statusText = isDanger ? node.dangerMsg : node.safeMsg;
      const statusClass = isDanger ? 'status-danger' : 'status-safe';

      popover.innerHTML = `
        <div class="popover-header">
          <strong>${node.friendlyName}</strong>
          <span class="popover-tag">${node.role}</span>
        </div>
        <div class="popover-status ${statusClass}">${statusText}</div>
        <div class="popover-desc">${node.desc}</div>
      `;
      popover.style.display = 'block';

      // Keep inside container bounds
      const containerRect = this.container.getBoundingClientRect();
      let left = clientX - containerRect.left + 16;
      let top = clientY - containerRect.top + 16;

      if (left + 240 > containerRect.width) left = containerRect.width - 250;
      if (top + 120 > containerRect.height) top = containerRect.height - 130;

      popover.style.left = `${Math.max(12, left)}px`;
      popover.style.top = `${Math.max(12, top)}px`;
    }

    hideNodePopover() {
      const popover = document.getElementById('node-hud-popover');
      if (popover && !this.selectedNodeId) {
        popover.style.display = 'none';
      }
    }

    initFromSystemState(stateData) {
      if (!stateData || !stateData.catalog_summary) return;
      const cat = stateData.catalog_summary;
      if (this.nodeMeshes['enterprise_accounts']) {
        this.nodeMeshes['enterprise_accounts'].data.desc = `${cat.enterprise_accounts_count} enterprise accounts, $${(cat.total_arr_usd || 0).toLocaleString()} ARR.`;
      }
      if (this.nodeMeshes['payment_ledger']) {
        this.nodeMeshes['payment_ledger'].data.desc = `${cat.payment_ledger_count} ledger rows, $${(cat.total_ledger_usd || 0).toLocaleString()} volume.`;
      }
      if (this.nodeMeshes['service_configs']) {
        this.nodeMeshes['service_configs'].data.desc = `${cat.service_configs_count} active security policy settings.`;
      }
      if (this.nodeMeshes['outbound_mail_queue']) {
        this.nodeMeshes['outbound_mail_queue'].data.desc = `${cat.outbound_mail_queue_count} queued outbound client communications.`;
      }
    }

    triggerShockwaves(affectedIds, blastScore, recordsMutated = 0, financialExposure = 0) {
      this.isSafeLocked = false;
      this.affectedNodeIds = affectedIds || [];
      this.targetScore = blastScore || 0.0;

      // Dynamic scale proportional to actual row mutations and financial delta
      const dynamicScale = 1.25 + Math.min(0.65, (recordsMutated / 20.0) * 0.35 + (financialExposure / 500000.0) * 0.35);

      // Update node visual highlight: Affected nodes pulse with #F5AFAF & wireframe #2B1919
      Object.entries(this.nodeMeshes).forEach(([id, item]) => {
        if (this.affectedNodeIds.includes(id)) {
          item.mat.color.setHex(this.COLOR_CORAL);
          item.wireMat.color.setHex(this.COLOR_INK);
          item.ringMesh.scale.set(dynamicScale, dynamicScale, dynamicScale);

          // Spawn expanding 3D torus shockwave ring dynamically sized to blast score
          const ringRadius = 3.2 + Math.min(2.0, (blastScore / 100.0) * 1.5);
          const ringGeom = new THREE.TorusGeometry(ringRadius, 0.45, 8, 32);
          const ringMat = new THREE.MeshBasicMaterial({
            color: this.COLOR_CORAL,
            transparent: true,
            opacity: 1.0,
            wireframe: false
          });
          const ring = new THREE.Mesh(ringGeom, ringMat);
          ring.position.set(item.data.x, item.data.y, item.data.z);
          ring.rotation.x = Math.PI / 2;
          this.scene.add(ring);

          // Concentric outer wireframe shockwave ring in #2B1919
          const wireRingGeom = new THREE.TorusGeometry(ringRadius * 1.08, 0.22, 6, 24);
          const wireRingMat = new THREE.MeshBasicMaterial({
            color: this.COLOR_INK,
            transparent: true,
            opacity: 0.9,
            wireframe: true
          });
          const wireRing = new THREE.Mesh(wireRingGeom, wireRingMat);
          wireRing.position.set(item.data.x, item.data.y, item.data.z);
          wireRing.rotation.x = Math.PI / 2;
          this.scene.add(wireRing);

          this.shockwaves.push({
            mesh: ring,
            wireMesh: wireRing,
            scale: 1.0,
            opacity: 1.0
          });
        } else {
          item.mat.color.setHex(this.COLOR_CARD);
          item.wireMat.color.setHex(this.COLOR_INK);
          item.ringMesh.scale.set(1.0, 1.0, 1.0);
        }
      });

      // Update HTML Risk Score Dial Text
      const hudScore = document.getElementById('gauge-score-value');
      if (hudScore) {
        hudScore.innerText = blastScore.toFixed(1);
      }
    }

    animateSafeFormation() {
      // Smoothly lock all nodes into safe balanced state (#F9DFDF solid, #2B1919 wireframe)
      this.isSafeLocked = true;
      this.affectedNodeIds = [];
      this.targetScore = 0.0;

      Object.values(this.nodeMeshes).forEach(item => {
        item.mat.color.setHex(this.COLOR_CARD);
        item.wireMat.color.setHex(this.COLOR_INK);
        item.ringMesh.scale.set(1.0, 1.0, 1.0);
      });

      const hudScore = document.getElementById('gauge-score-value');
      if (hudScore) {
        hudScore.innerText = '0.0';
      }

      this.hideNodePopover();
    }

    resetTopologyState() {
      this.isSafeLocked = false;
      this.affectedNodeIds = [];
      this.targetScore = 0.0;
      Object.values(this.nodeMeshes).forEach(item => {
        item.mat.color.setHex(this.COLOR_CARD);
        item.wireMat.color.setHex(this.COLOR_INK);
        item.ringMesh.scale.set(1.0, 1.0, 1.0);
      });
      const hudScore = document.getElementById('gauge-score-value');
      if (hudScore) {
        hudScore.innerText = '0.0';
      }
      this.hideNodePopover();
    }

    pulseNodes(nodeIds) {
      if (!nodeIds || !nodeIds.length) return;
      nodeIds.forEach(id => {
        const item = this.nodeMeshes[id];
        if (item) {
          item.mat.color.setHex(this.COLOR_CORAL);
          item.ringMesh.scale.set(1.5, 1.5, 1.5);

          const ringGeom = new THREE.TorusGeometry(3.6, 0.4, 8, 32);
          const ringMat = new THREE.MeshBasicMaterial({
            color: this.COLOR_CORAL,
            transparent: true,
            opacity: 1.0
          });
          const ring = new THREE.Mesh(ringGeom, ringMat);
          ring.position.set(item.data.x, item.data.y, item.data.z);
          ring.rotation.x = Math.PI / 2;
          this.scene.add(ring);
          this.shockwaves.push({ mesh: ring, scale: 1.0, opacity: 1.0 });

          if (id === nodeIds[0]) {
            this.glideCameraToNode(item.data);
          }
        }
      });

      setTimeout(() => {
        nodeIds.forEach(id => {
          const item = this.nodeMeshes[id];
          if (item && !this.affectedNodeIds.includes(id)) {
            item.mat.color.setHex(this.COLOR_CARD);
            item.ringMesh.scale.set(1.0, 1.0, 1.0);
          }
        });
      }, 1500);
    }

    animate() {
      requestAnimationFrame(() => this.animate());

      const time = performance.now() * 0.001;

      // Smooth Camera Glide Interpolation
      if (this.targetCameraPos) {
        this.camera.position.lerp(this.targetCameraPos, 0.08);
        this.currentCameraLookAt.lerp(this.targetCameraLookAt, 0.08);
        this.camera.lookAt(this.currentCameraLookAt);
        if (this.camera.position.distanceTo(this.targetCameraPos) < 0.6) {
          this.targetCameraPos = null;
        }
      }

      // Animate subtle node idle floating & ring rotation
      Object.values(this.nodeMeshes).forEach((item, idx) => {
        item.mesh.rotation.y = time * 0.3 + idx * 0.4;
        item.ringMesh.rotation.z = -time * 0.5;
      });

      // Smooth mechanical dial needle spring interpolation
      this.currentScore += (this.targetScore - this.currentScore) * 0.09;
      const needleAngle = (Math.PI / 2) - (this.currentScore / 100.0) * Math.PI;
      if (this.needleMesh) {
        this.needleMesh.rotation.z = needleAngle - Math.PI / 2;
      }

      // Animate active rotating risk arc sweep in #F5AFAF
      if (this.activeRiskArcMesh) {
        const sweepAngle = Math.max(0.01, (this.currentScore / 100.0) * Math.PI);
        this.activeRiskArcMesh.rotation.z = needleAngle;
        this.activeRiskArcMesh.material.opacity = this.currentScore > 0 ? 0.85 : 0.2;
      }

      // Animate expanding shockwave rings in #F5AFAF and #2B1919
      for (let i = this.shockwaves.length - 1; i >= 0; i--) {
        const sw = this.shockwaves[i];
        sw.scale += 0.38;
        sw.opacity -= 0.02;
        sw.mesh.scale.set(sw.scale, sw.scale, sw.scale);
        sw.mesh.material.opacity = Math.max(0, sw.opacity);
        if (sw.wireMesh) {
          sw.wireMesh.scale.set(sw.scale * 1.04, sw.scale * 1.04, sw.scale * 1.04);
          sw.wireMesh.material.opacity = Math.max(0, sw.opacity * 0.85);
        }

        if (sw.opacity <= 0.0) {
          this.scene.remove(sw.mesh);
          sw.mesh.geometry.dispose();
          sw.mesh.material.dispose();
          if (sw.wireMesh) {
            this.scene.remove(sw.wireMesh);
            sw.wireMesh.geometry.dispose();
            sw.wireMesh.material.dispose();
          }
          this.shockwaves.splice(i, 1);
        }
      }

      // Edge pulse animation in #F5AFAF / #2B1919 vs #6E4747
      this.edgeLines.forEach((edge, idx) => {
        const isImpacted = this.affectedNodeIds.includes(edge.fromId) || this.affectedNodeIds.includes(edge.toId);
        if (isImpacted) {
          edge.tubeMesh.material.opacity = 0.55 + Math.sin(time * 6 + idx) * 0.4;
          edge.tubeMesh.material.color.setHex(this.COLOR_CORAL);
        } else {
          edge.tubeMesh.material.opacity = 0.4;
          edge.tubeMesh.material.color.setHex(this.COLOR_MUTED);
        }
      });

      this.renderer.render(this.scene, this.camera);
    }
  }

  window.BlastRadiusCanvas3D = BlastRadiusCanvas3D;
})();
