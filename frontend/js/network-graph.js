/**
 * ShieldPlus AI - Force-Directed Entity & Mule Ring Visualizer
 */
const API_BASE = (() => {
  if (typeof window === 'undefined') return '';
  const port = window.location.port;
  if (port && port !== '8000') {
    return `${window.location.protocol}//${window.location.hostname || '127.0.0.1'}:8000`;
  }
  return '';
})();

function apiUrl(path) {
  if (!path.startsWith('/')) path = '/' + path;
  return `${API_BASE}${path}`;
}

export class NetworkGraph {
  constructor(canvasId) {
    this.canvas = document.getElementById(canvasId);
    if (!this.canvas) return;
    this.ctx = this.canvas.getContext('2d');
    this.nodes = [];
    this.links = [];
    this.nodeMap = new Map();
    this.resize();
    window.addEventListener('resize', () => this.resize());
    this.fetchData();
    setInterval(() => this.fetchData(), 8000);
    this.animate();
  }

  resize() {
    const rect = this.canvas.parentElement.getBoundingClientRect();
    this.canvas.width = rect.width * window.devicePixelRatio;
    this.canvas.height = rect.height * window.devicePixelRatio;
    this.ctx.scale(window.devicePixelRatio, window.devicePixelRatio);
    this.width = rect.width;
    this.height = rect.height;
  }

  async fetchData() {
    try {
      const res = await fetch(apiUrl('/api/metrics/graph'));
      if (!res.ok) return;
      const data = await res.json();
      this.updateGraph(data.nodes, data.links);
    } catch (e) {
      // Fallback placeholder network
    }
  }

  updateGraph(rawNodes, rawLinks) {
    // Preserve existing node positions to prevent visual jitter
    const newNodes = [];
    rawNodes.forEach(n => {
      const existing = this.nodeMap.get(n.id);
      const node = {
        id: n.id,
        label: n.label,
        type: n.type,
        shared_count: n.shared_count,
        is_suspicious: n.is_suspicious,
        x: existing ? existing.x : this.width / 2 + (Math.random() - 0.5) * 120,
        y: existing ? existing.y : this.height / 2 + (Math.random() - 0.5) * 120,
        vx: 0,
        vy: 0
      };
      newNodes.push(node);
      this.nodeMap.set(n.id, node);
    });

    this.nodes = newNodes;
    this.links = rawLinks.map(l => ({
      source: this.nodeMap.get(l.source),
      target: this.nodeMap.get(l.target)
    })).filter(l => l.source && l.target);
  }

  animate() {
    this.ctx.clearRect(0, 0, this.width, this.height);

    // Apply simple spring repulsion forces
    const kRepel = 800;
    const kSpring = 0.05;
    const centerAttract = 0.015;

    for (let i = 0; i < this.nodes.length; i++) {
      const n1 = this.nodes[i];
      // Pull to center
      n1.vx += (this.width / 2 - n1.x) * centerAttract;
      n1.vy += (this.height / 2 - n1.y) * centerAttract;

      // Node repulsion
      for (let j = i + 1; j < this.nodes.length; j++) {
        const n2 = this.nodes[j];
        const dx = n1.x - n2.x;
        const dy = n1.y - n2.y;
        const dist = Math.sqrt(dx * dx + dy * dy) || 1;
        if (dist < 120) {
          const force = kRepel / (dist * dist);
          n1.vx += (dx / dist) * force;
          n1.vy += (dy / dist) * force;
          n2.vx -= (dx / dist) * force;
          n2.vy -= (dy / dist) * force;
        }
      }
    }

    // Link spring attraction
    this.links.forEach(link => {
      const dx = link.target.x - link.source.x;
      const dy = link.target.y - link.source.y;
      link.source.vx += dx * kSpring;
      link.source.vy += dy * kSpring;
      link.target.vx -= dx * kSpring;
      link.target.vy -= dy * kSpring;
    });

    // Update positions & friction
    this.nodes.forEach(n => {
      n.vx *= 0.88;
      n.vy *= 0.88;
      n.x += n.vx;
      n.y += n.vy;
      n.x = Math.max(20, Math.min(this.width - 20, n.x));
      n.y = Math.max(20, Math.min(this.height - 20, n.y));
    });

    // Draw links
    this.links.forEach(l => {
      this.ctx.beginPath();
      this.ctx.moveTo(l.source.x, l.source.y);
      this.ctx.lineTo(l.target.x, l.target.y);
      this.ctx.strokeStyle = (l.source.is_suspicious || l.target.is_suspicious)
        ? 'rgba(224, 108, 117, 0.45)'
        : 'rgba(123, 97, 255, 0.22)';
      this.ctx.lineWidth = (l.source.is_suspicious || l.target.is_suspicious) ? 1.5 : 1;
      this.ctx.stroke();
    });

    // Draw nodes
    this.nodes.forEach(n => {
      this.ctx.beginPath();
      const r = n.type === 'device' ? 6 : 4;
      this.ctx.arc(n.x, n.y, r, 0, Math.PI * 2);

      if (n.is_suspicious) {
        this.ctx.fillStyle = '#E06C75';
        this.ctx.shadowColor = 'rgba(224, 108, 117, 0.6)';
        this.ctx.shadowBlur = 10;
      } else if (n.type === 'device') {
        this.ctx.fillStyle = '#7B61FF';
        this.ctx.shadowColor = 'rgba(123, 97, 255, 0.5)';
        this.ctx.shadowBlur = 8;
      } else {
        this.ctx.fillStyle = '#C3B9FF';
        this.ctx.shadowBlur = 0;
      }
      this.ctx.fill();
      this.ctx.shadowBlur = 0;

      // Label
      if (n.is_suspicious || n.type === 'device') {
        this.ctx.font = '9px monospace';
        this.ctx.fillStyle = n.is_suspicious ? '#F4F3F8' : '#9491A6';
        this.ctx.fillText(n.label, n.x + 8, n.y + 3);
      }
    });

    requestAnimationFrame(() => this.animate());
  }
}
