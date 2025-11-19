/**
 * Mock data generator for DENSO Demand Forecasting Dashboard
 * Provides comprehensive test data for all dashboard components
 */

// Helper function to generate dates
const generateDates = (days) => {
  const dates = [];
  const today = new Date();
  for (let i = -30; i < days; i++) {
    const date = new Date(today);
    date.setDate(today.getDate() + i);
    dates.push(date.toISOString().split('T')[0]);
  }
  return dates;
};

// Helper to generate random number
const random = (min, max) => Math.floor(Math.random() * (max - min + 1)) + min;

// Helper to generate weekly time series data for products
const generateWeeklyTimeSeries = (baseValue, historicalWeeks = 12, forecastWeeks = 8, options = {}) => {
  const {
    trendDirection = 'up',    // 'up', 'down', 'stable'
    seasonalStrength = 0.15,  // 0-1, độ mạnh của biến động mùa vụ
    volatility = 0.1,         // 0-1, độ biến động ngẫu nhiên
    growthRate = 0.02         // tỷ lệ tăng trưởng dự báo
  } = options;
  
  const data = [];
  const today = new Date();
  
  // Historical data (past 12 weeks = ~3 months)
  for (let i = -historicalWeeks; i < 0; i++) {
    const date = new Date(today);
    date.setDate(today.getDate() + (i * 7)); // Weekly intervals
    
    // Seasonal variation với pattern khác nhau
    const seasonalFactor = 1 + Math.sin((i / 4) + (baseValue % 10)) * seasonalStrength;
    
    // Trend factor cho historical data
    let trendFactor = 1;
    if (trendDirection === 'up') {
      trendFactor = 1 + ((-i / historicalWeeks) * growthRate * 3); // Tăng dần về hiện tại
    } else if (trendDirection === 'down') {
      trendFactor = 1 - ((-i / historicalWeeks) * growthRate * 2);
    }
    
    const actual = Math.round(
      baseValue * seasonalFactor * trendFactor + 
      random(-baseValue * volatility, baseValue * volatility)
    );
    
    const weekNumber = historicalWeeks + i + 1;
    data.push({
      date: date.toISOString().split('T')[0],
      week: `Tuần ${weekNumber}`,
      weekLabel: `T${weekNumber}`,
      actual: actual,
      forecast: null,
      upperBound: null,
      lowerBound: null,
      isHistorical: true
    });
  }
  
  // Forecast data (next 8 weeks = ~2 months)
  const lastActual = data[data.length - 1].actual;
  for (let i = 0; i < forecastWeeks; i++) {
    const date = new Date(today);
    date.setDate(today.getDate() + (i * 7));
    
    let trendFactor = 1;
    if (trendDirection === 'up') {
      trendFactor = 1 + (i * growthRate);
    } else if (trendDirection === 'down') {
      trendFactor = 1 - (i * growthRate * 0.8);
    } else {
      trendFactor = 1 + (i * growthRate * 0.3); // Stable với tăng nhẹ
    }
    
    const forecast = Math.round(lastActual * trendFactor);
    const confidenceWidth = trendDirection === 'stable' ? 0.08 : 0.12;
    
    const weekNumber = historicalWeeks + i + 1;
    data.push({
      date: date.toISOString().split('T')[0],
      week: `Tuần ${weekNumber}`,
      weekLabel: `T${weekNumber}`,
      actual: null,
      forecast: forecast,
      upperBound: Math.round(forecast * (1 + confidenceWidth)),
      lowerBound: Math.round(forecast * (1 - confidenceWidth)),
      isHistorical: false
    });
  }
  
  return data;
};

// ========== TIER 1: KPI Overview Data ==========
export const mockKPIs = [
   {
      id: 'forecast_accuracy',
      title: 'Forecast Accuracy',
      icon: '🎯',
      value: 89,
      change: 4,
      trend: 'up',
      status: 'good'
    },
    {
      id: 'demand_change',
      title: 'Demand Change',
      icon: '📈',
      value: 8,
      change: 2,
      trend: 'up',
      status: 'good'
    },
    {
      id: 'production_load',
      title: 'Production Load',
      icon: '🏭',
      value: 76,
      change: -3,
      trend: 'down',
      status: 'warning'
    },
    {
      id: 'inventory_cover',
      title: 'Inventory Cover',
      icon: '📦',
      value: 32, // ngày tồn kho
      change: 5,
      trend: 'up',
      status: 'good'
    },
    {
      id: 'stockout_risk',
      title: 'Stockout Risk (Top SKUs)',
      icon: '⚠️',
      value: '5 SKUs',
      riskScore: 40, // % lấp đầy thanh risk-bar
      change: -10,
      trend: 'down',
      status: 'warning'
    },
    {
      id: 'service_level',
      title: 'Service Level (OTIF)',
      icon: '🚚',
      value: 96,
      change: 1,
      trend: 'up',
      status: 'excellent'
    },
    {
      id: 'data_coverage',
      title: 'Data Coverage (SKU-Region)',
      icon: '🧩',
      value: 92,
      change: 3,
      trend: 'up',
      status: 'good'
    },
    {
      id: 'data_latency',
      title: 'Data Freshness',
      icon: '⏱️',
      value: 2, // 2 giờ từ lần ETL/forecast gần nhất
      change: -1,
      trend: 'down',
      status: 'excellent'
    }
];

// ========== TIER 2: Demand Forecasting Data ==========
export const mockForecastData = {
  // Time series data for main chart (aggregate view - ALSO WEEKLY)
  timeSeries: generateWeeklyTimeSeries(2650, 12, 8, {
    trendDirection: 'up',
    seasonalStrength: 0.15,
    volatility: 0.10,
    growthRate: 0.022
  }),
  
  // Products breakdown with individual time series
  productBreakdown: [
    {
      product_id: 'BUGI-IRIDIUM-VCH20',
      name: 'Bugi Iridium Tough VCH20',
      category: 'Spark Plugs',
      forecast: 3200,
      change: 12.3,
      trend: 'up',
      confidence: 95,
      risk: 'Low',
      timeSeries: generateWeeklyTimeSeries(750, 12, 8, {
        trendDirection: 'up',
        seasonalStrength: 0.12,
        volatility: 0.08,
        growthRate: 0.025
      })
    },
    {
      product_id: 'BUGI-PLATIN-PK16TT',
      name: 'Bugi Platin PK16TT',
      category: 'Spark Plugs',
      forecast: 2400,
      change: 14.3,
      trend: 'up',
      confidence: 94,
      risk: 'Low',
      timeSeries: generateWeeklyTimeSeries(550, 12, 8, {
        trendDirection: 'up',
        seasonalStrength: 0.18,
        volatility: 0.12,
        growthRate: 0.03
      })
    },
    {
      product_id: 'AC-COMPRESSOR-6SEU14C',
      name: 'Máy Nén Điều Hòa 6SEU14C',
      category: 'AC System',
      forecast: 2100,
      change: 16.7,
      trend: 'up',
      confidence: 92,
      risk: 'Medium',
      timeSeries: generateWeeklyTimeSeries(480, 12, 8, {
        trendDirection: 'up',
        seasonalStrength: 0.25, // Mùa vụ mạnh (điều hòa)
        volatility: 0.15,
        growthRate: 0.035
      })
    },
    {
      product_id: 'AC-EVAPORATOR-CORE',
      name: 'Giàn Lạnh Evaporator',
      category: 'AC System',
      forecast: 1650,
      change: 10.0,
      trend: 'up',
      confidence: 95,
      risk: 'Low',
      timeSeries: generateWeeklyTimeSeries(380, 12, 8, {
        trendDirection: 'stable',
        seasonalStrength: 0.20,
        volatility: 0.10,
        growthRate: 0.015
      })
    },
    {
      product_id: 'AC-CONDENSER-CORE',
      name: 'Giàn Nóng Condenser',
      category: 'AC System',
      forecast: 1550,
      change: 6.9,
      trend: 'up',
      confidence: 96,
      risk: 'Low',
      timeSeries: generateWeeklyTimeSeries(360, 12, 8, {
        trendDirection: 'stable',
        seasonalStrength: 0.15,
        volatility: 0.08,
        growthRate: 0.012
      })
    }
  ],
  
  // Heatmap data (monthly demand by category)
  heatmap: [
    {
      category: 'Spark Plugs',
      values: [
        { month: 'Jan', value: 4500, intensity: 0.6 },
        { month: 'Feb', value: 4800, intensity: 0.65 },
        { month: 'Mar', value: 5200, intensity: 0.75 },
        { month: 'Apr', value: 5500, intensity: 0.85 },
        { month: 'May', value: 5300, intensity: 0.8 },
        { month: 'Jun', value: 5000, intensity: 0.7 }
      ]
    },
    {
      category: 'AC System',
      values: [
        { month: 'Jan', value: 3200, intensity: 0.4 },
        { month: 'Feb', value: 3500, intensity: 0.5 },
        { month: 'Mar', value: 4200, intensity: 0.7 },
        { month: 'Apr', value: 5000, intensity: 0.9 },
        { month: 'May', value: 5500, intensity: 1.0 },
        { month: 'Jun', value: 5800, intensity: 1.0 }
      ]
    },
    {
      category: 'Filters',
      values: [
        { month: 'Jan', value: 2800, intensity: 0.5 },
        { month: 'Feb', value: 2900, intensity: 0.55 },
        { month: 'Mar', value: 3100, intensity: 0.6 },
        { month: 'Apr', value: 3300, intensity: 0.65 },
        { month: 'May', value: 3200, intensity: 0.6 },
        { month: 'Jun', value: 3000, intensity: 0.55 }
      ]
    },
    {
      category: 'Sensors',
      values: [
        { month: 'Jan', value: 1900, intensity: 0.3 },
        { month: 'Feb', value: 2000, intensity: 0.35 },
        { month: 'Mar', value: 2200, intensity: 0.4 },
        { month: 'Apr', value: 2400, intensity: 0.5 },
        { month: 'May', value: 2300, intensity: 0.45 },
        { month: 'Jun', value: 2100, intensity: 0.4 }
      ]
    }
  ],
  
  // Model performance metrics
  metrics: [
    {
      name: 'MAPE',
      value: '5.8%',
      description: 'Mean Absolute Percentage Error',
      status: 'excellent'
    },
    {
      name: 'RMSE',
      value: '287',
      description: 'Root Mean Squared Error',
      status: 'good'
    },
    {
      name: 'R²',
      value: '0.94',
      description: 'Coefficient of Determination',
      status: 'excellent'
    }
  ]
};

// ========== TIER 3: Risk & News Intelligence ==========
const mockNewsRisksList = [
  {
    id: 1,
    title: 'Tắc nghẽn cảng Busan gây chậm trễ 48 giờ trong vận chuyển',
    summary: 'Cảng Busan đang đối mặt với tình trạng quá tải nghiêm trọng, ảnh hưởng đến lịch trình sản xuất Q1/2025 cho bugi và linh kiện AC.',
    source: 'Nikkei Asia',
    date: '2025-01-15T08:30:00Z',
    risk_score: 82,
    category: 'supply_chain',
    category_name: 'Chuỗi cung ứng',
    tags: ['vận chuyển', 'chậm trễ', 'hàn quốc'],
    impact: 'negative',
    affected_products: ['BUGI-IRIDIUM-VCH20', 'BUGI-PLATIN-PK16TT']
  },
  {
    id: 2,
    title: 'Giá thép tăng vọt 15% do Trung Quốc cắt giảm sản xuất',
    summary: 'Các nhà máy thép Trung Quốc giảm công suất sản xuất, dẫn đến giá thép toàn cầu tăng mạnh, ảnh hưởng đến chi phí sản xuất máy nén điều hòa.',
    source: 'Reuters',
    date: '2025-01-14T10:15:00Z',
    risk_score: 72,
    category: 'supply_chain',
    category_name: 'Chuỗi cung ứng',
    tags: ['thép', 'giá cả', 'trung quốc'],
    impact: 'negative',
    affected_products: ['AC-COMPRESSOR-6SEU14C']
  },
  {
    id: 3,
    title: 'Thị trường ô tô Việt Nam tăng trưởng 18% so với cùng kỳ',
    summary: 'Doanh số bán ô tô Q4/2024 tại Việt Nam đạt mức tăng trưởng ấn tượng, tạo triển vọng tích cực cho nhu cầu linh kiện thay thế.',
    source: 'VnExpress',
    date: '2025-01-13T14:20:00Z',
    risk_score: 35,
    category: 'market',
    category_name: 'Thị trường',
    tags: ['việt nam', 'tăng trưởng', 'ô tô'],
    impact: 'positive',
    affected_products: ['Tất cả sản phẩm']
  },
  {
    id: 4,
    title: 'Bão nhiệt đới tiến gần các trung tâm sản xuất Đông Nam Á',
    summary: 'Cơn bão mạnh đang di chuyển về phía các khu công nghiệp tại Thái Lan, có thể gây gián đoạn chuỗi cung ứng linh kiện điều hòa.',
    source: 'Weather Channel',
    date: '2025-01-12T06:45:00Z',
    risk_score: 68,
    category: 'weather',
    category_name: 'Thời tiết',
    tags: ['bão', 'thời tiết', 'sản xuất'],
    impact: 'negative',
    affected_products: ['AC-EVAPORATOR-CORE', 'AC-CONDENSER-CORE']
  },
  {
    id: 5,
    title: 'Tỷ lệ sử dụng xe điện đạt 25% tại thị trường đô thị Việt Nam',
    summary: 'Xu hướng chuyển đổi sang xe điện đang tăng nhanh ở các thành phố lớn, ảnh hưởng đến nhu cầu bugi nhưng duy trì ổn định cho hệ thống AC.',
    source: 'Vietnam Automotive',
    date: '2025-01-11T09:00:00Z',
    risk_score: 55,
    category: 'market',
    category_name: 'Thị trường',
    tags: ['xe điện', 'xu hướng', 'việt nam'],
    impact: 'neutral',
    affected_products: ['BUGI-IRIDIUM-VCH20', 'BUGI-PLATIN-PK16TT']
  },
  {
    id: 6,
    title: 'Đối thủ cạnh tranh công bố chiến dịch giảm giá 20%',
    summary: 'Một thương hiệu cạnh tranh lớn vừa khởi động chương trình khuyến mãi mạnh tay, đe dọa thị phần của DENSO trong phân khúc bugi.',
    source: 'Industry Weekly',
    date: '2025-01-10T11:30:00Z',
    risk_score: 78,
    category: 'competition',
    category_name: 'Cạnh tranh',
    tags: ['đối thủ', 'giá cả', 'thị phần'],
    impact: 'negative',
    affected_products: ['BUGI-IRIDIUM-VCH20', 'BUGI-PLATIN-PK16TT']
  },
  {
    id: 7,
    title: 'Chính phủ gia hạn ưu đãi cho linh kiện ô tô xanh',
    summary: 'Bộ Công Thương mở rộng chương trình hỗ trợ sản xuất linh kiện thân thiện môi trường, tạo cơ hội cho DENSO tiếp cận nguồn vốn ưu đãi.',
    source: 'Bộ Công Thương',
    date: '2025-01-09T15:00:00Z',
    risk_score: 25,
    category: 'policy',
    category_name: 'Chính sách',
    tags: ['chính phủ', 'ưu đãi', 'xanh'],
    impact: 'positive',
    affected_products: ['Tất cả sản phẩm']
  }
];

// Wrap news risks with timeline and keywords
export const mockNewsRisks = {
  news: mockNewsRisksList,
  timeline: generateDates(14).map((date, i) => ({
    date: new Date(date).toLocaleDateString('vi-VN', { month: 'short', day: 'numeric' }),
    count: random(2, 8),
    avg_risk: random(40, 80)
  })),
  keywords: [
    { word: 'Cảng', frequency: 0.9 },
    { word: 'Thép', frequency: 0.7 },
    { word: 'EV/Điện', frequency: 0.6 },
    { word: 'Bão/Thời tiết', frequency: 0.5 },
    { word: 'Cạnh tranh', frequency: 0.8 },
    { word: 'Tăng trưởng', frequency: 0.4 },
    { word: 'Giá cả', frequency: 0.7 },
    { word: 'Ưu đãi', frequency: 0.3 }
  ]
};

// Risk timeline data
export const mockRiskTimeline = generateDates(30).map((date, i) => ({
  date,
  riskCount: random(1, 5),
  highSeverity: random(0, 2),
  mediumSeverity: random(0, 2),
  lowSeverity: random(0, 2),
  avgSentiment: (Math.random() * 2 - 1).toFixed(2) // -1 to 1
}));

// Top risk keywords
export const mockRiskKeywords = [
  { word: 'delay', count: 12, trend: 'up' },
  { word: 'price increase', count: 8, trend: 'up' },
  { word: 'shortage', count: 6, trend: 'stable' },
  { word: 'competition', count: 5, trend: 'up' },
  { word: 'weather', count: 4, trend: 'down' },
  { word: 'regulation', count: 3, trend: 'stable' },
  { word: 'logistics', count: 7, trend: 'up' },
  { word: 'market growth', count: 5, trend: 'stable' }
];

// ========== TIER 4: Action Recommendations ==========
export const mockActionRecommendations = [
  {
    id: 1,
    priority: 'high',
    severity: 'critical',
    title: 'Secure alternative shipping route to mitigate port congestion',
    description: 'Yokohama port delays threaten Q1 production schedule. Recommend expediting shipments through alternative ports.',
    estimatedImpact: 'Prevent $450K loss from production delays',
    affectedProducts: ['BUGI-IRIDIUM-VCH20', 'BUGI-PLATIN-PK16TT'],
    deadline: '2025-01-20',
    status: 'pending',
    actionItems: [
      'Contact logistics partner for alternative routes',
      'Negotiate expedited customs clearance',
      'Update production schedule with 5-day buffer'
    ]
  },
  {
    id: 2,
    priority: 'high',
    severity: 'warning',
    title: 'Increase production capacity by 15% to meet Q2 demand forecast',
    description: 'Forecasted demand spike in Q2 exceeds current production capacity. Recommend adding overtime shifts or contracting third-party manufacturers.',
    estimatedImpact: 'Capture additional $680K revenue from demand surge',
    affectedProducts: ['AC-COMPRESSOR-6SEU14C', 'AC-EVAPORATOR-CORE'],
    deadline: '2025-02-01',
    status: 'in_progress',
    actionItems: [
      'Schedule overtime shifts for Lines A & B',
      'Evaluate third-party manufacturing partners',
      'Secure additional raw material inventory'
    ]
  },
  {
    id: 3,
    priority: 'medium',
    severity: 'warning',
    title: 'Launch promotional campaign to counter competitor price reduction',
    description: 'Competitor launched 20% price cut. Recommend targeted promotions and value-added services to retain market share.',
    estimatedImpact: 'Prevent 8-12% market share erosion',
    affectedProducts: ['BUGI-IRIDIUM-VCH20', 'BUGI-PLATIN-PK16TT'],
    deadline: '2025-01-25',
    status: 'pending',
    actionItems: [
      'Design 10-15% discount campaign for key distributors',
      'Highlight premium quality and warranty benefits',
      'Bundle spark plugs with maintenance services'
    ]
  },
  {
    id: 4,
    priority: 'medium',
    severity: 'info',
    title: 'Hedge steel purchases to mitigate raw material cost surge',
    description: 'Steel prices increased 15% and projected to rise further. Recommend forward contracts or bulk purchasing.',
    estimatedImpact: 'Save $120K in Q2 material costs',
    affectedProducts: ['AC-COMPRESSOR-6SEU14C'],
    deadline: '2025-01-30',
    status: 'pending',
    actionItems: [
      'Negotiate 6-month forward contract with steel supplier',
      'Evaluate alternative materials if feasible',
      'Lock in current pricing for Q2 needs'
    ]
  },
  {
    id: 5,
    priority: 'low',
    severity: 'info',
    title: 'Optimize inventory distribution to reduce stockout risk',
    description: 'Regional inventory analysis shows imbalances. Recommend redistributing stock to high-demand areas.',
    estimatedImpact: 'Improve service level by 5-8%',
    affectedProducts: ['all'],
    deadline: '2025-02-10',
    status: 'pending',
    actionItems: [
      'Transfer 500 units from Hanoi to Ho Chi Minh City',
      'Increase safety stock in Da Nang warehouse',
      'Implement demand-driven inventory allocation'
    ]
  },
  {
    id: 6,
    priority: 'low',
    severity: 'success',
    title: 'Apply for government green manufacturing incentives',
    description: 'New government program offers subsidies for eco-friendly production. Deadline approaching.',
    estimatedImpact: 'Potential $200K subsidy for facility upgrades',
    affectedProducts: ['all'],
    deadline: '2025-02-15',
    status: 'pending',
    actionItems: [
      'Prepare application documents',
      'Document current environmental practices',
      'Submit by February 5 deadline'
    ]
  }
];

// ========== Market Regions Data ==========
export const mockRegions = [
  {
    id: 'hanoi',
    name: 'Hanoi',
    demandIndex: 1.2,
    inventoryCover: 32,
    riskLevel: 'low',
    topProducts: ['BUGI-IRIDIUM-VCH20', 'AC-COMPRESSOR-6SEU14C']
  },
  {
    id: 'hcmc',
    name: 'Ho Chi Minh City',
    demandIndex: 1.8,
    inventoryCover: 18,
    riskLevel: 'high',
    topProducts: ['AC-COMPRESSOR-6SEU14C', 'AC-EVAPORATOR-CORE']
  },
  {
    id: 'danang',
    name: 'Da Nang',
    demandIndex: 1.0,
    inventoryCover: 28,
    riskLevel: 'medium',
    topProducts: ['BUGI-PLATIN-PK16TT', 'AC-CONDENSER-CORE']
  },
  {
    id: 'haiphong',
    name: 'Hai Phong',
    demandIndex: 0.9,
    inventoryCover: 35,
    riskLevel: 'low',
    topProducts: ['BUGI-IRIDIUM-VCH20', 'BUGI-PLATIN-PK16TT']
  }
];

// ========== Product Categories ==========
export const mockCategories = [
  { id: 'spark_plugs', name: 'Spark Plugs', count: 2 },
  { id: 'ac_system', name: 'AC System', count: 3 },
  { id: 'filters', name: 'Filters', count: 4 },
  { id: 'sensors', name: 'Sensors', count: 3 }
];

// Export all mock data
export const mockData = {
  kpis: mockKPIs,
  forecast: mockForecastData,
  newsRisks: mockNewsRisks,
  actions: mockActionRecommendations,
  regions: mockRegions,
  categories: mockCategories
};

export default mockData;
