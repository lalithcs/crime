// Predefined locations for Hyderabad and Chicago
export const HYDERABAD_LOCATIONS = [
  // Central Hyderabad
  { name: "Madhapur", lat: 17.4485, lng: 78.3908 },
  { name: "Gachibowli", lat: 17.4400, lng: 78.3487 },
  { name: "Hitech City", lat: 17.4435, lng: 78.3772 },
  { name: "Begumpet", lat: 17.4455, lng: 78.4682 },
  { name: "Secunderabad", lat: 17.4399, lng: 78.4983 },
  { name: "Banjara Hills", lat: 17.4183, lng: 78.4485 },
  { name: "Jubilee Hills", lat: 17.4239, lng: 78.4095 },
  { name: "Ameerpet", lat: 17.4372, lng: 78.4482 },
  { name: "Charminar", lat: 17.3616, lng: 78.4747 },
  
  // Western Hyderabad
  { name: "Kukatpally", lat: 17.4849, lng: 78.4138 },
  { name: "Miyapur", lat: 17.4968, lng: 78.3585 },
  { name: "Kondapur", lat: 17.4652, lng: 78.3636 },
  { name: "Manikonda", lat: 17.4027, lng: 78.3817 },
  { name: "Lingampally", lat: 17.4914, lng: 78.3255 },
  { name: "KPHB Colony", lat: 17.4923, lng: 78.3912 },
  { name: "Nizampet", lat: 17.5078, lng: 78.3951 },
  
  // Eastern Hyderabad
  { name: "Uppal", lat: 17.4065, lng: 78.5591 },
  { name: "LB Nagar", lat: 17.3427, lng: 78.5520 },
  { name: "Dilsukhnagar", lat: 17.3687, lng: 78.5248 },
  { name: "Nacharam", lat: 17.4436, lng: 78.5504 },
  { name: "Habsiguda", lat: 17.4179, lng: 78.5414 },
  { name: "Tarnaka", lat: 17.4315, lng: 78.5293 },
  { name: "Ramanthapur", lat: 17.4098, lng: 78.5542 },
  
  // Medchal-Malkajgiri District
  { name: "Malkajgiri", lat: 17.4474, lng: 78.5268 },
  { name: "Sainikpuri", lat: 17.4936, lng: 78.5392 },
  { name: "AS Rao Nagar", lat: 17.4850, lng: 78.5570 },
  { name: "Kapra", lat: 17.4586, lng: 78.5666 },
  { name: "Medchal", lat: 17.6282, lng: 78.4814 },
  { name: "Alwal", lat: 17.5038, lng: 78.5131 },
  { name: "Kompally", lat: 17.5416, lng: 78.4903 },
  { name: "Quthbullapur", lat: 17.5021, lng: 78.4530 },
  { name: "Balanagar", lat: 17.4719, lng: 78.4423 },
  { name: "Cherlapally", lat: 17.4267, lng: 78.5684 },
  { name: "Keesara", lat: 17.4804, lng: 78.6152 },
  { name: "Ghatkesar", lat: 17.4502, lng: 78.6864 },
  { name: "Shamirpet", lat: 17.5592, lng: 78.5261 },
  
  // Southern Hyderabad
  { name: "Mehdipatnam", lat: 17.3933, lng: 78.4404 },
  { name: "Tolichowki", lat: 17.3988, lng: 78.4087 },
  { name: "Attapur", lat: 17.3640, lng: 78.4093 },
  { name: "Rajendranagar", lat: 17.3222, lng: 78.4069 },
  { name: "Shamshabad", lat: 17.2380, lng: 78.3990 },
  
  // Northern Hyderabad
  { name: "Jeedimetla", lat: 17.5085, lng: 78.4458 },
  { name: "Bollaram", lat: 17.5485, lng: 78.4394 },
  { name: "Patancheru", lat: 17.5336, lng: 78.2646 },
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
