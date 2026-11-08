/**
 * ShieldPlus AI - Transaction Activity Wave & Risk Donut Chart Visualizer
 * Fully real-time, interactive canvas-based dual spline wave and risk donut charts.
 * Reacts dynamically to live streaming transactions, timeframe changes, and country jurisdiction scoping.
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

export class ActivityChart {
  constructor(canvasId) {
    this.canvas = document.getElementById(canvasId);
    if (!this.canvas) return;
    this.ctx = this.canvas.getContext('2d');
    this.phase = 0;
    this.activeTimeframe = 'Daily';
    this.currentCountry = 'ALL';
    this.currentState = 'ALL';

    // Timeframe configurations calibrated to authentic SQLite database volume
    this.timeframeConfig = {
      Daily: {
        labels: ['12 AM', '4 AM', '8 AM', '12 PM', '4 PM', '8 PM', 'Now'],
        baselineLegit: [2780, 1390, 7877, 17607, 22241, 24094, 16680],
        baselineFraud: [1679, 1119, 2239, 4479, 5599, 6998, 5878]
      },
      Weekly: {
        labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Today'],
        baselineLegit: [13900, 14820, 15750, 16680, 17600, 7410, 6490],
        baselineFraud: [3630, 3910, 4190, 4750, 5590, 3070, 2790]
      },
      Monthly: {
        labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4', 'Current'],
        baselineLegit: [21310, 23160, 24090, 18530, 5560],
        baselineFraud: [6150, 6710, 7550, 5870, 1670]
      }
    };

    // Regional & City volume scale multipliers (Derived from SQLite database volumes)
    this.geoScales = {
      // Global
      'ALL': 1.0,

      // Countries
      'United States': 0.210,
      'USA': 0.210,
      'India': 0.189,
      'Japan': 0.175,
      'Germany': 0.173,
      'United Kingdom': 0.138,
      'UK': 0.138,
      'Australia': 0.0266,
      'Canada': 0.0264,
      'Brazil': 0.0195,
      'Singapore': 0.0129,
      'France': 0.0128,
      'United Arab Emirates': 0.0126,
      'UAE': 0.0126,

      // Cities in India
      'Mumbai': 0.0356,
      'Maharashtra': 0.0356,
      'Bengaluru': 0.0355,
      'Karnataka': 0.0355,
      'Chennai': 0.0351,
      'Tamil Nadu': 0.0351,
      'Delhi': 0.0347,
      'Delhi NCR': 0.0347,
      'Hyderabad': 0.0344,
      'Telangana': 0.0344,
      'Bhubaneswar': 0.0067,
      'Odisha': 0.0067,
      'Kolkata': 0.0065,
      'West Bengal': 0.0065,

      // Cities in United States
      'Miami': 0.0362,
      'Florida': 0.0362,
      'Houston': 0.0353,
      'Texas': 0.0353,
      'Chicago': 0.0351,
      'Illinois': 0.0351,
      'Los Angeles': 0.0349,
      'California': 0.0349,
      'New York': 0.0348,
      'Seattle': 0.0346,
      'Washington': 0.0346,

      // Cities in United Kingdom
      'Cardiff': 0.0357,
      'Wales': 0.0357,
      'London': 0.0344,
      'Greater London': 0.0344,
      'Edinburgh': 0.0344,
      'Scotland': 0.0344,
      'Manchester': 0.0342,
      'Greater Manchester': 0.0342,

      // Cities in Japan
      'Osaka': 0.0356,
      'Osaka Prefecture': 0.0356,
      'Tokyo': 0.0349,
      'Tokyo Prefecture': 0.0349,
      'Yokohama': 0.0348,
      'Kanagawa': 0.0348,
      'Sapporo': 0.0346,
      'Hokkaido': 0.0346,
      'Kyoto': 0.0344,
      'Kyoto Prefecture': 0.0344,

      // Cities in Germany
      'Frankfurt': 0.0351,
      'Hesse': 0.0351,
      'Munich': 0.0351,
      'Bavaria': 0.0351,
      'Cologne': 0.0346,
      'North Rhine-Westphalia': 0.0346,
      'Berlin': 0.0341,
      'Hamburg': 0.0338,

      // Cities in Australia
      'Brisbane': 0.0068,
      'Queensland': 0.0068,
      'Perth': 0.0068,
      'Western Australia': 0.0068,
      'Sydney': 0.0065,
      'New South Wales': 0.0065,
      'Melbourne': 0.0065,
      'Victoria': 0.0065,

      // Cities in Canada
      'Vancouver': 0.0069,
      'British Columbia': 0.0069,
      'Montreal': 0.0067,
      'Quebec': 0.0067,
      'Toronto': 0.0065,
      'Ontario': 0.0065,
      'Calgary': 0.0063,
      'Alberta': 0.0063,

      // Cities in Brazil
      'Sao Paulo': 0.0066,
      'Sao Paulo State': 0.0066,
      'Rio de Janeiro': 0.0066,
      'Rio de Janeiro State': 0.0066,
      'Brasilia': 0.0064,
      'Federal District': 0.0064,

      // Cities in France
      'Paris': 0.0066,
      'Ile-de-France': 0.0066,
      'Lyon': 0.0062,
      'Auvergne-Rhone-Alpes': 0.0062,

      // UAE & Singapore
      'Abu Dhabi': 0.0064,
      'Abu Dhabi Emirate': 0.0064,
      'Dubai': 0.0062,
      'Dubai Emirate': 0.0062,
      'Jurong East': 0.0065,
      'West Region': 0.0065,
      'Singapore': 0.0064,
      'Central Region': 0.0064
    };

    this.labels = [];
    this.legitData = [];
    this.fraudData = [];

    // Interactive hover inspection
    this.hoverIdx = -1;
    this.pulseAlpha = 0;
    this.pulseColor = '#0EA5E9';

    this.initData();
    this.initInteraction();
    this.resize();
    window.addEventListener('resize', () => this.resize());
    this.fetchActivityTimeseries();
    this.animate();
  }

  initData() {
    const tf = this.timeframeConfig[this.activeTimeframe] || this.timeframeConfig.Daily;
    
    // Choose most granular scale: City/State > Country > Global
    let scale = 1.0;
    if (this.currentState && this.currentState !== 'ALL' && this.geoScales[this.currentState]) {
      scale = this.geoScales[this.currentState];
    } else if (this.currentCountry && this.currentCountry !== 'ALL' && this.geoScales[this.currentCountry]) {
      scale = this.geoScales[this.currentCountry];
    }

    this.labels = [...tf.labels];
    this.legitData = tf.baselineLegit.map(v => Math.max(1, Math.round(v * scale)));
    this.fraudData = tf.baselineFraud.map(v => Math.max(1, Math.round(v * scale)));
  }

  async fetchActivityTimeseries() {
    try {
      const countryParam = (this.currentCountry && this.currentCountry !== 'ALL') ? `country=${encodeURIComponent(this.currentCountry)}` : '';
      const cityParam = (this.currentState && this.currentState !== 'ALL') ? `city=${encodeURIComponent(this.currentState)}` : '';
      const tfParam = `timeframe=${encodeURIComponent(this.activeTimeframe || 'Daily')}`;

      const params = [countryParam, cityParam, tfParam].filter(Boolean).join('&');
      const url = apiUrl(`/api/metrics/activity?${params}`);

      const res = await fetch(url);
      if (!res.ok) return;
      const data = await res.json();
      if (data && Array.isArray(data.labels) && Array.isArray(data.legitimate) && data.labels.length > 0) {
        this.labels = data.labels;
        this.legitData = data.legitimate;
        this.fraudData = data.fraudulent;
        this.totalTransactions = data.total_transactions;
        this.draw();
      }
    } catch (e) {
      console.warn('Activity timeseries fetch fallback:', e);
    }
  }

  setTimeframe(tf, country = null, state = null) {
    if (country !== null) this.currentCountry = country;
    if (state !== null) this.currentState = state;
    this.activeTimeframe = tf || 'Daily';
    this.fetchActivityTimeseries();
  }

  setGeoScope(country, state = 'ALL') {
    this.currentCountry = country || 'ALL';
    this.currentState = state || 'ALL';
    this.fetchActivityTimeseries();
  }

  setCountryScope(country) {
    this.setGeoScope(country, 'ALL');
  }

  // Live real-time transaction ingestion with scope filtering
  addTransaction(enriched) {
    if (!enriched || !enriched.transaction || !enriched.decision) return;
    const loc = enriched.transaction.location || {};
    const c = (loc.country || '').trim().toLowerCase();
    const code = (loc.country_code || '').trim().toLowerCase();
    const targetC = (this.currentCountry || 'ALL').trim().toLowerCase();
    const targetS = (this.currentState || 'ALL').trim().toLowerCase();

    if (targetC !== 'all') {
      const isMatch = (c === targetC || code === targetC ||
        (targetC === 'india' && (c === 'india' || code === 'in')) ||
        (targetC === 'united states' && (c === 'united states' || c === 'usa' || code === 'us')) ||
        (targetC === 'japan' && (c === 'japan' || code === 'jp')) ||
        (targetC === 'united kingdom' && (c === 'united kingdom' || c === 'uk' || code === 'gb')) ||
        (targetC === 'germany' && (c === 'germany' || code === 'de'))
      );
      if (!isMatch) return;
    }

    if (targetS !== 'all') {
      const s = (loc.state || '').trim().toLowerCase();
      const city = (loc.city || '').trim().toLowerCase();
      if (s !== targetS && !s.includes(targetS) && city !== targetS && !city.includes(targetS)) return;
    }

    const lastIdx = this.legitData.length - 1;
    if (lastIdx < 0) return;

    const st = enriched.decision.status;
    const isBlocked = (st === 'BLOCKED');
    const isReview = (st === 'FLAGGED' || st === 'REVIEW' || st === 'UNDER_REVIEW' || st === 'IN_REVIEW');

    if (isBlocked || isReview) {
      this.fraudData[lastIdx]++;
      this.pulseColor = isBlocked ? '#EF4444' : '#F59E0B';
    } else {
      this.legitData[lastIdx]++;
      this.pulseColor = '#0EA5E9';
    }

    this.pulseAlpha = 1.0;
  }

  initInteraction() {
    if (!this.canvas) return;

    this.canvas.addEventListener('mousemove', (e) => {
      const rect = this.canvas.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const padLeft = 38;
      const padRight = 24;
      const chartW = this.width - padLeft - padRight;

      if (x < padLeft || x > this.width - padRight) {
        this.hoverIdx = -1;
        return;
      }

      const numPoints = this.labels.length;
      const step = chartW / (numPoints - 1);
      const idx = Math.round((x - padLeft) / step);
      this.hoverIdx = Math.max(0, Math.min(numPoints - 1, idx));
    });

    this.canvas.addEventListener('mouseleave', () => {
      this.hoverIdx = -1;
    });
  }

  resize() {
    if (!this.canvas || !this.canvas.parentElement) return;
    const rect = this.canvas.parentElement.getBoundingClientRect();
    this.width = rect.width;
    this.height = Math.max(160, rect.height || 180);
    this.canvas.width = this.width * window.devicePixelRatio;
    this.canvas.height = this.height * window.devicePixelRatio;
    this.ctx.scale(window.devicePixelRatio, window.devicePixelRatio);
  }

  animate() {
    this.draw();
    this.phase += 0.012;
    if (this.pulseAlpha > 0) {
      this.pulseAlpha = Math.max(0, this.pulseAlpha - 0.02);
    }
    requestAnimationFrame(() => this.animate());
  }

  draw() {
    if (!this.ctx) return;
    const ctx = this.ctx;
    const w = this.width;
    const h = this.height;
    ctx.clearRect(0, 0, w, h);

    const padLeft = 38;
    const padRight = 24;
    const padBottom = 26;
    const padTop = 22;
    const chartW = w - padLeft - padRight;
    const chartH = h - padTop - padBottom;

    const numPoints = this.labels.length;
    if (numPoints < 2) return;

    // Calculate dynamic vertical scale based on real-time data
    const maxVal = Math.max(
      ...this.legitData,
      ...this.fraudData,
      10
    ) * 1.25;

    // 1. Grid Lines and Y-Axis Labels
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.04)';
    ctx.lineWidth = 1;
    ctx.font = '9px "JetBrains Mono", monospace';
    ctx.fillStyle = '#64748B';
    ctx.textAlign = 'right';

    const yTicksCount = 6;
    for (let i = 0; i < yTicksCount; i++) {
      const yFrac = i / (yTicksCount - 1);
      const y = padTop + chartH * yFrac;
      const val = Math.round(maxVal * (1 - yFrac));

      let valStr = val.toString();
      if (val >= 1000) {
        valStr = (val / 1000).toFixed(val >= 10000 ? 0 : 1) + 'k';
      }

      ctx.beginPath();
      ctx.moveTo(padLeft, y);
      ctx.lineTo(w - padRight, y);
      ctx.stroke();
      ctx.fillText(valStr, padLeft - 6, y + 3);
    }

    // 2. X-Axis Labels
    ctx.textAlign = 'center';
    this.labels.forEach((label, i) => {
      const x = padLeft + (chartW / (numPoints - 1)) * i;
      ctx.fillStyle = (i === numPoints - 1) ? '#38BDF8' : '#64748B';
      ctx.font = (i === numPoints - 1)
        ? '700 9px "JetBrains Mono", monospace'
        : '9px "JetBrains Mono", monospace';
      ctx.fillText(label, x, h - 8);
    });

    // Compute coordinate points from real-time data with natural organic wave harmonics
    const computePoints = (dataArray, harmonicMod = 0) => {
      const points = [];
      for (let i = 0; i < numPoints; i++) {
        const x = padLeft + (chartW / (numPoints - 1)) * i;
        const val = dataArray[i];
        const frac = Math.max(0.04, Math.min(0.96, val / maxVal));

        // Subtle organic breathing motion on historical points, anchor tightly on Now point
        const isLatest = (i === numPoints - 1);
        const waveSlight = isLatest ? 0 : Math.sin(this.phase + i * 0.8 + harmonicMod) * 3.5;
        const y = padTop + chartH * (1 - frac) + waveSlight;
        points.push({ x, y, val });
      }
      return points;
    };

    const pointsLegit = computePoints(this.legitData, 0);
    const pointsFraud = computePoints(this.fraudData, 1.4);

    // 3. Legitimate Transactions Glowing Gradient Fill
    const gradLegit = ctx.createLinearGradient(0, padTop, 0, padTop + chartH);
    gradLegit.addColorStop(0, 'rgba(14, 165, 233, 0.32)');
    gradLegit.addColorStop(0.55, 'rgba(14, 165, 233, 0.08)');
    gradLegit.addColorStop(1, 'rgba(14, 165, 233, 0.0)');

    ctx.beginPath();
    ctx.moveTo(pointsLegit[0].x, padTop + chartH);
    pointsLegit.forEach((p, idx) => {
      if (idx === 0) ctx.lineTo(p.x, p.y);
      else {
        const prev = pointsLegit[idx - 1];
        const cx = (prev.x + p.x) / 2;
        ctx.bezierCurveTo(cx, prev.y, cx, p.y, p.x, p.y);
      }
    });
    ctx.lineTo(pointsLegit[pointsLegit.length - 1].x, padTop + chartH);
    ctx.closePath();
    ctx.fillStyle = gradLegit;
    ctx.fill();

    // Legitimate Stroke Curve
    ctx.beginPath();
    pointsLegit.forEach((p, idx) => {
      if (idx === 0) ctx.moveTo(p.x, p.y);
      else {
        const prev = pointsLegit[idx - 1];
        const cx = (prev.x + p.x) / 2;
        ctx.bezierCurveTo(cx, prev.y, cx, p.y, p.x, p.y);
      }
    });
    ctx.strokeStyle = '#38BDF8';
    ctx.lineWidth = 1.8;
    ctx.stroke();

    // 4. Fraudulent Transactions Spline Wave (Red Line)
    ctx.beginPath();
    pointsFraud.forEach((p, idx) => {
      if (idx === 0) ctx.moveTo(p.x, p.y);
      else {
        const prev = pointsFraud[idx - 1];
        const cx = (prev.x + p.x) / 2;
        ctx.bezierCurveTo(cx, prev.y, cx, p.y, p.x, p.y);
      }
    });
    ctx.strokeStyle = '#EF4444';
    ctx.lineWidth = 1.8;
    ctx.stroke();

    // 5. Active "Now" / "Current" Endpoint Marker
    const nowIdx = numPoints - 1;
    const nowP = pointsLegit[nowIdx];

    // Solid core dot
    ctx.beginPath();
    ctx.arc(nowP.x, nowP.y, 3.5, 0, Math.PI * 2);
    ctx.fillStyle = '#38BDF8';
    ctx.fill();

    // Fraud endpoint marker
    const nowFraudP = pointsFraud[nowIdx];
    ctx.beginPath();
    ctx.arc(nowFraudP.x, nowFraudP.y, 3.5, 0, Math.PI * 2);
    ctx.fillStyle = '#EF4444';
    ctx.fill();

    // 6. Interactive Floating Tooltip (Hovered Point or Real-Time Peak Point)
    const activeTargetIdx = (this.hoverIdx >= 0) ? this.hoverIdx : nowIdx;
    const targetLegit = pointsLegit[activeTargetIdx];
    const targetFraud = pointsFraud[activeTargetIdx];

    const legitCount = this.legitData[activeTargetIdx];
    const fraudCount = this.fraudData[activeTargetIdx];
    const totalCount = legitCount + fraudCount;

    // Subtle guide line on active point
    ctx.beginPath();
    ctx.moveTo(targetLegit.x, padTop);
    ctx.lineTo(targetLegit.x, padTop + chartH);
    ctx.strokeStyle = 'rgba(56, 189, 248, 0.2)';
    ctx.lineWidth = 1;
    ctx.setLineDash([3, 3]);
    ctx.stroke();
    ctx.setLineDash([]);

    // Target indicator dot
    ctx.beginPath();
    ctx.arc(targetLegit.x, targetLegit.y, 4, 0, Math.PI * 2);
    ctx.fillStyle = '#38BDF8';
    ctx.fill();

    // Floating Tooltip Box
    let tooltipText = `${totalCount.toLocaleString()} Transactions (${legitCount.toLocaleString()} Legit, ${fraudCount.toLocaleString()} Fraud)`;
    if (this.hoverIdx >= 0) {
      tooltipText = `${this.labels[activeTargetIdx]}: ${totalCount.toLocaleString()} Tx (${legitCount.toLocaleString()} Legit, ${fraudCount.toLocaleString()} Fraud)`;
    }

    ctx.font = '600 10px "JetBrains Mono", monospace';
    const textWidth = ctx.measureText(tooltipText).width;
    const tipW = Math.max(110, textWidth + 18);
    const tipH = 24;

    let tipX = targetLegit.x - tipW / 2;
    tipX = Math.max(padLeft, Math.min(w - padRight - tipW, tipX));
    let tipY = targetLegit.y - 34;
    if (tipY < padTop - 5) tipY = targetLegit.y + 14;

    ctx.fillStyle = '#08090C';
    ctx.strokeStyle = '#222733';
    ctx.lineWidth = 1;

    ctx.beginPath();
    if (ctx.roundRect) {
      ctx.roundRect(tipX, tipY, tipW, tipH, 2);
    } else {
      ctx.rect(tipX, tipY, tipW, tipH);
    }
    ctx.fill();
    ctx.stroke();

    ctx.fillStyle = '#F1F5F9';
    ctx.textAlign = 'center';
    ctx.fillText(tooltipText, tipX + tipW / 2, tipY + 15);
  }
}

export class DonutChart {
  constructor(canvasId) {
    this.canvas = document.getElementById(canvasId);
    if (!this.canvas) return;
    this.ctx = this.canvas.getContext('2d');
    this.high = 19;
    this.medium = 9;
    this.low = 72;
    this.lastRate = 28;
    this.resize();
    window.addEventListener('resize', () => {
      this.resize();
      this.draw(this.high, this.medium, this.low, this.lastRate);
    });
    this.draw(19, 9, 72, 28);
  }

  resize() {
    if (!this.canvas || !this.canvas.parentElement) return;
    const rect = this.canvas.parentElement.getBoundingClientRect();
    const size = Math.min(rect.width, rect.height || 140) || 130;
    this.size = size;
    const dpr = window.devicePixelRatio || 1;
    this.canvas.width = size * dpr;
    this.canvas.height = size * dpr;
    this.ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  }

  addTransaction(status) {
    // Benchmark Donut preserves authentic country/state baseline data and does not jitter on stream ticks
  }

  draw(high = 18, medium = 9, low = 73, explicitFraudRate = null) {
    this.high = high;
    this.medium = medium;
    this.low = low;
    this.lastRate = explicitFraudRate;

    if (!this.ctx) return;
    if (!this.size || this.size === 0) {
      this.resize();
    }
    const ctx = this.ctx;
    const s = this.size || 130;
    const cx = s / 2;
    const cy = s / 2;
    const rOuter = s * 0.44;
    const rInner = s * 0.31;
    ctx.clearRect(0, 0, s, s);

    // 1. Draw 3D Milled Inset Chassis / Under-Track (Recessed Well)
    ctx.save();
    ctx.beginPath();
    ctx.arc(cx, cy, rOuter + 2, 0, Math.PI * 2);
    ctx.arc(cx, cy, rInner - 2, 0, Math.PI * 2, true);
    ctx.closePath();
    ctx.fillStyle = '#0E1118';
    ctx.fill();

    // Specular Outer Rim Highlight (top-down light source simulation)
    const rimGrad = ctx.createLinearGradient(cx, cy - rOuter, cx, cy + rOuter);
    rimGrad.addColorStop(0, 'rgba(255, 255, 255, 0.22)');
    rimGrad.addColorStop(0.5, 'rgba(197, 198, 201, 0.08)');
    rimGrad.addColorStop(1, 'rgba(0, 0, 0, 0.7)');
    ctx.strokeStyle = rimGrad;
    ctx.lineWidth = 1;
    ctx.stroke();
    ctx.restore();

    const total = (high + medium + low) || 100;
    const highAngle = (high / total) * Math.PI * 2;
    const medAngle = (medium / total) * Math.PI * 2;
    const lowAngle = (low / total) * Math.PI * 2;

    let start = -Math.PI / 2;

    const drawSlice = (angle, colorStart, colorEnd) => {
      if (angle <= 0.005) return;
      ctx.save();
      ctx.beginPath();
      ctx.arc(cx, cy, rOuter, start, start + angle);
      ctx.arc(cx, cy, rInner, start + angle, start, true);
      ctx.closePath();

      // Top-down specular bevel gradient for tactile 3D volume
      const sliceGrad = ctx.createLinearGradient(cx, cy - rOuter, cx, cy + rOuter);
      sliceGrad.addColorStop(0, colorStart);
      sliceGrad.addColorStop(1, colorEnd);
      ctx.fillStyle = sliceGrad;

      // Tactile 3D drop-edge shadow
      ctx.shadowColor = 'rgba(0, 0, 0, 0.6)';
      ctx.shadowBlur = 4;
      ctx.shadowOffsetY = 2;
      ctx.fill();

      // Specular segment rim
      ctx.shadowColor = 'transparent';
      ctx.strokeStyle = 'rgba(255, 255, 255, 0.18)';
      ctx.lineWidth = 0.75;
      ctx.stroke();
      ctx.restore();

      start += angle;
    };

    // Low Risk: Vibrant Cyan / Blue (3D volume gradient)
    drawSlice(lowAngle, '#22D3EE', '#0891B2');
    // Medium Risk: Cognitive Amber (3D volume gradient)
    drawSlice(medAngle, '#FBBF24', '#D97706');
    // High Risk: Cognitive Coral Red (3D volume gradient)
    drawSlice(highAngle, '#F87171', '#DC2626');

    // 2. Center Milled Core Well (Tactile Countersunk 3D Inset)
    ctx.save();
    ctx.beginPath();
    ctx.arc(cx, cy, rInner - 1, 0, Math.PI * 2);
    ctx.closePath();
    const coreGrad = ctx.createRadialGradient(cx, cy - 8, 2, cx, cy, rInner);
    coreGrad.addColorStop(0, '#161922');
    coreGrad.addColorStop(0.85, '#0B0D12');
    coreGrad.addColorStop(1, '#07080B');
    ctx.fillStyle = coreGrad;
    ctx.shadowColor = 'rgba(0, 0, 0, 0.9)';
    ctx.shadowBlur = 8;
    ctx.shadowOffsetY = 3;
    ctx.fill();

    // 3D Titanium Inner Bevel
    const innerBevel = ctx.createLinearGradient(cx, cy - rInner, cx, cy + rInner);
    innerBevel.addColorStop(0, 'rgba(0, 0, 0, 0.9)');
    innerBevel.addColorStop(1, 'rgba(197, 198, 201, 0.28)');
    ctx.strokeStyle = innerBevel;
    ctx.lineWidth = 1;
    ctx.stroke();
    ctx.restore();

    // Center Text: Overall Fraud Rate percentage (STRICTLY NUMERIC in JetBrains Mono)
    let fraudRatePct = 0;
    if (typeof explicitFraudRate === 'number' && !isNaN(explicitFraudRate) && isFinite(explicitFraudRate)) {
      fraudRatePct = Math.min(100, Math.max(0, Math.round(explicitFraudRate)));
    } else if (typeof explicitFraudRate === 'string' && !isNaN(parseFloat(explicitFraudRate))) {
      fraudRatePct = Math.min(100, Math.max(0, Math.round(parseFloat(explicitFraudRate))));
    } else {
      const tot = (high + medium + low) || 1;
      fraudRatePct = Math.min(100, Math.max(0, Math.round(((high + medium) / tot) * 100)));
    }

    ctx.save();
    ctx.shadowColor = 'rgba(0, 0, 0, 0.85)';
    ctx.shadowBlur = 4;
    ctx.shadowOffsetY = 1;
    ctx.font = '700 1.3rem "JetBrains Mono", monospace';
    ctx.fillStyle = '#FFFFFF';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(`${fraudRatePct}%`, cx, cy - 6);

    ctx.shadowBlur = 0;
    ctx.font = '700 0.6rem "JetBrains Mono", monospace';
    ctx.fillStyle = '#C5C6C9';
    ctx.fillText('FRAUD RATE', cx, cy + 12);
    ctx.restore();
  }
}
