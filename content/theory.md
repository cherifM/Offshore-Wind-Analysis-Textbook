---
title: Theory
header_title: Theoretical Foundations
icon: 🌬️
subtitle: Understanding Wind Physics and Atmospheric Dynamics
---

# Wind Resource Fundamentals

## Introduction

Wind energy is one of the fastest-growing renewable energy sources worldwide. Understanding the theoretical foundations of wind behavior is crucial for successful offshore wind farm development.

## Wind Formation

Wind is caused by differences in atmospheric pressure, which are primarily driven by:

- **Solar heating**: Uneven heating of Earth's surface
- **Rotation**: Coriolis effect influences wind direction
- **Topography**: Mountains, valleys, and water bodies affect wind patterns

### Global Wind Patterns

The Earth's rotation and uneven heating create distinct wind patterns:

1. **Trade Winds**: Blow from east to west near the equator
2. **Westerlies**: Prevail in mid-latitudes (30-60°)
3. **Polar Easterlies**: Found near the poles

## Atmospheric Boundary Layer (ABL)

The ABL is the lowest part of the atmosphere, directly influenced by the Earth's surface. For offshore wind, key characteristics include:

### Vertical Wind Profile

The wind speed typically increases with height following a logarithmic or power law profile:

**Power Law**:
```
V(z) = V_ref × (z/z_ref)^α
```

Where:
- V(z) = wind speed at height z
- V_ref = reference wind speed
- z_ref = reference height
- α = wind shear exponent (typically 0.1-0.14 offshore)

[CHART:windProfile]

### Wind Shear

Wind shear represents the change in wind speed with height. Offshore environments typically have:

- **Lower shear** compared to onshore (α ≈ 0.10-0.14)
- **More uniform profiles** due to reduced surface friction
- **Seasonal variations** influenced by air-sea temperature differences

## Turbulence

Turbulence is characterized by chaotic, irregular flow patterns. Key metrics include:

### Turbulence Intensity (TI)

```
TI = σ_u / U
```

Where:
- σ_u = standard deviation of wind speed
- U = mean wind speed

Typical offshore TI values:
- **Low turbulence**: 0.06-0.08
- **Medium turbulence**: 0.08-0.10
- **High turbulence**: >0.10

[CHART:turbulenceSpectrum]

## Atmospheric Stability

Atmospheric stability significantly affects wind profiles and turbulence:

### Stability Classes

1. **Unstable (Convective)**
   - Occurs when surface is warmer than air
   - Enhanced vertical mixing
   - Lower wind shear
   - Higher turbulence

2. **Neutral**
   - No temperature gradient
   - Logarithmic wind profile
   - Moderate turbulence

3. **Stable**
   - Surface cooler than air
   - Suppressed vertical mixing
   - Higher wind shear
   - Lower turbulence

### Monin-Obukhov Theory

The stability parameter ζ = z/L, where L is the Obukhov length:

```
L = -u*³ / (κ × g/T × w'θ')
```

## Statistical Wind Analysis

### Weibull Distribution

Wind speed distributions are commonly described by the Weibull function:

```
f(v) = (k/A) × (v/A)^(k-1) × exp[-(v/A)^k]
```

Parameters:
- A = scale parameter (related to mean wind speed)
- k = shape parameter (typically 2.0-2.5 offshore)

[CHART:weibullDistribution]

### Wind Rose Analysis

Wind roses show the frequency distribution of wind speeds and directions:

[CHART:windRose]

## Power Production Theory

### Power in the Wind

The power available in wind is:

```
P = 0.5 × ρ × A × V³
```

Where:
- ρ = air density (kg/m³)
- A = swept area (m²)
- V = wind speed (m/s)

### Betz Limit

The theoretical maximum power extraction efficiency is 59.3% (16/27).

### Power Curve

A typical wind turbine power curve shows:

1. **Cut-in speed**: 3-5 m/s
2. **Rated speed**: 12-15 m/s
3. **Cut-out speed**: 25 m/s

[CHART:powerCurve]

## Offshore-Specific Considerations

### Sea Breeze Effects

- **Daytime**: Land heats faster, creating onshore flow
- **Nighttime**: Land cools faster, creating offshore flow
- **Magnitude**: Can reach 5-10 m/s

### Wave-Wind Interactions

- **Growing seas**: Waves extract momentum from wind
- **Swell**: Minimal impact on wind profile
- **Wave age**: Affects surface roughness

### Internal Boundary Layers

When air flows from land to sea:
- New boundary layer develops
- Height grows with fetch distance
- Affects turbine inflow conditions

## Summary

Understanding these theoretical foundations is essential for:
- Accurate wind resource assessment
- Optimal turbine selection and placement
- Reliable energy production estimates
- Effective wind farm design

The offshore environment presents unique advantages:
- Higher and more consistent wind speeds
- Lower turbulence
- Larger areas for development
- Reduced visual and noise impacts