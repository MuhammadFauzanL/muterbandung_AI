export type FavoritePlaceType =
  | 'nature'
  | 'culinary'
  | 'shopping'
  | 'history'
  | 'culture'
  | 'wildlife'
  | 'religion'
  | 'education'
  | 'family';

export type FavoriteActivity =
  | 'healing'
  | 'photo_spot'
  | 'adventure';

export type VisitorTarget = 'family' | 'child_friendly';

export type PreferredAtmosphere = 'indoor' | 'outdoor' | 'night';

export interface UserPreferencePayload {
  favoritePlaceTypes: FavoritePlaceType[];
  favoriteActivities: FavoriteActivity[];
  visitorTarget: VisitorTarget | null;
  preferredAtmospheres: PreferredAtmosphere[];
  freeOnly: boolean;
}

export interface UserPreference extends UserPreferencePayload {
  id: string;
  userId: string;
  createdAt: string;
  updatedAt: string;
}
