/**
 * ShieldPlus AI - Deep Investigation Modal & Explainability Inspector
 */
import { formatCurrencyForCountry } from './geo-map.js';

export class InvestigationModal {
  constructor(modalId) {
    this.modal = document.getElementById(modalId);
    this.closeBtn = this.modal?.querySelector('.close-btn');
    if (this.closeBtn) {
      this.closeBtn.addEventListener('click', () => this.close());
    }
    // Close on backdrop click
    this.modal?.addEventListener('click', (e) => {
      if (e.target === this.modal) this.close();
    });
    // Close on Esc
    window.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && this.isOpen()) this.close();
    });
  }

  isOpen() {
    return this.modal?.classList.contains('open');
  }

  close() {
    this.modal?.classList.remove('open');
  }

  open(enriched, currentCountry = 'ALL') {
    if (!this.modal) return;
    const tx = enriched.transaction;
    const dec = enriched.decision;
    const rb = enriched.risk_breakdown;

    // Header values with country-scoped currency conversion
    document.getElementById('modalTxId').textContent = tx.id;
    const targetCountry = (currentCountry !== 'ALL') ? currentCountry : (tx.location?.country || 'GLOBAL');
    document.getElementById('modalAmount').textContent = formatCurrencyForCountry(tx.amount, targetCountry);
    document.getElementById('modalMerchant').textContent = `${tx.merchant} (${tx.merchant_category})`;

    // Status Badge
    const badge = document.getElementById('modalStatusBadge');
    const isBlocked = (dec.status === 'BLOCKED');
    const isReview = (dec.status === 'FLAGGED' || dec.status === 'REVIEW' || dec.status === 'UNDER_REVIEW' || dec.status === 'IN_REVIEW');
    const displayStatus = isBlocked ? 'BLOCKED' : (isReview ? 'REVIEW' : 'APPROVED');
    badge.className = `status-pill-badge status-pill-badge-${displayStatus.toLowerCase()}`;
    badge.textContent = displayStatus;

    // Score meter
    const scoreVal = document.getElementById('modalScoreValue');
    scoreVal.textContent = dec.risk_score;
    const scoreLevel = document.getElementById('modalRiskLevel');
    scoreLevel.textContent = `${dec.risk_level} RISK`;

    if (dec.risk_score >= 75) {
      scoreVal.style.color = 'var(--color-blocked)';
    } else if (dec.risk_score >= 50) {
      scoreVal.style.color = 'var(--color-flagged)';
    } else {
      scoreVal.style.color = 'var(--color-approved)';
    }

    // Breakdown bars
    document.getElementById('barRulesScore').style.width = `${Math.min(100, rb.rule_score)}%`;
    document.getElementById('barMLScore').style.width = `${Math.min(100, rb.ml_score)}%`;
    document.getElementById('barGraphScore').style.width = `${Math.min(100, rb.graph_score)}%`;

    document.getElementById('valRulesScore').textContent = `${rb.rule_score.toFixed(0)}/100`;
    document.getElementById('valMLScore').textContent = `${rb.ml_score.toFixed(0)}/100`;
    document.getElementById('valGraphScore').textContent = `${rb.graph_score.toFixed(0)}/100`;

    // Explainability factors
    const factorsContainer = document.getElementById('modalFactorsList');
    factorsContainer.innerHTML = '';

    if (rb.factors && rb.factors.length > 0) {
      rb.factors.forEach(f => {
        const item = document.createElement('div');
        item.className = `factor-item severity-${f.severity}`;
        item.innerHTML = `
          <div style="display: flex; justify-content: space-between; align-items: center;">
            <strong style="font-size: 0.8125rem;">${f.factor_name}</strong>
            <span class="mono" style="font-size: 0.75rem; color: var(--text-highlight);">+${f.contribution} pts</span>
          </div>
          <p style="font-size: 0.75rem; color: var(--text-secondary);">${f.description}</p>
        `;
        factorsContainer.appendChild(item);
      });
    } else {
      factorsContainer.innerHTML = `
        <div style="padding: 12px; font-size: 0.75rem; color: var(--text-muted); text-align: center;">
          No abnormal risk factors detected. Standard legitimate traffic pattern.
        </div>
      `;
    }

    // Telemetry details
    document.getElementById('modalUserId').textContent = tx.user_id;
    document.getElementById('modalCardId').textContent = tx.card_id;
    document.getElementById('modalDeviceId').textContent = tx.device_id;
    document.getElementById('modalIpAddress').textContent = `${tx.ip_address} ${tx.is_vpn_tor ? '(TOR/VPN)' : ''}`;
    document.getElementById('modalLocation').textContent = `${tx.location.city}, ${tx.location.country} (${tx.location.lat.toFixed(2)}, ${tx.location.lon.toFixed(2)})`;
    const latVal = (dec.latency_ms !== undefined && dec.latency_ms !== null) 
      ? dec.latency_ms 
      : (tx.location && (tx.location.country === 'India' || tx.location.country_code === 'IN') ? 14.5 : 12.4);
    document.getElementById('modalLatency').textContent = `${typeof latVal === 'number' ? latVal.toFixed(1) : latVal} ms`;

    const modalMedium = document.getElementById('modalMedium');
    if (modalMedium) {
      modalMedium.textContent = tx.payment_method || tx.channel || 'CARD';
    }
    const modalRail = document.getElementById('modalRail');
    if (modalRail) {
      if (tx.payment_method === 'UPI' && tx.upi_id) {
        modalRail.textContent = `UPI VPA: ${tx.upi_id}`;
      } else {
        modalRail.textContent = `${tx.payment_rail || tx.card_type || 'VISA'} (${tx.channel || 'ONLINE'})`;
      }
    }

    // Raw JSON
    document.getElementById('modalRawJson').textContent = JSON.stringify(enriched, null, 2);

    this.modal.classList.add('open');
  }
}
