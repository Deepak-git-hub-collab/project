/**
 * ShieldPlus AI - Tactical Threat Vector Radar & Regional Anomaly Visualizer
 * Supports smooth camera zooming, tactical radar sweep, and multi-tier
 * Global -> Country -> State surveillance modes.
 */

export const COUNTRY_LOCATIONS = {
  "India": [
    { city: "Mumbai", state: "Maharashtra", label: "Mumbai (Maharashtra)" },
    { city: "Bengaluru", state: "Karnataka", label: "Bengaluru (Karnataka)" },
    { city: "Delhi", state: "Delhi NCR", label: "Delhi (NCR)" },
    { city: "Hyderabad", state: "Telangana", label: "Hyderabad (Telangana)" },
    { city: "Chennai", state: "Tamil Nadu", label: "Chennai (Tamil Nadu)" },
    { city: "Kolkata", state: "West Bengal", label: "Kolkata (West Bengal)" },
    { city: "Bhubaneswar", state: "Odisha", label: "Bhubaneswar (Odisha)" }
  ],
  "United States": [
    { city: "New York", state: "New York", label: "New York City (NY)" },
    { city: "Los Angeles", state: "California", label: "Los Angeles (CA)" },
    { city: "Chicago", state: "Illinois", label: "Chicago (IL)" },
    { city: "Houston", state: "Texas", label: "Houston (TX)" },
    { city: "Miami", state: "Florida", label: "Miami (FL)" },
    { city: "Seattle", state: "Washington", label: "Seattle (WA)" }
  ],
  "United Kingdom": [
    { city: "London", state: "Greater London", label: "London (Greater London)" },
    { city: "Manchester", state: "Greater Manchester", label: "Manchester" },
    { city: "Edinburgh", state: "Scotland", label: "Edinburgh (Scotland)" },
    { city: "Cardiff", state: "Wales", label: "Cardiff (Wales)" }
  ],
  "Japan": [
    { city: "Tokyo", state: "Tokyo Prefecture", label: "Tokyo (Kanto)" },
    { city: "Osaka", state: "Osaka Prefecture", label: "Osaka (Kansai)" },
    { city: "Kyoto", state: "Kyoto Prefecture", label: "Kyoto (Kansai)" },
    { city: "Yokohama", state: "Kanagawa", label: "Yokohama (Kanagawa)" },
    { city: "Sapporo", state: "Hokkaido", label: "Sapporo (Hokkaido)" }
  ],
  "Germany": [
    { city: "Frankfurt", state: "Hesse", label: "Frankfurt (Hesse)" },
    { city: "Berlin", state: "Berlin", label: "Berlin (Capital)" },
    { city: "Munich", state: "Bavaria", label: "Munich (Bavaria)" },
    { city: "Hamburg", state: "Hamburg", label: "Hamburg" },
    { city: "Cologne", state: "North Rhine-Westphalia", label: "Cologne (NRW)" }
  ],
  "Australia": [
    { city: "Sydney", state: "New South Wales", label: "Sydney (NSW)" },
    { city: "Melbourne", state: "Victoria", label: "Melbourne (VIC)" },
    { city: "Brisbane", state: "Queensland", label: "Brisbane (QLD)" },
    { city: "Perth", state: "Western Australia", label: "Perth (WA)" }
  ],
  "Canada": [
    { city: "Toronto", state: "Ontario", label: "Toronto (Ontario)" },
    { city: "Vancouver", state: "British Columbia", label: "Vancouver (BC)" },
    { city: "Montreal", state: "Quebec", label: "Montreal (Quebec)" },
    { city: "Calgary", state: "Alberta", label: "Calgary (Alberta)" }
  ],
  "Brazil": [
    { city: "Sao Paulo", state: "Sao Paulo State", label: "São Paulo" },
    { city: "Rio de Janeiro", state: "Rio de Janeiro State", label: "Rio de Janeiro" },
    { city: "Brasilia", state: "Federal District", label: "Brasília (Capital)" }
  ],
  "France": [
    { city: "Paris", state: "Ile-de-France", label: "Paris (Île-de-France)" },
    { city: "Lyon", state: "Auvergne-Rhone-Alpes", label: "Lyon (Auvergne)" }
  ],
  "United Arab Emirates": [
    { city: "Dubai", state: "Dubai Emirate", label: "Dubai" },
    { city: "Abu Dhabi", state: "Abu Dhabi Emirate", label: "Abu Dhabi" }
  ],
  "Singapore": [
    { city: "Singapore", state: "Central Region", label: "Central Singapore" },
    { city: "Jurong East", state: "West Region", label: "Jurong East" }
  ]
};
COUNTRY_LOCATIONS["USA"] = COUNTRY_LOCATIONS["United States"];
COUNTRY_LOCATIONS["UK"] = COUNTRY_LOCATIONS["United Kingdom"];
COUNTRY_LOCATIONS["UAE"] = COUNTRY_LOCATIONS["United Arab Emirates"];

export const COUNTRY_STATES = {
  "United States": ["California", "New York", "Texas", "Florida", "Illinois", "Washington"],
  "United Kingdom": ["Greater London", "Greater Manchester", "Scotland", "Wales"],
  "Japan": ["Tokyo Prefecture", "Osaka Prefecture", "Kyoto Prefecture", "Kanagawa", "Hokkaido"],
  "Germany": ["Hesse", "Berlin", "Bavaria", "Hamburg", "North Rhine-Westphalia"],
  "India": ["Maharashtra", "Delhi NCR", "Karnataka", "Telangana", "Tamil Nadu", "West Bengal", "Odisha"],
  "Canada": ["Ontario", "British Columbia", "Quebec", "Alberta"],
  "Australia": ["New South Wales", "Victoria", "Queensland", "Western Australia"],
  "Brazil": ["Sao Paulo State", "Rio de Janeiro State", "Federal District"],
  "United Arab Emirates": ["Dubai Emirate", "Abu Dhabi Emirate"],
  "UAE": ["Dubai Emirate", "Abu Dhabi Emirate"],
  "Singapore": ["Central Region", "West Region"],
  "France": ["Ile-de-France", "Auvergne-Rhone-Alpes"],
  "UK": ["Greater London", "Greater Manchester", "Scotland", "Wales"],
  "USA": ["California", "New York", "Texas", "Florida", "Illinois", "Washington"]
};

export const COUNTRY_CURRENCY = {
  "United States": { code: "USD", symbol: "$", rate: 1.0, decimals: 2, flag: "🇺🇸", name: "US Dollar" },
  "USA": { code: "USD", symbol: "$", rate: 1.0, decimals: 2, flag: "🇺🇸", name: "US Dollar" },
  "United Kingdom": { code: "GBP", symbol: "£", rate: 0.79, decimals: 2, flag: "🇬🇧", name: "British Pound" },
  "UK": { code: "GBP", symbol: "£", rate: 0.79, decimals: 2, flag: "🇬🇧", name: "British Pound" },
  "Japan": { code: "JPY", symbol: "¥", rate: 152.0, decimals: 0, flag: "🇯🇵", name: "Japanese Yen" },
  "Germany": { code: "EUR", symbol: "€", rate: 0.92, decimals: 2, flag: "🇩🇪", name: "Euro" },
  "France": { code: "EUR", symbol: "€", rate: 0.92, decimals: 2, flag: "🇫🇷", name: "Euro" },
  "India": { code: "INR", symbol: "₹", rate: 84.0, decimals: 2, flag: "🇮🇳", name: "Indian Rupee" },
  "Canada": { code: "CAD", symbol: "CA$", rate: 1.39, decimals: 2, flag: "🇨🇦", name: "Canadian Dollar" },
  "Australia": { code: "AUD", symbol: "A$", rate: 1.52, decimals: 2, flag: "🇦🇺", name: "Australian Dollar" },
  "Brazil": { code: "BRL", symbol: "R$", rate: 5.75, decimals: 2, flag: "🇧🇷", name: "Brazilian Real" },
  "United Arab Emirates": { code: "AED", symbol: "AED ", rate: 3.67, decimals: 2, flag: "🇦🇪", name: "UAE Dirham" },
  "UAE": { code: "AED", symbol: "AED ", rate: 3.67, decimals: 2, flag: "🇦🇪", name: "UAE Dirham" },
  "Singapore": { code: "SGD", symbol: "S$", rate: 1.32, decimals: 2, flag: "🇸🇬", name: "Singapore Dollar" },
  "GLOBAL": { code: "USD", symbol: "$", rate: 1.0, decimals: 2, flag: "🌐", name: "Global USD" }
};

export function formatCurrencyForCountry(amountUSD, country) {
  const curr = COUNTRY_CURRENCY[country] || COUNTRY_CURRENCY.GLOBAL;
  const converted = (amountUSD || 0) * curr.rate;
  if (curr.decimals === 0) {
    return `${curr.symbol}${Math.round(converted).toLocaleString()}`;
  }
  return `${curr.symbol}${converted.toLocaleString(undefined, { minimumFractionDigits: curr.decimals, maximumFractionDigits: curr.decimals })}`;
}

export const REGION_BOUNDS = {
  GLOBAL: { minLat: -55, maxLat: 75, minLon: -175, maxLon: 175, label: "GLOBAL SURVEILLANCE RADAR" },

  // Countries
  "United States": { minLat: 22, maxLat: 52, minLon: -128, maxLon: -64, label: "UNITED STATES THEATER" },
  "USA": { minLat: 22, maxLat: 52, minLon: -128, maxLon: -64, label: "UNITED STATES THEATER" },
  "United Kingdom": { minLat: 49.5, maxLat: 59.5, minLon: -9.0, maxLon: 3.0, label: "UNITED KINGDOM SECTOR" },
  "UK": { minLat: 49.5, maxLat: 59.5, minLon: -9.0, maxLon: 3.0, label: "UNITED KINGDOM SECTOR" },
  "Japan": { minLat: 30, maxLat: 46, minLon: 128, maxLon: 147, label: "JAPAN THEATER" },
  "Germany": { minLat: 47, maxLat: 55.5, minLon: 5.5, maxLon: 15.5, label: "GERMANY REGION" },
  "India": { minLat: 7, maxLat: 36, minLon: 67, maxLon: 98, label: "INDIA THEATER" },
  "Canada": { minLat: 41, maxLat: 65, minLon: -135, maxLon: -55, label: "CANADA REGION" },
  "Australia": { minLat: -44, maxLat: -10, minLon: 110, maxLon: 156, label: "AUSTRALIA THEATER" },
  "Brazil": { minLat: -34, maxLat: 6, minLon: -75, maxLon: -34, label: "BRAZIL SECTOR" },
  "United Arab Emirates": { minLat: 22.5, maxLat: 26.5, minLon: 51.0, maxLon: 57.0, label: "UAE SECTOR" },
  "UAE": { minLat: 22.5, maxLat: 26.5, minLon: 51.0, maxLon: 57.0, label: "UAE SECTOR" },
  "Singapore": { minLat: 1.15, maxLat: 1.50, minLon: 103.60, maxLon: 104.05, label: "SINGAPORE SECTOR" },
  "France": { minLat: 41.5, maxLat: 51.5, minLon: -5.5, maxLon: 9.8, label: "FRANCE SECTOR" },

  // States & Provinces
  // United States
  "California": { minLat: 32.0, maxLat: 42.5, minLon: -125.0, maxLon: -113.5, label: "CALIFORNIA - US-WEST" },
  "New York": { minLat: 40.2, maxLat: 45.3, minLon: -80.0, maxLon: -71.5, label: "NEW YORK - US-EAST" },
  "Texas": { minLat: 25.5, maxLat: 36.8, minLon: -107.0, maxLon: -93.2, label: "TEXAS - US-SOUTH" },
  "Florida": { minLat: 24.2, maxLat: 31.2, minLon: -88.0, maxLon: -79.5, label: "FLORIDA - US-SOUTHEAST" },
  "Illinois": { minLat: 36.8, maxLat: 42.8, minLon: -91.8, maxLon: -87.2, label: "ILLINOIS - US-MIDWEST" },
  "Washington": { minLat: 45.3, maxLat: 49.2, minLon: -125.0, maxLon: -116.8, label: "WASHINGTON - US-PACIFIC" },

  // United Kingdom
  "Greater London": { minLat: 51.2, maxLat: 51.75, minLon: -0.6, maxLon: 0.35, label: "GREATER LONDON METRO" },
  "Greater Manchester": { minLat: 53.25, maxLat: 53.7, minLon: -2.6, maxLon: -1.9, label: "GREATER MANCHESTER" },
  "Scotland": { minLat: 54.5, maxLat: 59.2, minLon: -7.5, maxLon: -1.5, label: "SCOTLAND SECTOR" },
  "Wales": { minLat: 51.2, maxLat: 53.5, minLon: -5.5, maxLon: -2.5, label: "WALES REGION" },

  // Japan
  "Tokyo Prefecture": { minLat: 35.4, maxLat: 36.0, minLon: 139.3, maxLon: 140.1, label: "TOKYO METROPOLITAN" },
  "Osaka Prefecture": { minLat: 34.2, maxLat: 35.1, minLon: 135.0, maxLon: 135.8, label: "OSAKA KANSAI REGION" },
  "Kyoto Prefecture": { minLat: 34.8, maxLat: 35.7, minLon: 135.2, maxLon: 136.1, label: "KYOTO PREFECTURE" },
  "Kanagawa": { minLat: 35.1, maxLat: 35.7, minLon: 138.9, maxLon: 139.8, label: "KANAGAWA PREFECTURE" },
  "Hokkaido": { minLat: 41.2, maxLat: 45.6, minLon: 139.5, maxLon: 146.0, label: "HOKKAIDO NORTHERN THEATER" },

  // Germany
  "Hesse": { minLat: 49.3, maxLat: 51.7, minLon: 7.7, maxLon: 10.4, label: "HESSE - FRANKFURT HUB" },
  "Bavaria": { minLat: 47.1, maxLat: 50.7, minLon: 8.8, maxLon: 14.0, label: "BAVARIA - MUNICH SECTOR" },
  "Berlin": { minLat: 52.3, maxLat: 52.7, minLon: 13.0, maxLon: 13.8, label: "BERLIN METRO" },
  "Hamburg": { minLat: 53.3, maxLat: 53.8, minLon: 9.6, maxLon: 10.4, label: "HAMBURG SECTOR" },
  "North Rhine-Westphalia": { minLat: 50.2, maxLat: 52.6, minLon: 5.8, maxLon: 9.6, label: "NRW - COLOGNE/DUSSELDORF" },

  // India
  "Maharashtra": { minLat: 15.5, maxLat: 22.2, minLon: 72.4, maxLon: 81.0, label: "MAHARASHTRA - MUMBAI HUB" },
  "Delhi NCR": { minLat: 28.3, maxLat: 28.9, minLon: 76.8, maxLon: 77.5, label: "NATIONAL CAPITAL REGION DELHI" },
  "Karnataka": { minLat: 11.4, maxLat: 18.6, minLon: 74.0, maxLon: 78.7, label: "KARNATAKA - BENGALURU TECH HUB" },
  "Telangana": { minLat: 15.7, maxLat: 19.9, minLon: 77.1, maxLon: 81.4, label: "TELANGANA - HYDERABAD" },
  "Tamil Nadu": { minLat: 8.0, maxLat: 13.6, minLon: 76.1, maxLon: 80.5, label: "TAMIL NADU - CHENNAI" },
  "West Bengal": { minLat: 21.4, maxLat: 27.4, minLon: 85.7, maxLon: 89.9, label: "WEST BENGAL - KOLKATA" },

  // Canada
  "Ontario": { minLat: 41.5, maxLat: 55.0, minLon: -95.0, maxLon: -74.0, label: "ONTARIO - TORONTO METRO" },
  "British Columbia": { minLat: 48.0, maxLat: 60.0, minLon: -139.0, maxLon: -114.0, label: "BRITISH COLUMBIA - VANCOUVER" },
  "Quebec": { minLat: 44.8, maxLat: 62.0, minLon: -80.0, maxLon: -57.0, label: "QUEBEC - MONTREAL REGION" },
  "Alberta": { minLat: 48.8, maxLat: 60.0, minLon: -120.0, maxLon: -110.0, label: "ALBERTA - CALGARY SECTOR" },

  // Australia
  "New South Wales": { minLat: -38.0, maxLat: -28.0, minLon: 140.5, maxLon: 154.0, label: "NSW - SYDNEY THEATER" },
  "Victoria": { minLat: -39.5, maxLat: -33.9, minLon: 140.5, maxLon: 150.2, label: "VICTORIA - MELBOURNE" },
  "Queensland": { minLat: -29.2, maxLat: -10.0, minLon: 137.8, maxLon: 154.0, label: "QUEENSLAND - BRISBANE" },
  "Western Australia": { minLat: -35.5, maxLat: -13.5, minLon: 112.5, maxLon: 129.2, label: "WESTERN AUSTRALIA - PERTH" },

  // Brazil
  "Sao Paulo State": { minLat: -25.5, maxLat: -19.6, minLon: -53.2, maxLon: -44.0, label: "SAO PAULO STATE THEATER" },
  "Rio de Janeiro State": { minLat: -23.5, maxLat: -20.6, minLon: -45.0, maxLon: -40.8, label: "RIO DE JANEIRO REGION" },
  "Federal District": { minLat: -16.2, maxLat: -15.4, minLon: -48.4, maxLon: -47.2, label: "BRASILIA FEDERAL DISTRICT" },

  // UAE
  "Dubai Emirate": { minLat: 24.75, maxLat: 25.40, minLon: 54.95, maxLon: 55.60, label: "DUBAI FINANCIAL SECTOR" },
  "Abu Dhabi Emirate": { minLat: 22.8, maxLat: 25.2, minLon: 51.5, maxLon: 56.0, label: "ABU DHABI EMIRATE" },

  // Singapore
  "Central Region": { minLat: 1.25, maxLat: 1.35, minLon: 103.80, maxLon: 103.89, label: "SINGAPORE CENTRAL FINTECH HUB" },
  "West Region": { minLat: 1.29, maxLat: 1.38, minLon: 103.68, maxLon: 103.78, label: "SINGAPORE WEST REGION" },

  // France
  "Ile-de-France": { minLat: 48.1, maxLat: 49.3, minLon: 1.4, maxLon: 3.6, label: "ILE-DE-FRANCE - PARIS" },
  "Auvergne-Rhone-Alpes": { minLat: 44.5, maxLat: 46.8, minLon: 2.5, maxLon: 7.2, label: "AUVERGNE-RHONE-ALPES - LYON" },

  // Key Global Cities
  "Mumbai": { minLat: 18.8, maxLat: 19.35, minLon: 72.7, maxLon: 73.1, label: "MUMBAI FINANCIAL HUB" },
  "Bengaluru": { minLat: 12.8, maxLat: 13.15, minLon: 77.4, maxLon: 77.8, label: "BENGALURU TECH SECTOR" },
  "Delhi": { minLat: 28.4, maxLat: 28.9, minLon: 76.9, maxLon: 77.4, label: "DELHI CAPITAL REGION" },
  "Hyderabad": { minLat: 17.2, maxLat: 17.6, minLon: 78.3, maxLon: 78.7, label: "HYDERABAD CYBERABAD" },
  "Chennai": { minLat: 12.9, maxLat: 13.25, minLon: 80.1, maxLon: 80.35, label: "CHENNAI METRO" },
  "Kolkata": { minLat: 22.4, maxLat: 22.75, minLon: 88.25, maxLon: 88.5, label: "KOLKATA METRO" },
  "Bhubaneswar": { minLat: 20.15, maxLat: 20.4, minLon: 85.7, maxLon: 85.95, label: "BHUBANESWAR SMART CITY" },
  "Odisha": { minLat: 17.8, maxLat: 22.6, minLon: 81.3, maxLon: 87.5, label: "ODISHA - BHUBANESWAR" },
  "New York": { minLat: 40.5, maxLat: 40.92, minLon: -74.1, maxLon: -73.7, label: "NEW YORK FINANCIAL DISTRICT" },
  "Los Angeles": { minLat: 33.7, maxLat: 34.35, minLon: -118.6, maxLon: -118.1, label: "LOS ANGELES METRO" },
  "Chicago": { minLat: 41.6, maxLat: 42.1, minLon: -87.9, maxLon: -87.5, label: "CHICAGO FINANCIAL THEATER" },
  "Houston": { minLat: 29.5, maxLat: 30.15, minLon: -95.6, maxLon: -95.1, label: "HOUSTON METRO" },
  "Miami": { minLat: 25.6, maxLat: 26.0, minLon: -80.35, maxLon: -80.1, label: "MIAMI INTERNATIONAL" },
  "Seattle": { minLat: 47.4, maxLat: 47.8, minLon: -122.5, maxLon: -122.2, label: "SEATTLE PACIFIC TECH" },
  "London": { minLat: 51.4, maxLat: 51.65, minLon: -0.3, maxLon: 0.15, label: "CITY OF LONDON & METRO" },
  "Manchester": { minLat: 53.4, maxLat: 53.6, minLon: -2.35, maxLon: -2.15, label: "MANCHESTER SECTOR" },
  "Edinburgh": { minLat: 55.85, maxLat: 56.05, minLon: -3.35, maxLon: -3.05, label: "EDINBURGH SECTOR" },
  "Cardiff": { minLat: 51.4, maxLat: 51.6, minLon: -3.3, maxLon: -3.05, label: "CARDIFF SECTOR" },
  "Tokyo": { minLat: 35.55, maxLat: 35.8, minLon: 139.6, maxLon: 139.9, label: "TOKYO GINZA / MARUNOUCHI" },
  "Osaka": { minLat: 34.6, maxLat: 34.8, minLon: 135.4, maxLon: 135.6, label: "OSAKA COMMERCIAL HUB" },
  "Kyoto": { minLat: 34.9, maxLat: 35.1, minLon: 135.7, maxLon: 135.9, label: "KYOTO DISTRICT" },
  "Yokohama": { minLat: 35.4, maxLat: 35.55, minLon: 139.6, maxLon: 139.75, label: "YOKOHAMA PORT SECTOR" },
  "Sapporo": { minLat: 42.95, maxLat: 43.15, minLon: 141.25, maxLon: 141.45, label: "SAPPORO HUB" },
  "Frankfurt": { minLat: 49.95, maxLat: 50.2, minLon: 8.5, maxLon: 8.8, label: "FRANKFURT BANKING CENTER" },
  "Berlin": { minLat: 52.4, maxLat: 52.65, minLon: 13.25, maxLon: 13.55, label: "BERLIN METRO" },
  "Munich": { minLat: 48.05, maxLat: 48.25, minLon: 11.45, maxLon: 11.7, label: "MUNICH TECH REGION" },
  "Hamburg": { minLat: 53.45, maxLat: 53.65, minLon: 9.85, maxLon: 10.15, label: "HAMBURG MARITIME HUB" },
  "Cologne": { minLat: 50.85, maxLat: 51.05, minLon: 6.85, maxLon: 7.1, label: "COLOGNE REGION" },
  "Sydney": { minLat: -34.0, maxLat: -33.7, minLon: 151.05, maxLon: 151.3, label: "SYDNEY HARBOUR SECTOR" },
  "Melbourne": { minLat: -37.95, maxLat: -37.7, minLon: 144.85, maxLon: 145.1, label: "MELBOURNE CBD" },
  "Brisbane": { minLat: -27.6, maxLat: -27.35, minLon: 152.9, maxLon: 153.15, label: "BRISBANE REGION" },
  "Perth": { minLat: -32.1, maxLat: -31.8, minLon: 115.75, maxLon: 116.0, label: "PERTH METRO" },
  "Toronto": { minLat: 43.55, maxLat: 43.85, minLon: -79.55, maxLon: -79.25, label: "TORONTO BAY STREET" },
  "Vancouver": { minLat: 49.2, maxLat: 49.35, minLon: -123.25, maxLon: -123.0, label: "VANCOUVER HUB" },
  "Montreal": { minLat: 45.4, maxLat: 45.65, minLon: -73.75, maxLon: -73.45, label: "MONTREAL METRO" },
  "Calgary": { minLat: 50.9, maxLat: 51.15, minLon: -114.2, maxLon: -113.9, label: "CALGARY SECTOR" },
  "Paris": { minLat: 48.75, maxLat: 48.95, minLon: 2.2, maxLon: 2.45, label: "PARIS LA DÉFENSE / BOURSE" },
  "Lyon": { minLat: 45.7, maxLat: 45.85, minLon: 4.75, maxLon: 4.95, label: "LYON REGION" },
  "Dubai": { minLat: 25.1, maxLat: 25.3, minLon: 55.2, maxLon: 55.4, label: "DUBAI DIFC FINANCIAL HUB" },
  "Abu Dhabi": { minLat: 24.35, maxLat: 24.55, minLon: 54.3, maxLon: 54.5, label: "ABU DHABI ADGM" },
  "Singapore": { minLat: 1.25, maxLat: 1.45, minLon: 103.75, maxLon: 103.95, label: "SINGAPORE MARINA BAY / CBD" },
  "Jurong East": { minLat: 1.3, maxLat: 1.36, minLon: 103.7, maxLon: 103.76, label: "JURONG EAST INNOVATION DISTRICT" }
};

export class ThreatMap {
  constructor(canvasId) {
    this.canvas = document.getElementById(canvasId);
    if (!this.canvas) return;
    this.ctx = this.canvas.getContext('2d');
    this.beacons = [
      { lat: 40.71, lon: -74.00, radius: 2, maxRadius: 28, alpha: 0.9, color: '#EF4444', status: 'BLOCKED', city: 'New York', country: 'United States' },
      { lat: 51.50, lon: -0.12, radius: 6, maxRadius: 24, alpha: 0.75, color: '#EF4444', status: 'BLOCKED', city: 'London', country: 'United Kingdom' },
      { lat: 19.07, lon: 72.87, radius: 10, maxRadius: 26, alpha: 0.85, color: '#F59E0B', status: 'FLAGGED', city: 'Mumbai', country: 'India' },
      { lat: 35.67, lon: 139.65, radius: 4, maxRadius: 22, alpha: 0.7, color: '#EF4444', status: 'BLOCKED', city: 'Tokyo', country: 'Japan' },
      { lat: -23.55, lon: -46.63, radius: 8, maxRadius: 24, alpha: 0.8, color: '#EF4444', status: 'BLOCKED', city: 'Sao Paulo', country: 'Brazil' }
    ];
    this.arcs = [];
    this.countryFilter = 'ALL';
    this.stateFilter = 'ALL';

    // Current camera viewport (interpolated)
    this.currentBounds = { ...REGION_BOUNDS.GLOBAL };
    // Target camera viewport (desired)
    this.targetBounds = { ...REGION_BOUNDS.GLOBAL };

    this.currentLabel = REGION_BOUNDS.GLOBAL.label;
    this.radarAngle = 0;

    this.resize();
    window.addEventListener('resize', () => this.resize());
    this.animate();
  }

  setCountryFilter(country) {
    this.setScope(country, 'ALL');
  }

  setScope(country, state) {
    this.countryFilter = country || 'ALL';
    this.stateFilter = state || 'ALL';

    // Pick target bounds based on granularity: State > Country > Global
    if (this.stateFilter !== 'ALL' && REGION_BOUNDS[this.stateFilter]) {
      this.targetBounds = { ...REGION_BOUNDS[this.stateFilter] };
      this.currentLabel = REGION_BOUNDS[this.stateFilter].label;
    } else if (this.countryFilter !== 'ALL' && REGION_BOUNDS[this.countryFilter]) {
      this.targetBounds = { ...REGION_BOUNDS[this.countryFilter] };
      this.currentLabel = REGION_BOUNDS[this.countryFilter].label;
    } else {
      this.targetBounds = { ...REGION_BOUNDS.GLOBAL };
      this.currentLabel = REGION_BOUNDS.GLOBAL.label;
    }

    // Filter active beacons
    this.beacons = this.beacons.filter(b => {
      const matchCountry = (this.countryFilter === 'ALL' || b.country === this.countryFilter);
      const matchState = (this.stateFilter === 'ALL' || !b.state || b.state === this.stateFilter);
      return matchCountry && matchState;
    });

    this.arcs = [];
  }

  resize() {
    if (!this.canvas || !this.canvas.parentElement) return;
    const rect = this.canvas.parentElement.getBoundingClientRect();
    this.width = rect.width || 300;
    this.height = Math.max(110, rect.height || 110);
    this.canvas.width = this.width * window.devicePixelRatio;
    this.canvas.height = this.height * window.devicePixelRatio;
    this.ctx.scale(window.devicePixelRatio, window.devicePixelRatio);
  }

  // Dynamic projection with smoothly interpolated bounding camera
  project(lat, lon) {
    const pad = 24;
    const drawW = this.width - pad * 2;
    const drawH = this.height - pad * 2;

    const b = this.currentBounds;
    const lonSpan = Math.max(0.001, b.maxLon - b.minLon);
    const latSpan = Math.max(0.001, b.maxLat - b.minLat);

    const x = pad + ((lon - b.minLon) / lonSpan) * drawW;
    const y = pad + ((b.maxLat - lat) / latSpan) * drawH;
    return { x, y };
  }

  addTransaction(enriched) {
    const loc = enriched.transaction.location;

    // Filter check
    if (this.countryFilter !== 'ALL' && loc.country !== this.countryFilter) return;
    if (this.stateFilter !== 'ALL' && loc.state && loc.state !== this.stateFilter) return;

    const { x, y } = this.project(loc.lat, loc.lon);
    const status = enriched.decision.status;
    const isBlocked = (status === 'BLOCKED');
    const isReview = (status === 'FLAGGED' || status === 'REVIEW' || status === 'UNDER_REVIEW' || status === 'IN_REVIEW');

    let color = '#10B981'; // Approved (emerald)
    if (isReview) color = '#F59E0B'; // Review (amber)
    if (isBlocked) color = '#EF4444'; // Blocked (crimson)

    this.beacons.push({
      lat: loc.lat,
      lon: loc.lon,
      radius: 2,
      maxRadius: isBlocked ? 32 : (isReview ? 24 : 18),
      alpha: 1.0,
      color,
      status: isBlocked ? 'BLOCKED' : (isReview ? 'REVIEW' : 'APPROVED'),
      city: loc.city,
      state: loc.state || '',
      country: loc.country
    });

    // Check for impossible travel arc
    const speed = enriched.decision.triggered_rules.some(r => r.includes('Impossible Travel'));
    if (speed && this.lastPoint) {
      this.arcs.push({
        lat1: this.lastPoint.lat,
        lon1: this.lastPoint.lon,
        lat2: loc.lat,
        lon2: loc.lon,
        progress: 0,
        color: '#fc081cff'
      });
    }

    this.lastPoint = { lat: loc.lat, lon: loc.lon };
  }

  animate() {
    this.ctx.clearRect(0, 0, this.width, this.height);

    // 1. Smooth camera interpolation
    const ease = 0.08;
    this.currentBounds.minLat += (this.targetBounds.minLat - this.currentBounds.minLat) * ease;
    this.currentBounds.maxLat += (this.targetBounds.maxLat - this.currentBounds.maxLat) * ease;
    this.currentBounds.minLon += (this.targetBounds.minLon - this.currentBounds.minLon) * ease;
    this.currentBounds.maxLon += (this.targetBounds.maxLon - this.currentBounds.maxLon) * ease;

    // 2. Rotate radar sweep
    this.radarAngle += 0.032;
    if (this.radarAngle >= Math.PI * 2) this.radarAngle = 0;

    // 3. Draw Cyber Radar Elements
    this.drawRadarGrid();
    this.drawRadarSweep();
    this.drawReferenceNodes();
    this.drawArcs();
    this.drawBeacons();
    this.drawHudOverlay();

    requestAnimationFrame(() => this.animate());
  }

  drawRadarGrid() {
    const cx = this.width / 2;
    const cy = this.height / 2;
    const maxR = Math.min(this.width, this.height) * 0.46;

    // Concentric tactical range rings (Electric violet & subtle slate-violet)
    this.ctx.strokeStyle = 'rgba(123, 97, 255, 0.16)';
    this.ctx.lineWidth = 1;

    for (let r = maxR * 0.25; r <= maxR; r += maxR * 0.25) {
      this.ctx.beginPath();
      this.ctx.arc(cx, cy, r, 0, Math.PI * 2);
      this.ctx.stroke();
    }

    // Crosshairs
    this.ctx.strokeStyle = 'rgba(195, 185, 255, 0.2)';
    this.ctx.beginPath();
    this.ctx.moveTo(cx - maxR, cy);
    this.ctx.lineTo(cx + maxR, cy);
    this.ctx.moveTo(cx, cy - maxR);
    this.ctx.lineTo(cx, cy + maxR);
    this.ctx.stroke();

    // Subtle background geo-grid
    this.ctx.strokeStyle = 'rgba(59, 55, 89, 0.08)';
    for (let x = 0; x < this.width; x += 45) {
      this.ctx.beginPath();
      this.ctx.moveTo(x, 0);
      this.ctx.lineTo(x, this.height);
      this.ctx.stroke();
    }
    for (let y = 0; y < this.height; y += 40) {
      this.ctx.beginPath();
      this.ctx.moveTo(0, y);
      this.ctx.lineTo(this.width, y);
      this.ctx.stroke();
    }
  }

  drawRadarSweep() {
    const cx = this.width / 2;
    const cy = this.height / 2;
    const maxR = Math.min(this.width, this.height) * 0.46;

    // Radar beam fan wedge
    const wedgeAngle = Math.PI * 0.25; // 45 degree fan
    const startAngle = this.radarAngle - wedgeAngle;

    const grad = this.ctx.createRadialGradient(cx, cy, 0, cx, cy, maxR);
    grad.addColorStop(0, 'rgba(123, 97, 255, 0.22)');
    grad.addColorStop(0.5, 'rgba(123, 97, 255, 0.07)');
    grad.addColorStop(1, 'rgba(123, 97, 255, 0.01)');

    this.ctx.save();
    this.ctx.beginPath();
    this.ctx.moveTo(cx, cy);
    this.ctx.arc(cx, cy, maxR, startAngle, this.radarAngle);
    this.ctx.closePath();
    this.ctx.fillStyle = grad;
    this.ctx.fill();

    // Sharp leading sweep edge line
    this.ctx.beginPath();
    this.ctx.moveTo(cx, cy);
    const endX = cx + Math.cos(this.radarAngle) * maxR;
    const endY = cy + Math.sin(this.radarAngle) * maxR;
    this.ctx.lineTo(endX, endY);
    this.ctx.strokeStyle = 'rgba(195, 185, 255, 0.75)';
    this.ctx.lineWidth = 1.5;
    this.ctx.stroke();
    this.ctx.restore();
  }

  drawReferenceNodes() {
    let hubs = [];

    // If focused on a specific country or state, render local hubs
    if (this.countryFilter === 'United States') {
      hubs = [
        { name: 'NYC (NY)', lat: 40.71, lon: -74.00 },
        { name: 'LAX (CA)', lat: 34.05, lon: -118.24 },
        { name: 'CHI (IL)', lat: 41.87, lon: -87.62 },
        { name: 'HOU (TX)', lat: 29.76, lon: -95.36 },
        { name: 'MIA (FL)', lat: 25.76, lon: -80.19 },
        { name: 'SEA (WA)', lat: 47.60, lon: -122.33 }
      ];
    } else if (this.countryFilter === 'Japan') {
      hubs = [
        { name: 'TYO (Tokyo)', lat: 35.67, lon: 139.65 },
        { name: 'OSA (Osaka)', lat: 34.69, lon: 135.50 },
        { name: 'KYO (Kyoto)', lat: 35.01, lon: 135.76 },
        { name: 'YOK (Kanagawa)', lat: 35.44, lon: 139.63 },
        { name: 'SPK (Hokkaido)', lat: 43.06, lon: 141.35 }
      ];
    } else if (this.countryFilter === 'India') {
      hubs = [
        { name: 'BOM (MH)', lat: 19.07, lon: 72.87 },
        { name: 'DEL (NCR)', lat: 28.61, lon: 77.20 },
        { name: 'BLR (KA)', lat: 12.97, lon: 77.59 },
        { name: 'HYD (TS)', lat: 17.38, lon: 78.48 },
        { name: 'MAA (TN)', lat: 13.08, lon: 80.27 },
        { name: 'CCU (WB)', lat: 22.57, lon: 88.36 }
      ];
    } else if (this.countryFilter === 'Germany') {
      hubs = [
        { name: 'FRA (Hesse)', lat: 50.11, lon: 8.68 },
        { name: 'BER (Berlin)', lat: 52.52, lon: 13.40 },
        { name: 'MUC (Bavaria)', lat: 48.13, lon: 11.58 },
        { name: 'HAM (Hamburg)', lat: 53.55, lon: 9.99 },
        { name: 'CGN (NRW)', lat: 50.93, lon: 6.96 }
      ];
    } else if (this.countryFilter === 'United Kingdom') {
      hubs = [
        { name: 'LON (London)', lat: 51.50, lon: -0.12 },
        { name: 'MAN (Manc)', lat: 53.48, lon: -2.24 },
        { name: 'EDI (Scot)', lat: 55.95, lon: -3.18 },
        { name: 'CWL (Wales)', lat: 51.48, lon: -3.17 }
      ];
    } else if (this.countryFilter === 'Canada') {
      hubs = [
        { name: 'YYZ (ON)', lat: 43.65, lon: -79.38 },
        { name: 'YVR (BC)', lat: 49.28, lon: -123.12 },
        { name: 'YUL (QC)', lat: 45.50, lon: -73.56 },
        { name: 'YYC (AB)', lat: 51.04, lon: -114.07 }
      ];
    } else if (this.countryFilter === 'Australia') {
      hubs = [
        { name: 'SYD (NSW)', lat: -33.86, lon: 151.20 },
        { name: 'MEL (VIC)', lat: -37.81, lon: 144.96 },
        { name: 'BNE (QLD)', lat: -27.46, lon: 153.02 },
        { name: 'PER (WA)', lat: -31.95, lon: 115.86 }
      ];
    } else {
      // Global Primary Centers
      hubs = [
        { name: 'NYC [US]', lat: 40.71, lon: -74.00 },
        { name: 'LON [UK]', lat: 51.50, lon: -0.12 },
        { name: 'TYO [JP]', lat: 35.67, lon: 139.65 },
        { name: 'FRA [DE]', lat: 50.11, lon: 8.68 },
        { name: 'BOM [IN]', lat: 19.07, lon: 72.87 },
        { name: 'SGP [SG]', lat: 1.35, lon: 103.81 },
        { name: 'DXB [AE]', lat: 25.20, lon: 55.27 },
        { name: 'SYD [AU]', lat: -33.86, lon: 151.20 },
        { name: 'SAO [BR]', lat: -23.55, lon: -46.63 },
        { name: 'TOR [CA]', lat: 43.65, lon: -79.38 }
      ];
    }

    hubs.forEach(h => {
      const p = this.project(h.lat, h.lon);
      if (p.x < 0 || p.x > this.width || p.y < 0 || p.y > this.height) return;

      this.ctx.beginPath();
      this.ctx.arc(p.x, p.y, 2.5, 0, Math.PI * 2);
      this.ctx.fillStyle = 'rgba(195, 185, 255, 0.75)';
      this.ctx.fill();

      this.ctx.font = '9px "JetBrains Mono", monospace';
      this.ctx.fillStyle = 'rgba(160, 158, 176, 0.55)';
      this.ctx.fillText(h.name, p.x + 5, p.y + 3);
    });
  }

  drawArcs() {
    for (let i = this.arcs.length - 1; i >= 0; i--) {
      const arc = this.arcs[i];
      arc.progress += 0.025;

      const p1 = this.project(arc.lat1, arc.lon1);
      const p2 = this.project(arc.lat2, arc.lon2);

      this.ctx.beginPath();
      this.ctx.moveTo(p1.x, p1.y);

      const cx = (p1.x + p2.x) / 2;
      const cy = Math.min(p1.y, p2.y) - 35;

      this.ctx.quadraticCurveTo(cx, cy, p2.x, p2.y);
      this.ctx.strokeStyle = `rgba(224, 108, 117, ${Math.max(0, 1.0 - arc.progress)})`;
      this.ctx.lineWidth = 2;
      this.ctx.setLineDash([4, 4]);
      this.ctx.stroke();
      this.ctx.setLineDash([]);

      if (arc.progress >= 1.0) {
        this.arcs.splice(i, 1);
      }
    }
  }

  drawBeacons() {
    // Keep active background threat pulses on global surveillance matching screenshot
    if (this.countryFilter === 'ALL' && this.beacons.length < 4 && Math.random() < 0.04) {
      const hubs = [
        { lat: 40.71, lon: -74.00, city: 'New York', country: 'United States' },
        { lat: 51.50, lon: -0.12, city: 'London', country: 'United Kingdom' },
        { lat: 19.07, lon: 72.87, city: 'Mumbai', country: 'India' },
        { lat: -23.55, lon: -46.63, city: 'Sao Paulo', country: 'Brazil' },
        { lat: 35.67, lon: 139.65, city: 'Tokyo', country: 'Japan' }
      ];
      const pick = hubs[Math.floor(Math.random() * hubs.length)];
      this.beacons.push({
        lat: pick.lat,
        lon: pick.lon,
        radius: 2,
        maxRadius: 26,
        alpha: 0.9,
        color: '#EF4444',
        status: 'BLOCKED',
        city: pick.city,
        country: pick.country
      });
    }

    for (let i = this.beacons.length - 1; i >= 0; i--) {
      const b = this.beacons[i];
      const p = this.project(b.lat, b.lon);

      b.radius += 0.5;
      b.alpha -= 0.012;

      if (p.x >= 0 && p.x <= this.width && p.y >= 0 && p.y <= this.height) {
        // Ripple wave
        this.ctx.beginPath();
        this.ctx.arc(p.x, p.y, b.radius, 0, Math.PI * 2);
        this.ctx.strokeStyle = b.color.replace(')', `, ${b.alpha})`).replace('rgb', 'rgba');
        this.ctx.lineWidth = 1.6;
        this.ctx.stroke();

        // Pulsing Core
        this.ctx.beginPath();
        this.ctx.arc(p.x, p.y, 3.5, 0, Math.PI * 2);
        this.ctx.fillStyle = b.color;
        this.ctx.fill();

        // Tactical label for flagged/blocked threats
        if (b.status === 'BLOCKED' && b.alpha > 0.4) {
          this.ctx.font = '8px "JetBrains Mono", monospace';
          this.ctx.fillStyle = '#E06C75';
          const tag = b.state ? `${b.city}, ${b.state}` : b.city;
          this.ctx.fillText(`🚨 THREAT [${tag}]`, p.x + 6, p.y - 4);
        }
      }

      if (b.alpha <= 0) {
        this.beacons.splice(i, 1);
      }
    }
  }

  drawHudOverlay() {
    // Top-left tactical scope readout
    this.ctx.save();
    this.ctx.font = '10px "JetBrains Mono", monospace';
    this.ctx.fillStyle = 'rgba(195, 185, 255, 0.9)';
    this.ctx.fillText(`RADAR LOCK // ${this.currentLabel}`, 12, 18);

    this.ctx.font = '8.5px "JetBrains Mono", monospace';
    this.ctx.fillStyle = 'rgba(148, 145, 166, 0.7)';
    const b = this.currentBounds;
    const coords = `LAT: ${b.minLat.toFixed(1)}° to ${b.maxLat.toFixed(1)}° | LON: ${b.minLon.toFixed(1)}° to ${b.maxLon.toFixed(1)}°`;
    this.ctx.fillText(coords, 12, 32);

    // Top-right sweep status
    const deg = Math.round((this.radarAngle * 180) / Math.PI);
    this.ctx.textAlign = 'right';
    this.ctx.fillStyle = 'rgba(123, 97, 255, 0.85)';
    this.ctx.fillText(`BEAM AZIMUTH: ${deg.toString().padStart(3, '0')}°`, this.width - 12, 18);
    this.ctx.restore();
  }
}
