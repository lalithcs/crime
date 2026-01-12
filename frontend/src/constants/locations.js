// Predefined locations for Hyderabad and Chicago
export const HYDERABAD_LOCATIONS = [
  { name: "Madhapur", lat: 17.450, lng: 78.390 },
  { name: "Gachibowli", lat: 17.440, lng: 78.355 },
  { name: "Hitech City", lat: 17.450, lng: 78.380 },
  { name: "Begumpet", lat: 17.445, lng: 78.468 },
  { name: "Secunderabad", lat: 17.440, lng: 78.503 },
  { name: "Banjara Hills", lat: 17.418, lng: 78.448 },
  { name: "Kukatpally", lat: 17.493, lng: 78.398 },
  { name: "LB Nagar", lat: 17.343, lng: 78.553 },
  { name: "Dilsukhnagar", lat: 17.373, lng: 78.528 },
  { name: "Charminar", lat: 17.363, lng: 78.473 },
  { name: "Jubilee Hills", lat: 17.432, lng: 78.408 },
  { name: "Kondapur", lat: 17.465, lng: 78.365 },
  { name: "Ameerpet", lat: 17.437, lng: 78.448 },
  { name: "Uppal", lat: 17.406, lng: 78.556 },
  { name: "Miyapur", lat: 17.495, lng: 78.353 },
];

export const CHICAGO_LOCATIONS = [
  { name: "The Loop", lat: 41.8781, lng: -87.6298 },
  { name: "Lincoln Park", lat: 41.9210, lng: -87.6532 },
  { name: "Hyde Park", lat: 41.7944, lng: -87.5907 },
  { name: "Wicker Park", lat: 41.9095, lng: -87.6773 },
  { name: "River North", lat: 41.8919, lng: -87.6278 },
  { name: "Lakeview", lat: 41.9395, lng: -87.6541 },
  { name: "Gold Coast", lat: 41.9026, lng: -87.6296 },
  { name: "South Loop", lat: 41.8708, lng: -87.6267 },
  { name: "Old Town", lat: 41.9117, lng: -87.6370 },
  { name: "West Loop", lat: 41.8832, lng: -87.6502 },
];

export const ALL_LOCATIONS = [
  ...HYDERABAD_LOCATIONS.map(loc => ({ ...loc, city: "Hyderabad" })),
  ...CHICAGO_LOCATIONS.map(loc => ({ ...loc, city: "Chicago" })),
];
