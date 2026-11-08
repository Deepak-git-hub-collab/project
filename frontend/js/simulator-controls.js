/**
 * ShieldPlus AI - Attack Simulation & Policy Control Manager
 */
const API_BASE = (() => {
  if (typeof window === 'undefined') return '';
  const port = window.location.port;
  if (port === '5500' || port === '3000') {
    return `${window.location.protocol}//${window.location.hostname || '127.0.0.1'}:8000`;
  }
  return '';
})();

function apiUrl(path) {
  if (!path.startsWith('/')) path = '/' + path;
  return `${API_BASE}${path}`;
}

export class SimulatorControls {
  constructor(showToast, streamManager = null) {
    this.showToast = showToast;
    this.streamManager = streamManager;
    this.initAttackButtons();
    this.initStreamControls();
    this.loadRules();
  }

  initAttackButtons() {
    const attackBtns = document.querySelectorAll('[data-scenario]');
    attackBtns.forEach(btn => {
      btn.addEventListener('click', async () => {
        const scenario = btn.getAttribute('data-scenario');
        btn.style.opacity = '0.6';
        btn.disabled = true;

        // 1. Immediately inject attack transactions into the stream manager
        if (this.streamManager) {
          this.streamManager.simulateAttack(scenario);
        }

        // 2. Also try backend API if online
        try {
          await fetch(apiUrl('/api/simulator/attack'), {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ scenario, count: 5 })
          });
        } catch (err) { }

        const titles = {
          IMPOSSIBLE_TRAVEL: 'Impossible Travel (>800km/h)',
          RAPID_CARDING: 'Carding Micro-Probe',
          MULE_RING: 'Mule Ring Syndicate',
          UPI_COLLECT_FRAUD: 'UPI Collect Scam',
          BURST_VELOCITY: 'Rapid Burst Surge'
        };

        this.showToast(`🚨 Infiltration Simulated: ${titles[scenario] || scenario}`, 'danger');

        setTimeout(() => {
          btn.style.opacity = '1';
          btn.disabled = false;
        }, 700);
      });
    });
  }

  initStreamControls() {
    const toggleBtn = document.getElementById('btnStreamToggle');
    const rateSlider = document.getElementById('sliderStreamRate');
    const rateDisplay = document.getElementById('txtStreamRate');

    if (rateSlider && rateDisplay) {
      rateSlider.addEventListener('input', async (e) => {
        const val = parseFloat(e.target.value);
        rateDisplay.textContent = `${val.toFixed(1)} TPS`;

        if (this.streamManager) {
          this.streamManager.setRate(val);
        }

        try {
          await fetch(apiUrl('/api/simulator/rate'), {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ tps: val })
          });
        } catch (err) { }
      });
    }

    if (toggleBtn) {
      toggleBtn.addEventListener('click', async () => {
        const isRunning = toggleBtn.getAttribute('data-running') === 'true';
        const newRunning = !isRunning;
        toggleBtn.setAttribute('data-running', newRunning ? 'true' : 'false');
        toggleBtn.innerHTML = newRunning ? '⏸ Pause Feed' : '▶ Resume Feed';

        if (this.streamManager) {
          this.streamManager.isPaused = !newRunning;
        }

        try {
          const endpoint = newRunning ? apiUrl('/api/simulator/start') : apiUrl('/api/simulator/stop');
          await fetch(endpoint, { method: 'POST' });
        } catch (err) { }

        this.showToast(newRunning ? 'Live transaction feed running' : 'Live transaction feed paused', 'info');
      });
    }
  }

  async loadRules() {
    const rulesList = document.getElementById('rulesListContainer');
    if (!rulesList) return;

    try {
      const res = await fetch(apiUrl('/api/rules'));
      if (!res.ok) return;
      const rules = await res.json();

      rulesList.innerHTML = '';
      rules.forEach(rule => {
        const item = document.createElement('div');
        item.className = 'rule-item';
        item.innerHTML = `
          <div class="rule-info">
            <span class="rule-name">${rule.name}</span>
            <span class="rule-desc">${rule.description}</span>
          </div>
          <label class="switch">
            <input type="checkbox" id="switch_${rule.id}" ${rule.enabled ? 'checked' : ''}>
            <span class="slider-toggle"></span>
          </label>
        `;
        rulesList.appendChild(item);

        const checkbox = item.querySelector(`#switch_${rule.id}`);
        checkbox.addEventListener('change', async (e) => {
          const enabled = e.target.checked;
          try {
            await fetch(apiUrl(`/api/rules/${rule.id}`), {
              method: 'PATCH',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ enabled })
            });
            this.showToast(`Policy updated: ${rule.name} is now ${enabled ? 'ENABLED' : 'DISABLED'}`, 'info');
          } catch (err) {
            e.target.checked = !enabled;
            this.showToast('Failed to update rule policy', 'warning');
          }
        });
      });
    } catch (err) { }
  }
}
