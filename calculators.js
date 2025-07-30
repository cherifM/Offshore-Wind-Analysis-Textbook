// Offshore Wind Analysis Calculators
// Interactive calculation tools for wind resource assessment

// Weibull Distribution Calculator
function calculateWeibull(k, A, v) {
    // Probability density function
    const pdf = (k/A) * Math.pow(v/A, k-1) * Math.exp(-Math.pow(v/A, k));
    
    // Cumulative distribution function
    const cdf = 1 - Math.exp(-Math.pow(v/A, k));
    
    return { pdf, cdf };
}

// Wind Power Density Calculator
function calculateWindPowerDensity(rho, v) {
    // P/A = 0.5 * rho * v^3
    return 0.5 * rho * Math.pow(v, 3);
}

// Shear Exponent Calculator
function calculateShearExponent(v1, h1, v2, h2) {
    // alpha = ln(v2/v1) / ln(h2/h1)
    return Math.log(v2/v1) / Math.log(h2/h1);
}

// Power Law Extrapolation
function powerLawExtrapolation(vRef, hRef, hTarget, alpha) {
    // v = vRef * (hTarget/hRef)^alpha
    return vRef * Math.pow(hTarget/hRef, alpha);
}

// Log Law Extrapolation
function logLawExtrapolation(vRef, hRef, hTarget, z0) {
    // v = vRef * ln(hTarget/z0) / ln(hRef/z0)
    return vRef * Math.log(hTarget/z0) / Math.log(hRef/z0);
}

// Turbulence Intensity Calculator
function calculateTurbulenceIntensity(sigma, vMean) {
    return sigma / vMean;
}

// Annual Energy Production Calculator
function calculateAEP(powerCurve, windDistribution, availability = 0.97) {
    let aep = 0;
    const hoursPerYear = 8760;
    
    for (let i = 0; i < windDistribution.length; i++) {
        const windSpeed = windDistribution[i].speed;
        const frequency = windDistribution[i].frequency;
        const power = getPowerAtSpeed(powerCurve, windSpeed);
        aep += power * frequency * hoursPerYear;
    }
    
    return aep * availability;
}

// Helper function to get power at specific wind speed
function getPowerAtSpeed(powerCurve, speed) {
    // Linear interpolation between power curve points
    for (let i = 0; i < powerCurve.length - 1; i++) {
        if (speed >= powerCurve[i].speed && speed <= powerCurve[i + 1].speed) {
            const fraction = (speed - powerCurve[i].speed) / 
                           (powerCurve[i + 1].speed - powerCurve[i].speed);
            return powerCurve[i].power + 
                   fraction * (powerCurve[i + 1].power - powerCurve[i].power);
        }
    }
    
    // Outside range
    if (speed < powerCurve[0].speed) return 0;
    if (speed > powerCurve[powerCurve.length - 1].speed) return 0;
    
    return powerCurve[powerCurve.length - 1].power;
}

// Capacity Factor Calculator
function calculateCapacityFactor(aep, ratedPower) {
    const maxProduction = ratedPower * 8760; // kWh
    return aep / maxProduction;
}

// Wake Loss Calculator (Simple Jensen Model)
function calculateWakeLoss(Ct, k, x, D) {
    // Velocity deficit = 1 - sqrt(1 - Ct) / (1 + k*x/D)^2
    const a = (1 - Math.sqrt(1 - Ct)) / 2;
    const deficit = 2 * a / Math.pow(1 + k * x / D, 2);
    return deficit;
}

// Richardson Number Calculator
function calculateRichardsonNumber(g, theta, dThetaDz, dUdz) {
    // Ri = (g/theta) * (dtheta/dz) / (du/dz)^2
    return (g / theta) * dThetaDz / Math.pow(dUdz, 2);
}

// Obukhov Length Calculator
function calculateObukhovLength(uStar, theta, heatFlux, k = 0.4, g = 9.81) {
    // L = -u*^3 * theta / (k * g * heat_flux)
    return -Math.pow(uStar, 3) * theta / (k * g * heatFlux);
}

// Wind Direction Statistics
function calculateWindDirectionStats(directions) {
    // Convert to unit vectors
    let sumX = 0, sumY = 0;
    
    directions.forEach(dir => {
        const rad = dir * Math.PI / 180;
        sumX += Math.cos(rad);
        sumY += Math.sin(rad);
    });
    
    const meanX = sumX / directions.length;
    const meanY = sumY / directions.length;
    
    // Mean direction
    let meanDir = Math.atan2(meanY, meanX) * 180 / Math.PI;
    if (meanDir < 0) meanDir += 360;
    
    // Resultant vector length
    const r = Math.sqrt(meanX * meanX + meanY * meanY);
    
    // Standard deviation (Yamartino method)
    const epsilon = Math.sqrt(1 - r * r);
    const sigma = Math.asin(epsilon) * 180 / Math.PI * (1 + 0.1547 * Math.pow(epsilon, 3));
    
    return { meanDirection: meanDir, standardDeviation: sigma, resultantLength: r };
}

// Economic Calculations
function calculateLCOE(capex, opex, aep, discountRate, lifetime) {
    // LCOE = (CAPEX + NPV(OPEX)) / NPV(AEP)
    let npvOpex = 0;
    let npvAep = 0;
    
    for (let year = 1; year <= lifetime; year++) {
        const discountFactor = Math.pow(1 + discountRate, -year);
        npvOpex += opex * discountFactor;
        npvAep += aep * discountFactor;
    }
    
    return (capex + npvOpex) / npvAep;
}

// Extreme Wind Speed Calculator (Gumbel Distribution)
function calculateExtremeWind(annualMaxima, returnPeriod) {
    const n = annualMaxima.length;
    
    // Calculate mean and standard deviation
    const mean = annualMaxima.reduce((a, b) => a + b) / n;
    const variance = annualMaxima.reduce((sum, x) => sum + Math.pow(x - mean, 2), 0) / (n - 1);
    const stdDev = Math.sqrt(variance);
    
    // Gumbel parameters
    const beta = stdDev * Math.sqrt(6) / Math.PI;
    const mu = mean - 0.5772 * beta;
    
    // Return level
    const yT = -Math.log(-Math.log(1 - 1/returnPeriod));
    const extremeSpeed = mu + beta * yT;
    
    return extremeSpeed;
}

// Air Density Calculator
function calculateAirDensity(pressure, temperature, humidity = 0) {
    // Using ideal gas law with humidity correction
    const R = 287.05; // J/(kg·K) for dry air
    const Rv = 461.495; // J/(kg·K) for water vapor
    
    // Saturation vapor pressure (Magnus formula)
    const es = 611.2 * Math.exp(17.67 * temperature / (temperature + 243.5));
    
    // Actual vapor pressure
    const e = humidity / 100 * es;
    
    // Virtual temperature
    const Tv = (temperature + 273.15) / (1 - (e/pressure) * (1 - R/Rv));
    
    // Air density
    return pressure / (R * Tv);
}

// MCP Variance Ratio Method
function mcpVarianceRatio(siteData, refData) {
    // Calculate means
    const siteMean = siteData.reduce((a, b) => a + b) / siteData.length;
    const refMean = refData.reduce((a, b) => a + b) / refData.length;
    
    // Calculate standard deviations
    const siteStd = Math.sqrt(siteData.reduce((sum, x) => sum + Math.pow(x - siteMean, 2), 0) / (siteData.length - 1));
    const refStd = Math.sqrt(refData.reduce((sum, x) => sum + Math.pow(x - refMean, 2), 0) / (refData.length - 1));
    
    // Calculate correlation
    let sumProduct = 0;
    for (let i = 0; i < siteData.length; i++) {
        sumProduct += (siteData[i] - siteMean) * (refData[i] - refMean);
    }
    const correlation = sumProduct / ((siteData.length - 1) * siteStd * refStd);
    
    // Variance ratio parameters
    const slope = correlation * siteStd / refStd;
    const intercept = siteMean - slope * refMean;
    
    return { slope, intercept, correlation, siteStd, refStd };
}

// Export functions for use in HTML
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        calculateWeibull,
        calculateWindPowerDensity,
        calculateShearExponent,
        powerLawExtrapolation,
        logLawExtrapolation,
        calculateTurbulenceIntensity,
        calculateAEP,
        calculateCapacityFactor,
        calculateWakeLoss,
        calculateRichardsonNumber,
        calculateObukhovLength,
        calculateWindDirectionStats,
        calculateLCOE,
        calculateExtremeWind,
        calculateAirDensity,
        mcpVarianceRatio
    };
}