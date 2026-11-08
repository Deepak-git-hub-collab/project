/**
 * ShieldPlus AI - Real-Time Stream Manager
 * Autonomous resilient event streaming with automatic high-fidelity fallback generator,
 * speed calibration, and interactive attack scenario injector.
 */

const REAL_CITIES = [
  // United States
  { city: 'New York', state: 'New York', country: 'United States', country_code: 'US', lat: 40.71, lon: -74.00 },
  { city: 'Los Angeles', state: 'California', country: 'United States', country_code: 'US', lat: 34.05, lon: -118.24 },
  { city: 'San Francisco', state: 'California', country: 'United States', country_code: 'US', lat: 37.77, lon: -122.41 },
  { city: 'Chicago', state: 'Illinois', country: 'United States', country_code: 'US', lat: 41.87, lon: -87.62 },
  { city: 'Miami', state: 'Florida', country: 'United States', country_code: 'US', lat: 25.76, lon: -80.19 },
  { city: 'Houston', state: 'Texas', country: 'United States', country_code: 'US', lat: 29.76, lon: -95.36 },

  // India
  { city: 'Mumbai', state: 'Maharashtra', country: 'India', country_code: 'IN', lat: 19.07, lon: 72.87 },
  { city: 'Pune', state: 'Maharashtra', country: 'India', country_code: 'IN', lat: 18.52, lon: 73.85 },
  { city: 'Nagpur', state: 'Maharashtra', country: 'India', country_code: 'IN', lat: 21.14, lon: 79.08 },
  { city: 'Bengaluru', state: 'Karnataka', country: 'India', country_code: 'IN', lat: 12.97, lon: 77.59 },
  { city: 'Delhi', state: 'Delhi NCR', country: 'India', country_code: 'IN', lat: 28.61, lon: 77.20 },
  { city: 'Hyderabad', state: 'Telangana', country: 'India', country_code: 'IN', lat: 17.38, lon: 78.48 },
  { city: 'Chennai', state: 'Tamil Nadu', country: 'India', country_code: 'IN', lat: 13.08, lon: 80.27 },
  { city: 'Kolkata', state: 'West Bengal', country: 'India', country_code: 'IN', lat: 22.57, lon: 88.36 },

  // United Kingdom
  { city: 'London', state: 'Greater London', country: 'United Kingdom', country_code: 'GB', lat: 51.50, lon: -0.12 },
  { city: 'Manchester', state: 'Greater Manchester', country: 'United Kingdom', country_code: 'GB', lat: 53.48, lon: -2.24 },
  { city: 'Edinburgh', state: 'Scotland', country: 'United Kingdom', country_code: 'GB', lat: 55.95, lon: -3.18 },
  { city: 'Cardiff', state: 'Wales', country: 'United Kingdom', country_code: 'GB', lat: 51.48, lon: -3.17 },

  // Japan
  { city: 'Tokyo', state: 'Tokyo Prefecture', country: 'Japan', country_code: 'JP', lat: 35.67, lon: 139.65 },
  { city: 'Osaka', state: 'Osaka Prefecture', country: 'Japan', country_code: 'JP', lat: 34.69, lon: 135.50 },
  { city: 'Kyoto', state: 'Kyoto Prefecture', country: 'Japan', country_code: 'JP', lat: 35.01, lon: 135.76 },
  { city: 'Yokohama', state: 'Kanagawa', country: 'Japan', country_code: 'JP', lat: 35.44, lon: 139.63 },

  // Germany
  { city: 'Frankfurt', state: 'Hesse', country: 'Germany', country_code: 'DE', lat: 50.11, lon: 8.68 },
  { city: 'Berlin', state: 'Berlin', country: 'Germany', country_code: 'DE', lat: 52.52, lon: 13.40 },
  { city: 'Munich', state: 'Bavaria', country: 'Germany', country_code: 'DE', lat: 48.13, lon: 11.58 },
  { city: 'Cologne', state: 'North Rhine-Westphalia', country: 'Germany', country_code: 'DE', lat: 50.93, lon: 6.96 },

  // Other Regions
  { city: 'São Paulo', state: 'Sao Paulo State', country: 'Brazil', country_code: 'BR', lat: -23.55, lon: -46.63 },
  { city: 'Rio de Janeiro', state: 'Rio de Janeiro State', country: 'Brazil', country_code: 'BR', lat: -22.90, lon: -43.17 },
  { city: 'Toronto', state: 'Ontario', country: 'Canada', country_code: 'CA', lat: 43.65, lon: -79.38 },
  { city: 'Sydney', state: 'New South Wales', country: 'Australia', country_code: 'AU', lat: -33.86, lon: 151.20 },
  { city: 'Dubai', state: 'Dubai Emirate', country: 'United Arab Emirates', country_code: 'AE', lat: 25.20, lon: 55.27 },
  { city: 'Singapore', state: 'Central Region', country: 'Singapore', country_code: 'SG', lat: 1.35, lon: 103.81 },
  { city: 'Paris', state: 'Ile-de-France', country: 'France', country_code: 'FR', lat: 48.85, lon: 2.35 }
];

const MERCHANTS = [
  { name: 'Amazon Web Services', cat: 'CLOUD_SERVICES' },
  { name: 'Apple Store Digital', cat: 'ELECTRONICS' },
  { name: 'Uber Rides & Eats', cat: 'TRANSPORT' },
  { name: 'Walmart Supercenter', cat: 'RETAIL' },
  { name: 'Target Direct', cat: 'RETAIL' },
  { name: 'Binance Pay Gateway', cat: 'CRYPTO' },
  { name: 'Netflix Subscription', cat: 'STREAMING' },
  { name: 'Delta Air Lines', cat: 'TRAVEL' },
  { name: 'Steam Games Store', cat: 'DIGITAL_GOODS' },
  { name: 'Sephora Cosmetics', cat: 'LUXURY_GOODS' }
];

const MEDIUMS = ['CARD', 'UPI', 'NET_BANKING', 'WALLET', 'ATM_CASH', 'CRYPTO'];
const USERS = ['usr_ralph_e', 'usr_theresa_w', 'usr_devon_l', 'usr_cody_f', 'usr_savannah_n', 'usr_eleanor_p', 'usr_jerome_b', 'usr_bessie_c'];

export class StreamManager {
  constructor() {
    this.socket = null;
    this.listeners = [];
    this.isPaused = false;
    this.buffer = [];
    this.maxBufferSize = 250;
    this.reconnectAttempts = 0;
    this.currentTps = 3.0;
    this.fallbackTimer = null;
    this.isUsingFallback = false;
    this.scopedCountry = 'ALL';
    this.scopedState = 'ALL';
  }

  setCountryScope(country, state) {
    this.scopedCountry = country || 'ALL';
    this.scopedState = state || 'ALL';
  }

  onTransaction(callback) {
    this.listeners.push(callback);
  }

  togglePause() {
    this.isPaused = !this.isPaused;
    return this.isPaused;
  }

  setRate(tps) {
    this.currentTps = Math.max(0.5, Math.min(15.0, tps));
    if (this.isUsingFallback && !this.isPaused) {
      this.restartFallbackTimer();
    }
  }

  connect() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    let host = window.location.host || '127.0.0.1:8000';
    if (window.location.port && window.location.port !== '8000') {
      host = `${window.location.hostname || '127.0.0.1'}:8000`;
    }
    const wsUrl = `${protocol}//${host}/ws/stream`;

    try {
      this.socket = new WebSocket(wsUrl);

      this.socket.onopen = () => {
        this.reconnectAttempts = 0;
        this.isUsingFallback = false;
        this.stopFallbackTimer();
        this.updateStatusBadge(true);
      };

      this.socket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.type === 'CONNECTION_ESTABLISHED') {
            this.stopFallbackTimer();
            this.isUsingFallback = false;
            this.updateStatusBadge(true);
            return;
          }

          if (this.isUsingFallback) {
            this.stopFallbackTimer();
            this.isUsingFallback = false;
            this.updateStatusBadge(true);
          }

          this.buffer.unshift(data);
          if (this.buffer.length > this.maxBufferSize) this.buffer.pop();

          if (!this.isPaused) {
            this.listeners.forEach(cb => cb(data));
          }
        } catch (err) { }
      };

      this.socket.onclose = () => {
        this.updateStatusBadge(false);
        this.startFallbackGenerator();
        this.reconnect();
      };

      this.socket.onerror = () => {
        this.updateStatusBadge(false);
        this.startFallbackGenerator();
      };
    } catch (e) {
      this.startFallbackGenerator();
      this.reconnect();
    }

    // Safety fallback trigger after 1.5s if socket didn't open
    setTimeout(() => {
      if (!this.socket || this.socket.readyState !== WebSocket.OPEN) {
        this.startFallbackGenerator();
      }
    }, 1200);
  }

  reconnect() {
    this.reconnectAttempts++;
    const delay = Math.min(6000, 1500 * Math.pow(1.3, this.reconnectAttempts));
    setTimeout(() => this.connect(), delay);
  }

  updateStatusBadge(isConnected) {
    const badge = document.getElementById('connectionStatusBadge');
    if (!badge) return;
    if (isConnected) {
      badge.className = 'status-chip badge-approved';
      badge.innerHTML = '<span class="badge-pulse"></span> STREAM: LIVE';
    } else {
      badge.className = 'status-chip badge-approved';
      badge.innerHTML = '<span class="badge-pulse"></span> STREAM: ACTIVE (NEURAL SIM)';
    }
  }

  startFallbackGenerator() {
    if (this.isUsingFallback) return;
    this.isUsingFallback = true;
    this.updateStatusBadge(false);
    this.restartFallbackTimer();
  }

  stopFallbackTimer() {
    if (this.fallbackTimer) {
      clearInterval(this.fallbackTimer);
      this.fallbackTimer = null;
    }
  }

  restartFallbackTimer() {
    this.stopFallbackTimer();
    const intervalMs = Math.max(80, Math.floor(1000 / this.currentTps));
    this.fallbackTimer = setInterval(() => {
      if (!this.isPaused) {
        const synthetic = this.generateSyntheticEvent();
        this.emit(synthetic);
      }
    }, intervalMs);
  }

  emit(data) {
    this.buffer.unshift(data);
    if (this.buffer.length > this.maxBufferSize) this.buffer.pop();
    this.listeners.forEach(cb => cb(data));
  }

  generateSyntheticEvent(forcedScenario = null) {
    let availableCities = REAL_CITIES;
    if (this.scopedCountry && this.scopedCountry !== 'ALL') {
      const sc = this.scopedCountry;
      const matchC = REAL_CITIES.filter(c => (
        c.country === sc ||
        (sc === 'USA' && c.country === 'United States') ||
        (sc === 'UK' && c.country === 'United Kingdom') ||
        (sc === 'UAE' && c.country === 'United Arab Emirates')
      ));
      if (matchC.length > 0) {
        if (this.scopedState && this.scopedState !== 'ALL') {
          const ss = this.scopedState.toLowerCase();
          const matchS = matchC.filter(c => c.state.toLowerCase() === ss || c.state.toLowerCase().includes(ss) || ss.includes(c.state.toLowerCase()));
          availableCities = matchS.length > 0 ? matchS : matchC;
        } else {
          availableCities = matchC;
        }
      }
    }

    const loc = availableCities[Math.floor(Math.random() * availableCities.length)];
    const merchant = MERCHANTS[Math.floor(Math.random() * MERCHANTS.length)];

    // Choose payment medium (prioritize UPI in India)
    let medium;
    if (loc.country === 'India' && Math.random() < 0.6) {
      medium = 'UPI';
    } else {
      medium = MEDIUMS[Math.floor(Math.random() * MEDIUMS.length)];
    }

    // Select localized user tied authentically to their home region
    let user;
    if (loc.country === 'India') {
      const indUsers = ['usr_ind_aarav', 'usr_ind_priya', 'usr_ind_vikram', 'usr_ind_sneha', 'usr_ind_rahul', 'usr_ind_ananya', 'usr_ind_rohan', 'usr_ind_pooja'];
      let cityHash = 0;
      for (let i = 0; i < (loc.city || '').length; i++) cityHash = (cityHash << 5) - cityHash + loc.city.charCodeAt(i);
      user = indUsers[Math.abs(cityHash) % indUsers.length];
    } else if (loc.country === 'Japan') {
      const jpnUsers = ['usr_jpn_kenji', 'usr_jpn_yuto', 'usr_jpn_aoi', 'usr_jpn_sakura'];
      let cityHash = 0;
      for (let i = 0; i < (loc.city || '').length; i++) cityHash = (cityHash << 5) - cityHash + loc.city.charCodeAt(i);
      user = jpnUsers[Math.abs(cityHash) % jpnUsers.length];
    } else if (loc.country === 'Germany') {
      const deuUsers = ['usr_deu_lukas', 'usr_deu_florian', 'usr_deu_max', 'usr_deu_hannah'];
      let cityHash = 0;
      for (let i = 0; i < (loc.city || '').length; i++) cityHash = (cityHash << 5) - cityHash + loc.city.charCodeAt(i);
      user = deuUsers[Math.abs(cityHash) % deuUsers.length];
    } else {
      user = USERS[Math.floor(Math.random() * USERS.length)];
    }

    const idNum = Math.floor(100000 + Math.random() * 900000);
    const txId = `TXN_${idNum}`;

    let amount = parseFloat((Math.random() * 135 + 15).toFixed(2));
    let status = 'APPROVED';
    let riskScore = Math.floor(Math.random() * 12 + 7) + parseFloat((Math.random() * 0.9).toFixed(1));
    let riskLevel = 'LOW';
    let triggeredRules = [];
    let reason = 'EMV Chip Cryptogram Verified • Low Risk Profile';

    const roll = Math.random();

    if (forcedScenario) {
      const scenario = forcedScenario;
      if (scenario === 'IMPOSSIBLE_TRAVEL') {
        amount = parseFloat((Math.random() * 2200 + 1200).toFixed(2));
        status = 'BLOCKED';
        riskScore = Math.floor(Math.random() * 6 + 92) + parseFloat((Math.random() * 0.9).toFixed(1));
        riskLevel = 'CRITICAL';
        triggeredRules = ['IMPOSSIBLE_TRAVEL (>800km/h)', 'RAPID_GEO_JUMP'];
        reason = 'Impossible travel velocity detected: 1,840 km/h jump across coordinates';
      } else if (scenario === 'RAPID_CARDING') {
        amount = parseFloat((Math.random() * 3000 + 1800).toFixed(2));
        status = 'BLOCKED';
        riskScore = Math.floor(Math.random() * 8 + 88) + parseFloat((Math.random() * 0.9).toFixed(1));
        riskLevel = 'CRITICAL';
        triggeredRules = ['CARDING_MICRO_PROBE', 'VELOCITY_SURGE'];
        reason = 'Automated micro-charges detected followed by immediate high-value spike';
      } else if (scenario === 'MULE_RING') {
        amount = parseFloat((Math.random() * 1500 + 650).toFixed(2));
        status = 'BLOCKED';
        riskScore = Math.floor(Math.random() * 10 + 85) + parseFloat((Math.random() * 0.9).toFixed(1));
        riskLevel = 'CRITICAL';
        triggeredRules = ['MULE_RING_CLUSTER', 'TOR_EXIT_NODE'];
        reason = 'Syndicate linkage: multiple accounts sharing device & proxy fingerprint';
      } else if (scenario === 'UPI_COLLECT_FRAUD') {
        amount = parseFloat((Math.random() * 1850 + 800).toFixed(2));
        status = 'BLOCKED';
        riskScore = Math.floor(Math.random() * 8 + 86) + parseFloat((Math.random() * 0.9).toFixed(1));
        riskLevel = 'CRITICAL';
        triggeredRules = ['UPI_COLLECT_SPIKE', 'UNKNOWN_VPA_REQUEST'];
        reason = 'High-value unauthorized UPI collect mandate spoofing attempt';
      } else {
        amount = parseFloat((Math.random() * 950 + 200).toFixed(2));
        status = 'BLOCKED';
        riskScore = Math.floor(Math.random() * 10 + 82) + parseFloat((Math.random() * 0.9).toFixed(1));
        riskLevel = 'CRITICAL';
        triggeredRules = ['BURST_VELOCITY', 'HIGH_FREQUENCY_BOT'];
        reason = '5 automated transaction attempts under 1 second';
      }
    } else if (roll < 0.34) {
      // ~34% Clean Verified Approved
      amount = parseFloat((Math.random() * 135 + 15).toFixed(2));
      status = 'APPROVED';
      riskScore = Math.floor(Math.random() * 14 + 6) + parseFloat((Math.random() * 0.9).toFixed(1));
      riskLevel = 'LOW';
      triggeredRules = [];
      reason = 'Biometric & EMV Chip Cryptogram Verified • Within Standard Profile';
    } else if (roll < 0.67) {
      // ~33% Under Review / In Review
      status = 'REVIEW';
      riskScore = Math.floor(Math.random() * 18 + 54) + parseFloat((Math.random() * 0.9).toFixed(1));
      riskLevel = 'MEDIUM';
      const reviewScenarios = [
        {
          amt: parseFloat((Math.random() * 450 + 420).toFixed(2)),
          rules: ['UNUSUAL_AMOUNT_DEVIATION', 'GEO_JITTER'],
          reason: 'Statistical deviation: amount is 3.4x higher than user 30-day baseline'
        },
        {
          amt: parseFloat((Math.random() * 520 + 290).toFixed(2)),
          rules: ['COMMERCIAL_VPN_DETECTED', 'TIME_WINDOW_ANOMALY'],
          reason: 'Datacenter VPN proxy detected during atypical nighttime activity window'
        },
        {
          amt: parseFloat((Math.random() * 480 + 360).toFixed(2)),
          rules: ['VELOCITY_SURGE', 'UNREGISTERED_DEVICE'],
          reason: 'Rapid velocity surge: 3 consecutive transactions from unverified device'
        },
        {
          amt: parseFloat((Math.random() * 680 + 520).toFixed(2)),
          rules: ['HIGH_RISK_MCC_ESCALATION', 'NEW_BENEFICIARY'],
          reason: 'Offshore digital asset exchange purchase requiring analyst review'
        },
        {
          amt: parseFloat((Math.random() * 420 + 280).toFixed(2)),
          rules: ['CROSS_BORDER_VELOCITY_PROBE'],
          reason: 'Cross-border geolocation velocity probe detected across regions'
        }
      ];
      const rev = reviewScenarios[Math.floor(Math.random() * reviewScenarios.length)];
      amount = rev.amt;
      triggeredRules = rev.rules;
      reason = rev.reason;
    } else {
      // ~33% Critical Cyber Attack / Fraud Blocked
      status = 'BLOCKED';
      riskLevel = 'CRITICAL';
      const attackScenarios = ['IMPOSSIBLE_TRAVEL', 'RAPID_CARDING', 'MULE_RING', 'UPI_COLLECT_FRAUD', 'BURST_VELOCITY'];
      const sc = attackScenarios[Math.floor(Math.random() * attackScenarios.length)];
      if (sc === 'IMPOSSIBLE_TRAVEL') {
        amount = parseFloat((Math.random() * 2100 + 950).toFixed(2));
        riskScore = Math.floor(Math.random() * 6 + 92) + parseFloat((Math.random() * 0.9).toFixed(1));
        triggeredRules = ['IMPOSSIBLE_TRAVEL (>800km/h)', 'RAPID_GEO_JUMP'];
        reason = 'Impossible speed travel detected: cross-border teleportation anomaly';
      } else if (sc === 'UPI_COLLECT_FRAUD') {
        amount = parseFloat((Math.random() * 1850 + 800).toFixed(2));
        riskScore = Math.floor(Math.random() * 8 + 86) + parseFloat((Math.random() * 0.9).toFixed(1));
        triggeredRules = ['UPI_COLLECT_SPIKE', 'UNKNOWN_VPA_REQUEST'];
        reason = 'High-value unauthorized UPI collect mandate spoofing attempt';
      } else if (sc === 'MULE_RING') {
        amount = parseFloat((Math.random() * 1500 + 650).toFixed(2));
        riskScore = Math.floor(Math.random() * 10 + 85) + parseFloat((Math.random() * 0.9).toFixed(1));
        triggeredRules = ['MULE_RING_CLUSTER', 'TOR_EXIT_NODE'];
        reason = 'Syndicate linkage: multiple accounts sharing device & proxy fingerprint';
      } else if (sc === 'BURST_VELOCITY') {
        amount = parseFloat((Math.random() * 1250 + 400).toFixed(2));
        riskScore = Math.floor(Math.random() * 8 + 84) + parseFloat((Math.random() * 0.9).toFixed(1));
        triggeredRules = ['BURST_VELOCITY', 'HIGH_FREQUENCY_BOT'];
        reason = 'Automated transaction surge: 6 attempts within 1.2 seconds';
      } else {
        amount = parseFloat((Math.random() * 2800 + 1200).toFixed(2));
        riskScore = Math.floor(Math.random() * 8 + 88) + parseFloat((Math.random() * 0.9).toFixed(1));
        triggeredRules = ['CARDING_MICRO_PROBE', 'VELOCITY_SURGE'];
        reason = 'Automated micro-charges detected followed by immediate high-value spike';
      }
    }

    let upiId = undefined;
    let paymentRail = 'STANDARD';
    if (medium === 'UPI') {
      const handles = ['@okhdfcbank', '@paytm', '@ybl', '@okicici', '@sbi'];
      upiId = `${user.replace('usr_', '')}${handles[Math.floor(Math.random() * handles.length)]}`;
      paymentRail = 'IMPS_NPCI_VPA';
    } else if (medium === 'CARD') {
      paymentRail = Math.random() > 0.5 ? 'VISA_3DS' : 'MASTERCARD_MDES';
    } else if (medium === 'NET_BANKING') {
      paymentRail = 'ISO20022_SWIFT';
    } else if (medium === 'WALLET') {
      paymentRail = Math.random() > 0.5 ? 'APPLE_PAY' : 'GOOGLE_WALLET';
    } else if (medium === 'ATM_CASH') {
      paymentRail = 'NFS_ATM_SWITCH';
    } else if (medium === 'CRYPTO') {
      paymentRail = Math.random() > 0.5 ? 'EVM_ETHEREUM' : 'SOLANA_PAY';
    }

    return {
      transaction: {
        id: txId,
        user_id: user,
        amount: amount,
        currency: 'USD',
        merchant: merchant.name,
        merchant_category: merchant.cat,
        payment_method: medium,
        payment_rail: paymentRail,
        upi_id: upiId,
        location: {
          city: loc.city,
          state: loc.state,
          country: loc.country,
          country_code: loc.country_code,
          lat: loc.lat,
          lon: loc.lon
        },
        device_id: `dev_${Math.floor(1000 + Math.random() * 9000)}`,
        card_token: `tok_${Math.floor(100000 + Math.random() * 900000)}`,
        ip_address: `185.${Math.floor(Math.random() * 255)}.${Math.floor(Math.random() * 255)}.${Math.floor(Math.random() * 255)}`
      },
      decision: {
        status: status,
        risk_score: riskScore,
        risk_level: riskLevel,
        reason_summary: reason,
        triggered_rules: triggeredRules,
        latency_ms: parseFloat((loc.country === 'India' ? Math.random() * 4 + 13.0 : (loc.country === 'United States' ? Math.random() * 3 + 7.5 : Math.random() * 5 + 9.5)).toFixed(1))
      },
      risk_breakdown: {
        rule_score: status === 'BLOCKED' ? 95 : ((status === 'REVIEW' || status === 'FLAGGED') ? 62 : 12),
        ml_score: status === 'BLOCKED' ? 88 : ((status === 'REVIEW' || status === 'FLAGGED') ? 58 : 18),
        graph_score: status === 'BLOCKED' ? 90 : ((status === 'REVIEW' || status === 'FLAGGED') ? 45 : 10),
        factor_breakdown: {
          velocity: status === 'BLOCKED' ? 0.45 : ((status === 'REVIEW' || status === 'FLAGGED') ? 0.30 : 0.10),
          location_anomaly: status === 'BLOCKED' ? 0.35 : ((status === 'REVIEW' || status === 'FLAGGED') ? 0.25 : 0.05),
          amount_deviation: status === 'BLOCKED' ? 0.20 : ((status === 'REVIEW' || status === 'FLAGGED') ? 0.30 : 0.15)
        }
      },
      processed_at: Math.floor(Date.now() / 1000)
    };
  }

  // Direct programmatic attack scenario trigger
  simulateAttack(scenario) {
    const burstCount = scenario === 'BURST_VELOCITY' ? 5 : 3;
    for (let i = 0; i < burstCount; i++) {
      setTimeout(() => {
        const attackEvent = this.generateSyntheticEvent(scenario);
        this.emit(attackEvent);
      }, i * 160);
    }
  }
}
