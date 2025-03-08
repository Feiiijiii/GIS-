export interface Spot {
  id: string;
  name: string;
  description: string;
  shortDesc?: string;
  longitude: number;
  latitude: number;
  coordinates: [number, number];
  address: string;
  openTime: string;
  price: string;
  ticket_price: number;
  imageUrl?: string;
  tags: string[];
  suggestedTime: string;
}

export interface RouteStep {
  instruction: string;
  distance: string;
  duration: string;
  polyline: string;
}

export interface Route {
  id: string;
  name: string;
  description: string;
  spots: Spot[];
  duration: string;
  estimatedCost: number;
  transportation: string;
  distance: string;
  difficulty: 'easy' | 'moderate' | 'hard';
  path?: RouteStep[];
}

export interface RoutePreferences {
  days: number;
  preferences: string[];
  budget: 'low' | 'medium' | 'high';
  transportation: 'public' | 'car' | 'walk';
} 